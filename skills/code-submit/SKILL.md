---
name: code-submit
description: "代码提交：Maven 编译/测试、Git 初始化与提交"
author: chubby
version: 1.0
invoke: on-demand
metadata:
  openclaw:
    emoji: "✅"
    requires: { mvn: "Maven", git: "Git" }
---

# 代码提交技能

对生成的代码执行 Maven 编译、测试，并完成 Git 初始化与提交。

## 调用方式

```bash
cd /path/to/auto-code-project && python3 skills/code-submit/run.py --task-id <task_id>
```

## 参数

- `--task-id`: 任务 ID（代码路径为 output/code/{task_id}/）
