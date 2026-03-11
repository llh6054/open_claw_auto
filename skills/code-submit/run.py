#!/usr/bin/env python3
"""代码提交：Maven 编译/测试、Git 初始化与提交。"""
import argparse
import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from lib.state import get_root


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-id", required=True)
    args = parser.parse_args()

    root = get_root()
    code_base = root / "output" / "code"
    code_dir = code_base / args.task_id
    if not code_dir.exists():
        matches = [d for d in code_base.iterdir() if d.is_dir() and d.name.startswith(args.task_id)]
        if matches:
            code_dir = matches[0]
    if not code_dir.exists():
        print(f"Error: {code_dir} not found", file=sys.stderr)
        sys.exit(1)

    if not (code_dir / "pom.xml").exists():
        print(f"Error: pom.xml not found in {code_dir}", file=sys.stderr)
        sys.exit(1)

    cwd = str(code_dir)
    try:
        subprocess.run(["mvn", "clean", "compile", "-q"], cwd=cwd, check=True)
        subprocess.run(["mvn", "test", "-q"], cwd=cwd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Maven failed: {e}", file=sys.stderr)
        sys.exit(1)

    if not (code_dir / ".git").exists():
        subprocess.run(["git", "init"], cwd=cwd, check=True)
    subprocess.run(["git", "add", "-A"], cwd=cwd, check=True)
    subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=cwd, check=True)
    print(f"code-submit done: {code_dir.relative_to(root)}")


if __name__ == "__main__":
    main()
