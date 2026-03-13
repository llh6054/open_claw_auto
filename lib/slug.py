"""
从需求文本生成短提示词，用于输出目录名，便于快速定位。
"""
import hashlib
import re


# 常见前缀 filler 词（无实质语义），生成需求总结时去掉
_PREFIX_FILLER = re.compile(r"^(一|目前|关于|针对|实现|需要|进行|等)+")
_SUFFIX_FILLER = re.compile(r"(一|等)$")


def make_demand_slug(text: str, max_len: int = 10) -> str:
    """
    从需求文本生成需求总结，10 字以内。
    去掉前后 filler 词，保留核心语义，不做简单截取前几位或后几位。
    """
    if not text or not text.strip():
        h = hashlib.md5((text or "").encode("utf-8")).hexdigest()[:6]
        return f"d{h}"
    s = text.strip()
    s = re.sub(r"[\s/\\:*?\"<>|，。、！？；：''""（）【】+]+", "", s)
    s = re.sub(r"[^\u4e00-\u9fa5a-zA-Z0-9]", "", s)
    if not s:
        h = hashlib.md5(text.encode("utf-8")).hexdigest()[:6]
        return f"d{h}"
    s = _PREFIX_FILLER.sub("", s)
    s = _SUFFIX_FILLER.sub("", s)
    if not s:
        h = hashlib.md5(text.encode("utf-8")).hexdigest()[:6]
        return f"d{h}"
    if len(s) > max_len:
        s = s[:max_len]
    return s or "demand"
