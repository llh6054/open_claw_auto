#!/usr/bin/env python3
"""
通用补全：根据设计文档在已有项目上添加功能或生成缺失文件。
适用于任意项目类型（Java/Spring Boot 等），支持新建或增强已有项目。
"""
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
from lib.state import get_root


def _find_code_dir(root: Path, task_id: str, target_dir: str | None) -> Path | None:
    """解析代码目录：--target-dir 或 output/code 下 task_id/task_id_*。"""
    if target_dir and target_dir.strip():
        p = Path(target_dir)
        if not p.is_absolute():
            p = root / target_dir
        return p if p.exists() else None
    code_base = root / "output" / "code"
    direct = code_base / task_id
    if direct.exists():
        return direct
    matches = [d for d in code_base.iterdir() if d.is_dir() and d.name.startswith(task_id)]
    return matches[0] if matches else None


def _list_existing_files(code_dir: Path) -> list[str]:
    """列出代码目录中已存在的相对路径。"""
    paths = []
    for p in code_dir.rglob("*"):
        if p.is_file():
            paths.append(str(p.relative_to(code_dir)))
    return sorted(paths)


def _parse_and_write(content: str, out_dir: Path) -> int:
    """解析 === FILE: === 格式并写入，返回生成文件数。"""
    count = 0
    if "=== FILE:" not in content:
        return count
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
                count += 1
                print(f"Generated: {path}")
    return count


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--design-path", required=True)
    parser.add_argument("--target-dir", default="", help="已有项目路径，不填则从 output/code 按 task_id 查找")
    args = parser.parse_args()

    root = get_root()
    design_path = root / args.design_path
    if not design_path.exists():
        print(f"Error: {design_path} not found", file=sys.stderr)
        sys.exit(1)

    code_dir = _find_code_dir(root, args.task_id, args.target_dir or None)
    if not code_dir:
        print(f"Error: code dir not found (task_id={args.task_id}, target-dir={args.target_dir})", file=sys.stderr)
        sys.exit(1)

    design_text = design_path.read_text(encoding="utf-8")
    existing = _list_existing_files(code_dir)
    existing_str = "\n".join(existing) if existing else "（无）"

    prompt = f"""根据以下设计文档，在已有项目上添加功能或生成缺失文件。

设计文档：
{design_text[:12000]}

项目已有文件：
{existing_str}

请分析设计文档与已有文件，生成需要新增的代码文件（Controller、Service、Repository、Entity、配置等）。
保持与现有项目结构、包名、风格一致。若设计描述的是「添加功能」，仅生成新增部分。
输出格式：
=== FILE: 相对路径（相对于项目根） ===
文件内容
=== END ===

只输出文件内容，不要其他说明。"""

    content = run_until_complete(
        initial_prompt=prompt,
        is_truncated=is_code_truncated,
        continue_prompt_fn=code_continue_prompt,
        max_continue=3,
    )

    n = _parse_and_write(content, code_dir)
    print(f"Done: {n} files generated, output: {code_dir.relative_to(root)}")


if __name__ == "__main__":
    main()
