#!/usr/bin/env python3
"""代码生成：根据设计文档生成完整 Spring Boot 项目。"""
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
    parser.add_argument("--design-path", required=True)
    args = parser.parse_args()

    root = get_root()
    design_path = root / args.design_path
    if not design_path.exists():
        print(f"Error: {design_path} not found", file=sys.stderr)
        sys.exit(1)

    design_text = design_path.read_text(encoding="utf-8")

    prompt = f"""根据以下设计文档，生成完整的 Spring Boot 项目代码。

设计文档：
{design_text}

请按以下结构生成项目（可分批输出，每次输出一个或多个文件）：

1. pom.xml - Maven 配置
2. src/main/java/com/example/demo/DemoApplication.java - 主类
3. src/main/java/com/example/demo/controller/ - 控制器
4. src/main/java/com/example/demo/service/ - 服务层
5. src/main/java/com/example/demo/entity/ - 实体
6. src/main/resources/application.properties
7. src/test/java/ - 测试

请用以下格式输出每个文件：

```
=== FILE: 相对路径 ===
文件内容
=== END ===
```

只输出文件内容，不要其他说明。"""

    content = run_completion(messages=[{"role": "user", "content": prompt}])

    out_dir = root / "output" / "code" / args.task_id
    out_dir.mkdir(parents=True, exist_ok=True)

    if "=== FILE:" in content:
        for block in content.split("=== FILE:")[1:]:
            if "=== END ===" not in block:
                continue
            path_part, body = block.split("=== END ===", 1)
            path = path_part.strip().strip("=").strip()
            body = body.strip()
            if path:
                fp = out_dir / path
                fp.parent.mkdir(parents=True, exist_ok=True)
                fp.write_text(body, encoding="utf-8")
    else:
        (out_dir / "README.md").write_text(content, encoding="utf-8")

    print(str(out_dir.relative_to(root)))


if __name__ == "__main__":
    main()
