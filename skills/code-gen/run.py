#!/usr/bin/env python3
"""代码生成：根据设计文档生成代码，支持新建项目或在已有项目上添加功能。"""
import argparse
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from lib.completion import (
    code_continue_prompt,
    is_code_truncated,
    run_until_complete,
)
from lib.slug import make_demand_slug
from lib.state import get_root, load


def _parse_and_write(content: str, out_dir: Path) -> None:
    """解析 === FILE: === 格式并写入文件。"""
    if "=== FILE:" not in content:
        (out_dir / "README.md").write_text(content, encoding="utf-8")
        return
    for block in content.split("=== FILE:")[1:]:
        if "=== END ===" not in block:
            continue
        if "\n" in block:
            path_line, body = block.split("\n", 1)
            path = path_line.strip().strip("=").strip()
            body = body.split("=== END ===")[0].strip()
            if path and not path.startswith("<") and len(path) < 200:
                fp = out_dir / path
                fp.parent.mkdir(parents=True, exist_ok=True)
                fp.write_text(body, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--design-path", required=True)
    parser.add_argument("--target-dir", default="", help="已有项目路径，若提供则在其上添加功能；否则新建项目")
    args = parser.parse_args()

    root = get_root()
    design_path = root / args.design_path
    if not design_path.exists():
        print(f"Error: {design_path} not found", file=sys.stderr)
        sys.exit(1)

    design_text = design_path.read_text(encoding="utf-8")
    has_existing = bool(args.target_dir.strip())

    if has_existing:
        target = Path(args.target_dir)
        if not target.is_absolute():
            target = root / args.target_dir
        if not target.exists():
            print(f"Error: target dir {target} not found", file=sys.stderr)
            sys.exit(1)
        out_dir = target
        mode_hint = """目标为**已有项目**，请在指定目录下生成需要新增或修改的文件。
保持与现有代码风格、包名、依赖一致。仅输出新增文件或需完整替换的文件。"""
    else:
        mode_hint = """目标为**新建项目**，请生成完整项目结构（含构建配置、主类、分层代码等）。"""

    prompt = f"""根据以下设计文档生成代码。

设计文档：
{design_text}

{mode_hint}

输出格式：
=== FILE: 相对路径（相对于项目根） ===
文件内容
=== END ===

只输出文件内容，不要其他说明。"""

    content = run_until_complete(
        initial_prompt=prompt,
        is_truncated=is_code_truncated,
        continue_prompt_fn=code_continue_prompt,
        max_continue=4,
        model_default="claude_cli",
    )

    if not has_existing:
        state = load()
        demand = ""
        if state.get("task_id") == args.task_id:
            demand = state.get("initial_demand", {}).get("demand_text", "")
        slug = make_demand_slug(demand)
        dir_name = f"{args.task_id}_{slug}"
        out_dir = root / "output" / "code" / dir_name
        out_dir.mkdir(parents=True, exist_ok=True)
    _parse_and_write(content, out_dir)
    try:
        print(str(out_dir.relative_to(root)))
    except ValueError:
        print(str(out_dir))


if __name__ == "__main__":
    main()
