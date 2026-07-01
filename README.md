# AI 智能招聘系统 🎯

> **端到端 AI 招聘一体化平台** — 简历智能分析 → AI模拟面试 → 评估报告生成
>
> 合并自 [AI-Interview Agent](https://github.com/luke99810/AII-Interview-Agent) + [AIOffer-Research](https://github.com/luke99810/AIOffer-Research)

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/Framework-Streamlit-red.svg" alt="Streamlit">
  <img src="https://img.shields.io/badge/LLM-OpenAI_Compatible-green.svg" alt="LLM">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License">
  <img src="https://img.shields.io/badge/Status-Merged_v2.0-brightgreen.svg" alt="Status">
</p>

## 演示视频 🎬

<p align="center">
  <a href="https://github.com/luke99810/AI-recruitment-system/releases/download/v2.0.0-demo/Demo-Video.mp4">
    <img src="https://img.shields.io/badge/⬇️ 下载演示视频-8A2BE2?style=for-the-badge" alt="下载演示视频">
  </a>
</p>

> ⚠️ **备注**：由于电脑性能和网络卡顿，录制视频时略有加速，实际系统运行流畅。视频已压缩至 50MB 以内上传至 GitHub Releases。

---

## 一、一句话介绍

**上传 JD + 简历 → AI 自动解析匹配 → 生成12+道面试题 → 一键生成候选人面试链接 → 候选人独立面试（支持语音+文字） → 自动生成评估报告。**

---

## 二、核心功能

### 2.1 简历分析

| 功能 | 说明 |
|------|------|
| **📄 多格式解析** | 支持 PDF/Word/TXT，PyMuPDF→pdfplumber→OCR 三级降级策略 |
| **🎯 智能匹配评分** | 技能/经验/学历/项目 4 维度匹配度评估（0-100分），含推进/待定/不推进建议 |
| **📝 面试题生成** | 至少12道题覆盖5个维度（技术基础/项目深挖/场景设计/行为面试/模糊点追问） |
| **🔍 模糊点追问** | 识别简历模糊点，生成3-5个递进式追问，含 red_flag 危险信号 |

### 2.2 AI 模拟面试

| 功能 | 说明 |
|------|------|
| **🎭 智能角色扮演** | 根据 JD 自动生成面试官人格（严厉技术总监 / 亲和 HR / 挑剔业务负责人） |
| **🔄 多轮动态对话** | Agent 有记忆、能追问、每轮评估后自主决策下一步 |
| **🧠 反思决策机制** | 评估 → 反思 → 决策 → 追踪覆盖维度，实现真正的"面试官思维" |
| **🗣 TTS 语音播报** | edge-tts（免费）/ 讯飞 WebSocket / XTTS 离线 三引擎自动 fallback |
| **👤 虚拟数字人** | SVG + CSS 动画虚拟主播，口型随语音同步，极低渲染成本 |
| **🔗 面试链接分享** | 一键生成候选人专属面试链接（48h有效期），自动打包面试配置 |
| **🎤 语音输入** | 候选人端支持浏览器语音识别输入（Web Speech API），同时保留文字输入 |
| **👥 候选人独立页面** | 纯候选人视角面试页面（无侧边栏/无管理功能），即开即面 |

### 2.3 评估报告

| 功能 | 说明 |
|------|------|
| **📊 5维雷达图** | 交互式 plotly 雷达图（岗位匹配/技术能力/沟通表达/综合素质/诚信度） |
| **📋 逐题评审** | 每一题的题目、回答摘要、AI评分、评语 |
| **🏆 加权总分** | 维度权重 × 维度得分 → 综合总分 |
| **✅ 录用建议** | 强烈推荐/推荐录用/待定/不推荐 |
| **🔴 矛盾标注** | 回答与简历矛盾之处高亮标注 |

### 2.4 核心差异化亮点

| 维度 | 传统方案 | 本系统 |
|------|----------|--------|
| **出题方式** | 固定题库，千人一面 | **简历驱动 + JD 对齐**，每人不同 |
| **追问能力** | 无追问，一题一答 | **动态连环追问**，Agent 有记忆 |
| **面试风格** | 中性机械 | **角色扮演**：多种面试官人格 |
| **评估报告** | 人工撰写 | **AI 自动生成**：雷达图+逐题分析+录用建议 |
| **面试分发** | 线下约时间 | **一键生成链接**，候选人自主完成 |
| **输入方式** | 仅文字 | **语音 + 文字** 双模式 |
| **部署形态** | 单机/服务端 | **管理员端 + 候选人端** 分离 |

---

## 三、使用流程

```
┌──────────────────────────────────────────────────────────────────────┐
│                        管理员端 (管理员)                               │
│                                                                      │
│  上传 JD + 简历                                                      │
│       ↓                                                              │
│  点击「开始智能分析」                                                  │
│       ↓                                                              │
│  查看匹配度 · 面试题库 · 模糊点追问                                     │
│       ↓                                                              │
│  点击「📎 生成面试链接」                                               │
│       ↓                                                              │
│  复制链接 ──→ 发给候选人                                               │
│                                                                      │
├──────────────────────────────────────────────────────────────────────┤
│                        候选人端 (候选人)                               │
│                                                                      │
│  打开链接 → 输入姓名 → 🎤语音 / ⌨️打字 → 完成面试                     │
│                                                                      │
├──────────────────────────────────────────────────────────────────────┤
│                        管理员端 (管理员)                               │
│                                                                      │
│  查看评估报告：雷达图 · 逐题评审 · 录用建议 · 矛盾标注                  │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 四、系统架构

### 4.1 整体架构

```
+==========================================================================+
|                  Streamlit 统一前端 (Single Frontend)                     |
|                                                                           |
|   管理员路由 (/)                    候选人路由 (?role=candidate&token=xxx)  |
|  +----------------+-----------+    +----------------------------------+  |
|  | 📄 简历分析    | 🤖 AI面试 |    |  独立面试页面 (无侧边栏/无Tab)     |  |
|  | 📊 评估报告    |           |    |  🎤 语音输入 + ⌨️ 文字输入         |  |
|  +----------------+-----------+    +----------------------------------+  |
+----------|------------------------------|--------------------------------+
           |                              |
+----------v------------------------------v--------------------------------+
|                          业务逻辑层 (app/)                                 |
|                                                                           |
|  ┌──────────────────┐  ┌───────────────────┐  ┌────────────────────┐     |
|  │  matcher.py      │  │  interviewer.py   │  │  parser.py         │     |
|  │  question_gen    │  │  reporter.py      │  │  llm_client.py     │     |
|  │  question_sampler│  │  interview_link   │  │  prompts.py (11)   │     |
|  │                  │  │  tts_utils.py     │  │  config.py         │     |
|  │                  │  │  xunfei_tts.py    │  │                    │     |
|  └──────────────────┘  └───────────────────┘  └────────────────────┘     |
+---------------------------------------------------------------------------+
           |
+----------v---------------------------------------------------------------+
|                          外部服务层                                       |
|  +----------------+  +----------------+  +---------------------------+   |
|  | LLM API        |  | TTS 引擎       |  | 浏览器能力                 |   |
|  | DeepSeek/Qwen  |  | edge-tts (免费) |  | Web Speech API (语音识别) |   |
|  | GPT / Kimi     |  | 讯飞 WebSocket  |  | Canvas/WebSocket          |   |
|  +----------------+  | XTTS 离线 DLL  |  +---------------------------+   |
|                      +----------------+                                   |
+---------------------------------------------------------------------------+
```

### 4.2 数据流

```
用户上传 JD + 简历
       ↓
 parser.py（PyMuPDF→pdfplumber→OCR 三级降级）
       ↓
 ① 简历分析 Tab
   JD解析 → 简历解析 → 匹配评分(0-100) → 12+道面试题 → 模糊点追问
       ↓                                    ↓
   环形图+卡片展示                    session_state 传递
       ↓
  点击 [📎 生成面试链接]
       ↓
  question_sampler.py 分层随机抽取 N 道题
       ↓
  interview_link.py 创建 token + 打包配置 → 生成候选人链接
       ↓                            ↓
  [🚀 自行测试]              发送给候选人
       ↓                            ↓
 ② AI面试 Tab             候选人打开链接
   Agent 多轮对话               ↓
       ↓                   ③ 候选人面试页
 ③ 评估报告 Tab             输入姓名 → Agent初始化
   雷达图 + 逐题评审            → 语音/文字多轮对话
   + 录用建议                  → 面试结束 Token 失效
```

---

## 五、技术难点与挑战

### 5.1 Streamlit Widget 与 Session State 绑定冲突

**挑战**：`st.radio(key="xxx")` 会将 widget 绑定到 `session_state.xxx`，一旦渲染完成，任何代码直接修改 `session_state.xxx` 都会触发 `StreamlitAPIException: cannot be modified after widget is instantiated`。

**场景**：用户浏览简历分析 Tab 时点击"开始 AI 面试"按钮，需要程序化跳转到 AI 面试 Tab。传统方案 `active_tab = st.radio(key="active_tab", ...)` 会绑定 key，导致后续 `st.session_state.active_tab = "🤖 AI 面试"` 报错。

**解决方案**：

```
Radio 用独立 key "_nav_radio"（不绑定业务 key active_tab）
    ↓
Radio 渲染后手动同步：st.session_state.active_tab = active
    ↓
程序化跳转前：del st.session_state["_nav_radio"]  强制 widget 重建
    ↓
st.rerun() → Radio 读取 active_tab 作为 index 重新渲染
```

关键洞察：`del st.session_state["_nav_radio"]` 是 Streamlit 官方支持的 widget 重置方式，下一轮 `st.radio` 的 `index` 参数会重新生效。

### 5.2 LLM 面试决策对齐——过早终止问题

**挑战**：LLM 倾向于高估面试进度。设置 4 道题（max_rounds=6），LLM 在 2 轮后判定 "所有维度已覆盖" 并触发 wrap_up，导致面试提前结束。`pending_dimensions` 作为 LLM 输出的衍生变量，本身不稳定。

**解决方案**：放弃 `pending_dimensions` 作为终止条件，**只保留 `max_rounds` 硬约束**。简化决策逻辑避免了 LLM 主观判断与业务预期的冲突。

```python
# 修复前（不可靠）
if not self.pending_dimensions:
    next_action = "wrap_up"

# 修复后（可靠）
if round_num >= self.max_rounds:
    next_action = "wrap_up"
```

### 5.3 两个异构项目合并——数据贯通与状态管理

**挑战**：AI-Interview Agent 和 AIOffer-Research 是两个独立项目，分别有各自的目录结构、配置方式、数据流。合并面临：
- **目录冲突**：两项目各有 main.py / prompts.py / config.py，需统一到 `app/` 包
- **配置隔离**：两套 `.env` 变量和 Settings 类需要合并
- **数据贯通**：Tab1（分析）→ Tab2（面试）→ Tab3（报告），中间数据全部通过 `st.session_state` 传递，但 InterviewerAgent 包含 LLM client 等不可序列化对象

**解决方案**：

| 问题 | 方案 |
|------|------|
| 目录冲突 | 统一 `app/` 包结构，合并同名模块（prompts.py 扩展至 11 套模板） |
| 配置隔离 | `config.py` 统一所有 Settings，策略枚举区分场景 A/B |
| 数据贯通 | `session_state` 仅存储可序列化数据（jd_data/resume_data/questions），Agent 实例在 Tab2 入口重新构造并注入缓存数据 |
| Agent 初始化 | `interviewer.load_parsed_data(jd_data, resume_data)` 跳过 LLM 解析步骤，`inject_questions()` 跳过题库重新生成 |

### 5.4 候选人独立页面——Streamlit 无后端路由

**挑战**：Streamlit 是单页应用框架，没有原生路由机制。需要实现"管理员端"和"候选人端"两套完全不同的 UI，后者不应显示侧边栏、Tab 导航、配置面板等管理功能。

**解决方案**：

```
main.py 入口处检测 st.query_params
    ↓
?role=candidate&token=xxx → page_candidate() → st.stop()
    ↓ (阻断后续 sidebar + tabs 渲染)
无参数 → 正常渲染管理端 sidebar + tabs
```

候选页面通过 `st.stop()` 阻断后续代码执行，避免管理端 UI 泄漏。Token 机制：
- `interview_link.py` 内存存储 `{token: {config, expires_at, status}}`
- 候选页面通过 `get_interview(token)` 验证有效性
- 面试结束后自动 `deactivate_interview(token)`

### 5.5 浏览器语音识别集成——跨 iframe 通信

**挑战**：为候选人提供语音输入能力，但 Streamlit 没有内置 STT 组件，且 Python 端无法直接访问浏览器麦克风。需要在不增加服务端依赖（如 Whisper API）的前提下实现。

**解决方案**：利用浏览器内置 Web Speech API，通过 `st.components.v1.html` 自定义组件注入 JS 代码：

```
JS 端:
  new SpeechRecognition() → lang='zh-CN'
  recognition.onresult → 获取 transcript
  window.parent.postMessage({type: 'streamlit:setComponentValue', value}, '*')

Python 端:
  voice_text = st.components.v1.html(voice_input_html, height=60)
  if voice_text:
      st.session_state.voice_input_text = voice_text
```

关键点：
- Web Speech API 仅在 Chrome/Edge 中稳定支持中文
- `postMessage` 回传依赖 Streamlit 的 iframe 通信协议
- 通过 `SpeechRecognition` 的 `continuous=false` + `interimResults=false` 确保单次完整识别

### 5.6 TTS 多引擎 Fallback——异步嵌套与 DLL 调用

**挑战**：需要支持三种 TTS 引擎的无缝切换，且各引擎有截然不同的调用方式：

| 引擎 | 接口类型 | 核心难点 |
|------|----------|----------|
| edge-tts | Python async / asyncio | Streamlit 事件循环内 `asyncio.run()` 嵌套冲突 |
| 讯飞 WebSocket | WebSocket + HMAC-SHA256 | 鉴权 URL 构建、流式音频拼接 |
| XTTS 离线 | DLL (ctypes) | C 结构体映射、PCM→WAV 转换、DLL 缺失场景 |

**解决方案**：

```
speak_text(text)
    ↓
    ├─ edge-tts (默认)：nest_asyncio.apply() 解决嵌套，内存 base64 不写磁盘
    ├─ 讯飞 WebSocket：HMAC-SHA256 鉴权 URL → ws.connect() → 收集 audio chunks → base64
    └─ XTTS 离线：ctypes 调用 AEE_lib.dll → PCM buffer → WAV header → base64
    ↓
任何引擎失败 → fallback 到 edge-tts
    ↓
存入 session_state.pending_audio_b64 → 页面底部 <audio autoplay>
```

### 5.7 虚拟数字人——纯 SVG 动画替代方案

**挑战**：虚拟主播需要"像真人"，但项目中无 3D 模型、无视频文件。Canvas 逐帧绘制简陋，性能开销大（60fps 无意义渲染）。需要在视觉质量和渲染成本之间取得平衡。

**解决方案**：纯 SVG 矢量图形方案，综合使用多层动画技术：

| 动画层 | 技术 | 频率 | 效果 |
|--------|------|------|------|
| 呼吸 | CSS `@keyframes breathe` | 3.5s | 身体微微起伏 |
| 眨眼 | CSS `@keyframes blinkE` | 4s | 眼睛闭合 |
| 口型 | JS `requestAnimationFrame` 修改 mouth path `d` 属性 | ~15fps | 说话时嘴巴开合 |

- SVG 直接在 DOM 中渲染，无需 Canvas 双缓冲
- 通过 `st.components.v1.html` iframe 沙箱渲染，避免 Streamlit CSS 冲突
- 15fps 动画帧率大幅降低 CPU 占用

### 5.8 题库分层抽样——保底与动态补题

**挑战**：12+ 道面试题分布在 5 个类别中，用户设置 3-15 轮面试，需要保证：每个类别至少 1 题，总数精确等于设置值，未被选中的题目作为备选池供 Agent 动态切换维度时使用。

**解决方案（question_sampler.py）**：

```
输入：N 轮面试，5 类题目分布
    ↓
Step 1: 每类保底 1 题（遍历 5 类，每类随机抽 1 题）
    ↓
Step 2: 剩余 N-5 题，从全部未抽取题目中随机补齐
    ↓
输出：selected_questions (N 题) + remaining_pool (备用池)
```

面试官 Agent 在 `_get_question_from_pool(dimension)` 中实现：切换维度时优先从 `remaining_pool` 按维度匹配取题，耗尽后才用 LLM 动态生成。

### 5.9 LLM 输出稳定性——JSON 解析的三层防护

**挑战**：LLM 在生成结构化 JSON 时频繁出现截断、多余文本、markdown 代码块包裹、字段缺失等问题，导致下游解析崩溃。

**解决方案（llm_client.py）**：

```
Layer 1 — Prompt 层：JSON Schema 约束 + "只输出 JSON" + 禁 markdown 包裹
    ↓ 仍然失败
Layer 2 — 修复层：正则清洗非 JSON 前缀/后缀 → 自动闭合花括号/方括号
    → 字典截断补全（匹配最后完整 kv → 补闭合 }
    → 数组截断补全（匹配最后一个完整元素 → 补 ]）
    ↓ 仍然失败
Layer 3 — 重试层：指数退避重试（max 3 次）
    → 第 2 次起注入修复指令："Your last output was truncated. Ensure valid JSON."
```

### 5.10 PDF 解析鲁棒性——三级降级策略

| 级别 | 引擎 | 适用场景 | 失败处理 |
|:----:|------|----------|----------|
| 1 | PyMuPDF (fitz) | 文字型 PDF（90% 场景） | 降级到 Level 2 |
| 2 | pdfplumber | 复杂排版 PDF | 降级到 Level 3 |
| 3 | RapidOCR | 扫描件/图片型 PDF | OCR 也失败 → 返回错误 |

每级提取的文本会进行质量检查（min 50 字符），不达标自动降级。避免因单级解析失败导致流程中断。

### 5.11 面试官人格注入——System Prompt 工程

根据 JD 信息动态构造 system prompt，实现三种面试官风格：

| 人格类型 | 语气风格 | 追问烈度 | System Prompt 关键指令 |
|----------|----------|:--------:|------------------------|
| 严厉技术总监 | 直击要害，不容含糊 | 🔴 高 | "对含糊回答穷追不舍，发现矛盾立刻追问" |
| 亲和 HR | 温和引导，注重体验 | 🟢 低 | "保持友善，给候选人多一次阐述机会" |
| 挑剔业务负责人 | 结果导向，挖边界 | 🟡 中 | "关注业务结果和决策逻辑，追问边界条件" |

`PERSONA_GEN_PROMPT` 模板包含角色设定、JD 信息注入、追问策略、语气约束四个模块，LLM 根据 JD 自动选择最匹配的人格类型。

---

## 六、快速开始

### 环境要求

- Python 3.10+
- LLM API Key（支持 DeepSeek / Qwen / GPT / Kimi）

### 安装

```bash
# 1. 克隆仓库
git clone https://github.com/luke99810/AI-recruitment-system.git
cd AI-recruitment-system

# 2. 创建虚拟环境（推荐）
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # macOS/Linux

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env，填入 LLM_API_KEY

# 4. 安装依赖
pip install -r requirements.txt

# 5. 启动
python run.py
# 或直接：
streamlit run app/main.py --server.port 8501
```

启动后访问 `http://localhost:8501`。

### 使用流程

**管理员端**（`http://localhost:8501`）：
1. **简历分析 Tab**：上传 JD + 简历 → "开始智能分析" → 查看匹配度/面试题/模糊点
2. **生成面试链接**：点击 "📎 生成面试链接" → 复制链接发给候选人
3. **自行测试（可选）**：点击 "🚀 自行测试面试" 在系统内模拟
4. **评估报告 Tab**：查看雷达图、逐题评审、录用建议

**候选人端**（打开链接）：
1. 输入姓名 → 开始面试
2. 选择输入方式：🎤 语音（Chrome/Edge）或 ⌨️ 打字
3. 完成全部问题 → 面试结束

---

## 七、配置说明

`.env` 文件主要配置项：

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `LLM_API_KEY` | LLM API Key（必填） | - |
| `LLM_BASE_URL` | LLM API 地址 | `https://api.deepseek.com/v1` |
| `LLM_MODEL` | 模型名称 | `deepseek-chat` |
| `HOST` | 服务地址 | `127.0.0.1` |
| `PORT` | 服务端口 | `8501` |
| `TTS_ENGINE` | TTS 引擎 | `edge-tts` |
| `XUNFEI_APP_ID` | 讯飞 App ID（可选） | - |
| `XUNFEI_API_KEY` | 讯飞 API Key（可选） | - |
| `XUNFEI_API_SECRET` | 讯飞 API Secret（可选） | - |

---

## 八、技术栈

| 层级 | 技术 |
|------|------|
| 前端框架 | Streamlit |
| 前端组件 | `st.components.v1.html` (自定义 HTML/JS)、`st.query_params` (路由) |
| LLM | DeepSeek / Qwen / GPT / Kimi (OpenAI 兼容 API) |
| 文档解析 | PyMuPDF + pdfplumber + RapidOCR |
| 图表 | plotly (雷达图) |
| TTS | edge-tts / 讯飞 WebSocket / XTTS 离线 DLL |
| 语音识别 | Web Speech API (浏览器内置) |
| 虚拟数字人 | SVG + CSS animations + JS requestAnimationFrame |
| 会话管理 | `st.session_state` + 内存 `dict` (token→config) |

---

## 九、License

MIT License

---

## 十、致谢

本项目合并自以下两个开源项目：
- [AI-Interview Agent](https://github.com/luke99810/AII-Interview-Agent) — AI 模拟面试官
- [AIOffer-Research](https://github.com/luke99810/AIOffer-Research) — 智能简历解析与试题生成
