"""
从需求文本生成短提示词，用于输出目录名，便于快速定位。
"""
import re


def make_demand_slug(text: str, max_len: int = 8) -> str:
    """
    从需求文本生成文件系统安全的短提示词。
    仅保留中文、英文、数字，去除标点与特殊符号，取前 max_len 个字符。
    """
    if not text or not text.strip():
        return "untitled"
    s = text.strip()
    s = re.sub(r"[\s/\\:*?\"<>|，。、！？；：''""（）【】+]+", "", s)
    s = re.sub(r"[^\u4e00-\u9fa5a-zA-Z0-9]", "", s)
    if not s:
        return "untitled"
    if len(s) > max_len:
        s = s[:max_len]
    return s or "untitled"
