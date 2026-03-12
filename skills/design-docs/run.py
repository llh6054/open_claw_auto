#!/usr/bin/env python3
"""设计文档：根据需求分析生成架构、接口、数据模型设计。"""
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
from lib.state import get_root, load


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--analysis-path", required=True)
    args = parser.parse_args()

    root = get_root()
    analysis_path = root / args.analysis_path
    if not analysis_path.exists():
        print(f"Error: {analysis_path} not found", file=sys.stderr)
        sys.exit(1)

    analysis_text = analysis_path.read_text(encoding="utf-8")

    newsales_path = root / "NEWSALES_CONTEXT.md"
    newsales_ctx = newsales_path.read_text(encoding="utf-8") if newsales_path.exists() else ""

    prompt = ""
    if newsales_ctx:
        prompt += "## 现有项目上下文（设计必须基于此）\n\n" + newsales_ctx.strip() + "\n\n---\n\n"

    prompt += f"""根据以下需求分析文档，**结合上述 newsales 项目上下文**，生成设计文档（Markdown 格式）。

需求分析：
{analysis_text}

请根据需求类型输出设计文档：
- 若为**新建完整项目**：包含架构设计、接口定义、数据模型、技术选型
- 若为**在已有项目上添加功能**：**必须基于 bms_Polaris、tms-React_Polaris**，重点描述要新增的模块、接口、数据变更、与现有代码的集成方式，遵循现有技术栈（Spring Boot、React、DDD 分层等）

只输出 Markdown 内容，不要其他说明。"""

    content = run_until_complete(
        initial_prompt=prompt,
        is_truncated=is_markdown_truncated,
        continue_prompt_fn=markdown_continue_prompt,
        max_continue=3,
    )

    state = load()
    demand = ""
    if state.get("task_id") == args.task_id:
        demand = state.get("initial_demand", {}).get("demand_text", "")
    slug = make_demand_slug(demand)
    dir_name = f"{args.task_id}_{slug}"
    out_dir = root / "output" / "design-docs" / dir_name
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "design.md"
    out_path.write_text(content, encoding="utf-8")
    print(str(out_path.relative_to(root)))


if __name__ == "__main__":
    main()
