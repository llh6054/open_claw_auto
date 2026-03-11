---
name: java-dev-coordinator
description: "主控：阶段管理、状态读写、用户确认、断点恢复"
author: chubby
version: 1.0
invoke: on-demand
metadata:
  openclaw:
    emoji: "☕"
    requires: {}
---

# Java 开发主控技能

管理多阶段需求分析 → 设计文档 → 代码生成 → 代码提交的流程。

## 执行约定

**必须使用 exec 运行各阶段的 run.py**，不能只靠对话。执行前读取 flow-state.json，执行后更新 output_path。

## 命令

```bash
# 查看状态
cd /path/to/auto-code-project && python3 skills/java-dev-coordinator/coordinator.py status

# 新建任务
cd /path/to/auto-code-project && python3 skills/java-dev-coordinator/coordinator.py new --demand "你的需求描述"

# 重置
cd /path/to/auto-code-project && python3 skills/java-dev-coordinator/coordinator.py restart
```

## 各阶段 exec 调用

### req-analysis
```bash
cd /path/to/auto-code-project && python3 skills/req-analysis/run.py --task-id <task_id> --version 1 --demand "<需求>"
```

### design-docs
```bash
cd /path/to/auto-code-project && python3 skills/design-docs/run.py --task-id <task_id> --analysis-path output/req-analysis/<task_id>/analysis-v1.md
```

### code-gen
```bash
cd /path/to/auto-code-project && python3 skills/code-gen/run.py --task-id <task_id> --design-path output/design-docs/<task_id>/design.md
```

### code-submit
```bash
cd /path/to/auto-code-project && python3 skills/code-submit/run.py --task-id <task_id>
```

## 状态文件

`output/flow-state.json`
