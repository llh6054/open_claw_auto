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

根据需求分析文档，使用 **Cursor CLI (agent)** 以 newsales 各中心目录为 workspace 生成执行计划和设计文档。

## 输出路径

`output/design-docs/{task_id}_{slug}/`
- `plan.md`：执行计划（文档内按中心分章节）
- `design.md`：设计文档（文档内按中心分章节）
- 使用 Cursor CLI 以 newsales 为 workspace 生成（不按中心拆分执行上下文）

## 调用方式

```bash
cd /path/to/auto-code-project && python3 skills/design-docs/run.py --task-id <task_id> --analysis-path output/req-analysis/<task_id>/analysis-v1.md
```

## 依赖

- **Cursor CLI**：需安装 `agent` 命令（`curl https://cursor.com/install -fsS | bash`）

## 参数

- `--task-id`: 任务 ID
- `--analysis-path`: 需求分析文档路径（相对于项目根）
