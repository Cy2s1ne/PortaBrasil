# PortaBrasil — 巴西海关清关管理系统

> 一个全栈 Web 平台，用于管理巴西海关清关全流程业务，涵盖 PDF 单据上传与 AI 智能解析、10 步清关流程跟踪、成本费用分析，以及 AI 辅助业务审计与财务复核。

---

## 目录

- [项目概述](#项目概述)
- [系统架构](#系统架构)
- [技术栈](#技术栈)
- [项目结构](#项目结构)
- [功能特性](#功能特性)
- [快速开始](#快速开始)
  - [环境要求](#环境要求)
  - [后端安装](#后端安装)
  - [前端安装](#前端安装)
- [配置说明](#配置说明)
- [数据库](#数据库)
- [接口文档](#接口文档)
- [用户操作指南](#用户操作指南)
- [系统模块](#系统模块)
- [安全机制](#安全机制)
- [开发指南](#开发指南)

---

## 项目概述

PortaBrasil 是一款面向物流公司、报关行和货代企业的 **巴西海关清关业务管理平台**。它将清关全流程数字化——从上传原始 PDF 单据（提单、发票、海关申报单等），经过 AI 辅助数据提取、财务成本分析，到完整的 10 步清关生命周期管理。

系统内置支持 **三种语言**：简体中文、英语、葡萄牙语。

---

## 系统架构

```
┌─────────────────────────────────────────────────────────┐
│            浏览器 (React SPA)                            │
│  http://localhost:5173                                  │
└─────────────────────┬───────────────────────────────────┘
                      │ HTTP / REST API (JSON)
┌─────────────────────▼───────────────────────────────────┐
│            Flask 后端 API                                │
│  http://localhost:5001 /api/*                           │
│  ┌──────────┬───────────┬───────────┬─────────────┐      │
│  │ 认证模块  │ PDF 解析  │ 业务与成本 │ AI 审计与   │      │
│  │          │          │           │ 财务复核    │      │
│  └──────────┴───────────┴───────────┴─────────────┘      │
└─────────────────────┬───────────────────────────────────┘
                      │ SQL
┌─────────────────────▼───────────────────────────────────┐
│         MySQL 8.x  (生产环境)                            │
│         SQLite      (开发环境，自动创建)                  │
└─────────────────────────────────────────────────────────┘
```

---

## 技术栈

| 层级 | 技术 |
|---|---|
| **前端** | React 19, Vite 7, Tailwind CSS 3, Lucide React |
| **后端** | Python 3.11+, Flask 3, Flask-CORS |
| **认证** | JWT (PyJWT)，SHA-256 密码哈希 |
| **数据库** | MySQL 8.x（生产）/ SQLite（开发）|
| **AI 解析** | 智谱 AI（ZAI SDK）— PDF 文档解析 |
| **AI 审核** | 智谱 AI（ZAI SDK）— 业务审计与财务分析 |
| **ORM** | SQLAlchemy 风格原生 SQL（pymysql / sqlite3）|
| **汇率** | Open Exchange Rates API（回退：数据库缓存汇率）|

---

## 项目结构

```
PortaBrasil/
├── Portabrasil-server/           # Flask 后端
│   ├── main.py                   # 启动入口
│   ├── app/
│   │   ├── factory.py            # App 工厂（CORS、错误处理、蓝图注册）
│   │   ├── core/
│   │   │   ├── auth.py           # JWT、密码哈希、认证装饰器
│   │   │   └── responses.py      # 统一 JSON 响应封装
│   │   └── routes/
│   │       ├── health.py         # GET /api/health
│   │       ├── auth.py           # 登录/注册/忘记密码/用户管理
│   │       ├── files.py          # PDF 上传 & 解析触发
│   │       ├── documents.py      # 原始文本入库
│   │       ├── business.py        # 业务记录 CRUD & 费用查询
│   │       ├── tasks.py           # 解析任务状态查询
│   │       ├── dashboard.py       # 首页仪表盘数据
│   │       ├── process.py         # 10 步清关流程跟踪
│   │       ├── reports.py         # 报表记录
│   │       ├── cost.py            # 成本分析 & 汇率
│   │       ├── ai_review.py       # AI 审计与财务复核
│   │       └── admin.py           # 用户管理
│   ├── database.py               # 数据库连接 & SQLite 模式
│   ├── services.py               # 业务逻辑服务
│   ├── pdf_parser.py             # 智谱 AI PDF 解析器
│   ├── parser_rules.py           # 正则提取规则
│   ├── sql/
│   │   └── migrations/           # 增量迁移脚本
│   └── instance/                 # SQLite 数据库自动创建于此
│
├── Portabrasil-web/
│   └── customs-dashboard/        # React 前端
│       ├── src/
│       │   ├── App.jsx           # 主应用外壳（侧边栏、顶栏、路由分发）
│       │   ├── LoginPage.jsx     # 登录页
│       │   ├── views/
│       │   │   ├── HomeView.jsx           # 首页仪表盘
│       │   │   ├── UploadView.jsx         # PDF 上传
│       │   │   ├── ProcessTrackingView.jsx # 10 步流程跟踪
│       │   │   ├── CostAnalysisView.jsx   # 成本计算 & 记录
│       │   │   ├── ReportView.jsx         # 报表中心
│       │   │   └── AdminManagementView.jsx # 用户 & 角色管理
│       │   ├── components/navigation/
│       │   │   └── SidebarItem.jsx
│       │   └── shared/
│       │       ├── auth/storage.js   # JWT 存储（localStorage / sessionStorage）
│       │       ├── config/api.js     # API 基础地址配置
│       │       ├── i18n/
│       │       │   ├── translations.js      # 全部 UI 翻译（zh / en / pt）
│       │       │   └── language-context.jsx
│       │       ├── utils/
│       │       │   ├── http.js    # 带认证的 fetch 封装
│       │       │   └── format.js  # 数字 / 货币格式化
│       │
│       └── package.json
│
├── portabrasil.sql                # MySQL 完整模式导出
└── docs/
    ├── README.md                # 英文 README
    └── 系统模块流程图.md          # 模块流程图（Mermaid）
```

---

## 功能特性

### 1. 登录认证与权限控制
- 基于 JWT 的身份认证（访问令牌，120 分钟过期）
- **5 种角色**：超级管理员、管理员、货代、报关员、财务
- 所有受保护接口均做 RBAC 校验
- 密码 SHA-256 哈希存储（登录时自动升级旧明文密码）
- 用户注册、密码重置

### 2. PDF 单据上传与解析
- 上传 PDF 文件（最大 25 MB）
- SHA-256 哈希去重
- 智谱 AI 智能解析（支持 LLM / OCR / RULE 三种解析模式）
- 异步任务轮询解析状态
- 按 S/Ref Upsert——同一单据重新上传会更新已有记录
- 原始文本直接入库接口（适用于直接输入解析结果）

### 3. 业务数据提取
解析 PDF 后自动提取：
- **头部字段**：S/Ref、N/Ref、发票号、NF 号、流程号
- **企业信息**：客户名称、地址、城市、州、税号（CNPJ/CPF）、开单公司
- **运输信息**：MAWB/MBL（主运单）、HAWB/HBL（分运单）、船名/航班
- **关键日期**：登记日期、到港日期、清关日期、装载日期
- **货物信息**：毛重、体积件数、货物描述
- **财务数据**：运费（币种+金额）、FOB、CIF、CIF-雷亚尔、汇率
- **费用明细**：日期+代码+名称+借贷金额（每条记录最多 50 条费用项）

### 4. 10 步清关流程跟踪
- 每个提单号（BL）对应一条流程记录
- 每条流程记录有 10 个步骤，逐一跟踪：待处理(PENDING) / 已完成(COMPLETE)
- 自动推导整体状态：
  - 10 步全部完成 → **CLEARED**（已清关，绿色）
  - 第 6 步及以上完成 → **INSPECTION**（查验中，黄色）
  - 其他情况 → **PROCESSING**（处理中，蓝色）
- 可编辑每个步骤的状态、完成时间和描述

### 5. 成本分析
- 输入：海关费、退税、美元额、汇率、其他费用、商品数量
- 计算：净海关费、美元折算、总成本、单件成本
- 实时获取汇率（USD/BRL），数据库缓存，有回退默认值
- 保存计算记录到历史，支持按商品明细分摊
- AI 财务健康度复核（基于规则引擎）

### 6. AI 业务审计与财务复核
- **业务审计**（`POST /api/ai-review/business/:id/run`）：
  - 借贷余额一致性
  - 费用明细汇总一致性
  - 核心字段完整性（发票号、DI 编号）
  - 退款金额异常检测
- **财务复核**（`POST /api/ai-review/cost-record/:id/review`）：
  - 总数量有效性
  - 汇率合理性（0 < 汇率 ≤ 20）
  - 退款与海关费比例
  - 单件成本 > 0
- 结果存入数据库：风险等级、评分、具体问题、建议、证据

### 7. 仪表盘与报表
- 首页：总记录数、各状态数量、税费总额、10 步看板、最近活动时间轴
- 报表中心：可筛选/搜索的所有清关记录列表

### 8. 多语言支持
- UI 支持：**简体中文（zh）**、**英语（en）**、**葡萄牙语（pt）**
- 顶栏右侧语言切换按钮即时切换
- 所有界面标签、提示信息均有三种翻译

---

## 快速开始

### 环境要求

- **Python** 3.11+
- **Node.js** 18+ 和 **npm**
- （可选）**MySQL 8.x** — 未配置时自动使用 SQLite
- （可选）**智谱 AI API Key** — 仅在使用 PDF 解析和 AI 审核功能时需要

### 后端安装

```bash
# 1. 进入后端目录
cd PortaBrasil/Portabrasil-server

# 2. 安装依赖
uv sync
# 或用 pip: pip install -e .

# 3. （可选）设置环境变量
export DATABASE_URL='mysql://root:password@127.0.0.1:3306/portabrasil?charset=utf8mb4'
export ZHIPU_API_KEY='your-zhipu-api-key'
export JWT_SECRET='your-long-random-secret-here'
export JWT_EXPIRES_MINUTES='120'

# 4. 初始化 MySQL 数据库（如使用 MySQL）
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS portabrasil DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
mysql -u root -p portabrasil < ../portabrasil.sql

# 5. 启动服务
uv run flask --app main run --host 0.0.0.0 --port 5001 --debug
```

> **注意**：未设置 `DATABASE_URL` 时，服务器自动使用 SQLite（`instance/portabrasil.db`），非常适合本地开发。

**默认管理员账号**（由 `portabrasil.sql` 初始化）：
- 用户名：`admin`
- 密码：`admin123456`

### 前端安装

```bash
# 1. 进入前端目录
cd PortaBrasil/Portabrasil-web/customs-dashboard

# 2. 安装依赖
npm install

# 3. 启动开发服务器
npm run dev
```

前端运行在 `http://localhost:5173`，会自动代理 API 请求到 `http://localhost:5001`。

---

## 配置说明

### 环境变量（后端）

| 变量 | 默认值 | 说明 |
|---|---|---|
| `DATABASE_URL` | SQLite（`instance/portabrasil.db`）| MySQL 连接字符串 |
| `ZHIPU_API_KEY` | — | 智谱 AI API Key（PDF 解析与 AI 审核用）|
| `JWT_SECRET` | `change-this-in-production...` | JWT 签名密钥 |
| `JWT_EXPIRES_MINUTES` | `120` | JWT 访问令牌过期时间（分钟）|
| `UPLOAD_DIR` | `./uploads` | 上传 PDF 的存储目录 |
| `DEFAULT_REGISTER_ROLE` | `FORWARDER` | 新注册用户默认角色 |

### 环境变量（前端）

| 变量 | 默认值 | 说明 |
|---|---|---|
| `VITE_API_BASE_URL` | `http://127.0.0.1:5001` | 后端 API 基础地址 |

---

## 数据库

### 支持的数据库

| 环境 | 数据库 | 模式来源 |
|---|---|---|
| 生产环境 | MySQL 8.x | `portabrasil.sql`（完整模式） |
| 开发环境 | SQLite | 由 `database.py` 自动创建 |

### 增量迁移（MySQL）

已有数据库不想全量重建时，执行增量迁移：

```bash
# 成本模块 + 汇率缓存 + AI 审核相关表
mysql -u root -p portabrasil < Portabrasil-server/sql/migrations/20260416_add_cost_module_tables.sql
mysql -u root -p portabrasil < Portabrasil-server/sql/migrations/20260416_add_ai_review_tables.sql
```

### 核心数据表

| 表名 | 用途 |
|---|---|
| `pdf_file` | 上传的 PDF 文件 |
| `pdf_parse_task` | 解析任务状态 & 原始结果 |
| `customs_business` | 核心业务记录（每条对应一个 S/Ref）|
| `customs_business_fee_item` | 每条业务记录的费明细 |
| `users` | 用户账号 |
| `roles` | 5 种预定义角色 |
| `user_role` | 用户-角色多对多映射 |
| `customs_process_record` | 每个提单号的清关流程主记录 |
| `customs_process_step` | 10 步流程节点状态 |
| `customs_activity` | 首页活动时间轴 |
| `fx_rate_cache` | 汇率缓存 |
| `customs_cost_record` | 成本分析主记录 |
| `customs_cost_item` | 每条成本记录的商品明细 |
| `ai_audit_run` / `ai_audit_finding` | AI 业务审计运行 & 问题列表 |
| `ai_finance_review` / `ai_finance_item` | AI 财务复核运行 & 问题列表 |

> 注意：`statement_summary` 和 `statement_summary_item` 仅存在于 MySQL 模式（`portabrasil.sql`），不在 SQLite 开发模式中。

---

## 接口文档

### 公开接口（无需认证）

| 方法 | 路径 | 说明 |
|---|---|---|
| `GET` | `/api/health` | 健康检查 |
| `POST` | `/api/auth/login` | 登录（返回 JWT）|
| `POST` | `/api/auth/register` | 注册新用户 |
| `POST` | `/api/auth/forgot-password` | 密码重置 |

### 仪表盘与流程

| 方法 | 路径 | 说明 |
|---|---|---|
| `GET` | `/api/dashboard/overview` | 首页统计数据 |
| `GET` | `/api/process/records` | 清关记录列表 |
| `GET` | `/api/process/records/{id}` | 清关记录详情 |
| `PUT` | `/api/process/records/{id}/steps/{no}` | 更新步骤状态 |
| `GET` | `/api/reports/records` | 报表记录列表 |

### 业务与文件

| 方法 | 路径 | 说明 |
|---|---|---|
| `POST` | `/api/files/upload` | 上传 PDF（multipart）|
| `GET` | `/api/files` | 文件列表 |
| `GET` | `/api/files/{id}` | 文件详情 |
| `POST` | `/api/files/{id}/parse` | 触发解析 |
| `GET` | `/api/tasks/{id}` | 解析任务状态 |
| `POST` | `/api/documents/from-text` | 原始文本入库 |
| `GET` | `/api/business` | 搜索业务记录 |
| `GET` | `/api/business/{id}` | 业务记录详情 |
| `GET` | `/api/business/{id}/fees` | 费用明细 |

### 成本分析

| 方法 | 路径 | 说明 |
|---|---|---|
| `GET` | `/api/cost/overview` | 成本概览 |
| `GET` | `/api/cost/exchange-rate` | 查询汇率 |
| `POST` | `/api/cost/calculate` | 成本计算 |
| `POST` | `/api/cost/records` | 保存成本记录 |
| `GET` | `/api/cost/records` | 成本记录列表 |
| `GET` | `/api/cost/records/{id}` | 成本记录详情 |

### AI 审核

| 方法 | 路径 | 说明 |
|---|---|---|
| `POST` | `/api/ai-review/business/{id}/run` | 执行业务审计 |
| `GET` | `/api/ai-review/audit/runs` | 审计运行列表 |
| `GET` | `/api/ai-review/audit/runs/{id}` | 审计运行详情 |
| `POST` | `/api/ai-review/cost-record/{id}/review` | 执行财务复核 |
| `GET` | `/api/ai-review/finance/reviews` | 财务复核列表 |

### 系统管理

| 方法 | 路径 | 说明 |
|---|---|---|
| `GET` | `/api/auth/me` | 获取当前用户信息 |
| `POST` | `/api/auth/users` | 创建用户（仅管理员）|
| `PUT` | `/api/auth/users/{id}` | 更新用户（仅管理员）|
| `PUT` | `/api/auth/users/{id}/password` | 重置密码（仅管理员）|
| `PUT` | `/api/auth/users/{id}/status` | 启用/禁用用户（仅管理员）|

---

## 用户操作指南

### 登录

1. 打开 `http://localhost:5173`
2. 输入账号密码（默认：`admin` / `admin123456`）
3. 登录成功后跳转至首页仪表盘
4. 右上角点击 **ZH / EN / PT** 按钮切换语言

### 上传单据

1. 点击侧边栏 **资料上传**
2. 选择一个 PDF 文件
3. 选择 **上传并立即解析** 或 **仅上传**
4. 若选择 **上传并立即解析**：等待任务完成（约 10–30 秒）
5. 可在资料上传页面或任务列表查看解析状态

### 清关流程跟踪

1. 点击侧边栏 **流程跟踪**
2. 浏览清关记录列表（可按提单号、货物描述、状态筛选）
3. 点击任意记录进入详情页
4. 10 步看板展示每步状态：⬜ 待处理 / ✅ 已完成
5. 点击任意步骤的 **编辑** 按钮，设置状态和完成日期
6. 保存后整体状态自动推导（处理中 → 查验中 → 已清关）

### 成本分析

1. 点击侧边栏 **成本分析**
2. 输入：海关费、退税、美元额、汇率、其他费用、商品数量
3. 点击 **计算**——查看净费用、美元折算、总成本、单件成本
4. 点击 **保存记录** 持久化到历史
5. 点击任意历史记录，查看按商品分摊的成本明细

### AI 审计与财务复核

1. 进入任意业务记录或成本记录详情页
2. 点击 **AI 审计** 或 **财务复核** 按钮
3. 系统执行审核并展示结果
4. 结果包含：风险/健康等级、评分、具体问题列表（含严重程度、证据、建议）

### 系统管理（管理员）

1. 点击侧边栏 **系统管理**——仅 SUPER_ADMIN 和 ADMIN 角色可见
2. 查看、创建、更新或禁用用户账号
3. 分配或变更用户角色
4. 重置用户密码

---

## 系统模块

系统共包含 **9 大核心模块**，详细流程图见 `docs/系统模块流程图.md`：

| # | 模块 | 说明 |
|---|---|---|
| 1 | 登录认证 | JWT 认证、5 角色 RBAC |
| 2 | 资料上传 | PDF 上传、SHA-256 去重 |
| 3 | 单据解析 | 智谱 AI PDF 解析、字段提取 |
| 4 | 审计校验 | AI 业务审计 + 财务复核 |
| 5 | 费用核算 | 成本计算、汇率换算 |
| 6 | 流程流转 | 10 步清关生命周期 |
| 7 | 任务管理 | 异步解析任务状态追踪 |
| 8 | 统计分析 | 首页看板、活动时间轴 |
| 9 | 系统管理 | 用户 CRUD、角色分配 |

---

## 安全机制

- **JWT Bearer Token**：除 `/api/health`、`/api/auth/login`、`/api/auth/register`、`/api/auth/forgot-password` 外，所有接口均需认证
- **密码安全**：SHA-256 哈希存储，登录时自动升级旧明文密码
- **CORS**：开发环境全开，生产环境请限制
- **SQL 注入防护**：所有查询使用参数化语句
- **超管保护**：SUPER_ADMIN 账号不能通过 API 修改或禁用
- **自禁用保护**：用户不能禁用自己的账号
- **越权防护**：非超管不能分配 SUPER_ADMIN 角色

---

## 开发指南

### 新增后端路由

1. 在 `Portabrasil-server/app/routes/` 下创建新文件，如 `my_resource.py`
2. 在 `app/factory.py` 中注册蓝图：
   ```python
   from app.routes.my_resource import bp as my_resource_bp
   # ...
   app.register_blueprint(my_resource_bp, url_prefix='/api/my-resource')
   ```
3. 使用 `@jwt_required` 装饰器保护需要认证的路由
4. 统一使用 `api_response()`（来自 `app/core/responses.py`）返回 JSON

### 新增前端页面

1. 在 `src/views/` 下创建新的 `.jsx` 文件
2. 在 `src/views/index.js` 中导出
3. 在 `App.jsx` 的 `menuItems` 数组和 `renderContent()` switch 中添加

### 运行测试

人工验收测试（无需写单元测试）：
1. 启动后端：`cd Portabrasil-server && uv run flask --app main run --port 5001 --debug`
2. 启动前端：`cd Portabrasil-web/customs-dashboard && npm run dev`
3. 打开 `http://localhost:5173`，按照[用户操作指南](#用户操作指南)逐步体验

---

*PortaBrasil — 让巴西海关清关更简单。*
