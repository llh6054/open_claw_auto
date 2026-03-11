# auto-code-project 工作上下文

> 用于断点恢复、继续开发时快速进入状态。更新于 2026-03-11。

## 当前任务

| 字段 | 值 |
|------|-----|
| task_id | `f3f2065a-8e11-4d52-9688-27a8914640b7` |
| current_stage | req-analysis |
| 需求 | 做一个用户登陆页面，支持账号密码登陆、忘记密码功能 |

## 已完成

- [x] req-analysis → `output/req-analysis/f3f2065a-8e11-4d52-9688-27a8914640b7/analysis-v1.md`

## 待执行

1. **design-docs**
   ```bash
   python3 skills/design-docs/run.py --task-id f3f2065a-8e11-4d52-9688-27a8914640b7 \
     --analysis-path output/req-analysis/f3f2065a-8e11-4d52-9688-27a8914640b7/analysis-v1.md
   ```

2. **code-gen**（design.md 生成后）
   ```bash
   python3 skills/code-gen/run.py --task-id f3f2065a-8e11-4d52-9688-27a8914640b7 \
     --design-path output/design-docs/f3f2065a-8e11-4d52-9688-27a8914640b7/design.md
   ```

3. **code-submit**（代码生成后）
   ```bash
   python3 skills/code-submit/run.py --task-id f3f2065a-8e11-4d52-9688-27a8914640b7
   ```

## 项目结构速览

```
lib/iwhalecloud.py  → 鲸云 API（Key 从 env/auth-profiles 读取）
lib/state.py        → flow-state 读写、get_root()
skills/req-analysis/run.py
skills/design-docs/run.py
skills/code-gen/run.py
skills/code-submit/run.py
skills/java-dev-coordinator/coordinator.py  → status / new / restart
```

## 需求分析要点（analysis-v1.md）

- 登陆：用户名/邮箱 + 密码，验证非空、密码≥6位
- 忘记密码：邮箱 → 重置链接 → 新密码
- 技术栈：Spring Boot、MySQL/PostgreSQL、JWT/Session、SMTP
