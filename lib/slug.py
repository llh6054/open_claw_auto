"""
从需求文本生成短提示词，用于输出目录名，便于快速定位。
"""
import re


def make_demand_slug(text: str, max_len: int = 24) -> str:
    """
    从需求文本生成文件系统安全的短提示词。
    取前 max_len 个有效字符，替换非法字符为下划线。
    """
    if not text or not text.strip():
        return "untitled"
    s = text.strip()
    s = re.sub(r"[\s/\\:*?\"<>|]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    if not s:
        return "untitled"
    if len(s) > max_len:
        s = s[:max_len].rstrip("_")
    return s or "untitled"
