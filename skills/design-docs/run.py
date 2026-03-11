#!/usr/bin/env python3
"""设计文档：根据需求分析生成架构、接口、数据模型设计。"""
import argparse
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from lib.iwhalecloud import run_completion
from lib.state import get_root


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

    prompt = f"""根据以下需求分析文档，生成 Spring Boot 项目的设计文档（Markdown 格式）。

需求分析：
{analysis_text}

请输出完整的设计文档，包含：
1. 架构设计（分层、模块划分）
2. 接口定义（REST API、请求/响应格式）
3. 数据模型（实体、表结构）
4. 技术选型说明

只输出 Markdown 内容，不要其他说明。"""

    content = run_completion(messages=[{"role": "user", "content": prompt}])

    out_dir = root / "output" / "design-docs" / args.task_id
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "design.md"
    out_path.write_text(content, encoding="utf-8")
    print(str(out_path.relative_to(root)))


if __name__ == "__main__":
    main()
