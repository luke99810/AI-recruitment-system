"""AI 模拟面试页。

数字人渲染与 TTS 播报仍留在 main.py（它们和 Streamlit 的
components.v1 / 音频注入耦合），这里**通过参数注入**而不是反向 import ——
否则 main → views → main 会绕成循环导入。
"""
import streamlit as st

from app.ui import (
    empty_state, page_header, pill, progress_steps, question_card,
    score_color, section, stat_grid,
)

STEPS = ["上传材料", "智能分析", "AI 面试", "评估报告"]


def render(render_digital_human=None, speak=None) -> None:
    page_header("AI 模拟面试", "多维度追问 · 数字人交互 · 实时评估", "🤖")

    if not st.session_state.get("analysis_done"):
        progress_steps(STEPS, 0)
        empty_state(
            "请先完成简历分析",
            "切换到「简历分析」，上传 JD 与简历后系统会自动生成面试题库",
            "📄",
        )
        return

    progress_steps(STEPS, 2)
    if not st.session_state.get("interview_started"):
        _render_prep()
    else:
        _render_active(render_digital_human, speak)


def _render_prep() -> None:
    questions = st.session_state.get("all_questions") or []
    match = st.session_state.get("match_result") or {}
    jd_title = (st.session_state.get("jd_data") or {}).get("title", "未知岗位")
    score = match.get("overall_score", 0)

    stat_grid([
        {"label": "目标岗位", "value": jd_title},
        {"label": "题库总量", "value": f"{len(questions)} 道"},
        {"label": "本次抽取", "value": f"{st.session_state.n_rounds} 道",
         "hint": "可在左侧「设置」调整"},
        {"label": "简历匹配度", "value": score, "color": score_color(score),
         "hint": match.get("recommendation", "")},
    ])

    st.markdown("")
    st.info(
        f"系统将从 {len(questions)} 道题中随机抽取 {st.session_state.n_rounds} 道，"
        "并根据你的回答实时追问。面试过程可随时结束并生成报告。"
    )

    with st.expander("题库预览", expanded=False):
        st.markdown(
            "".join(question_card(q, i + 1) for i, q in enumerate(questions[:9])),
            unsafe_allow_html=True,
        )
        if len(questions) > 9:
            st.caption(f"另有 {len(questions) - 9} 道未展示")

    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        if st.button("开始面试", type="primary", use_container_width=True):
            from app.question_sampler import sample_questions_for_interview
            selected, remaining = sample_questions_for_interview(
                questions, st.session_state.n_rounds)
            st.session_state.selected_questions = selected
            st.session_state.remaining_pool = remaining
            st.session_state.interview_started = True
            st.rerun()


def _render_active(render_digital_human, speak) -> None:
    from app.interviewer import InterviewerAgent, InterviewState

    if st.session_state.get("interviewer") is None:
        with st.spinner("正在启动面试官…"):
            try:
                agent = InterviewerAgent(
                    max_rounds=len(st.session_state.selected_questions) + 2)
                agent.load_parsed_data(st.session_state.jd_data, st.session_state.resume_data)
                agent.initialize_persona()
                agent.inject_questions(
                    st.session_state.selected_questions, st.session_state.remaining_pool)
                greeting, first_q = agent.generate_opening()
                st.session_state.interviewer = agent
                st.session_state.chat_messages = [
                    {"role": "interviewer", "content": greeting},
                    {"role": "interviewer", "content": first_q},
                ]
                if st.session_state.tts_enabled and speak:
                    speak(first_q)
                st.rerun()
            except Exception as e:                    # noqa: BLE001
                st.error(f"面试官初始化失败：{e}")
                st.stop()

    agent = st.session_state.interviewer
    done = (agent.state in (InterviewState.REPORTING, InterviewState.DONE)
            or st.session_state.get("interview_done"))

    # ── 进度条 ────────────────────────────────
    pct = int(len(agent.turns) / agent.max_rounds * 100) if agent.max_rounds else 0
    st.markdown(
        f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:6px">'
        + pill("面试中" if not done else "已结束", "brand" if not done else "success")
        + f'<span style="font-size:13px;color:var(--text-2)">'
          f'{agent.persona.get("persona_name", "面试官")} · '
          f'{agent.jd_data.get("title", "岗位")} · '
          f'第 {len(agent.turns)}/{agent.max_rounds} 轮</span></div>'
        f'<div class="br-track" style="height:6px;margin-bottom:16px">'
        f'<div class="br-fill" style="width:{pct}%;background:var(--brand)"></div></div>',
        unsafe_allow_html=True,
    )

    col_chat, col_side = st.columns([2.6, 1], gap="large")

    with col_side:
        if st.session_state.get("digital_human_enabled") and render_digital_human:
            last = next((m["content"] for m in reversed(st.session_state.chat_messages)
                         if m["role"] == "interviewer"), "")
            render_digital_human(last, agent.persona.get("persona_name", "面试官"))
        st.markdown("")
        st.markdown(
            f'<div class="kv"><span class="k">人格</span>'
            f'<span class="v">{agent.persona.get("persona_type", "balanced")}</span></div>'
            f'<div class="kv"><span class="k">已覆盖维度</span>'
            f'<span class="v">{len(agent.covered_dimensions)}</span></div>'
            f'<div class="kv"><span class="k">题库剩余</span>'
            f'<span class="v">{len(agent.remaining_pool)}</span></div>'
            f'<div class="kv"><span class="k">待覆盖</span>'
            f'<span class="v">{"、".join(agent.pending_dimensions[:2]) or "—"}</span></div>',
            unsafe_allow_html=True,
        )

    with col_chat:
        # ★ 改用 st.chat_message：原来是手搓 HTML 气泡塞进一个固定高度的
        #   div，长回答会被截断到 500 字且不能滚动。原生组件自带头像、
        #   自动换行与可选中文本。
        for msg in st.session_state.chat_messages:
            is_itv = msg["role"] == "interviewer"
            with st.chat_message("assistant" if is_itv else "user",
                                 avatar="🎓" if is_itv else "🙋"):
                st.markdown(msg["content"])

        if not done:
            answer = st.chat_input("输入你的回答…")
            if answer and answer.strip():
                _handle_answer(answer.strip(), speak)
            if st.button("结束面试", use_container_width=True):
                closing = agent._generate_closing()
                st.session_state.chat_messages.append(
                    {"role": "interviewer", "content": closing})
                st.session_state.interview_done = True
                agent.state = InterviewState.REPORTING
                st.rerun()
        else:
            st.success("面试已结束")
            if st.button("查看评估报告", type="primary", use_container_width=True):
                _generate_report()


def _handle_answer(text: str, speak) -> None:
    from app.interviewer import InterviewState
    agent = st.session_state.interviewer
    st.session_state.chat_messages.append({"role": "candidate", "content": text})

    with st.spinner("面试官思考中…"):
        result = agent.process_answer(text)

    msg = result.get("message", "")
    st.session_state.chat_messages.append({"role": "interviewer", "content": msg})
    if result.get("interview_ongoing"):
        if st.session_state.tts_enabled and msg and speak:
            speak(msg)
    else:
        st.session_state.interview_done = True
        agent.state = InterviewState.REPORTING
    st.rerun()


def _generate_report() -> None:
    from app.reporter import generate_report
    agent = st.session_state.interviewer
    try:
        st.session_state.report_data = generate_report(agent.get_interview_data())
        st.session_state.interview_done = True
        st.session_state.active_tab = "report"
        st.session_state.pop("_nav_radio", None)
    except Exception as e:                            # noqa: BLE001
        st.error(f"报告生成失败：{e}")
    st.rerun()
