---
name: code-gen
description: "代码生成：根据设计文档生成代码，支持新建项目或在已有项目上添加功能"
author: chubby
version: 1.0
invoke: on-demand
metadata:
  openclaw:
    emoji: "💻"
    requires: { mvn: "Maven" }
---

# 代码生成技能

根据设计文档生成代码，支持**新建完整项目**或**在已有项目上添加功能**。

## 新建项目

```bash
python3 skills/code-gen/run.py --task-id <task_id> --design-path output/design-docs/<task_id>_<提示词>/design.md
```
输出到 `output/code/{task_id}_{提示词}/`

## 在已有项目上添加功能

```bash
python3 skills/code-gen/run.py --task-id <task_id> --design-path <design_path> --target-dir <已有项目路径>
```
在指定目录下生成新增文件，保持与现有代码一致。

## 补全缺失文件

```bash
python3 skills/code-gen/generate_missing.py --task-id <task_id> --design-path <design_path> [--target-dir <项目路径>]
```
根据设计文档分析已有文件，生成缺失部分。适用于任意项目类型。
