# Java 开发 Agent 系统

通过聊天驱动的多阶段 Java 项目自动化开发流程。

## 流程

1. **需求分析** → `output/req-analysis/{task_id}/analysis-v{N}.md`
2. **设计文档** → `output/design-docs/{task_id}/design.md`
3. **代码生成** → `output/code/{task_id}/`（Spring Boot 项目）
4. **代码提交** → Maven 编译/测试、Git 提交

## 使用方式

### 主控命令

```bash
cd auto-code-project
python3 skills/java-dev-coordinator/coordinator.py status
python3 skills/java-dev-coordinator/coordinator.py new --demand "你的需求"
python3 skills/java-dev-coordinator/coordinator.py restart
```

### 子技能（由主控或 exec 调用）

```bash
python3 skills/req-analysis/run.py --task-id <id> --version 1 --demand "需求"
python3 skills/design-docs/run.py --task-id <id> --analysis-path output/req-analysis/<id>/analysis-v1.md
python3 skills/code-gen/run.py --task-id <id> --design-path output/design-docs/<id>/design.md
python3 skills/code-submit/run.py --task-id <id>
```

## 配置

- **鲸云 API**：`lib/iwhalecloud.py` 使用 `https://lab.iwhalecloud.com/gpt-proxy/anthropic`，模型 `claude-4.5-haiku`
- **API Key**：环境变量 `WHALELLM_API_KEY` 或 `~/.openclaw/agents/main/agent/auth-profiles.json` 中的 `whalellm:default`
- **工作目录**：脚本可从 workspace 根或 auto-code-project 运行

## 状态

`output/flow-state.json` 持久化任务状态，支持断点恢复。
