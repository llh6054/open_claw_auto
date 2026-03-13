# 新销售平台（newsales）项目上下文

> 需求分析、设计文档均需基于 newsales 下的现有项目进行分析和设计。
> 路径：`newsales/`（相对 auto-code-project 根目录）

---

## 一、工程概览与架构

newsales 为电信集团新销售平台，包含**管理门户（PC）**和**商家门户**，采用前后端分离、微服务架构。

### 1.1 前端入口

| 路径 | 说明 |
|------|------|
| /portal | 基础管理中心（BMS），直连 bms-controller |
| /dmos | PC Web 聚合服务，由 tms-PCWeb 聚合各中心 |

### 1.2 工程列表

| 工程 | 类型 | Controller | 说明 |
|------|------|------------|------|
| **bms_Polaris** | 后端 | **自有 controller**（bms-controller，context-path /bms） | 基础数据中心，用户/角色/权限/组织等。前端通过 /portal 直连，**非聚合** |
| **mms_Polaris** | 后端 | 有 mms-controller（/mms） | 会员管理中心。PC 端业务通过 PCWeb 聚合调用 mms-app |
| **mms-extend_Polaris** | 后端 | **controller 已停用** | 会员扩展中心。仅 app 服务，PC 端通过 PCWeb 聚合调用 |
| **tms-React_Polaris** | 前端 | - | 管理门户 + 商家门户，`yarn start` / `yarn start busi` |
| **tms-PCWeb_Polaris** | 后端 | **纯聚合**（context-path /dmos） | 无自有业务，通过 Feign 聚合 mms、mmsextend、cms、oms、pms、sms 等中心，为 PC 端提供统一 API |

### 1.3 调用关系

```
前端 tms-React
    ├── /portal  ──────────────► bms-controller（bms_Polaris 自有，直连）
    └── /dmos   ──────────────► tms-PCWeb（聚合层）
                                    ├── Feign ─► mms-app
                                    ├── Feign ─► mms-extend-app
                                    ├── Feign ─► cms-app（外部）
                                    ├── Feign ─► oms-app（外部）
                                    └── ...
```

- **bms**：独立部署，有 bms-controller，前端直连，**不经过 PCWeb 聚合**
- **mms、mms-extend**：业务接口由 PCWeb 聚合，PCWeb 通过 Feign 调用其 app 服务
- **cms、oms、pms、sms 等**：外部中心（不在 newsales 目录），由 PCWeb 聚合

---

## 二、后端中心与模块

### 2.1 BMS（bms_Polaris）— 基础数据中心，自有 Controller

| 模块 | 业务含义 | 主要能力 |
|------|----------|----------|
| user | 用户/账号 | 用户、子账号、主账号、会员、员工、实名认证、账号绑定 |
| org | 组织架构 | 组织、组织用户关系 |
| role | 角色管理 | 角色、角色权限关联 |
| privilege | 权限管理 | 权限目录、菜单、数据权限、属性权限 |
| usergroup | 用户组 | 用户分组管理 |
| login | 登录认证 | 登录、JWT、验证码 |
| channel / salechannel | 渠道 | 渠道管理、销售渠道、渠道编号 |
| area / province | 区域 | 省市区、区域缓存、ES 同步 |
| blacklist | 黑名单 | 黑名单、黑名单策略 |
| risklist | 风控名单 | 风控名单、ES 同步 |
| sms / notice / cuturl / attr / system / log / cache / minio / file | 系统 | 短信、公告、短链、属性、系统参数、日志、缓存、文件等 |

- **包名**：`com.iwhalecloud.dmos.bms`
- **端口**：app 8081，controller 8089（context-path /bms）
- **启动**：BmsAppApplication → BmsControllerApplication
- **前端**：/portal 直连 bms-controller

### 2.2 MMS（mms_Polaris）— 会员管理中心，由 PCWeb 聚合

| 模块 | 业务含义 | 主要能力 |
|------|----------|----------|
| member | 会员 | 会员注册、信息维护、状态、推荐关系 |
| memberbenefits | 会员权益 | 会员权益管理 |
| point | 积分 | 积分管理 |
| invoice | 发票 | 发票模板、发票管理 |
| cust / black / event | 其他 | 客户、黑名单、领域事件 |

- **包名**：`com.iwhalecloud.dmos.mms`
- **端口**：app 8089，controller 8080（/mms）
- **PC 端**：通过 PCWeb consumer/mms 聚合，Feign 调 mms-app

### 2.3 MMS-EXTEND（mms-extend_Polaris）— 会员扩展中心，Controller 已停用

| 模块 | 业务含义 | 主要能力 |
|------|----------|----------|
| archives | 档案 | 档案创建/激活/停用、云档案、超期处理 |
| number | 号码 | 号码分配/回收、状态、与账户关联 |
| balance | 余额 | 余额相关 |
| member | 会员等级 | 会员等级变更、转移 |
| quene | 队列 | 到期数据队列 |

- **包名**：`com.iwhalecloud.dmos.mms.extend`
- **端口**：app 8096（controller 已停用）
- **PC 端**：通过 PCWeb consumer/mmsextend 聚合，Feign 调 mms-extend-app

### 2.4 PCWeb（tms-PCWeb_Polaris）— 纯聚合层

- **职责**：聚合各中心 API，为 PC 端提供 /dmos 统一入口
- **包名**：`com.iwhalecloud.dmos.consumer`
- **端口**：8078，context-path /dmos
- **聚合中心**：bms（仅登录等）、mms、mmsextend、cms、csms、datasync、ems、fms、ims、mcms、oms、pms、rule、scms、sms、tms
- **依赖**：bms-client、mms-client、mms-extend-client、cms-client、tms-client、oms-client 等
- **说明**：bms 主要业务接口由 bms-controller 直连 /portal，PCWeb 的 consumer/bms 仅含登录、权限校验等

---

## 三、前端页面

### 3.1 管理门户（polaris）

`src/page/container/`，`yarn start`

Login、Home、User、Role、Org、Privilege、Usergroup、Blacklist、RiskControl、Goods、Order、Store、Sales、Members、FlowManagement、Logistics、CMSManage、System、BaseCenter、CustServer、RulesView、Point、UIM 等

### 3.2 商家门户（polarisbusi）

`src/page/containerBusi/`，`yarn start busi`

Login、Home、Workbench、Account、User、Role、Privilege、Usergroup、Customer、Goods、Order、Store、Sales、Flow、Invoice、Marketing、CMS、AntiFraudBlackList、AuditDetail、Demolition、EnterpriseRun 等

---

## 四、核心业务关系

```
组织(org) ──┬── 用户(user) ──┬── 角色(role) ── 权限(privilege)
            │                │
            └── 用户组(usergroup)   └── 渠道(channel) / 区域(area) / 黑名单(blacklist) / 风控(risklist)
```

---

## 五、需求分析与设计约束

1. **bms 改造**：改 bms_Polaris 自有 controller 和 app，不经过 PCWeb
2. **mms / mms-extend 改造**：改对应中心 app，PCWeb consumer 层如需适配则改 tms-PCWeb
3. **前端改造**：改 tms-React_Polaris
4. **遵循现有模块**：归属到已有 service/domain，或说明新增理由
5. **参考代码**：`newsales/bms_Polaris`、`newsales/mms_Polaris`、`newsales/mms-extend_Polaris`、`newsales/tms-React_Polaris`、`newsales/tms-PCWeb_Polaris`
