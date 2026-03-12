---
name: java-dev-coordinator
description: "主控：需求分析→设计→代码生成→提交。触发词：自动化、需求开发、代码生成、重新开始、清空、重置、查看状态。Use when user says 自动化, 需求开发, 代码生成, 重新开始, 清空, 重置, 查看状态, or wants to automate/restart/check project flow."
author: chubby
version: 1.0
invoke: on-demand
metadata:
  openclaw:
    emoji: "☕"
    requires: {}
---

# Java 开发主控技能

**触发词**：用户输入以下任一关键词时启用本技能。
- 启动流程：**自动化**、**需求开发**、**代码生成**
- 重新开始：**重新开始**、**清空**、**聊叉了**、**从头来** → exec `coordinator.py clear`
- 重置阶段：**重置**、**重做需求分析** → exec `coordinator.py restart`
- 查看进度：**查看状态**、**当前进度**、**到哪一步了** → exec `coordinator.py status`

管理多阶段需求分析 → 设计文档 → 代码生成 → 代码提交的流程。

## ⚠️ 交互规则（必须遵守）

1. **每次只执行一个阶段**：不要连续 exec 多个阶段。执行完一个阶段后必须停止，等待用户回复。
2. **接收需求后先确认**：用户提出需求后，先总结需求要点并展示，询问「以上理解是否正确？确认后我开始需求分析」。用户确认后才 exec req-analysis。
3. **每阶段完成后必须确认**：阶段执行完成后，用 read 读取产出内容，向用户展示摘要或关键部分，询问「确认无误后继续下一步？回复 确认/继续 或提供修改意见」。用户确认后才 exec 下一阶段。
4. **用户反馈优先**：若用户说「修改 XX」「重新生成」等，对该阶段做反馈迭代，不要进入下一阶段。
5. **断点恢复**：若 flow-state 显示某阶段已完成，从下一阶段开始；同样，每阶段完成后等待确认再继续。

## 执行约定

**必须使用 exec 运行各阶段的 run.py**，不能只靠对话。执行前读取 flow-state.json，执行后更新 output_path。

**脚本会完整输出**：req-analysis、design-docs、code-gen 在输出被截断时会自动续写，无需询问用户「要不要继续」。等脚本执行完毕后再展示产出、询问是否进入下一阶段。

## 命令

```bash
# 查看状态
cd /path/to/auto-code-project && python3 skills/java-dev-coordinator/coordinator.py status

# 新建任务
cd /path/to/auto-code-project && python3 skills/java-dev-coordinator/coordinator.py new --demand "你的需求描述"

# 重置到需求分析（保留当前需求）
cd /path/to/auto-code-project && python3 skills/java-dev-coordinator/coordinator.py restart

# 完全清空（聊叉了、重新开始时用）
cd /path/to/auto-code-project && python3 skills/java-dev-coordinator/coordinator.py clear
```

## 各阶段 exec 调用

### req-analysis
```bash
cd /path/to/auto-code-project && python3 skills/req-analysis/run.py --task-id <task_id> --version 1 --demand "<需求>"
```

### design-docs
```bash
cd /path/to/auto-code-project && python3 skills/design-docs/run.py --task-id <task_id> --analysis-path <req-analysis 输出的路径>
```
（analysis-path 使用 req-analysis 打印的路径，形如 output/req-analysis/<task_id>_<提示词>/analysis-v1.md）

### code-gen
```bash
# 新建项目
python3 skills/code-gen/run.py --task-id <task_id> --design-path <design-docs 输出的路径>

# 在已有项目上添加功能
python3 skills/code-gen/run.py --task-id <task_id> --design-path <design_path> --target-dir <已有项目路径>
```

### code-submit
```bash
cd /path/to/auto-code-project && python3 skills/code-submit/run.py --task-id <task_id>
```

## 状态文件

`output/flow-state.json`

## 流程示例

1. 用户：「做一个登陆页面」
2. 你：总结需求（登陆、忘记密码等），问「以上理解是否正确？确认后我开始需求分析」
3. 用户：「确认」
4. 你：exec req-analysis，完成后 read analysis-v1.md，展示摘要，问「确认后继续设计文档？」
5. 用户：「确认」
6. 你：exec design-docs，完成后 read design.md，展示摘要，问「确认后继续代码生成？」
7. 依此类推，每阶段一次确认。
