# 新销售平台（newsales）项目上下文

> 需求分析、设计文档均需基于 newsales 下的现有项目进行分析和设计。

---

## 一、项目概览

newsales 为电信集团新销售平台，包含**管理门户（PC）**和**商家门户**，采用前后端分离架构。

| 项目 | 类型 | 技术栈 | 说明 |
|------|------|--------|------|
| **bms_Polaris** | 后端 | Spring Boot 2.1、Spring Cloud、MyBatis-Plus、Nacos、Redis、ES、MinIO | 业务管理服务（BMS），提供 PC 和商家门户的 API |
| **tms-React_Polaris** | 前端 | React、Ant Design 3、Axios、ECharts | 管理平台 + 商家平台，yarn 启动 |

---

## 二、业务域分析

### 2.1 BMS 业务模块（按 service/domain 划分）

| 模块 | 业务含义 | 主要能力 |
|------|----------|----------|
| **user** | 用户/账号管理 | 用户、子账号、主账号、会员、员工、实名认证、账号绑定 |
| **org** | 组织架构 | 组织、组织用户关系 |
| **role** | 角色管理 | 角色、角色权限关联 |
| **privilege** | 权限管理 | 权限目录、菜单、数据权限、属性权限 |
| **usergroup** | 用户组 | 用户分组管理 |
| **login** | 登录认证 | 登录、JWT、验证码 |
| **registerForm** | 注册表单 | 注册表单配置 |
| **channel** | 渠道 | 渠道管理 |
| **salechannel** | 销售渠道 | 销售渠道、渠道编号 |
| **area** | 区域 | 省市区、区域缓存、ES 同步 |
| **province** | 省份 | 省份级数据 |
| **blacklist** | 黑名单 | 黑名单、黑名单策略、黑名单策略日志 |
| **risklist** | 风控名单 | 风控名单、风控名单同步 ES |
| **sms** | 短信 | 短信发送、短信模板、验证码 |
| **notice** | 公告 | 群组公告、公告同步 ES |
| **cuturl** | 短链 | 短链生成、短链校验、短链 ES |
| **attr** | 属性/规格 | 属性规格、属性值、属性关联 |

| 模块 | 业务含义 | 主要能力 |
|------|----------|----------|
| **system** | 系统配置 | 系统参数、公共缓存、安全规则 |
| **log** | 日志 | 接口日志、操作日志 |
| **cache** | 缓存 | 缓存管理、刷新 |
| **minio** | 文件存储 | MinIO 文件上传下载 |
| **file** | 文件 | 文件信息 |

| 模块 | 业务含义 | 主要能力 |
|------|----------|----------|
| **bank** | 银行 | 银行、支行、银行卡 |
| **wechat** | 微信 | 微信相关 |
| **ai** | AI | AI 问题记录、统计 |
| **application** | 应用 | 应用管理 |
| **identity** | 身份 | 身份认证 |
| **captcha** | 验证码 | 验证码 |

### 2.2 管理门户（polaris）前端页面

| 页面 | 业务 |
|------|------|
| Login、Home | 登录、首页 |
| User、Role、Org、Privilege、Usergroup | 用户、角色、组织、权限、用户组 |
| Blacklist、RiskControl、RiskControlScreen | 黑名单、风控 |
| Goods、Order、Store、Sales、Members | 商品、订单、店铺、销售、会员 |
| FlowManagement、Logistics | 流程、物流 |
| CMSManage、AdvertBiliWeb | CMS、广告 |
| System、MasterDB、DevelopOprations、OPSManage | 系统、主数据、开发运维 |
| BaseCenter、CustServer、ForcePushServer | 基础中心、客服、强推 |
| RulesView、Point | 规则、积分 |
| UIM | UIM |

### 2.3 商家门户（polarisbusi）前端页面

| 页面 | 业务 |
|------|------|
| Login、Home、Workbench | 登录、首页、工作台 |
| Account、User、Role、Privilege、Usergroup | 账号、用户、角色、权限、用户组 |
| Customer、CustManager、CustView | 客户、客户经理、客户视图 |
| Goods、Order、Store、Sales | 商品、订单、店铺、销售 |
| Flow、TaskManagement、Plan | 流程、任务、计划 |
| Invoice、InvoiceStatusSearch、BalanceApply | 发票、余额申请 |
| Marketing、Evaluate、Monitor | 营销、评价、监控 |
| CMS、PageConfig、TermsOfServices、Agreement | CMS、页面配置、服务条款、协议 |
| AntiFraudBlackList、CircuitBreak、CardPreApproval | 反欺诈黑名单、熔断、卡预审 |
| AuditDetail、InspectionList、DisassemblyReserve、Demolition | 审核、巡检、拆机预约、拆机 |
| EnterpriseRun、Registered | 企业运营、注册 |
| TableExport | 表格导出 |

### 2.4 核心业务关系

```
组织(org) ──┬── 用户(user) ──┬── 角色(role) ── 权限(privilege)
            │                │
            └── 用户组(usergroup)   │
                                   └── 渠道(channel/salechannel)
                                   └── 区域(area)
                                   └── 黑名单(blacklist)/风控(risklist)
```

- **用户体系**：主账号、子账号、管理员、普通操作员；支持分级管理（上级管理员只能管理下级）
- **权限体系**：角色-权限关联、菜单权限、数据权限、属性权限
- **组织体系**：组织架构、区域（省市区）

---

## 三、技术架构

### 3.1 bms_Polaris（后端）

- **包名**：`com.iwhalecloud.dmos.bms`
- **架构**：DDD 分层，controller 通过 Spring Cloud 调用 app
- **模块**：bms-app、bms-controller、bms-domain、bms-infrastructure、bms-client、bms-plugins、bms-verify
- **技术**：Spring Boot 2.1.2、Spring Cloud Greenwich、MyBatis-Plus、Swagger、JWT、Druid、Elasticsearch、MinIO、Redis、Ehcache、CtgMQ、CtgCache、Udal
- **启动**：Nacos → BmsAppApplication(8081) → BmsControllerApplication(8089)
- **扩展点**：BizCode + ExtensionPoint，支持多业务身份扩展

### 3.2 tms-React_Polaris（前端）

- **入口**：`yarn start`（管理）、`yarn start busi`（商家）
- **账号**：管理 superman/Abcde!12345!；商家 18988888888@qq.com/Abcde!12345!
- **流程号**：newsalesplatform_busi(12857)、newsalesplatform_pc(12446)、APP-H5(12884)

---

## 四、应用门户

- **管理门户**：PC，面向平台运营/管理员
- **商家门户**：PC，面向商家用户（主账号、管理员、操作员）
- **商城/H5**：手机端

---

## 五、需求分析与设计约束

1. **必须基于 newsales**：需求分析、设计文档需说明与 bms/tms 的集成方式、涉及的中心和模块
2. **遵循现有模块**：新增功能归属到已有 service/domain（如 user、role、privilege 等），或说明新增模块理由
3. **遵循技术栈**：Spring Boot、React、DDD 分层、扩展点、缓存、事件驱动
4. **参考代码**：`newsales/bms_Polaris`、`newsales/tms-React_Polaris`
