#!/usr/bin/env python3
"""
批量重命名 output/req-analysis 和 output/design-docs 下的目录，
将后缀改为需求总结（10 字以内，去掉前后 filler，不做简单截取）。
"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from lib.slug import make_demand_slug
from lib.state import get_root


def _normalize_suffix(suffix: str) -> str:
    """去掉 _untitled 等系统后缀后生成需求总结。"""
    s = suffix.strip()
    if s.endswith("_untitled"):
        s = s[:-9].strip("_")
    return make_demand_slug(s) if s else ""


def main() -> None:
    root = get_root()

    renames: list[tuple[Path, Path]] = []
    for subdir in ("req-analysis", "design-docs"):
        base = root / "output" / subdir
        if not base.exists():
            continue
        for d in base.iterdir():
            if not d.is_dir():
                continue
            name = d.name
            if "_" not in name:
                continue
            task_id, suffix = name.split("_", 1)
            new_slug = _normalize_suffix(suffix)
            if not new_slug:
                continue
            new_name = f"{task_id}_{new_slug}"
            if new_name != name:
                renames.append((d, base / new_name))

    if not renames:
        print("无需重命名的目录")
        return

    for old_path, new_path in renames:
        if new_path.exists():
            print(f"跳过（目标已存在）: {old_path.name} -> {new_path.name}")
            continue
        print(f"重命名: {old_path.name} -> {new_path.name}")
        old_path.rename(new_path)

    print(f"共处理 {len(renames)} 个目录")


if __name__ == "__main__":
    main()
    sys.exit(0)
