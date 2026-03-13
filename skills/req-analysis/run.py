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
    parser.add_argument(
        "--stage",
        choices=("preliminary", "full"),
        default="preliminary",
        help="preliminary: 仅 3.1+3.2+中心分工计划; full: 完整 1～10 章",
    )
    args = parser.parse_args()

    root = get_root()
    slug = make_demand_slug(args.demand)
    dir_name = f"{args.task_id}_{slug}"
    out_dir = root / "output" / "req-analysis" / dir_name
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"analysis-v{args.version}.md"

    skill_dir = Path(__file__).resolve().parent
    newsales_path = root / "NEWSALES_CONTEXT.md"
    newsales_ctx = newsales_path.read_text(encoding="utf-8") if newsales_path.exists() else ""

    prompt = ""
    if newsales_ctx:
        prompt += "## NEWSALES_CONTEXT（用于判断中心/模块分工）\n\n" + newsales_ctx.strip() + "\n\n---\n\n"

    if args.stage == "preliminary":
        tpl_path = skill_dir / "preliminary_prompt.txt"
        tpl = tpl_path.read_text(encoding="utf-8") if tpl_path.exists() else ""
        if tpl:
            prompt += tpl.replace("{demand}", args.demand)
        else:
            prompt += f"原始需求：{args.demand}\n\n请输出：1) 仅 3.1 功能说明 + 3.2 功能点；2) 基于 newsales 的中心/模块分工计划。"
    else:
        tpl_path = skill_dir / "analyst_prompt.txt"
        tpl = tpl_path.read_text(encoding="utf-8") if tpl_path.exists() else ""
        if tpl:
            prompt += tpl.replace("{demand}", args.demand)
        else:
            prompt += f"原始需求：{args.demand}\n\n请按完整需求文档结构（1～10 章）输出。"

    if args.feedback:
        prompt += f"\n\n用户反馈（请根据反馈修改）：\n{args.feedback}\n"

    prompt += "\n\n只输出 Markdown，不要其他说明。"

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
