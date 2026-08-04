
"""
RecruitmentPipeline：基于 Graph DAG + Harness + Checker + Skills + Flywheel 的统一招聘流水线。

将原有线性调用封装为 Graph 节点，实现：
- 并行 JD/简历解析
- Harness 包裹每个 Agent 调用
- Checker 校准循环（Loop 2）
- Skills 触发和合并
- Flywheel 存储和检索
"""

import json
import time
from typing import Any, Optional
from pathlib import Path

from .graph import GraphOrchestrator, GraphNode, NodeStatus
from .harness import AgentHarness, HarnessConfig, HarnessResult
from .checker import CheckerAgent, CheckerResult, CALIBRATION_DIMENSIONS
from .skills import SkillRegistry, SkillMerger
from .flywheel import FlywheelStore, FlywheelRecord
from .config import settings


class RecruitmentPipeline:
    """
    招聘流水线编排器。

    Usage:
        pipeline = RecruitmentPipeline(llm_client=client)
        pipeline.setup(jd_text="...", resume_text="...", active_skills=[])
        results = pipeline.run()
        # results contains: jd_data, resume_data, match_result, questions, checker_result
    """

    def __init__(self, llm_client=None, skills_dir: str = None):
        self.llm_client = llm_client

        # ── 核心组件 ──
        self.harness = AgentHarness(
            config=HarnessConfig(max_retries=3, timeout_seconds=90),
            agent_name="recruitment",
        )
        self.checker = CheckerAgent(llm_client=llm_client, max_revision_rounds=3)
        self.skills = SkillRegistry(skills_dir or str(Path(__file__).parent / "skills"))
        self.flywheel = FlywheelStore()

        # ── Graph 编排器 ──
        self.graph = GraphOrchestrator(name="recruitment-pipeline", max_workers=4)

        # ── 状态 ──
        self.jd_text = ""
        self.resume_text = ""
        self.jd_data: dict = {}
        self.resume_data: dict = {}
        self.match_result: dict = {}
        self.questions: dict = {}
        self.checker_results: list[CheckerResult] = []
        self.flywheel_similar: list[FlywheelRecord] = []
        self.execution_log: list[dict] = []

    # ── 初始化 ──────────────────────────────────

    def setup(
        self,
        jd_text: str = "",
        resume_text: str = "",
        active_skills: list = None,
        enable_checker: bool = True,
        enable_flywheel: bool = True,
    ):
        """配置流水线参数"""
        self.jd_text = jd_text
        self.resume_text = resume_text
        self.enable_checker = enable_checker
        self.enable_flywheel = enable_flywheel

        # 加载 Skills
        self.skills.load_all()

        # 激活指定 Skills
        if active_skills:
            for sid in active_skills:
                self.skills.activate(sid)

        # Flywheel RAG 检索
        if enable_flywheel and resume_text:
            self.flywheel_similar = self.flywheel.retrieve_similar(
                resume_text + " " + jd_text, top_k=3
            )

    # ── 构建 Graph ──────────────────────────────

    def _build_graph(self):
        """构建 DAG 拓扑"""
        self.graph = GraphOrchestrator(name="recruitment-pipeline", max_workers=4)

        # 源数据节点
        self.graph.data_pool = {
            "jd_text": self.jd_text,
            "resume_text": self.resume_text,
            "flywheel_similar": self.flywheel_similar,
            "flywheel_notes": self.flywheel.generate_prompt_notes() if self.enable_flywheel else "",
        }

        # Node 1: JD 解析（与 Resume 解析并行）
        self.graph.add_node(GraphNode(
            name="parse_jd",
            fn=self._fn_parse_jd,
            harness=self.harness,
            metadata={"label": "JD解析"},
        ))

        # Node 2: 简历解析（与 JD 解析并行）
        self.graph.add_node(GraphNode(
            name="parse_resume",
            fn=self._fn_parse_resume,
            harness=self.harness,
            metadata={"label": "简历解析"},
        ))

        # Node 3: 匹配评分（依赖 JD + Resume 解析结果）
        self.graph.add_node(GraphNode(
            name="match",
            fn=self._fn_match,
            harness=self.harness,
            depends_on=["parse_jd", "parse_resume"],
            metadata={
                "label": "匹配评分",
                "output_schema": {
                    "type": "object",
                    "required": ["overall_score", "score_breakdown", "recommendation"],
                    "properties": {
                        "overall_score": {"type": "integer", "minimum": 0, "maximum": 100},
                    },
                },
            },
        ))

        # Node 4: 试题生成（依赖匹配结果）
        self.graph.add_node(GraphNode(
            name="generate_questions",
            fn=self._fn_generate_questions,
            harness=self.harness,
            depends_on=["match", "parse_resume", "parse_jd"],
            metadata={
                "label": "试题生成",
                "output_schema": {
                    "type": "object",
                    "required": ["questions"],
                    "properties": {"questions": {"type": "array"}},
                },
            },
        ))

        # Node 5: 模糊点追问
        self.graph.add_node(GraphNode(
            name="ambiguity",
            fn=self._fn_ambiguity,
            harness=self.harness,
            depends_on=["parse_resume", "generate_questions"],
            metadata={"label": "模糊点追问"},
        ))

        # Node 6: Skills 执行（插入到试题生成后）
        self.graph.add_node(GraphNode(
            name="skills_execution",
            fn=self._fn_execute_skills,
            harness=None,  # Skills 自身有简单的错误处理
            depends_on=["generate_questions", "match"],
            metadata={"label": "Skills执行"},
        ))

    # ── Agent 函数 ───────────────────────────────

    def _fn_parse_jd(self, inputs: dict, attempt: int = 0) -> dict:
        """JD 解析 Agent"""
        from .matcher import parse_jd
        jd_text = inputs.get("jd_text", "")
        if not jd_text:
            return {"title": "未知岗位", "error": "JD文本为空"}
        return parse_jd(jd_text)

    def _fn_parse_resume(self, inputs: dict, attempt: int = 0) -> dict:
        """简历解析 Agent"""
        from .matcher import parse_resume
        resume_text = inputs.get("resume_text", "")
        if not resume_text:
            return {"name": "未知候选人", "error": "简历文本为空"}
        return parse_resume(resume_text)

    def _fn_match(self, inputs: dict, attempt: int = 0) -> dict:
        """匹配评分 Agent"""
        from .matcher import calculate_match

        # 优先从命名key取（Graph多依赖模式），fallback到顶层展开的字段
        jd_data = inputs.get("parse_jd") or inputs.get("jd_data") or {}
        resume_data = inputs.get("parse_resume") or inputs.get("resume_data") or {}
        # 如果顶层有展开的字段（单依赖模式），直接使用inputs本身
        if not jd_data and "title" in inputs:
            jd_data = inputs
        if not resume_data and "name" in inputs:
            resume_data = inputs

        result = calculate_match(jd_data, resume_data)

        # 注入 Flywheel 历史上下文
        flywheel_notes = inputs.get("flywheel_notes", "")
        if flywheel_notes and "note" not in result:
            result["_flywheel_notes"] = flywheel_notes

        return result

    def _fn_generate_questions(self, inputs: dict, attempt: int = 0) -> dict:
        """试题生成 Agent"""
        from .question_generator import generate_questions

        jd_data = inputs.get("parse_jd") or inputs.get("jd_data") or {}
        resume_data = inputs.get("parse_resume") or inputs.get("resume_data") or {}
        match_result = inputs.get("match") or inputs.get("match_result") or {}
        # Fallback: if data was flat-merged
        if not jd_data and "title" in inputs:
            jd_data = {k: v for k, v in inputs.items() if k in ("title", "department", "responsibilities", "requirements", "keywords")}
        if not resume_data and "name" in inputs:
            resume_data = {k: v for k, v in inputs.items() if k in ("name", "contact", "education", "skills", "experience", "projects", "awards", "ambiguous_points")}

        return generate_questions(jd_data, resume_data, match_result)

    def _fn_ambiguity(self, inputs: dict, attempt: int = 0) -> dict:
        """模糊点追问 Agent"""
        from .question_generator import generate_ambiguity_followups

        resume_data = inputs.get("parse_resume") or inputs.get("resume_data") or {}
        if not resume_data and "name" in inputs:
            resume_data = inputs
        return generate_ambiguity_followups(resume_data)

    def _fn_execute_skills(self, inputs: dict, attempt: int = 0) -> dict:
        """执行激活的 Skills"""
        active_skills = self.skills.get_active_by_trigger("on_question_generation")
        if not active_skills:
            return {"skills_output": {}, "skills_used": []}

        jd_data = inputs.get("parse_jd") or inputs.get("jd_data") or {}
        resume_data = inputs.get("parse_resume") or inputs.get("resume_data") or {}
        match_result = inputs.get("match") or inputs.get("match_result") or {}

        skill_outputs = {}
        skills_used = []

        for skill in active_skills:
            try:
                prompt = skill.prompt_template.format(
                    jd_data=json.dumps(jd_data, ensure_ascii=False),
                    resume_data=json.dumps(resume_data, ensure_ascii=False),
                    match_result=json.dumps(match_result, ensure_ascii=False),
                )
                # 使用 LLM 生成 Skill 产出
                if self.llm_client:
                    result = self.llm_client.chat(
                        user_prompt=prompt,
                        system_prompt="你是一位招聘专家，请根据Skill要求生成内容。",
                        expect_json=True,
                    )
                    if isinstance(result, dict):
                        questions = result.get("questions", [result])
                        skill_outputs[skill.skill_id] = questions
                        skills_used.append(skill.skill_id)
            except Exception as e:
                print(f"[Skill] {skill.skill_id} failed: {e}")

        return {
            "skills_output": skill_outputs,
            "skills_used": skills_used,
        }

    # ── 运行 ──────────────────────────────────────

    def run(self) -> dict:
        """执行完整流水线"""
        t0 = time.time()

        # 1. 构建 Graph
        self._build_graph()

        # 2. 执行 Graph
        graph_results = self.graph.run()

        # 3. 提取结果
        self.jd_data = self.graph.get_output("parse_jd") or {}
        self.resume_data = self.graph.get_output("parse_resume") or {}
        self.match_result = self.graph.get_output("match") or {}
        self.questions = self.graph.get_output("generate_questions") or {}
        self.ambiguity_result = self.graph.get_output("ambiguity") or {}
        self.skills_result = self.graph.get_output("skills_execution") or {}

        # 4. Checker 校准循环
        if self.enable_checker and self.match_result:
            self._run_checker_loop()

        # 5. Skills 合并
        if self.skills_result and self.skills_result.get("skills_output"):
            merger = SkillMerger()
            base_questions = self.questions.get("questions", [])
            skill_outputs = self.skills_result.get("skills_output", {})
            merged = merger.merge_questions(base_questions, skill_outputs)
            self.questions["questions"] = merged
            self.questions["skills_merged"] = True
            self.questions["skills_used"] = self.skills_result.get("skills_used", [])

        # 6. Flywheel 存储
        if self.enable_flywheel:
            self._store_to_flywheel()

        # 7. 执行摘要
        self.execution_log = self.graph.execution_log
        total_duration = (time.time() - t0) * 1000

        return self.get_summary(total_duration)

    def _run_checker_loop(self):
        """执行 Checker 校准循环"""
        source = {
            "jd_text": self.jd_text,
            "resume_text": self.resume_text,
        }

        # 校验匹配结果
        match_check = self.checker.check(
            agent_output=self.match_result,
            source_data=source,
            output_type="match_result",
        )
        self.checker_results.append(match_check)

        # 校验试题
        if self.questions:
            questions_check = self.checker.check(
                agent_output=self.questions,
                source_data=source,
                output_type="questions_output",
            )
            self.checker_results.append(questions_check)

    def _store_to_flywheel(self):
        """存储到飞轮"""
        record = FlywheelRecord(
            id="",
            jd_summary=self.jd_data.get("title", "")[:200],
            resume_summary=json.dumps(self.resume_data, ensure_ascii=False)[:500],
            match_score=self.match_result.get("overall_score", 0),
            match_result=self.match_result,
            questions=self.questions.get("questions", []),
            checker_feedback=(
                {"issues": [self.checker.to_dict(r).get("issues", []) for r in self.checker_results]}
                if self.checker_results else None
            ),
            tags=[self.jd_data.get("title", ""), self.resume_data.get("name", "")],
        )
        self.flywheel.store(record)

    # ── 结果查询 ──────────────────────────────────

    def get_summary(self, total_duration: float = 0) -> dict:
        """获取执行摘要"""
        graph_summary = self.graph.get_execution_summary()

        return {
            "success": all(
                self.graph.get_result(n) and self.graph.get_result(n).status == NodeStatus.SUCCESS
                for n in ["parse_jd", "parse_resume", "match"]
            ),
            "jd_data": self.jd_data,
            "resume_data": self.resume_data,
            "match_result": self.match_result,
            "questions": self.questions,
            "ambiguity_result": self.ambiguity_result,
            "skills_result": self.skills_result,
            "checker_results": [
                {
                    "verdict": r.verdict if r.verdict else "N/A",
                    "passed": bool(r.overall_pass),
                    "scores": r.calibration_scores if r.calibration_scores else {},
                    "issues": [
                        {"dim": i.dimension or "unknown", "severity": i.severity.value if i.severity else "minor",
                         "desc": i.description or "", "location": i.location or ""}
                        for i in (r.issues or [])
                    ]
                }
                for r in self.checker_results
            ] if self.checker_results else [],
            "checker_passed": all(r.overall_pass for r in self.checker_results) if self.checker_results else False,
            "flywheel_similar_count": len(self.flywheel_similar),
            "flywheel_stats": self.flywheel.get_stats(),
            "graph_summary": graph_summary,
            "total_duration_ms": total_duration,
            "skills_active": self.skills.get_active_ids(),
            "skills_total": self.skills.count(),
        }

    def get_graph_mermaid(self) -> str:
        """获取 Graph 的 Mermaid 可视化"""
        return self.graph.print_dag()

    def get_checker_display(self) -> list[dict]:
        """获取 Checker 结果的前端展示数据"""
        result = []
        for r in self.checker_results:
            result.append({
                "verdict": r.verdict,
                "scores": r.calibration_scores,
                "passed": r.overall_pass,
                "issues_count": len(r.issues),
                "issues": [
                    {"dim": i.dimension, "severity": i.severity.value, "desc": i.description[:100]}
                    for i in r.issues
                ],
            })
        return result


# ── 快捷工厂函数 ───────────────────────────────

def create_pipeline(llm_client=None) -> RecruitmentPipeline:
    """创建流水线实例"""
    return RecruitmentPipeline(llm_client=llm_client)


# ── 独立 Skills 管理 API ────────────────────────

class SkillsManager:
    """Skills 管理器（供 UI 调用）"""

    def __init__(self, skills_dir: str = None):
        self.registry = SkillRegistry(skills_dir)

    def load(self) -> dict:
        self.registry.load_all()
        return self.registry.to_dict()

    def insert(self, skill_id: str) -> dict:
        skill = self.registry.insert(skill_id)
        return {"success": skill is not None, "skill": skill.skill_id if skill else None}

    def delete(self, skill_id: str) -> dict:
        ok = self.registry.delete(skill_id)
        return {"success": ok, "skill_id": skill_id}

    def toggle(self, skill_id: str, active: bool) -> dict:
        if active:
            ok = self.registry.activate(skill_id)
        else:
            ok = self.registry.deactivate(skill_id)
        return {"success": ok, "skill_id": skill_id, "active": active}

    def get_triggers(self) -> list[str]:
        return ["on_question_generation", "on_matching", "on_interview_start"]
