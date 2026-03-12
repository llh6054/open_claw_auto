"""
模型预设与快速切换。
环境变量 AUTO_CODE_MODEL=claude|kimi|claude_cli 可批量切换所有技能使用的模型。
预设：claude(iwhalecloud), claude_cli(Claude CLI), kimi(Moonshot)
"""
import os

# 模型预设：别名 -> (backend, model_id)
MODEL_PRESETS: dict[str, tuple[str, str]] = {
    "claude": ("iwhalecloud", "claude-4.5-sonnet"),
    "claude_cli": ("claude_cli", "claude-4.5-sonnet"),
    "kimi": ("ikimi", "moonshot/kimi-k2.5"),
}

# 支持的后端
BACKENDS = ("iwhalecloud", "ikimi", "claude_cli")


def resolve_model(model: str | None, default: str = "claude") -> tuple[str, str]:
    """
    解析模型参数，返回 (backend, model_id)。
    - model 为 None：优先从环境变量 AUTO_CODE_MODEL 读取，否则用 default
    - model 为预设别名（claude/kimi/claude_cli）：返回对应 backend 和 model_id
    - model 为完整 id（如 claude-4.5-sonnet）：返回 iwhalecloud 和该 id
    """
    effective = model or os.environ.get("AUTO_CODE_MODEL", "").strip().lower() or default
    if effective in MODEL_PRESETS:
        return MODEL_PRESETS[effective]
    if model:
        return ("iwhalecloud", model)
    return MODEL_PRESETS.get(default, MODEL_PRESETS["claude"])


def get_model_for_display() -> str:
    """返回当前模型显示名，用于日志。"""
    backend, model_id = resolve_model(None)
    for alias, (b, m) in MODEL_PRESETS.items():
        if b == backend and m == model_id:
            return alias
    return f"{backend}/{model_id}"
