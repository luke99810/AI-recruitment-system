"""
TTS 语音合成模块 — 浏览器内实时播放版

使用 edge-tts（免费、中文效果好）将面试官提问转为语音，
**音频在内存中生成 base64，不写磁盘、不弹外部播放器**。

浏览器通过 <audio autoplay> 直接解码播放，体验接近实时。
"""
import asyncio
import base64
import nest_asyncio

# Streamlit 内部运行着 Tornado asyncio 事件循环，asyncio.run() 会报 RuntimeError。
# nest_asyncio 允许嵌套调用，是 Streamlit + edge-tts 的标准解决方案。
nest_asyncio.apply()


async def _generate_edge_tts_base64(text: str, voice: str = "zh-CN-YunyangNeural",
                                     rate: str = "+5%", pitch: str = "+0Hz") -> str:
    """
    使用 edge-tts stream() 实时生成音频，内存中收集 → 返回 base64 字符串。
    零磁盘写入，零外部播放器。

    Args:
        text: 要朗读的文本
        voice: 语音角色（默认：云扬-专业男声）
        rate: 语速，如 "+10%" / "-10%"
        pitch: 音调，如 "+3Hz" / "-5Hz"

    Returns:
        base64 编码的 MP3 音频字符串，失败返回 None
    """
    try:
        import edge_tts
    except ImportError:
        raise ImportError("请安装 edge-tts: pip install edge-tts")

    communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
    audio_bytes = bytearray()

    # stream() 边生成边收集，无需等全部合成完
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_bytes.extend(chunk["data"])

    if not audio_bytes:
        return None

    return base64.b64encode(bytes(audio_bytes)).decode()


def generate_audio_base64(text: str, voice: str = "zh-CN-YunyangNeural",
                          rate: str = "+5%", pitch: str = "+0Hz") -> str | None:
    """
    同步接口：生成 edge-tts 音频并返回 base64 字符串。
    不写文件、不调外部播放器 — 交给浏览器 <audio> 元素播放。

    Returns:
        base64 字符串，可直接作为 data:audio/mp3;base64,... 的 src
    """
    try:
        return asyncio.run(_generate_edge_tts_base64(text, voice, rate, pitch))
    except ImportError:
        return None
    except Exception as e:
        import traceback
        print(f"[TTS edge-tts] 错误: {e}")
        traceback.print_exc()
        return None


# ============================================================
# 单一数据源：VOICE_REGISTRY
# 同时被 main.py（UI 下拉框）和 speak_text（发音人映射）引用,
# 绝无可能不一致。
# ============================================================
VOICE_REGISTRY = [
    # (voice_code,             display_label,        engine)
    ("zh-CN-YunyangNeural",    "云扬 (专业男声)",     "edge-tts"),
    ("zh-CN-YunjianNeural",    "云健 (热情男声)",     "edge-tts"),
    ("zh-CN-YunxiNeural",      "云希 (阳光男声)",     "edge-tts"),
    ("zh-CN-YunxiaNeural",     "云夏 (亲切男声)",     "edge-tts"),
    ("zh-CN-XiaoxiaoNeural",   "晓晓 (温暖女声)",     "edge-tts"),
    ("zh-CN-XiaoyiNeural",     "晓伊 (活泼女声)",     "edge-tts"),
    # 讯飞精品
    ("x4_jifeng",              "疾风-精品 (专业男声)", "xunfei"),
    ("x4_lingxiaoxuan",        "小璇-精品 (自然女声)", "xunfei"),
    ("x4_lingfeichen",         "飞晨-精品 (温暖男声)", "xunfei"),
    ("x4_lingxiaozhen",        "小臻-精品 (知性女声)", "xunfei"),
    ("x4_lingxiaoyi",          "小伊-精品 (温柔女声)", "xunfei"),
    ("x4_tingting",            "婷婷-精品 (甜美女声)", "xunfei"),
    # 讯飞基础
    ("xiaoyan",                "小燕 (亲切女声)",     "xunfei"),
    ("aisjiuxu",               "许久 (沉稳男声)",     "xunfei"),
    ("aisxping",               "小萍 (知性女声)",     "xunfei"),
    ("aisjinger",              "小婧 (温柔女声)",     "xunfei"),
]

def get_voice_options(engine: str) -> list:
    """返回指定引擎可用的 (display_label, voice_code) 列表"""
    engine_key = "xunfei" if "讯飞" in engine else "edge-tts"
    return [(label, code) for code, label, eng in VOICE_REGISTRY if eng == engine_key]

def get_voice_code(label: str) -> str:
    """通过 display_label 查 voice_code，找不到返回默认云扬"""
    for code, lbl, _ in VOICE_REGISTRY:
        if lbl == label:
            return code
    return "zh-CN-YunyangNeural"

# 兼容旧代码
AVAILABLE_VOICES = {code: code for code, _, _ in VOICE_REGISTRY}
