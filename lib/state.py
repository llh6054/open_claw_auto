"""
读写 output/flow-state.json，支持断点恢复。
工作目录为 auto-code-project（脚本从 workspace 根或 auto-code-project 运行）。
"""
import json
from pathlib import Path
from typing import Any


def _resolve_root() -> Path:
    """解析项目根目录（auto-code-project 或 workspace）。"""
    cwd = Path.cwd()
    for p in [cwd, cwd.parent]:
        if (p / "lib" / "state.py").exists():
            return p
        if (p / "auto-code-project" / "lib" / "state.py").exists():
            return p / "auto-code-project"
    if (cwd / "auto-code-project" / "lib" / "state.py").exists():
        return cwd / "auto-code-project"
    return cwd


def _flow_state_path() -> Path:
    root = _resolve_root()
    return root / "output" / "flow-state.json"


def load() -> dict[str, Any]:
    """加载 flow-state.json。"""
    path = _flow_state_path()
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save(state: dict[str, Any]) -> None:
    """保存 flow-state.json。"""
    path = _flow_state_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def get_root() -> Path:
    """返回项目根目录。"""
    return _resolve_root()
