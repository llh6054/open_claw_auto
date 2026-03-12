#!/usr/bin/env python3
"""需求分析：根据需求生成结构化 Markdown 文档。"""
import argparse
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from lib.completion import (
    is_markdown_truncated,
    markdown_continue_prompt,
    run_until_complete,
)
from lib.slug import make_demand_slug
from lib.state import get_root


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--version", type=int, default=1)
    parser.add_argument("--demand", required=True)
    parser.add_argument("--feedback", default="")
    args = parser.parse_args()

    root = get_root()
    slug = make_demand_slug(args.demand)
    dir_name = f"{args.task_id}_{slug}"
    out_dir = root / "output" / "req-analysis" / dir_name
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"analysis-v{args.version}.md"

    analyst_prompt_path = Path(__file__).resolve().parent / "analyst_prompt.txt"
    analyst_prompt = analyst_prompt_path.read_text(encoding="utf-8") if analyst_prompt_path.exists() else ""

    newsales_path = root / "NEWSALES_CONTEXT.md"
    newsales_ctx = newsales_path.read_text(encoding="utf-8") if newsales_path.exists() else ""

    prompt = ""
    if analyst_prompt:
        prompt += analyst_prompt.strip() + "\n\n---\n\n"
    if newsales_ctx:
        prompt += "## 现有项目上下文（必须基于此进行分析）\n\n" + newsales_ctx.strip() + "\n\n---\n\n"

    prompt += f"""请根据以下原始需求描述，**结合上述 newsales 现有项目上下文**，严格按照角色定位、工作原则和输出章节要求，生成《新销售平台业务需求方案文档》。需求分析必须说明与 bms_Polaris、tms-React_Polaris 的关联及涉及的中心/模块。

原始需求描述：
{args.demand}
"""
    if args.feedback:
        prompt += f"\n用户反馈（请根据反馈修改）：\n{args.feedback}\n"

    prompt += """
请输出完整的需求方案文档，只输出 Markdown 内容，不要其他说明。"""

    content = run_until_complete(
        initial_prompt=prompt,
        is_truncated=is_markdown_truncated,
        continue_prompt_fn=markdown_continue_prompt,
        max_tokens=16384,
        max_continue=6,
    )
    out_path.write_text(content, encoding="utf-8")
    print(str(out_path.relative_to(root)))


if __name__ == "__main__":
    main()
