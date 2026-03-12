# 快捷指令（OpenClaw 快速识别）

> 用户说以下关键词时，执行对应动作。

## 重新开始 / 聊叉了

| 用户说 | 动作 | 命令 |
|--------|------|------|
| **重新开始**、**清空**、**聊叉了**、**从头来** | 完全清空流程 | `coordinator.py clear` |
| **重置**、**重做需求分析** | 重置到需求分析阶段（保留当前需求） | `coordinator.py restart` |

## 启动流程

| 用户说 | 动作 |
|--------|------|
| **自动化**、**需求开发**、**代码生成** | 启用 java-dev-coordinator，按流程执行 |

## 查看状态

| 用户说 | 动作 |
|--------|------|
| **查看状态**、**当前进度**、**到哪一步了** | `coordinator.py status` |

## 新建任务

用户说「自动化」或「需求开发」+ 需求描述 → 先 `coordinator.py new --demand "需求"`，再 exec req-analysis。

## 运行方式

**统一使用 `./run`**（调用 litellm venv）：`cd auto-code-project && ./run skills/xxx/run.py ...`

## 模型切换

| 环境变量 | 值 | 说明 |
|----------|-----|------|
| `AUTO_CODE_MODEL` | `claude` | 鲸云 Claude（默认需求分析/设计） |
| | `claude_cli` | Claude CLI（默认代码生成） |
| | `kimi` | Kimi K2.5（**优先鲸云**，无鲸云 key 或鲸云 404 时用 Moonshot 官方） |

批量切换：`export AUTO_CODE_MODEL=kimi` 后，所有技能均使用 Kimi。Kimi 需配置 `WHALELLM_API_KEY`（鲸云）或 `MOONSHOT_API_KEY`（官方）。鲸云 Kimi 代理 URL 可通过 `WHALEKIMI_BASE_URL` 覆盖。
