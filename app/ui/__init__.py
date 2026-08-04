"""视图层公共设施占位文件。

原 v2.2 改造计划把 main.py 中 480 行 <style> 和可复用组件抽到此目录，
拆分为 theme.py（设计 token）和 components.py（复用组件）。由于拆分后
的文件暂未随本次提交一并落地，为避免本包被意外 import 时触发
ModuleNotFoundError（app.ui.theme / app.ui.components 不存在），这里
暂时作为空占位文件保留。待 theme.py / components.py 真正写入后，
再恢复 __all__ 导出。
"""

# 占位：等 theme.py 和 components.py 落地后再启用
# from .theme import inject_theme, TOKENS, score_color, score_tone
# from .components import (
#     page_header, section, stat_grid, score_ring, verdict_banner,
#     question_card, empty_state, kv_row, pill, evidence_list, progress_steps,
# )
#
# __all__ = [
#     "inject_theme", "TOKENS", "score_color", "score_tone",
#     "page_header", "section", "stat_grid", "score_ring", "verdict_banner",
#     "question_card", "empty_state", "kv_row", "pill", "evidence_list",
#     "progress_steps",
# ]
