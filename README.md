# AI 智能招聘系统 🎯

> **端到端 AI 招聘一体化平台** — 简历智能分析 → AI模拟面试 → 评估报告生成
>
> 合并自 [AI-Interview Agent](https://github.com/luke99810/AII-Interview-Agent) + [AIOffer-Research](https://github.com/luke99810/AIOffer-Research)
>
> **v2.2** — 五层 Agent 工程架构：Graph DAG + Harness + Checker Loop + Skills + Flywheel

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/Framework-Streamlit-red.svg" alt="Streamlit">
  <img src="https://img.shields.io/badge/LLM-OpenAI_Compatible-green.svg" alt="LLM">
  <img src="https://img.shields.io/badge/Architecture-Harness%2FGraph%2FLoop%2FSkills-orange.svg" alt="Architecture">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License">
  <img src="https://img.shields.io/badge/Version-v2.2-brightgreen.svg" alt="Version">
</p>

## 演示视频

<p align="center">
  <a href="https://github.com/luke99810/AI-recruitment-system/releases/download/v2.0.0-demo/Demo-Video.mp4">
    <img src="https://img.shields.io/badge/⬇️ 下载演示视频-8A2BE2?style=for-the-badge" alt="下载演示视频">
  </a>
</p>

---

## 一、系统架构（五层 Agent 工程）

v2.2 版本的核心升级：从线性管道进化为 **五层 Agent 工程架构**。

```
┌──────────────────────────────────────────────────────────────┐
│                    GRAPH DAG LAYER (编排层)                    │
│  parse_jd ──┐                                                 │
│             ├──→ match ──→ generate_questions ──→ ambiguity   │
│  parse_resume─┘       │              │                        │
│                        │    ┌─────────┴──────────┐             │
│                        │    │   SKILLS HUB        │             │
│                        │    │ (6个预置可插拔Skill) │             │
│                        │    └─────────┬──────────┘             │
│                        └────────→ Skill Merger                │
├──────────────────────────────────────────────────────────────┤
│                   HARNESS LAYER (护栏层)                       │
│  每个 Agent 包裹: 输入校验 → 执行重试 → 输出校验 → 5级降级      │
├──────────────────────────────────────────────────────────────┤
│                    LOOP LAYER (校准层)                         │
│  Checker Agent 五维校验 → PASS 前进 / FAIL 修订 → 最多3轮      │
├──────────────────────────────────────────────────────────────┤
│                   FLYWHEEL LAYER (飞轮层)                      │
│  面试记录 → 向量存储 → RAG检索 → Prompt优化 → 越用越聪明       │
└──────────────────────────────────────────────────────────────┘
```

| 层 | 模块 | 职责 | 关键特性 |
|----|------|------|----------|
| **Graph DAG** | `app/graph.py` | 工作流编排 | 拓扑排序 + 并行执行(JD/简历双路并发) + 显式数据边 |
| **Harness** | `app/harness.py` | 执行护栏 | 5级降级链(JSON修复→重生成→模板→降级→硬失败) |
| **Checker Loop** | `app/checker.py` | 输出校准 | 五维评分(数据准确性/归因正确性/格式合规/维度覆盖/幻觉检测) |
| **Skills** | `app/skills/` | 能力扩展 | 6个预置Skill + 插入/删除/激活/热更新 API |
| **Flywheel** | `app/flywheel.py` | 持续进化 | 历史记录存储 + RAG相似检索 + 常见问题模式自动注入Prompt |
| **Pipeline** | `app/pipeline.py` | 统一编排 | 整合五层到单一入口，兼容旧版线性管道 |

### 1.1 Graph DAG — 并行编排

JD解析和简历解析**并行执行**（而非顺序），通过 Kahn 算法拓扑排序 + ThreadPoolExecutor 实现层内并发。节点间通过显式 data_pool 传递结构化数据，杜绝隐式全局变量。

### 1.2 Harness — 五级降级链

```
输出JSON校验失败
  → Level 1: JSON修复（补全括号、清洗Markdown标记）
  → Level 2: 重新生成（降低 temperature=0.1）
  → Level 3: 模板兜底（标记 degraded:true）
  → Level 4: 降级输出（返回部分可用字段）
  → Level 5: 硬失败（阻断并报错）
```

### 1.3 Checker Loop — 五维校准

| 维度 | 通过规则 | 权重 |
|------|---------|:----:|
| 数据准确性 | 输出信息与简历/JD原文一致性 ≥ 95% | 25% |
| 归因正确性 | 每条评分理由引用原文 | 20% |
| 格式合规 | JSON Schema 100% 匹配 | 15% |
| 维度覆盖 | 面试题覆盖全部5个维度 | 20% |
| 幻觉检测 | 0 编造信息 | 20% |

### 1.4 Skills — 可插拔能力模块

预置 6 个 Skill，通过 trigger 机制挂载到 Graph DAG 的指定节点：

| Skill ID | 名称 | 触发点 | 用途 |
|----------|------|--------|------|
| `tech-coding-test` | 技术笔试 | on_question_generation | 生成编程/算法笔试题 |
| `english-assessment` | 英语评估 | on_question_generation | 生成英语能力面试题 |
| `culture-fit` | 文化契合 | on_question_generation | 生成价值观/文化匹配题 |
| `salary-negotiation` | 薪资谈判 | on_interview_start | 薪资期望探测话术 |
| `campus-recruit` | 校招专项 | on_matching | 调整评分适配校招 |
| `executive-search` | 高管猎头 | on_matching | 调整评分适配高管 |

Skills 支持运行时插入/删除/激活/停用，无需重启系统。每个 Skill 定义为 `skill.yaml` + `prompt_template.txt` 两个文件。

### 1.5 Flywheel — 越用越聪明

每次面试结束后结构化数据存入飞轮存储。新候选人进入时通过 RAG 检索相似历史案例，检索结果自动注入 Prompt。Checker 发现的常见问题模式自动提取并注入到 Prompt 的"注意事项"中。

---

## 二、核心功能

### 2.1 简历分析

| 功能 | 说明 |
|------|------|
| **多格式解析** | PDF/Word/TXT，PyMuPDF→pdfplumber→OCR 三级降级 |
| **智能匹配评分** | 4 维度匹配度（0-100分），含推进/待定/不推进建议 |
| **面试题生成** | 12+ 道题覆盖 5 维度，每题含考察点/难度/评分标准 |
| **模糊点追问** | 3-5 个递进式追问，含 red_flag 危险信号 |
| **Checker 校准** | 五维自动校验 + 最多3轮自动修订 |
| **Skills 增强** | 激活的 Skills 自动生成额外题目并合并 |

### 2.2 AI 模拟面试

| 功能 | 说明 |
|------|------|
| **智能角色扮演** | 3 种面试官人格（严厉技术总监/亲和HR/挑剔业务负责人） |
| **多轮动态对话** | Agent 有记忆、能追问、每轮评估后自主决策 |
| **反思决策机制** | 评估→反思→决策→追踪覆盖维度 |
| **TTS 语音播报** | edge-tts / 讯飞 WebSocket / XTTS 三引擎 fallback |
| **虚拟数字人** | SVG + CSS 动画，口型随语音同步 |
| **面试链接分享** | 一键生成候选人专属链接（48h有效） |
| **语音输入** | 浏览器 Web Speech API 语音识别 |
| **候选人独立页面** | 纯面试页面，无管理功能 |

### 2.3 评估报告

| 功能 | 说明 |
|------|------|
| **5维雷达图** | 交互式 plotly 雷达图 |
| **逐题评审** | 每题题目/回答/AI评分/评语 |
| **加权总分** | 维度权重 × 维度得分 |
| **录用建议** | 强烈推荐/推荐/待定/不推荐 |
| **矛盾标注** | 回答与简历矛盾高亮 |

---

## 三、使用流程

```
┌─────────────────────────────────────────────────────────┐
│                   管理员端 (/)                            │
│                                                          │
│  上传 JD + 简历 → 开始智能分析                             │
│       ↓                                                  │
│  查看：匹配度 · 面试题库 · Checker结果 · Graph状态         │
│       ↓                                                  │
│  管理 Skills（侧边栏激活/停用/安装）                        │
│       ↓                                                  │
│  生成面试链接 → 发给候选人                                 │
│                                                          │
├─────────────────────────────────────────────────────────┤
│                   候选人端 (?role=candidate&token=xxx)     │
│                                                          │
│  打开链接 → 输入姓名 → 语音/文字 → 完成面试                 │
│                                                          │
├─────────────────────────────────────────────────────────┤
│                   管理员端 (评估报告)                      │
│                                                          │
│  雷达图 · 逐题评审 · 录用建议 · 矛盾标注 · 飞轮统计        │
└─────────────────────────────────────────────────────────┘
```

---

## 四、项目结构

```
AI-recruitment-system/
├── run.py                    # 一键启动
├── .env.example              # 环境变量模板
├── requirements.txt          # 依赖清单
├── app/
│   ├── main.py               # 应用外壳：路由 / 侧边栏 / 数字人 / TTS（784 行）
│   │
│   │  # ── v2.3 视图层（从 main.py 2156 行中拆出）──
│   ├── ui/
│   │   ├── theme.py          # ★ 设计 token + 全局样式（唯一样式来源）
│   │   └── components.py     # ★ 可复用组件：页头/结论横幅/题卡/证据列表…
│   ├── views/
│   │   ├── analysis.py       # ★ 简历分析页
│   │   ├── interview.py      # ★ AI 面试页
│   │   └── report.py         # ★ 评估报告页
│   ├── i18n.py               # 中英双语
│   ├── settings_page.py      # 模型 API / 语音引擎配置
│   ├── config.py             # 全局配置
│   ├── llm_client.py         # LLM 客户端（含 JSON 修复）
│   ├── prompts.py            # Prompt 模板（11套）
│   ├── parser.py             # 文档解析（PDF/Word/TXT）
│   │
│   │  # ── v2.2 新架构模块 ──
│   ├── graph.py              # ★ Graph DAG 编排引擎
│   ├── harness.py            # ★ Agent 执行护栏
│   ├── checker.py            # ★ Checker 五维校准
│   ├── pipeline.py           # ★ 统一流水线编排
│   ├── integration.py        # ★ Streamlit UI 集成
│   ├── flywheel.py           # ★ 飞轮存储与 RAG
│   ├── skills/               # ★ Skills 模块
│   │   ├── registry.py       #   Skill 注册表
│   │   ├── loader.py         #   Skill 加载器
│   │   ├── merger.py         #   Skill 合并器
│   │   ├── tech-coding-test/ #   技术笔试 Skill
│   │   ├── english-assessment/#  英语评估 Skill
│   │   ├── culture-fit/      #   文化契合 Skill
│   │   ├── salary-negotiation/#  薪资谈判 Skill
│   │   ├── campus-recruit/   #   校招专项 Skill
│   │   └── executive-search/ #   高管猎头 Skill
│   │
│   │  # ── 原有模块 ──
│   ├── matcher.py            # 匹配度评分
│   ├── question_generator.py # 试题生成
│   ├── question_sampler.py   # 题库抽样
│   ├── interviewer.py        # 面试官 Agent
│   ├── interview_link.py     # 面试链接管理
│   ├── tts_utils.py          # TTS 工具
│   └── xunfei_tts.py         # 讯飞 TTS
├── assets/                   # 静态资源
├── sessions/                 # 飞轮存储目录
├── skills/                   # (备选) Skills 安装目录
└── references/               # 参考文档
```

---

## 五、快速开始

### 环境要求

- Python 3.10+
- LLM API Key（DeepSeek / Qwen / GPT / Kimi 等 OpenAI 兼容接口）

### 安装

```bash
# 1. 克隆
git clone https://github.com/luke99810/AI-recruitment-system.git
cd AI-recruitment-system

# 2. 虚拟环境
python -m venv .venv
.venv\Scriptsctivate    # Windows
# source .venv/bin/activate   # macOS/Linux

# 3. 配置
cp .env.example .env
# 编辑 .env，填入 LLM_API_KEY

# 4. 安装依赖
pip install -r requirements.txt

# 5. 启动
python run.py
# 访问 http://localhost:8501
```

### .env 配置

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `LLM_API_KEY` | LLM API Key（必填） | - |
| `LLM_BASE_URL` | API 地址 | `https://api.deepseek.com/v1` |
| `LLM_MODEL` | 模型名称 | `deepseek-chat` |
| `HOST` / `PORT` | 服务地址/端口 | `127.0.0.1` / `8501` |
| `TTS_ENGINE` | TTS 引擎 | `edge-tts` |

### 新架构使用

启动后自动检测 `app/integration.py` 是否可导入：

- **导入成功** → 启用五层架构，侧边栏出现 Skills 管理面板，分析结果附带 Checker/Graph/Flywheel 面板
- **导入失败** → 自动降级为 v2.1 线性管道，功能不受影响

---

## 六、技术栈

| 层级 | 技术 |
|------|------|
| **前端** | Streamlit + `st.components.v1.html` |
| **LLM** | DeepSeek / Qwen / GPT / Kimi (OpenAI 兼容) |
| **Agent 编排** | 自研 GraphOrchestrator（拓扑排序 + 并行执行） |
| **Agent 护栏** | 自研 AgentHarness（5级降级 + Schema校验） |
| **输出校准** | 自研 CheckerAgent（五维评分 + 修订闭环） |
| **能力扩展** | Skills 模块（YAML定义 + 运行时注册） |
| **持续进化** | FlywheelStore（TF-IDF相似检索 + Prompt自动优化） |
| **文档解析** | PyMuPDF + pdfplumber + RapidOCR 三级降级 |
| **图表** | plotly（雷达图） |
| **TTS** | edge-tts / 讯飞 WebSocket / XTTS DLL |
| **语音识别** | Web Speech API（浏览器内置） |
| **虚拟数字人** | SVG + CSS animation + JS requestAnimationFrame |

---

## 七、技术难点与解决（12项）

| # | 难点 | 解决方案 |
|---|------|---------|
| 1 | Streamlit Widget 状态绑定冲突 | `del session_state["_nav_radio"]` 强制重建 |
| 2 | LLM 面试过早终止 | 放弃 pending_dimensions，只用 max_rounds 硬约束 |
| 3 | 两个异构项目合并 | 统一 app/ 包结构 + session_state 序列化传递 |
| 4 | 候选人独立页面无路由 | `st.query_params` + `st.stop()` 阻断 |
| 5 | 浏览器语音识别 | Web Speech API + postMessage 跨 iframe 通信 |
| 6 | TTS 多引擎 fallback | nest_asyncio + HMAC-SHA256 + ctypes DLL 三路 |
| 7 | 虚拟数字人动画 | 纯 SVG + CSS @keyframes + 15fps requestAnimationFrame |
| 8 | 题库分层抽样 | 每类保底1题 + 随机补足到 N，剩余入备选池 |
| 9 | LLM JSON 不稳定 | 正则清洗 + 自动补全 + 指数退避重试 |
| 10 | PDF 解析鲁棒性 | PyMuPDF→pdfplumber→OCR 三级降级 |
| 11 | **Checker 结构性永不 PASS** | 五个维度按 `output_type` 判定适用性；不适用的维度排除在 `overall_pass` 与加权分之外（详见下方） |
| 12 | **单次分析耗时 4.5 分钟** | Skills 并行 + 两条校准链并行 + 消除无效重生成 → 实测 273.9s → 154.9s |

### 难点 11 详述：一个"防崩溃防对了、默认值取错了"的 bug

Checker 的五个维度里，`维度覆盖` 查的是 `output["questions"]`，`数据准确性`
查的是 `output` 的 `matched_points / gap_points`。但：

- `match_result` 结构上**没有** `questions` → 覆盖度恒为 0 分
- `questions_output` 结构上**没有** `matched_points` → 准确性恒为 0 分

而 `overall_pass` 要求全部维度达标，于是**两条校准链都永远不可能 PASS**。
后果是三重的：verdict 恒为 FAIL、结果恒被打上 `degraded:true`（自我校验输出的
信号是假的）；每次分析必然跑满 3 轮 = 4 次额外 LLM 重生成（实测占 273.9s 里的
约 159s，试题重生成一次就要 60~70s）；演示时评审看到的永远是"校验未通过"。

指纹是 `int(accuracy_passes / max(accuracy_checks, 1) * 100)` 里的
`max(..., 1)` —— 写的人知道分母可能为 0 并防了除零，但把"没什么可查"
变成了"查了，0 分"。**崩溃防对了，默认值取错了。**

修法是引入 `DIMENSION_APPLICABILITY`：不适用的维度**既不计 0 也不计 100**
（计 100 等于伪造通过，同样是假信号），而是排除在判定与加权之外，并在
`CheckerResult.skipped_dimensions` 里显式标注"不适用"。
加权分按实际参与的维度归一化，否则两种输出类型的分数无法互相比较。

修复后实测：试题链 **第 1 轮即 PASS**（0 次重生成），匹配链的
`数据准确性` 在 75 → 87 → 80 之间真实波动 —— 校准循环这才是在做事。

### 难点 12 详述：耗时从哪来（实测，不是估算）

| 环节 | 修复前 | 修复后 |
|---|---|---|
| 解析 JD + 简历（已并行） | 10.3s | 11.8s |
| 匹配评分 | 7.4s | 10.4s |
| 试题生成 | 61.5s | 69.9s |
| 追问 ∥ Skills | 35.2s | 46.2s |
| **Checker 校准循环** | **~159s** | **~17s** |
| **合计** | **273.9s** | **154.9s（−43%）** |

三处改动：

1. **Skills 并行** —— 原来 `for skill in active_skills:` 串行调 LLM，
   默认激活 3 个 `on_question_generation` 的 Skill 就是 3 次往返首尾相接。
   它们各自只读 jd/resume/match、互不依赖，串行没有任何理由。
2. **两条校准链并行** —— 匹配与试题的校准彼此不依赖。并行前先把
   `match_result` 快照给试题链，否则匹配链改到一半的中间态会被读到
   （竞态，且是偶发才现形的那种）。
3. **消除无效重生成** —— 即难点 11。这一条贡献最大。

剩余瓶颈是 `generate_questions` 单节点 70s（一次生成 10+ 道题、覆盖 5 个维度）。
可以按维度拆成 5 个并行调用，但那会改变 Graph 拓扑 ——
任务要求推荐的 DAG 形状是 `QuestionGen → Ambiguity` 串行，
为省时间偏离规定拓扑并不划算，故保留。

详见 `项目开发文档.md`。

---

## 八、License

MIT License

---

## 九、致谢

本项目合并自：
- [AI-Interview Agent](https://github.com/luke99810/AII-Interview-Agent) — AI 模拟面试官
- [AIOffer-Research](https://github.com/luke99810/AIOffer-Research) — 智能简历解析与试题生成

v2.2 架构升级参考：[任务要求文档](C:\Users\宿心\Desktop\任务要求文档.md)
