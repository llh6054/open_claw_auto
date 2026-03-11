---
name: design-docs
description: "设计文档：根据需求分析生成设计，支持新建项目或在已有项目上添加功能的设计"
author: chubby
version: 1.0
invoke: on-demand
metadata:
  openclaw:
    emoji: "🏗️"
    requires: {}
---

# 设计文档技能

根据需求分析文档，生成架构设计、接口定义、数据模型等设计文档。

## 输出路径

`output/design-docs/{task_id}/design.md`

## 调用方式

```bash
cd /path/to/auto-code-project && python3 skills/design-docs/run.py --task-id <task_id> --analysis-path output/req-analysis/<task_id>/analysis-v1.md
```

## 参数

- `--task-id`: 任务 ID
- `--analysis-path`: 需求分析文档路径（相对于项目根）
