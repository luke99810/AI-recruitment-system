"""评估报告页。

★ 同样按「结论 → 依据 → 明细」收敛；另外修掉一处实际的显示问题：
  雷达图原来把网格线设成 #2d3245、刻度字设成 #9aa0b0 —— 那是给深色底
  配的颜色，而主题已经锁定亮色，于是深色网格压在白底上，刻度几乎看不清。
"""
import streamlit as st

from app.ui import (
    empty_state, evidence_list, page_header, pill, progress_steps,
    score_color, score_ring, section, stat_grid, verdict_banner,
)

STEPS = ["上传材料", "智能分析", "AI 面试", "评估报告"]

REC_TEXT = {
    "strong_hire": "强烈推荐", "hire": "推荐录用",
    "hold": "待定", "no_hire": "不推荐",
}
DIM_LABELS = {
    "job_match": "岗位匹配", "technical_ability": "技术能力",
    "communication": "沟通表达", "comprehensive_quality": "综合素质",
    "integrity": "诚信度",
}


def render() -> None:
    page_header("面试评估报告", "五维雷达 · 逐题评审 · 录用建议", "📊")

    if not st.session_state.get("interview_done"):
        progress_steps(STEPS, 2)
        empty_state("暂无评估报告", "完成「AI 面试」后，系统会自动生成多维度评估报告", "📊")
        return

    progress_steps(STEPS, 3)
    report = st.session_state.get("report_data")
    if not report:
        agent = st.session_state.get("interviewer")
        if agent and getattr(agent, "turns", None):
            with st.spinner("正在生成报告…"):
                from app.reporter import generate_report
                report = generate_report(agent.get_interview_data())
                st.session_state.report_data = report
        else:
            st.warning("暂无面试数据")
            return
    if not report:
        return

    score = report.get("overall_score", report.get("calculated_score", 0))
    rec = report.get("recommendation", "")
    agent = st.session_state.get("interviewer")
    turns = len(agent.turns) if agent else 0

    # ── 结论 ────────────────────────────────────
    verdict_banner(
        score, REC_TEXT.get(rec, rec or "—"),
        report.get("summary") or report.get("overall_comment") or "",
        score_label="综合评分",
    )
    dim_scores = report.get("dimension_scores") or {}
    stat_grid([
        {"label": "面试轮数", "value": turns},
        {"label": "评估维度", "value": len(dim_scores)},
        {"label": "亮点", "value": len(report.get("highlights") or []),
         "color": score_color(90)},
        {"label": "关注点", "value": len(report.get("concerns") or []),
         "color": score_color(60)},
    ])

    # ── 依据：五维 ───────────────────────────────
    if dim_scores:
        section("五维能力评估")
        col_ring, col_radar = st.columns([1, 2], gap="large")
        with col_ring:
            st.markdown(score_ring(score, 150, "综合"), unsafe_allow_html=True)
            st.markdown("")
            for k, v in dim_scores.items():
                s = v.get("score", 0) if isinstance(v, dict) else v
                st.markdown(
                    f'<div class="kv"><span class="k">{DIM_LABELS.get(k, k)}</span>'
                    f'<span class="v" style="color:{score_color(s)}">{s}</span></div>',
                    unsafe_allow_html=True,
                )
        with col_radar:
            _render_radar(dim_scores)

    # ── 亮点 / 关注点 ────────────────────────────
    section("亮点与关注点")
    c1, c2 = st.columns(2, gap="large")
    with c1:
        st.markdown(pill("亮点", "success"), unsafe_allow_html=True)
        evidence_list(report.get("highlights") or [], "success", "★", "未识别到明显亮点")
    with c2:
        st.markdown(pill("关注点", "warning"), unsafe_allow_html=True)
        evidence_list(report.get("concerns") or [], "warning", "!", "未识别到明显关注点")

    if report.get("contradictions"):
        st.markdown("")
        st.markdown(pill("前后矛盾", "danger"), unsafe_allow_html=True)
        evidence_list(report["contradictions"], "danger", "▲")

    # ── 逐题评审（折叠）──────────────────────────
    _render_question_review(report)


def _render_radar(dim_scores: dict) -> None:
    import plotly.graph_objects as go

    cats, vals = [], []
    for k, v in dim_scores.items():
        cats.append(DIM_LABELS.get(k, k))
        vals.append(v.get("score", 0) if isinstance(v, dict) else v)
    if not cats:
        return

    fig = go.Figure(go.Scatterpolar(
        r=vals + [vals[0]], theta=cats + [cats[0]],
        fill="toself", fillcolor="rgba(79,70,229,0.16)",
        line=dict(color="#4f46e5", width=2.5),
        marker=dict(color="#4f46e5", size=7),
        hovertemplate="%{theta}: %{r}<extra></extra>",
    ))
    fig.update_layout(
        polar=dict(
            # ★ 亮色主题下的网格/刻度配色（原来是深色底的配色，白底上几乎看不清）
            radialaxis=dict(range=[0, 100], gridcolor="#e2e8f0", linecolor="#e2e8f0",
                            tickfont=dict(color="#94a3b8", size=10)),
            angularaxis=dict(gridcolor="#e2e8f0", linecolor="#cbd5e1",
                             tickfont=dict(color="#0f172a", size=12)),
            bgcolor="rgba(0,0,0,0)",
        ),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        height=360, margin=dict(l=60, r=60, t=24, b=24), showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)


def _render_question_review(report: dict) -> None:
    q_review = report.get("question_review") or []
    agent = st.session_state.get("interviewer")
    if not q_review and agent:
        q_review = [{
            "round": t.get("round", "?"),
            "question": t.get("question", ""),
            "answer_summary": (t.get("answer") or "")[:200],
            "score": (t.get("evaluation") or {}).get("score", "—"),
            "evaluation": (t.get("evaluation") or {}).get("answer_quality", ""),
        } for t in agent.turns]
    if not q_review:
        return

    section("逐题评审", f"共 {len(q_review)} 题")
    for r in q_review:
        sc = r.get("score", "—")
        tone = "neutral"
        if isinstance(sc, (int, float)) and sc > 0:
            tone = ("success" if sc >= 85 else "brand" if sc >= 70
                    else "warning" if sc >= 55 else "danger")
            sc = f"{int(sc)} 分"
        title = (r.get("question") or "")[:60]
        with st.expander(f'第 {r.get("round", "?")} 轮 · {title}…'):
            st.markdown(pill(str(sc), tone), unsafe_allow_html=True)
            st.markdown(f'**问题**\n\n{r.get("question", "")}')
            st.markdown(f'**回答摘要**\n\n{r.get("answer_summary", "") or "—"}')
            if r.get("evaluation"):
                st.markdown(f'**评价**\n\n{r["evaluation"]}')
