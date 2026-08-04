
"""
Agent Harness 执行护栏：为每个 Agent 提供输入/输出校验、降级策略、重试机制。

五级降级链：
  Level 1: JSON 修复
  Level 2: 重新生成（降低temperature）
  Level 3: 模板兜底
  Level 4: 降级输出（标记 degraded:true）
  Level 5: 硬失败（抛出异常）
"""

from __future__ import annotations
import json
import re
import time
import traceback
from dataclasses import dataclass, field
from typing import Any, Callable, Optional
from enum import Enum


class FallbackLevel(Enum):
    """降级级别"""
    JSON_FIX = 1        # JSON修复
    REGENERATE = 2      # 重新生成
    TEMPLATE = 3        # 模板兜底
    DEGRADED = 4        # 降级输出
    HARD_FAIL = 5       # 硬失败


@dataclass
class ValidationError:
    """校验错误"""
    field: str
    message: str
    severity: str = "error"  # error | warning
    expected: Any = None
    actual: Any = None


@dataclass
class HarnessResult:
    """Harness 执行结果"""
    data: Any                           # 最终输出数据
    passed: bool = True                 # 是否通过所有校验
    errors: list[ValidationError] = field(default_factory=list)
    degraded: bool = False              # 是否降级输出
    fallback_level: Optional[FallbackLevel] = None
    attempts: int = 1
    total_duration_ms: float = 0
    logs: list[str] = field(default_factory=list)


@dataclass
class HarnessConfig:
    """Harness 配置"""
    max_retries: int = 3
    timeout_seconds: int = 90
    temperature: float = 0.3
    temperature_fallback: float = 0.1    # 降级时使用的温度
    max_tokens: int = 8192
    enable_metrics: bool = True


class AgentHarness:
    """
    Agent 执行护栏。

    Usage:
        harness = AgentHarness(config=HarnessConfig(max_retries=3))

        def my_agent(inputs: dict, attempt: int = 0) -> dict:
            # attempt 可用于调整行为（如降低temperature）
            ...

        result = harness.run(
            agent_fn=my_agent,
            input_data={"jd_text": "...", "resume_text": "..."},
            schema={"type": "object", "required": ["overall_score", "questions"]},
            fallback_template=default_output_template,
        )
    """

    def __init__(self, config: HarnessConfig = None, agent_name: str = "agent"):
        self.config = config or HarnessConfig()
        self.agent_name = agent_name
        self.metrics: list[dict] = []  # 执行指标

    def run(
        self,
        agent_fn: Callable,
        input_data: dict,
        schema: dict = None,
        fallback_template: Any = None,
    ) -> HarnessResult:
        """
        执行 Agent 并应用完整 Harness 保护。

        Args:
            agent_fn: Agent 执行函数 fn(inputs, attempt) -> output
            input_data: 输入数据
            schema: 期望的 JSON Schema（用于输出校验）
            fallback_template: 兜底模板（Level 3 使用）

        Returns:
            HarnessResult: 包含最终数据和执行元信息
        """
        t0 = time.time()
        logs = []
        input_data = input_data or {}

        # ── Phase 1: 输入校验 ──────────────────────
        validated_input = self._validate_input(input_data, schema)
        logs.append(f"[{self.agent_name}] Input validated: {len(input_data)} keys")

        result = None
        attempt = 0

        for attempt in range(self.config.max_retries):
            try:
                # ── Phase 2: 执行 Agent ──────────────
                logs.append(f"[{self.agent_name}] Attempt {attempt + 1}/{self.config.max_retries}")
                output = agent_fn(validated_input, attempt=attempt)

                # ── Phase 3: 输出校验 ────────────────
                if schema:
                    errors = self._validate_output(output, schema)
                    if not errors:
                        logs.append(f"[{self.agent_name}] Output passed validation")
                        return HarnessResult(
                            data=output,
                            passed=True,
                            attempts=attempt + 1,
                            total_duration_ms=(time.time() - t0) * 1000,
                            logs=logs,
                        )
                    else:
                        logs.append(f"[{self.agent_name}] Output failed: {len(errors)} errors")
                        # Level 1: JSON 修复
                        if attempt == 0:
                            logs.append(f"[{self.agent_name}] Level 1: JSON fix")
                            fixed = self._try_json_fix(output, schema)
                            if fixed is not None:
                                return HarnessResult(
                                    data=fixed,
                                    passed=True,
                                    attempts=attempt + 1,
                                    total_duration_ms=(time.time() - t0) * 1000,
                                    logs=logs,
                                )
                        # Level 2: 重新生成
                        if attempt < self.config.max_retries - 1:
                            logs.append(f"[{self.agent_name}] Level 2: Regenerate with lower temperature")
                            input_data["_fallback"] = True
                            input_data["_errors"] = [e.message for e in errors]
                            continue
                else:
                    # 无 schema → 直接通过
                    return HarnessResult(
                        data=output,
                        passed=True,
                        attempts=attempt + 1,
                        total_duration_ms=(time.time() - t0) * 1000,
                        logs=logs,
                    )

            except Exception as e:
                logs.append(f"[{self.agent_name}] Exception: {e}")
                if attempt == self.config.max_retries - 1:
                    # 最后一次尝试也失败
                    break
                continue

        # ── Phase 4: 降级策略 ──────────────────────
        # Level 3: 模板兜底
        if fallback_template is not None:
            logs.append(f"[{self.agent_name}] Level 3: Template fallback")
            return HarnessResult(
                data=fallback_template,
                passed=False,
                degraded=True,
                fallback_level=FallbackLevel.TEMPLATE,
                errors=[ValidationError("output", "Used template fallback")],
                attempts=attempt + 1,
                total_duration_ms=(time.time() - t0) * 1000,
                logs=logs,
            )

        # Level 4-5: 硬失败
        logs.append(f"[{self.agent_name}] Level 5: Hard fail after {attempt + 1} attempts")
        raise RuntimeError(
            f"[{self.agent_name}] Failed after {self.config.max_retries} attempts. "
            f"Last output: {str(result)[:200] if result else 'N/A'}"
        )

    # ── 输入校验 ────────────────────────────────────

    def _validate_input(self, input_data: dict, schema: dict = None) -> dict:
        """校验输入数据"""
        if not isinstance(input_data, dict):
            raise ValueError(f"[{self.agent_name}] Input must be a dict, got {type(input_data)}")

        if schema and "required" in schema:
            for field in schema["required"]:
                # 以 "input." 前缀标记输入字段
                if field.startswith("input."):
                    key = field.replace("input.", "")
                    if key not in input_data or input_data[key] is None:
                        raise ValueError(f"[{self.agent_name}] Missing required input: {key}")

        return input_data

    # ── 输出校验 ────────────────────────────────────

    def _validate_output(self, output: Any, schema: dict) -> list[ValidationError]:
        """校验输出数据是否符合 Schema"""
        errors = []

        if not isinstance(output, dict):
            return [ValidationError(field="root", message=f"Output must be dict, got {type(output).__name__}")]

        # 检查 required 字段
        if "required" in schema:
            for field in schema["required"]:
                if field not in output or output[field] is None:
                    errors.append(ValidationError(
                        field=field,
                        message=f"Missing required field: {field}",
                        severity="error",
                    ))

        # 检查 properties 类型
        if "properties" in schema:
            for field, props in schema["properties"].items():
                if field in output and output[field] is not None:
                    expected_type = props.get("type")
                    if expected_type == "integer":
                        if not isinstance(output[field], int):
                            errors.append(ValidationError(
                                field=field,
                                message=f"Expected int, got {type(output[field]).__name__}",
                                expected="int",
                                actual=type(output[field]).__name__,
                            ))
                    elif expected_type == "number":
                        if not isinstance(output[field], (int, float)):
                            errors.append(ValidationError(
                                field=field,
                                message=f"Expected number, got {type(output[field]).__name__}",
                            ))
                    elif expected_type == "array":
                        if not isinstance(output[field], list):
                            errors.append(ValidationError(
                                field=field,
                                message=f"Expected array, got {type(output[field]).__name__}",
                            ))
                    elif expected_type == "string":
                        if not isinstance(output[field], str):
                            errors.append(ValidationError(
                                field=field,
                                message=f"Expected string, got {type(output[field]).__name__}",
                            ))

                    # 数值范围检查
                    if "minimum" in props and isinstance(output[field], (int, float)):
                        if output[field] < props["minimum"]:
                            errors.append(ValidationError(
                                field=field,
                                message=f"Value {output[field]} < minimum {props['minimum']}",
                            ))
                    if "maximum" in props and isinstance(output[field], (int, float)):
                        if output[field] > props["maximum"]:
                            errors.append(ValidationError(
                                field=field,
                                message=f"Value {output[field]} > maximum {props['maximum']}",
                            ))

        return errors

    # ── JSON 修复 ───────────────────────────────────

    def _try_json_fix(self, output: Any, schema: dict = None) -> Any:
        """
        Level 1: 尝试修复 JSON 输出。
        如果 output 是字符串，尝试提取和修复 JSON。
        """
        if not isinstance(output, str):
            return None

        text = output

        # 去除 Markdown 代码块标记
        text = re.sub(r"```(?:json)?\s*", "", text)
        text = text.replace("```", "").strip()

        # 尝试直接解析
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # 提取第一个 { } 或 [ ] 块
        for pattern in [r"\{[\s\S]*\}", r"\[[\s\S]*\]"]:
            match = re.search(pattern, text)
            if match:
                candidate = match.group()
                # 补全未闭合的括号和引号
                fixed = self._fix_brackets(candidate)
                try:
                    return json.loads(fixed)
                except json.JSONDecodeError:
                    continue

        return None

    def _fix_brackets(self, text: str) -> str:
        """补全未闭合的括号和引号"""
        # 计算括号差
        brace_diff = text.count("{") - text.count("}")
        bracket_diff = text.count("[") - text.count("]")

        # 检查是否在字符串内
        in_string = False
        escape = False
        for ch in text:
            if escape:
                escape = False
                continue
            if ch == "\\":
                escape = True
                continue
            if ch == '"':
                in_string = not in_string

        result = text
        if in_string:
            result += '"'
        result += "]" * max(0, bracket_diff)
        result += "}" * max(0, brace_diff)

        return result

    # ── 可观测性 ────────────────────────────────────

    def record_metric(self, metric: dict):
        """记录执行指标"""
        if self.config.enable_metrics:
            metric["agent"] = self.agent_name
            metric["timestamp"] = time.time()
            self.metrics.append(metric)

    def get_metrics_summary(self) -> dict:
        """获取指标摘要"""
        if not self.metrics:
            return {}
        total = len(self.metrics)
        return {
            "agent": self.agent_name,
            "total_calls": total,
            "recent_metrics": self.metrics[-5:],
        }
