"""国际化（i18n）—— 中/英双语。

════════════════════════════════════════════════════════════════
 设计取舍
════════════════════════════════════════════════════════════════

★ 用【扁平 key + 单一字典】，不用嵌套结构。
  嵌套读起来漂亮，但取值要写 t("nav")["resume"]，一旦某层缺失就是
  KeyError/TypeError，而翻译缺失是最常见的情况。扁平 key + 缺失回退，
  界面永远不会因为漏翻一句话而崩。

★ 缺失时的回退顺序：当前语言 → 中文 → key 本身。
  **回退到 key 本身而不是空字符串** —— 空字符串会让漏翻表现为"这里本来
  就没内容"，而露出 key（如 `nav.settings`）一眼就能看出是漏翻了。
  让缺陷可见，是这个项目里反复出现的同一条原则。

★ 语言状态存在 st.session_state，不落盘。
  切语言是会话级偏好，不该改 .env —— 那会影响别人的会话。
"""

from __future__ import annotations

LANGUAGES = {"zh": "简体中文", "en": "English"}
DEFAULT_LANG = "zh"

_STRINGS: dict[str, dict[str, str]] = {
    # ── 品牌 / 导航 ──────────────────────────────
    "app.name":            {"zh": "智能招聘系统",   "en": "AI Recruiting"},
    "app.tagline":         {"zh": "简历分析 · AI 面试 · 评估报告",
                            "en": "Screening · AI Interview · Assessment"},
    "nav.analysis":        {"zh": "简历分析",       "en": "Screening"},
    "nav.interview":       {"zh": "AI 面试",        "en": "Interview"},
    "nav.report":          {"zh": "评估报告",       "en": "Report"},
    "nav.skills":          {"zh": "Skills",         "en": "Skills"},
    "nav.settings":        {"zh": "设置",           "en": "Settings"},

    # ── 简历分析 ────────────────────────────────
    "analysis.title":      {"zh": "简历智能分析",   "en": "Resume Analysis"},
    "analysis.subtitle":   {"zh": "JD 解析 · 匹配评分 · 试题生成 · 模糊点追问",
                            "en": "JD parsing · Match scoring · Question generation · Follow-ups"},
    "analysis.jd":         {"zh": "职位描述 (JD)",  "en": "Job Description"},
    "analysis.jd_hint":    {"zh": "PDF / DOCX / TXT，或用下方文本框直接粘贴",
                            "en": "PDF / DOCX / TXT, or paste below"},
    "analysis.resume":     {"zh": "候选人简历",     "en": "Candidate Resume"},
    "analysis.resume_hint":{"zh": "PDF / DOCX / TXT，支持中英文简历",
                            "en": "PDF / DOCX / TXT, Chinese & English supported"},
    "analysis.or":         {"zh": "或",             "en": "or"},
    "analysis.paste_jd":   {"zh": "直接粘贴 JD 文本", "en": "Paste JD text"},
    "analysis.paste_ph":   {"zh": "在此粘贴职位描述...", "en": "Paste the job description here..."},
    "analysis.start":      {"zh": "开始分析",       "en": "Start Analysis"},
    "analysis.reset":      {"zh": "重新分析",       "en": "Reset"},

    # ── 设置 ────────────────────────────────────
    "settings.title":      {"zh": "系统设置",       "en": "Settings"},
    "settings.subtitle":   {"zh": "语言 · 模型接入 · 语音引擎",
                            "en": "Language · Model API · Speech engine"},
    "settings.language":   {"zh": "界面语言",       "en": "Language"},
    "settings.model":      {"zh": "模型接入",       "en": "Model API"},
    "settings.provider":   {"zh": "服务商预设",     "en": "Provider preset"},
    "settings.base_url":   {"zh": "API 地址 (Base URL)", "en": "API Base URL"},
    "settings.model_name": {"zh": "模型名称",       "en": "Model name"},
    "settings.api_key":    {"zh": "API Key",        "en": "API Key"},
    "settings.key_kept":   {"zh": "已配置（保持不变）", "en": "Configured (unchanged)"},
    "settings.key_empty":  {"zh": "未配置",         "en": "Not configured"},
    "settings.test":       {"zh": "测试连接",       "en": "Test connection"},
    "settings.save":       {"zh": "保存到 .env",    "en": "Save to .env"},
    "settings.saved":      {"zh": "已保存，重启应用后生效",
                            "en": "Saved. Restart the app to take effect."},
    "settings.test_ok":    {"zh": "连接成功",       "en": "Connection OK"},
    "settings.test_fail":  {"zh": "连接失败",       "en": "Connection failed"},
    "settings.current":    {"zh": "当前生效配置",   "en": "Currently active"},
    "settings.speech":     {"zh": "语音引擎",       "en": "Speech engine"},
    "settings.engine_ok":  {"zh": "可用",           "en": "Available"},
    "settings.engine_no":  {"zh": "不可用",         "en": "Unavailable"},
    "settings.key_help":   {"zh": "留空则保留现有 Key，不会被清除",
                            "en": "Leave blank to keep the existing key"},

    # ── 通用 ────────────────────────────────────
    "common.model":        {"zh": "模型",           "en": "Model"},
    "common.tts":          {"zh": "语音",           "en": "TTS"},
    "common.rounds":       {"zh": "面试题数",       "en": "Questions"},
    "common.settings":     {"zh": "设置",           "en": "Settings"},
    "common.reset_session":{"zh": "重置会话",       "en": "Reset session"},
    "common.tts_toggle":   {"zh": "TTS 语音播报",   "en": "Voice playback"},
    "common.avatar":       {"zh": "虚拟主播",       "en": "Virtual host"},
}


def get_lang() -> str:
    """当前语言。读 st.session_state；非 Streamlit 环境下回退默认值。"""
    try:
        import streamlit as st
        return st.session_state.get("ui_lang", DEFAULT_LANG)
    except Exception:  # noqa: BLE001
        return DEFAULT_LANG


def set_lang(lang: str) -> None:
    import streamlit as st
    st.session_state["ui_lang"] = lang if lang in LANGUAGES else DEFAULT_LANG


def t(key: str, **fmt) -> str:
    """取翻译。缺失时回退 中文 → key 本身（让漏翻可见，而不是显示空白）。"""
    entry = _STRINGS.get(key)
    if entry is None:
        return key
    text = entry.get(get_lang()) or entry.get(DEFAULT_LANG) or key
    return text.format(**fmt) if fmt else text


def missing_report() -> dict[str, list[str]]:
    """哪些 key 缺了哪个语种。

    ★ 提供这个函数是为了让"翻译完整度"可被检查，而不是靠人逐屏点。
      没有它，漏翻只会在用户切到英文时才暴露 —— 而那通常是演示现场。
    """
    out: dict[str, list[str]] = {lang: [] for lang in LANGUAGES}
    for key, entry in _STRINGS.items():
        for lang in LANGUAGES:
            if not entry.get(lang):
                out[lang].append(key)
    return {k: v for k, v in out.items() if v}
