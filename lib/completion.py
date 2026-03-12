"""
通用 LLM 补全：支持输出截断时自动续写，直到完整。
供 req-analysis、design-docs、code-gen 等技能复用。
"""
from typing import Callable


def run_until_complete(
    initial_prompt: str,
    is_truncated: Callable[[str], bool],
    continue_prompt_fn: Callable[[str], str],
    max_tokens: int = 8192,
    max_continue: int = 4,
    model: str | None = None,
    backend: str = "iwhalecloud",
) -> str:
    """
    调用 LLM 直到输出完整（不截断）。
    - initial_prompt: 首次 prompt
    - is_truncated: 检测内容是否被截断
    - continue_prompt_fn: 根据末尾内容生成续写 prompt
    - model: 可选，指定模型（如 claude-4.5-sonnet）
    - backend: "iwhalecloud" | "claude_cli"，代码生成默认用 claude_cli
    """
    if backend == "claude_cli":
        from lib.claude_cli import run_completion as cli_run

        def do_run(prompt: str) -> str:
            return cli_run(prompt)

    else:
        from lib.iwhalecloud import run_completion as whale_run

        kwargs = {"max_tokens": max_tokens}
        if model:
            kwargs["model"] = model

        def do_run(prompt: str) -> str:
            return whale_run(
                messages=[{"role": "user", "content": prompt}],
                **kwargs,
            )

    content = do_run(initial_prompt)
    for _ in range(max_continue):
        if not is_truncated(content):
            break
        tail = content[-1500:] if len(content) > 1500 else content
        extra = do_run(continue_prompt_fn(tail))
        if not extra or len(extra.strip()) < 30:
            break
        content = content.rstrip() + "\n\n" + extra.strip()
    return content


def is_markdown_truncated(content: str) -> bool:
    """检测 Markdown 输出是否被截断。"""
    if not content or len(content.strip()) < 100:
        return True
    stripped = content.rstrip()
    if stripped.count("```") % 2 != 0:
        return True
    last_line = stripped.split("\n")[-1] if "\n" in stripped else stripped
    if len(last_line) < 30 and ("POST" in last_line or "GET" in last_line or "curl" in last_line):
        return True
    if last_line.endswith("...") or last_line.endswith("---"):
        return True
    return False


def is_code_truncated(content: str) -> bool:
    """检测代码输出（=== FILE: === 格式）是否被截断。"""
    if not content or "=== FILE:" not in content:
        return False
    blocks = content.split("=== FILE:")[1:]
    if not blocks:
        return False
    return "=== END ===" not in blocks[-1]


def markdown_continue_prompt(tail: str) -> str:
    """Markdown 续写 prompt 模板。"""
    return f"""以下是文档的前半部分（可能被截断），请从断开处接着写完整。
只输出续写部分，不要重复上文。若上文在代码块内截断，请先补全该代码块再继续。

上文末尾：
```
{tail}
```

请接着写："""


def code_continue_prompt(tail: str) -> str:
    """代码续写 prompt 模板。"""
    return f"""以下是代码生成的前半部分（可能被截断），请从断开处接着写。
格式不变：=== FILE: 相对路径 === 文件内容 === END ===
只输出续写部分，不要重复上文。若在某个文件中间截断，请先补全该文件再继续。

上文末尾：
```
{tail}
```

请接着写："""
