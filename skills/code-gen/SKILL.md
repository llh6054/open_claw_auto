---
name: code-gen
description: "代码生成：根据设计文档生成完整 Spring Boot 项目"
author: chubby
version: 1.0
invoke: on-demand
metadata:
  openclaw:
    emoji: "💻"
    requires: { mvn: "Maven" }
---

# 代码生成技能

根据设计文档生成完整的 Spring Boot 项目代码。

## 输出路径

`output/code/{task_id}/`（完整 Maven 项目）

## 调用方式

```bash
cd /path/to/auto-code-project && python3 skills/code-gen/run.py --task-id <task_id> --design-path output/design-docs/<task_id>/design.md
```

## 参数

- `--task-id`: 任务 ID
- `--design-path`: 设计文档路径（相对于项目根）
