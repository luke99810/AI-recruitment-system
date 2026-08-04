"""
集成 UI 模块：将 Harness/Checker/Skills/Flywheel 的可视化组件注入 Streamlit。
"""

import streamlit as st
import json
import os
from pathlib import Path
from .pipeline import RecruitmentPipeline, SkillsManager, create_pipeline
from .skills import SkillRegistry
from .flywheel import FlywheelStore

def render_skills_panel():
    """Skills 管理面板"""
    st.markdown("### Skills 管理")
    manager = SkillsManager(skills_dir=str(Path(__file__).parent / "skills"))
    skills_data = manager.load()
    with st.expander(f"已加载 Skills ({skills_data.get('total', 0)}个)", expanded=False):
        for skill in skills_data.get("skills", []):
            icon = "[ON]" if skill["active"] else "[OFF]"
            c1, c2 = st.columns([3, 1])
            with c1:
                st.markdown(f"{icon} **{skill['name']}** `{skill['skill_id']}`")
                st.caption(f"{skill.get('description', '')[:60]}")
                st.caption(f"触发: `{skill['trigger']}`")
            with c2:
                if st.button("切换", key=f"sk_{skill['skill_id']}"):
                    manager.toggle(skill["skill_id"], not skill["active"])
                    st.rerun()
    with st.expander("插入自定义 Skill", expanded=False):
        sample = 'skill_id: "my-skill"\\nname: "My Skill"\\ncategory: "assessment"\\ntrigger: "on_question_generation"\\nactive: true'
        yaml_text = st.text_area("Skill YAML", height=150, value=sample)
        prompt_text = st.text_area("Prompt 模板", height=100, placeholder="你是招聘专家...")
        if st.button("安装 Skill"):
            try:
                lines = yaml_text.strip().split('\\n')
                sid = None
                for L in lines:
                    if L.startswith('skill_id:'):
                        sid = L.split(':', 1)[1].strip().strip('"').strip("'")
                        break
                if sid:
                    d = Path(__file__).parent / "skills" / sid
                    os.makedirs(d, exist_ok=True)
                    with open(d / "skill.yaml", 'w', encoding='utf-8') as f:
                        f.write(yaml_text)
                    with open(d / "prompt_template.txt", 'w', encoding='utf-8') as f:
                        f.write(prompt_text)
                    st.success(f"Skill {sid} installed!")
                    st.rerun()
                else:
                    st.error("Cannot parse skill_id")
            except Exception as e:
                st.error(f"Failed: {e}")

def render_checker_panel(checker_results):
    """Checker 校准结果面板"""
    if not checker_results:
        return
    st.markdown("### Checker 校准结果")
    for i, cr in enumerate(checker_results):
        verdict = cr.get("verdict", "N/A")
        passed = cr.get("passed", False)
        scores = cr.get("scores", {})
        icon = "PASS" if passed else "FAIL"
        st.markdown(f"#### {'OK' if passed else 'XX'} Check #{i+1}: {verdict}")
        if scores:
            cols = st.columns(5)
            dims = ["数据准确性", "归因正确性", "格式合规", "维度覆盖", "幻觉检测"]
            for j, d in enumerate(dims):
                s = scores.get(d, 0)
                with cols[j]:
                    st.metric(d[:2], s)
        issues = cr.get("issues", [])
        if issues:
            for iss in issues[:5]:
                st.caption(f"[{iss.get('severity','?')}] {iss.get('dim','')}: {iss.get('desc','')[:80]}")
        st.divider()

def render_graph_panel(pipeline):
    """Graph DAG 可视化"""
    if not pipeline or not pipeline.graph:
        return
    st.markdown("### Graph DAG 执行状态")
    s = pipeline.graph.get_execution_summary()
    c1, c2, c3 = st.columns(3)
    c1.metric("节点", s.get("total_nodes", 0))
    c2.metric("成功", s.get("success", 0))
    c3.metric("失败", s.get("failed", 0))
    with st.expander("DAG 拓扑"):
        st.code(pipeline.get_graph_mermaid(), language="mermaid")

def render_flywheel_panel(flywheel_store=None):
    """飞轮统计"""
    if flywheel_store is None:
        flywheel_store = FlywheelStore()
    st.markdown("### Flywheel 飞轮统计 (Loop 3)")
    stats = flywheel_store.get_stats()
    c1, c2, c3 = st.columns(3)
    c1.metric("历史记录", stats.get("total_records", 0))
    c2.metric("均分", f"{stats.get('avg_match_score',0):.0f}")
    c3.metric("标签", len(stats.get("recent_tags", [])))

def run_analysis_with_pipeline(jd_text, resume_text):
    """使用 Graph Pipeline 执行分析"""
    from .llm_client import llm_client
    skill_ids = st.session_state.get("active_skill_ids", [])
    pipeline = create_pipeline(llm_client=llm_client)
    pipeline.setup(jd_text=jd_text, resume_text=resume_text, active_skills=skill_ids, enable_checker=True, enable_flywheel=True)
    summary = pipeline.run()
    st.session_state.jd_data = summary.get("jd_data", {})
    st.session_state.resume_data = summary.get("resume_data", {})
    st.session_state.match_result = summary.get("match_result", {})
    st.session_state.all_questions = summary.get("questions", {}).get("questions", [])
    st.session_state.ambiguity_followups = summary.get("ambiguity_result", {})
    st.session_state.checker_results = summary.get("checker_results", [])
    st.session_state.graph_summary = summary.get("graph_summary", {})
    st.session_state.flywheel_stats = summary.get("flywheel_stats", {})
    st.session_state.skills_used = summary.get("skills_active", [])
    st.session_state.analysis_done = summary.get("success", False)
    st.session_state._pipeline = pipeline
    return summary
