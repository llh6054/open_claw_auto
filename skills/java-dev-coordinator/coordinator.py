#!/usr/bin/env python3
"""
主控 CLI：支持 status, new --demand, restart 命令。
工作目录为 auto-code-project（从 workspace 根或 auto-code-project 运行）。
"""
import argparse
import sys
import uuid
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from lib.state import load, save, get_root


STAGES = ["req-analysis", "design-docs", "code-gen", "code-submit", "completed"]


def cmd_status() -> int:
    """显示当前流程状态。"""
    state = load()
    if not state:
        print("无任务。使用: coordinator.py new --demand \"需求描述\"")
        return 0
    task_id = state.get("task_id", "")
    current = state.get("current_stage", "")
    stages = state.get("stages", {})
    demand = state.get("initial_demand", {}).get("demand_text", "")
    print(f"task_id: {task_id}")
    print(f"current_stage: {current}")
    print(f"demand: {demand[:80]}..." if len(demand) > 80 else f"demand: {demand}")
    for s in STAGES:
        info = stages.get(s, {})
        output = info.get("output_path", "")
        status = info.get("status", "")
        print(f"  {s}: output={output or '-'} status={status or '-'}")
    return 0


def cmd_new(demand: str) -> int:
    """创建新任务。"""
    task_id = str(uuid.uuid4())
    state = {
        "task_id": task_id,
        "current_stage": "req-analysis",
        "stages": {
            "req-analysis": {"iterations": 0, "output_path": None, "status": "pending"},
            "design-docs": {"output_path": None, "status": "pending"},
            "code-gen": {"output_path": None, "status": "pending"},
            "code-submit": {"output_path": None, "status": "pending"},
            "completed": {"status": "pending"},
        },
        "feedback_history": {},
        "initial_demand": {"demand_text": demand},
    }
    save(state)
    root = get_root()
    (root / "output" / "req-analysis").mkdir(parents=True, exist_ok=True)
    (root / "output" / "design-docs").mkdir(parents=True, exist_ok=True)
    (root / "output" / "code").mkdir(parents=True, exist_ok=True)
    print(f"task_id: {task_id}")
    return 0


def cmd_restart() -> int:
    """重置当前任务到 req-analysis 阶段。"""
    state = load()
    if not state:
        print("无任务。使用: coordinator.py new --demand \"需求描述\"")
        return 1
    state["current_stage"] = "req-analysis"
    state["stages"] = {
        "req-analysis": {"iterations": 0, "output_path": None, "status": "pending"},
        "design-docs": {"output_path": None, "status": "pending"},
        "code-gen": {"output_path": None, "status": "pending"},
        "code-submit": {"output_path": None, "status": "pending"},
        "completed": {"status": "pending"},
    }
    state["feedback_history"] = state.get("feedback_history", {})
    save(state)
    print("已重置到 req-analysis")
    return 0


def cmd_clear() -> int:
    """完全清空流程，下次需用 new 新建任务。"""
    save({})
    print("已清空，可重新开始。说「自动化」或「需求开发」+ 需求描述即可新建任务。")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status")

    p_new = sub.add_parser("new")
    p_new.add_argument("--demand", required=True, help="需求描述")

    sub.add_parser("restart")
    sub.add_parser("clear")

    args = parser.parse_args()
    if args.cmd == "status":
        return cmd_status()
    if args.cmd == "new":
        return cmd_new(args.demand)
    if args.cmd == "restart":
        return cmd_restart()
    if args.cmd == "clear":
        return cmd_clear()
    return 1


if __name__ == "__main__":
    sys.exit(main())
