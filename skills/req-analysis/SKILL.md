---
name: req-analysis
description: "需求分析：根据用户需求生成结构化需求分析文档，支持迭代修改"
author: chubby
version: 1.0
invoke: on-demand
metadata:
  openclaw:
    emoji: "📋"
    requires: {}
---

# 需求分析技能

根据用户需求描述，生成结构化的 Markdown 需求分析文档。

## 输出路径

`output/req-analysis/{task_id}/analysis-v{N}.md`

## 调用方式

由 java-dev-coordinator 通过 exec 调用：

```bash
cd /path/to/auto-code-project && python3 skills/req-analysis/run.py --task-id <task_id> --version <N> --demand "<需求文本>"
```

或从 workspace 根目录：

```bash
cd /path/to/workspace && python3 auto-code-project/skills/req-analysis/run.py --task-id <task_id> --version <N> --demand "<需求文本>"
```

## 参数

- `--task-id`: 任务 ID
- `--version`: 版本号（1, 2, 3...）
- `--demand`: 需求描述文本
- `--feedback`: 可选，用户反馈用于迭代
