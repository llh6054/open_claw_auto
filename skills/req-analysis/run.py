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

    prompt = f"""根据以下需求描述，生成结构化的需求分析文档（Markdown 格式）。

需求描述：
{args.demand}
"""
    if args.feedback:
        prompt += f"\n用户反馈（请根据反馈修改）：\n{args.feedback}\n"

    prompt += """
请输出完整的需求分析文档。根据需求类型选择结构：
- **新建项目**：项目概述、核心需求、功能详解、非功能需求、技术栈建议、交互设计
- **在已有项目上添加功能**：目标项目说明、要添加的功能、与现有模块的集成方式、接口/数据变更

只输出 Markdown 内容，不要其他说明。"""

    content = run_until_complete(
        initial_prompt=prompt,
        is_truncated=is_markdown_truncated,
        continue_prompt_fn=markdown_continue_prompt,
        max_continue=3,
    )
    out_path.write_text(content, encoding="utf-8")
    print(str(out_path.relative_to(root)))


if __name__ == "__main__":
    main()
