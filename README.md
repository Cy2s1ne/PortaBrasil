# PortaBrasil

<!-- Language Switcher -->
<div align="center">

**[English](#overview)** &nbsp;|&nbsp; **[简体中文](#项目概述)** &nbsp;|&nbsp; **[Português](#visão-geral)**

</div>

---

<!-- ============================================================
     ENGLISH SECTION
     ============================================================ -->

## Overview

**PortaBrasil** is a full-stack web platform for managing **Brazilian customs clearance operations**. It digitizes the end-to-end clearance workflow — from uploading raw PDF documents (bills of lading, invoices, customs declarations) through AI-assisted data extraction, financial cost analysis, and the full 10-step clearance process lifecycle.

Target users: logistics companies, customs brokers, and freight forwarders.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│              Browser (React SPA)                        │
│  http://localhost:5173                                  │
└─────────────────────┬───────────────────────────────────┘
                      │ HTTP / REST API (JSON)
┌─────────────────────▼───────────────────────────────────┐
│            Flask Backend                                │
│  http://localhost:5001 /api/*                           │
│  ┌──────────┬───────────┬───────────┬─────────────┐     │
│  │ Auth     │ PDF Parse │ Business  │ AI Audit &  │     │
│  │ Module   │ Module    │ & Cost    │ Finance Rev │     │
│  └──────────┴───────────┴───────────┴─────────────┘     │
└─────────────────────┬───────────────────────────────────┘
                      │ SQL
┌─────────────────────▼───────────────────────────────────┐
│         MySQL 8.x  (production)                         │
│         SQLite      (development, auto-created)         │
└─────────────────────────────────────────────────────────┘
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | React 19, Vite 7, Tailwind CSS 3, Lucide React |
| **Backend** | Python 3.11+, Flask 3, Flask-CORS |
| **Auth** | JWT (PyJWT), SHA-256 password hashing |
| **Database** | MySQL 8.x (production) / SQLite (development) |
| **AI Parsing** | Zhipu AI (ZAI SDK) — PDF document parsing |
| **AI Review** | Zhipu AI (ZAI SDK) — Audit & financial analysis |
| **ORM** | SQLAlchemy-style raw SQL (pymysql / sqlite3) |
| **Exchange Rates** | Open Exchange Rates API (fallback: cached rates) |

---

## Project Structure

```
PortaBrasil/
├── Portabrasil-server/           # Flask Backend
│   ├── main.py                   # Entry point
│   ├── app/
│   │   ├── factory.py            # App factory (CORS, error handling, blueprints)
│   │   ├── core/
│   │   │   ├── auth.py           # JWT, password hashing, auth decorator
│   │   │   └── responses.py      # Unified JSON response helpers
│   │   └── routes/
│   │       ├── health.py          # GET /api/health
│   │       ├── auth.py           # Auth: login / register / forgot-password / users
│   │       ├── files.py          # PDF upload & parse triggers
│   │       ├── documents.py      # Raw text ingestion
│   │       ├── business.py       # Business record CRUD & fee query
│   │       ├── tasks.py          # Parse task status
│   │       ├── dashboard.py      # Homepage statistics
│   │       ├── process.py        # 10-step clearance tracking
│   │       ├── reports.py        # Report records
│   │       ├── cost.py           # Cost analysis & exchange rates
│   │       ├── ai_review.py      # AI audit & finance review
│   │       └── admin.py          # User management
│   ├── database.py               # DB connection & SQLite schema
│   ├── services.py               # Business logic services
│   ├── pdf_parser.py            # Zhipu AI PDF parser
│   ├── parser_rules.py           # Regex rules for field extraction
│   ├── sql/                        # SQL schema directory
│   └── instance/                 # SQLite DB auto-created here
│
├── Portabrasil-web/
│   └── customs-dashboard/        # React Frontend
│       ├── src/
│       │   ├── App.jsx           # Main app shell (sidebar, header, routing)
│       │   ├── LoginPage.jsx    # Login page
│       │   ├── views/
│       │   │   ├── HomeView.jsx           # Dashboard overview
│       │   │   ├── UploadView.jsx         # PDF upload
│       │   │   ├── ProcessTrackingView.jsx # 10-step process tracking
│       │   │   ├── CostAnalysisView.jsx   # Cost calculation & records
│       │   │   ├── ReportView.jsx         # Reports
│       │   │   └── AdminManagementView.jsx # User & role management
│       │   ├── components/navigation/
│       │   │   └── SidebarItem.jsx
│       │   └── shared/
│       │       ├── auth/storage.js   # JWT storage
│       │       ├── config/api.js     # API base URL config
│       │       ├── i18n/
│       │       │   ├── translations.js      # All UI translations (zh/en/pt)
│       │       │   └── language-context.jsx
│       │       └── utils/
│       │           ├── http.js    # Authenticated fetch helper
│       │           └── format.js  # Number/currency formatters
│       └── package.json
│
├── portabrasil.sql                # MySQL full schema dump
└── docs/
    ├── README_zh.md              # Chinese version
    ├── README_pt.md              # Portuguese version
    └── 系统模块流程图.md          # Module flow diagrams (Mermaid)
```

---

## Features

### 1. Authentication & Authorization
- JWT-based authentication (access token, 120-minute expiry)
- 5 roles: **Super Admin**, **Admin**, **Forwarder**, **Customs Officer**, **Finance**
- Role-based access control (RBAC) on all protected endpoints
- Password SHA-256 hashing (with legacy plaintext upgrade on login)
- User registration, password reset

### 2. PDF Document Upload & Parsing
- Upload PDF files (max 25 MB) with SHA-256 hash deduplication
- AI-powered parsing via Zhipu AI (supports LLM / OCR / RULE parser types)
- Async task polling for parse status
- Upsert by S/Ref — re-uploading the same document updates existing records
- Raw text ingestion endpoint for direct text input

### 3. Business Data Extraction
Extracts from parsed PDFs: S/Ref, N/Ref, Invoice No., NF No., customer details (name, address, city, state, CNPJ/CPF), shipping docs (MAWB/MBL, HAWB/HBL), key dates (registration, arrival, clearance, loading), cargo info (weight, volume, description), financials (freight, FOB, CIF, CIF-BRL, exchange rates), and up to 50 fee line items per record.

### 4. 10-Step Customs Clearance Process
- Each Bill of Lading (BL) maps to one process record
- 10 sequential steps per process: PENDING / COMPLETE
- Auto-derive overall status: all complete → **CLEARED** | step 6+ → **INSPECTION** | otherwise → **PROCESSING**
- Editable step status, completion time, and description

### 5. Cost Analysis
- Input: customs fee, refund, USD amount, exchange rate, other fees, quantity
- Calculated: net customs fee, USD-to-BRL conversion, total cost, per-unit cost
- Real-time USD/BRL rate fetching with database cache and fallback
- Save calculation records to history with per-product breakdown
- AI financial health review with rule-based checks

### 6. AI Audit & Financial Review
- **Business Audit** (`POST /api/ai-review/business/:id/run`): debit/credit balance, fee summary consistency, field completeness, refund anomaly
- **Financial Review** (`POST /api/ai-review/cost-record/:id/review`): quantity validity, rate reasonability, refund ratio, per-unit cost positivity
- Results: risk level, score, findings with severity, evidence, suggestions

### 7. Dashboard & Reports
- Homepage: total records, status breakdown, tax totals, step kanban, activity feed
- Report view: filterable/searchable clearance records

### 8. Internationalization
- UI in **Simplified Chinese (zh)**, **English (en)**, **Portuguese (pt)**
- Language switcher in the header toolbar

---

## Quick Start

### Prerequisites
- **Python** 3.11+, **Node.js** 18+, **npm**
- (Optional) **MySQL 8.x** — SQLite used automatically if not set
- (Optional) **Zhipu AI API Key** — required only for PDF parsing and AI review

### Backend Setup

```bash
cd PortaBrasil/Portabrasil-server
uv sync

# Optional: set environment variables
export DATABASE_URL='mysql://root:password@127.0.0.1:3306/portabrasil?charset=utf8mb4'
export ZHIPU_API_KEY='your-zhipu-api-key'
export JWT_SECRET='your-long-random-secret-here'
export UPLOAD_DIR=''
export DASHSCOPE_API_KEY='your-dashscope-api-key'
export FX_API_ID='your-fx-api-id'
export FX_API_KEY='your-fx-api-key'

# MySQL: initialize database
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS portabrasil DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
mysql -u root -p portabrasil < ../portabrasil.sql

# Start server
uv run flask --app main run --host 0.0.0.0 --port 5001 --debug
```

> Without `DATABASE_URL`, the server automatically uses SQLite (`instance/portabrasil.db`).

**Default credentials**: `admin` / `admin123456`

### Frontend Setup

```bash
cd PortaBrasil/Portabrasil-web/customs-dashboard
npm install
npm run dev
```

Frontend at `http://localhost:5173` proxies API to `http://localhost:5001`.

---

## Configuration

### Backend Environment Variables

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | SQLite (`instance/portabrasil.db`) | MySQL connection string |
| `ZHIPU_API_KEY` | — | Zhipu AI API key for PDF parsing |
| `JWT_SECRET` | `change-this-in-production...` | JWT signing secret |
| `JWT_EXPIRES_MINUTES` | `120` | Token expiry in minutes |
| `UPLOAD_DIR` | `./uploads` | Uploaded PDF storage directory |
| `DEFAULT_REGISTER_ROLE` | `FORWARDER` | Role for new registrations |

### Frontend Environment Variables

| Variable | Default | Description |
|---|---|---|
| `VITE_API_BASE_URL` | `http://127.0.0.1:5001` | Backend API base URL |

---

## Database

| Environment | Engine | Schema Source |
|---|---|---|
| Production | MySQL 8.x | `portabrasil.sql` (full dump) |
| Development | SQLite | Auto-created by `database.py` |

**MySQL incremental migrations** (existing database upgrade — no longer needed, all tables are in `portabrasil.sql`):
```bash
# All tables are included in portabrasil.sql. If you have an existing database,
# drop and re-import for a clean setup:
mysql -u root -p portabrasil < portabrasil.sql
```

**Core tables**: `pdf_file`, `pdf_parse_task`, `customs_business`, `customs_business_fee_item`, `users`, `roles`, `user_role`, `customs_process_record`, `customs_process_step`, `customs_activity`, `fx_rate_cache`, `customs_cost_record`, `customs_cost_item`, `ai_audit_run`, `ai_audit_finding`, `ai_finance_review`, `ai_finance_item`

> Note: `statement_summary` and `statement_summary_item` exist only in the MySQL schema.

---

## API Reference

### Public (No Auth)
| Method | Path | Description |
|---|---|---|
| `GET` | `/api/health` | Health check |
| `POST` | `/api/auth/login` | Login (returns JWT) |
| `POST` | `/api/auth/register` | Register new user |
| `POST` | `/api/auth/forgot-password` | Reset password |

### Dashboard & Process
| Method | Path | Description |
|---|---|---|
| `GET` | `/api/dashboard/overview` | Homepage statistics |
| `GET` | `/api/process/records` | List clearance records |
| `GET` | `/api/process/records/{id}` | Get record detail |
| `PUT` | `/api/process/records/{id}/steps/{no}` | Update step status |
| `GET` | `/api/reports/records` | Report records |

### Business & Files
| Method | Path | Description |
|---|---|---|
| `POST` | `/api/files/upload` | Upload PDF (multipart) |
| `GET` | `/api/files` | List files |
| `GET` | `/api/files/{id}` | Get file detail |
| `POST` | `/api/files/{id}/parse` | Trigger parse |
| `GET` | `/api/tasks/{id}` | Get parse task status |
| `POST` | `/api/documents/from-text` | Raw text ingestion |
| `GET` | `/api/business` | Search business records |
| `GET` | `/api/business/{id}` | Get business record |
| `GET` | `/api/business/{id}/fees` | Get fee items |

### Cost Analysis
| Method | Path | Description |
|---|---|---|
| `GET` | `/api/cost/overview` | Cost overview |
| `GET` | `/api/cost/exchange-rate` | Get exchange rate |
| `POST` | `/api/cost/calculate` | Calculate cost |
| `POST` | `/api/cost/records` | Save cost record |
| `GET` | `/api/cost/records` | List cost records |
| `GET` | `/api/cost/records/{id}` | Get cost record detail |

### AI Review
| Method | Path | Description |
|---|---|---|
| `POST` | `/api/ai-review/business/{id}/run` | Run business audit |
| `GET` | `/api/ai-review/audit/runs` | List audit runs |
| `GET` | `/api/ai-review/audit/runs/{id}` | Get audit run detail |
| `POST` | `/api/ai-review/cost-record/{id}/review` | Run financial review |
| `GET` | `/api/ai-review/finance/reviews` | List finance reviews |

### Admin
| Method | Path | Description |
|---|---|---|
| `GET` | `/api/auth/me` | Get current user |
| `POST` | `/api/auth/users` | Create user (admin only) |
| `PUT` | `/api/auth/users/{id}` | Update user (admin only) |
| `PUT` | `/api/auth/users/{id}/password` | Reset password (admin only) |
| `PUT` | `/api/auth/users/{id}/status` | Enable/disable user (admin only) |

---

## User Guide

### Logging In
1. Open `http://localhost:5173`
2. Enter `admin` / `admin123456`
3. Switch language with the **ZH / EN / PT** button in the top-right toolbar

### Uploading a Document
1. Click **Upload** in the sidebar
2. Select a PDF file
3. Choose **Upload & Parse** or **Upload Only**
4. For **Upload & Parse**: wait ~10–30 seconds for completion

### Tracking a Clearance Process
1. Click **Process** in the sidebar
2. Browse records (filterable by BL number, status)
3. Click a record → 10-step kanban shows PENDING/COMPLETE per step
4. Click **Edit** on a step → set status + completion date → Save
5. Overall status auto-derives: PROCESSING → INSPECTION → CLEARED

### Cost Analysis
1. Click **Cost** in the sidebar
2. Enter: customs fee, refund, USD amount, rate, other fees, quantity
3. Click **Calculate** → see net fee, BRL conversion, total/per-unit cost
4. Click **Save Record** to persist to history

### AI Audit
1. Open a business record or cost record detail
2. Click **AI Audit** or **Finance Review**
3. Results show: risk/health level, score, findings with severity, evidence, suggestions

### Admin
1. Click **Admin** (visible only to SUPER_ADMIN and ADMIN roles)
2. Manage users: create, update, disable, reset passwords, assign roles

---

## System Modules

9 functional modules. See `docs/系统模块流程图.md` for Mermaid flow diagrams:

| # | Module | Description |
|---|---|---|
| 1 | Login Authentication | JWT auth, 5-role RBAC |
| 2 | Document Upload | PDF upload, SHA-256 deduplication |
| 3 | Document Parsing | Zhipu AI PDF parsing, field extraction |
| 4 | Audit & Review | AI business audit + financial review |
| 5 | Cost Accounting | Cost calculation with FX conversion |
| 6 | Process Tracking | 10-step clearance lifecycle |
| 7 | Task Management | Async parse task tracking |
| 8 | Statistics Dashboard | Homepage kanban, activity feed |
| 9 | System Administration | User CRUD, role assignment |

---

## Security

- **JWT Bearer tokens** on all protected endpoints
- **Password hashing**: SHA-256 with automatic plaintext upgrade on login
- **CORS**: open in development; restrict in production
- **SQL injection**: all queries use parameterized statements
- **SUPER_ADMIN protection**: super admin accounts cannot be modified/disabled via API
- **Self-disable prevention**: users cannot disable their own account
- **Role escalation prevention**: non-super-admins cannot assign SUPER_ADMIN role

---

## Development

### Adding a New Route
1. Create `app/routes/my_resource.py`
2. Register in `app/factory.py`:
   ```python
   from app.routes.my_resource import bp as my_resource_bp
   app.register_blueprint(my_resource_bp, url_prefix='/api/my-resource')
   ```
3. Use `@jwt_required` for protected routes and `api_response()` for JSON responses

### Adding a Frontend View
1. Create `src/views/MyView.jsx`
2. Export from `src/views/index.js`
3. Add to `menuItems` and `renderContent()` switch in `App.jsx`

### Running Tests
1. `cd Portabrasil-server && uv run flask --app main run --port 5001 --debug`
2. `cd Portabrasil-web/customs-dashboard && npm run dev`
3. Open `http://localhost:5173`

---

*PortaBrasil — Simplifying Brazilian Customs Operations.*

---

<!-- ============================================================
     CHINESE SECTION
     ============================================================ -->

## 项目概述

**PortaBrasil** 是一款面向物流公司、报关行和货代企业的 **巴西海关清关业务管理全栈平台**。它将清关全流程数字化——从上传原始 PDF 单据（提单、发票、海关申报单等），经过 AI 辅助数据提取、财务成本分析，到完整的 10 步清关生命周期管理。

目标用户：物流公司、报关行、货代企业。

---

## 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                   浏览器 (React SPA)                     │
│                 http://localhost:5173                   │
└─────────────────────┬───────────────────────────────────┘
                      │ HTTP / REST API (JSON)
┌─────────────────────▼───────────────────────────────────┐
│                   Flask 后端 API                         │
│             http://localhost:5001 /api/*                │
│  ┌──────────┬───────────┬───────────┬─────────────┐     │
│  │ 认证模块  │ PDF 解析   │ 业务与成本  │  AI 审计与   │      │
│  │          │           │           │ 财务复核     │     │
│  └──────────┴───────────┴───────────┴─────────────┘     │
└─────────────────────┬───────────────────────────────────┘
                      │ SQL
┌─────────────────────▼───────────────────────────────────┐
│         MySQL 8.x   (生产环境)                           │
│         SQLite      (开发环境，自动创建)                   │
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
│   │       ├── health.py          # GET /api/health
│   │       ├── auth.py           # 登录/注册/忘记密码/用户管理
│   │       ├── files.py          # PDF 上传 & 解析触发
│   │       ├── documents.py      # 原始文本入库
│   │       ├── business.py       # 业务记录 CRUD & 费用查询
│   │       ├── tasks.py          # 解析任务状态查询
│   │       ├── dashboard.py      # 首页仪表盘数据
│   │       ├── process.py        # 10 步清关流程跟踪
│   │       ├── reports.py        # 报表记录
│   │       ├── cost.py           # 成本分析 & 汇率
│   │       ├── ai_review.py      # AI 审计与财务复核
│   │       └── admin.py          # 用户管理
│   ├── database.py               # 数据库连接 & SQLite 模式
│   ├── services.py               # 业务逻辑服务
│   ├── pdf_parser.py            # 智谱 AI PDF 解析器
│   ├── parser_rules.py           # 正则提取规则
│   ├── sql/
│   ├── sql/                        # SQL 模式目录
│   └── instance/                 # SQLite 数据库自动创建于此
│
├── Portabrasil-web/
│   └── customs-dashboard/        # React 前端
│       ├── src/
│       │   ├── App.jsx           # 主应用外壳（侧边栏、顶栏、路由分发）
│       │   ├── LoginPage.jsx    # 登录页
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
│       │       ├── auth/storage.js   # JWT 存储
│       │       ├── config/api.js     # API 基础地址配置
│       │       ├── i18n/
│       │       │   ├── translations.js      # 全部 UI 翻译（zh/en/pt）
│       │       │   └── language-context.jsx
│       │       └── utils/
│       │           ├── http.js    # 带认证的 fetch 封装
│       │           └── format.js  # 数字 / 货币格式化
│       └── package.json
│
├── portabrasil.sql                # MySQL 完整模式导出
└── docs/
    ├── README.md                 # English version
    ├── README_pt.md              # Portuguese version
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
- 上传 PDF 文件（最大 25 MB），SHA-256 哈希去重
- 智谱 AI 智能解析（支持 LLM / OCR / RULE 三种解析模式）
- 异步任务轮询解析状态
- 按 S/Ref Upsert——同一单据重新上传会更新已有记录
- 原始文本直接入库接口（适用于直接输入解析结果）

### 3. 业务数据提取
解析 PDF 后自动提取：S/Ref、N/Ref、发票号、NF 号、客户信息（名称、地址、城市、州、CNPJ/CPF）、运输单据（MAWB/MBL、HAWB/HBL）、关键日期（登记、到港、清关、装载）、货物信息（毛重、体积、描述）、财务数据（运费、FOB、CIF、CIF-雷亚尔、汇率）、每条记录最多 50 条费用明细。

### 4. 10 步清关流程跟踪
- 每个提单号（BL）对应一条流程记录
- 每条流程有 10 个步骤逐一跟踪：待处理(PENDING) / 已完成(COMPLETE)
- 自动推导整体状态：全部完成 → **已清关** | 第6步+完成 → **查验中** | 其他 → **处理中**
- 可编辑每个步骤的状态、完成时间和描述

### 5. 成本分析
- 输入：海关费、退税、美元额、汇率、其他费用、商品数量
- 计算：净海关费、美元折算、总成本、单件成本
- 实时获取 USD/BRL 汇率，数据库缓存，有回退默认值
- 保存计算记录到历史，支持按商品明细分摊
- AI 财务健康度复核（基于规则引擎）

### 6. AI 业务审计与财务复核
- **业务审计**（`POST /api/ai-review/business/:id/run`）：借贷余额一致性、费用汇总一致性、字段完整性、退款异常检测
- **财务复核**（`POST /api/ai-review/cost-record/:id/review`）：数量有效性、汇率合理性、退款与海关费比例、单件成本 > 0
- 结果：风险/健康等级、评分、具体问题列表（含严重程度、证据、建议）

### 7. 仪表盘与报表
- 首页：总记录数、各状态数量、税费总额、10 步看板、最近活动时间轴
- 报表中心：可筛选/搜索的所有清关记录列表

### 8. 多语言支持
- UI 支持：**简体中文（zh）**、**英语（en）**、**葡萄牙语（pt）**
- 顶栏右侧语言切换按钮即时切换

---

## 快速开始

### 环境要求
- **Python** 3.11+、**Node.js** 18+、**npm**
- （可选）**MySQL 8.x** — 未配置时自动使用 SQLite
- （可选）**智谱 AI API Key** — 仅在 PDF 解析和 AI 审核时需要

### 后端安装

```bash
cd PortaBrasil/Portabrasil-server
uv sync

# 可选：设置环境变量
export DATABASE_URL='mysql://root:password@127.0.0.1:3306/portabrasil?charset=utf8mb4'
export ZHIPU_API_KEY='your-zhipu-api-key'
export JWT_SECRET='your-long-random-secret-here'
export UPLOAD_DIR=''
export DASHSCOPE_API_KEY='your-dashscope-api-key'
export FX_API_ID='your-fx-api-id'
export FX_API_KEY='your-fx-api-key'

# MySQL：初始化数据库
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS portabrasil DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
mysql -u root -p portabrasil < ../portabrasil.sql

# 启动服务
uv run flask --app main run --host 0.0.0.0 --port 5001 --debug
```

> 未设置 `DATABASE_URL` 时，服务器自动使用 SQLite（`instance/portabrasil.db`）。

**默认账号**：`admin` / `admin123456`

### 前端安装

```bash
cd PortaBrasil/Portabrasil-web/customs-dashboard
npm install
npm run dev
```

前端运行在 `http://localhost:5173`，自动代理 API 到 `http://localhost:5001`。

---

## 配置说明

### 后端环境变量

| 变量 | 默认值 | 说明 |
|---|---|---|
| `DATABASE_URL` | SQLite（`instance/portabrasil.db`）| MySQL 连接字符串 |
| `ZHIPU_API_KEY` | — | 智谱 AI API Key（PDF 解析与 AI 审核用）|
| `JWT_SECRET` | `change-this-in-production...` | JWT 签名密钥 |
| `JWT_EXPIRES_MINUTES` | `120` | JWT 访问令牌过期时间（分钟）|
| `UPLOAD_DIR` | `./uploads` | 上传 PDF 的存储目录 |
| `DEFAULT_REGISTER_ROLE` | `FORWARDER` | 新注册用户默认角色 |

### 前端环境变量

| 变量 | 默认值 | 说明 |
|---|---|---|
| `VITE_API_BASE_URL` | `http://127.0.0.1:5001` | 后端 API 基础地址 |

---

## 数据库

| 环境 | 数据库 | 模式来源 |
|---|---|---|
| 生产环境 | MySQL 8.x | `portabrasil.sql`（完整模式） |
| 开发环境 | SQLite | 由 `database.py` 自动创建 |

**MySQL 增量迁移**（已不需要，所有表已整合到 `portabrasil.sql`）：
```bash
# 所有表均在 portabrasil.sql 中，已有数据库直接重新导入即可：
mysql -u root -p portabrasil < ../portabrasil.sql
```

**核心数据表**：`pdf_file`、`pdf_parse_task`、`customs_business`、`customs_business_fee_item`、`users`、`roles`、`user_role`、`customs_process_record`、`customs_process_step`、`customs_activity`、`fx_rate_cache`、`customs_cost_record`、`customs_cost_item`、`ai_audit_run`、`ai_audit_finding`、`ai_finance_review`、`ai_finance_item`

> 注意：`statement_summary` 和 `statement_summary_item` 仅存在于 MySQL 模式中。

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
2. 输入 `admin` / `admin123456`
3. 右上角点击 **ZH / EN / PT** 按钮切换语言

### 上传单据
1. 点击侧边栏 **Upload**
2. 选择一个 PDF 文件
3. 选择 **Upload & Parse** 或 **Upload Only**
4. 若选择 **Upload & Parse**：等待约 10–30 秒完成

### 清关流程跟踪
1. 点击侧边栏 **Process**
2. 浏览清关记录列表（可按提单号、状态筛选）
3. 点击记录进入详情页 → 10 步看板展示每步状态
4. 点击任意步骤的 **Edit** → 设置状态和完成日期 → Save
5. 整体状态自动推导：PROCESSING → INSPECTION → CLEARED

### 成本分析
1. 点击侧边栏 **Cost**
2. 输入：海关费、退税、美元额、汇率、其他费用、商品数量
3. 点击 **Calculate** → 查看净费用、美元折算、总成本、单件成本
4. 点击 **Save Record** 持久化到历史

### AI 审计
1. 进入任意业务记录或成本记录详情页
2. 点击 **AI Audit** 或 **Finance Review**
3. 结果展示：风险/健康等级、评分、问题列表（含严重程度、证据、建议）

### 系统管理（管理员）
1. 点击侧边栏 **Admin**（仅 SUPER_ADMIN 和 ADMIN 角色可见）
2. 管理用户：创建、更新、禁用、重置密码、分配角色

---

## 系统模块

9 大核心模块。详细流程图见 `docs/系统模块流程图.md`：

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

- **JWT Bearer Token**：除公开接口外，所有接口均需认证
- **密码安全**：SHA-256 哈希存储，登录时自动升级旧明文密码
- **CORS**：开发环境全开，生产环境请限制
- **SQL 注入防护**：所有查询使用参数化语句
- **超管保护**：SUPER_ADMIN 账号不能通过 API 修改或禁用
- **自禁用保护**：用户不能禁用自己的账号
- **越权防护**：非超管不能分配 SUPER_ADMIN 角色

---

## 开发指南

### 新增后端路由
1. 在 `app/routes/` 下创建 `my_resource.py`
2. 在 `app/factory.py` 中注册：
   ```python
   from app.routes.my_resource import bp as my_resource_bp
   app.register_blueprint(my_resource_bp, url_prefix='/api/my-resource')
   ```
3. 使用 `@jwt_required` 装饰器保护路由，使用 `api_response()` 返回 JSON

### 新增前端页面
1. 在 `src/views/` 下创建 `MyView.jsx`
2. 在 `src/views/index.js` 中导出
3. 在 `App.jsx` 的 `menuItems` 和 `renderContent()` 中添加

### 运行测试
1. `cd Portabrasil-server && uv run flask --app main run --port 5001 --debug`
2. `cd Portabrasil-web/customs-dashboard && npm run dev`
3. 打开 `http://localhost:5173`

---

*PortaBrasil — 让巴西海关清关更简单。*

---

<!-- ============================================================
     PORTUGUESE SECTION
     ============================================================ -->

## Visão Geral

**PortaBrasil** é uma plataforma web full-stack para gerenciamento de **operações de despachância aduaneira brasileira**. Digitaliza todo o fluxo de liberação aduaneira — desde o upload de documentos PDF brutos (conhecimentos de embarque, faturas, declarações aduaneiras) passando pela extração de dados assistida por IA, análise de custos financeiros, até o ciclo completo de vida de 10 etapas do processo de liberação aduaneira.

Público-alvo: empresas de logística, despachantes aduaneiros e transitários.

---

## Arquitetura

```
┌─────────────────────────────────────────────────────────┐
│              Navegador (React SPA)                      │
│  http://localhost:5173                                  │
└─────────────────────┬───────────────────────────────────┘
                      │ HTTP / REST API (JSON)
┌─────────────────────▼───────────────────────────────────┐
│              Backend Flask                              │
│  http://localhost:5001 /api/*                           │
│  ┌──────────┬───────────┬───────────┬─────────────┐     │
│  │ Autent.  │ Análise   │ Negócio & │ Auditoria & │     │
│  │          │ PDF       │ Custo     │ Rev. Finan. │     │
│  └──────────┴───────────┴───────────┴─────────────┘     │
└─────────────────────┬───────────────────────────────────┘
                      │ SQL
┌─────────────────────▼───────────────────────────────────┐
│         MySQL 8.x  (produção)                           │
│         SQLite      (desenvolvimento, auto-criado)      │
└─────────────────────────────────────────────────────────┘
```

---

## Stack Tecnológico

| Camada | Tecnologia |
|---|---|
| **Frontend** | React 19, Vite 7, Tailwind CSS 3, Lucide React |
| **Backend** | Python 3.11+, Flask 3, Flask-CORS |
| **Autenticação** | JWT (PyJWT), hash de senha SHA-256 |
| **Banco de Dados** | MySQL 8.x (produção) / SQLite (desenvolvimento) |
| **IA - Parsing** | Zhipu AI (ZAI SDK) — análise de documentos PDF |
| **IA - Revisão** | Zhipu AI (ZAI SDK) — auditoria e análise financeira |
| **ORM** | SQL estilo SQLAlchemy (pymysql / sqlite3) |
| **Taxas de Câmbio** | API Open Exchange Rates (fallback: taxas em cache) |

---

## Estrutura do Projeto

```
PortaBrasil/
├── Portabrasil-server/           # Backend Flask
│   ├── main.py                   # Ponto de entrada
│   ├── app/
│   │   ├── factory.py            # Factory da app (CORS, tratamento de erros, blueprints)
│   │   ├── core/
│   │   │   ├── auth.py           # JWT, hash de senha, decorator de autenticação
│   │   │   └── responses.py     # Auxiliares de resposta JSON unificada
│   │   └── routes/
│   │       ├── health.py          # GET /api/health
│   │       ├── auth.py           # Auth: login / registro / esqueci a senha / usuários
│   │       ├── files.py          # Upload de PDF e gatilhos de análise
│   │       ├── documents.py      # Ingestão de texto bruto
│   │       ├── business.py       # CRUD de registros de negócio e consulta de taxas
│   │       ├── tasks.py          # Status de tarefa de análise
│   │       ├── dashboard.py      # Estatísticas da página inicial
│   │       ├── process.py        # Rastreamento de 10 etapas de liberação
│   │       ├── reports.py        # Registros de relatórios
│   │       ├── cost.py           # Análise de custos e taxas de câmbio
│   │       ├── ai_review.py      # Auditoria de IA e revisão financeira
│   │       └── admin.py          # Gerenciamento de usuários
│   ├── database.py               # Conexão BD e esquema SQLite
│   ├── services.py              # Serviços de lógica de negócio
│   ├── pdf_parser.py            # Parser de PDF via Zhipu AI
│   ├── parser_rules.py           # Regras regex para extração de campos
│   ├── sql/
│   ├── sql/                        # Diretório do esquema SQL
│   └── instance/                 # SQLite DB auto-criado aqui
│
├── Portabrasil-web/
│   └── customs-dashboard/        # Frontend React
│       ├── src/
│       │   ├── App.jsx           # Shell principal (sidebar, header, roteamento)
│       │   ├── LoginPage.jsx    # Página de login
│       │   ├── views/
│       │   │   ├── HomeView.jsx           # Visão geral do painel
│       │   │   ├── UploadView.jsx         # Upload de PDF
│       │   │   ├── ProcessTrackingView.jsx # Rastreamento de 10 etapas
│       │   │   ├── CostAnalysisView.jsx   # Cálculo e registros de custo
│       │   │   ├── ReportView.jsx         # Centro de relatórios
│       │   │   └── AdminManagementView.jsx # Gerenciamento de usuários e funções
│       │   ├── components/navigation/
│       │   │   └── SidebarItem.jsx
│       │   └── shared/
│       │       ├── auth/storage.js   # Armazenamento JWT
│       │       ├── config/api.js     # Configuração de URL base da API
│       │       ├── i18n/
│       │       │   ├── translations.js      # Todas as traduções da UI (zh/en/pt)
│       │       │   └── language-context.jsx
│       │       └── utils/
│       │           ├── http.js    # Auxiliar fetch autenticado
│       │           └── format.js  # Formatadores de número/moeda
│       └── package.json
│
├── portabrasil.sql                # Dump completo do esquema MySQL
└── docs/
    ├── README.md                 # English version
    ├── README_zh.md              # Versão em chinês
    └── 系统模块流程图.md          # Diagramas de fluxo dos módulos (Mermaid)
```

---

## Funcionalidades

### 1. Autenticação e Autorização
- Autenticação baseada em JWT (token de acesso, expiração de 120 minutos)
- 5 funções: **Super Admin**, **Admin**, **Despachante**, **Operador Aduaneiro**, **Financeiro**
- Controle de acesso baseado em função (RBAC) em todos os endpoints protegidos
- Hash de senha SHA-256 (com atualização automática de senhaplain legada no login)
- Registro de usuário, recuperação de senha

### 2. Upload e Análise de Documentos PDF
- Upload de arquivos PDF (máx. 25 MB) com deduplicação via hash SHA-256
- Análise orientada por IA via Zhipu AI (tipos de parser: LLM / OCR / RULE)
- Polling assíncrono do status da tarefa de análise
- Upsert por S/Ref — re-envio do mesmo documento atualiza registros existentes
- Endpoint de ingestão de texto bruto para entrada direta de texto

### 3. Extração de Dados de Negócios
Extraídos de PDFs analisados: S/Ref, N/Ref, Nº da Fatura, Nº da NF, dados do cliente (nome, endereço, cidade, estado, CNPJ/CPF), documentos de transporte (MAWB/MBL, HAWB/HBL), datas-chave (registro, chegada, liberação, carregamento), informações de carga (peso, volume, descrição), dados financeiros (frete, FOB, CIF, CIF-BRL, taxas de câmbio) e até 50 itens de taxa por registro.

### 4. Processo de Liberação Aduaneira em 10 Etapas
- Cada Conhecimento de Embarque (BL) mapeia um registro de processo
- 10 etapas sequenciais por processo: PENDENTE / CONCLUÍDO
- Derivação automática do status geral: todas completas → **LIBERADO** | etapa 6+ completa → **EM VISTORIA** | demais → **EM PROCESSO**
- Status da etapa, hora de conclusão e descrição editáveis

### 5. Análise de Custos
- Entrada: taxa aduaneira, reembolso, valor em USD, taxa de câmbio, outras taxas, quantidade
- Calculado: taxa aduaneira líquida, conversão USD→BRL, custo total, custo por unidade
- Busca de taxa USD/BRL em tempo real com cache no banco de dados e fallback
- Salvar registros de cálculo no histórico com detalhamento por produto
- Revisão de saúde financeira por IA com verificações baseadas em regras

### 6. Auditoria de IA e Revisão Financeira
- **Auditoria de Negócios** (`POST /api/ai-review/business/:id/run`): consistência de débito/crédito, consistência de resumo de taxas, completude de campos, detecção de anomalia de reembolso
- **Revisão Financeira** (`POST /api/ai-review/cost-record/:id/review`): validade da quantidade total, razoabilidade da taxa de câmbio, razão reembolso/taxa aduaneira, positividade do custo por unidade
- Resultados: nível de risco/saúde, pontuação, descobertas com severidade, evidências, sugestões

### 7. Painel e Relatórios
- Página inicial: total de registros, distribuição por status, total de impostos, kanban de etapas, feed de atividades recentes
- Centro de relatórios: lista filtrável/pesquisável de todos os registros de liberação

### 8. Internacionalização
- UI disponível em: **Chinês Simplificado (zh)**, **Inglês (en)**, **Português (pt)**
- Trocador de idioma na barra de ferramentas do cabeçalho

---

## Início Rápido

### Pré-requisitos
- **Python** 3.11+, **Node.js** 18+, **npm**
- (Opcional) **MySQL 8.x** — SQLite usado automaticamente se não configurado
- (Opcional) **Zhipu AI API Key** — necessário apenas para análise de PDF e revisão de IA

### Configuração do Backend

```bash
cd PortaBrasil/Portabrasil-server
uv sync

# Opcional: definir variáveis de ambiente
export DATABASE_URL='mysql://root:password@127.0.0.1:3306/portabrasil?charset=utf8mb4'
export ZHIPU_API_KEY='your-zhipu-api-key'
export JWT_SECRET='your-long-random-secret-here'
export UPLOAD_DIR=''
export DASHSCOPE_API_KEY='your-dashscope-api-key'
export FX_API_ID='your-fx-api-id'
export FX_API_KEY='your-fx-api-key'

# MySQL: inicializar banco de dados
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS portabrasil DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
mysql -u root -p portabrasil < ../portabrasil.sql

# Iniciar servidor
uv run flask --app main run --host 0.0.0.0 --port 5001 --debug
```

> Sem `DATABASE_URL`, o servidor usa SQLite automaticamente (`instance/portabrasil.db`).

**Credenciais padrão**: `admin` / `admin123456`

### Configuração do Frontend

```bash
cd PortaBrasil/Portabrasil-web/customs-dashboard
npm install
npm run dev
```

Frontend em `http://localhost:5173`, faz proxy da API para `http://localhost:5001`.

---

## Configuração

### Variáveis de Ambiente (Backend)

| Variável | Padrão | Descrição |
|---|---|---|
| `DATABASE_URL` | SQLite (`instance/portabrasil.db`) | String de conexão MySQL |
| `ZHIPU_API_KEY` | — | Chave API Zhipu AI para análise de PDF |
| `JWT_SECRET` | `change-this-in-production...` | Chave secreta para assinatura JWT |
| `JWT_EXPIRES_MINUTES` | `120` | Expiração do token em minutos |
| `UPLOAD_DIR` | `./uploads` | Diretório de armazenamento dos PDFs |
| `DEFAULT_REGISTER_ROLE` | `FORWARDER` | Função para novos registros |

### Variáveis de Ambiente (Frontend)

| Variável | Padrão | Descrição |
|---|---|---|
| `VITE_API_BASE_URL` | `http://127.0.0.1:5001` | URL base da API do backend |

---

## Banco de Dados

| Ambiente | Engine | Fonte do Esquema |
|---|---|---|
| Produção | MySQL 8.x | `portabrasil.sql` (dump completo) |
| Desenvolvimento | SQLite | Auto-criado por `database.py` |

**Migrações incrementais MySQL** (não são mais necessárias, todas as tabelas estão em `portabrasil.sql`):
```bash
# Todas as tabelas estão em portabrasil.sql. Para banco existente, basta reimportar:
mysql -u root -p portabrasil < ../portabrasil.sql
```

**Tabelas principais**: `pdf_file`, `pdf_parse_task`, `customs_business`, `customs_business_fee_item`, `users`, `roles`, `user_role`, `customs_process_record`, `customs_process_step`, `customs_activity`, `fx_rate_cache`, `customs_cost_record`, `customs_cost_item`, `ai_audit_run`, `ai_audit_finding`, `ai_finance_review`, `ai_finance_item`

> Nota: `statement_summary` e `statement_summary_item` existem apenas no esquema MySQL.

---

## Referência da API

### Públicos (Sem Autenticação)
| Método | Caminho | Descrição |
|---|---|---|
| `GET` | `/api/health` | Verificação de saúde |
| `POST` | `/api/auth/login` | Login (retorna JWT) |
| `POST` | `/api/auth/register` | Registrar novo usuário |
| `POST` | `/api/auth/forgot-password` | Redefinir senha |

### Painel e Processo
| Método | Caminho | Descrição |
|---|---|---|
| `GET` | `/api/dashboard/overview` | Estatísticas da página inicial |
| `GET` | `/api/process/records` | Listar registros de liberação |
| `GET` | `/api/process/records/{id}` | Obter detalhes do registro |
| `PUT` | `/api/process/records/{id}/steps/{no}` | Atualizar status da etapa |
| `GET` | `/api/reports/records` | Registros de relatórios |

### Negócio e Arquivos
| Método | Caminho | Descrição |
|---|---|---|
| `POST` | `/api/files/upload` | Upload de PDF (multipart) |
| `GET` | `/api/files` | Listar arquivos |
| `GET` | `/api/files/{id}` | Obter detalhes do arquivo |
| `POST` | `/api/files/{id}/parse` | Disparar análise |
| `GET` | `/api/tasks/{id}` | Obter status da tarefa |
| `POST` | `/api/documents/from-text` | Ingestão de texto bruto |
| `GET` | `/api/business` | Pesquisar registros de negócio |
| `GET` | `/api/business/{id}` | Obter registro de negócio |
| `GET` | `/api/business/{id}/fees` | Obter itens de taxa |

### Análise de Custos
| Método | Caminho | Descrição |
|---|---|---|
| `GET` | `/api/cost/overview` | Visão geral de custos |
| `GET` | `/api/cost/exchange-rate` | Obter taxa de câmbio |
| `POST` | `/api/cost/calculate` | Calcular custo |
| `POST` | `/api/cost/records` | Salvar registro de custo |
| `GET` | `/api/cost/records` | Listar registros de custo |
| `GET` | `/api/cost/records/{id}` | Obter detalhes do registro de custo |

### Revisão de IA
| Método | Caminho | Descrição |
|---|---|---|
| `POST` | `/api/ai-review/business/{id}/run` | Executar auditoria de negócio |
| `GET` | `/api/ai-review/audit/runs` | Listar execuções de auditoria |
| `GET` | `/api/ai-review/audit/runs/{id}` | Obter detalhes da auditoria |
| `POST` | `/api/ai-review/cost-record/{id}/review` | Executar revisão financeira |
| `GET` | `/api/ai-review/finance/reviews` | Listar revisões financeiras |

### Admin
| Método | Caminho | Descrição |
|---|---|---|
| `GET` | `/api/auth/me` | Obter usuário atual |
| `POST` | `/api/auth/users` | Criar usuário (admin only) |
| `PUT` | `/api/auth/users/{id}` | Atualizar usuário (admin only) |
| `PUT` | `/api/auth/users/{id}/password` | Redefinir senha (admin only) |
| `PUT` | `/api/auth/users/{id}/status` | Ativar/desativar usuário (admin only) |

---

## Guia do Usuário

### Fazer Login
1. Abra `http://localhost:5173`
2. Digite `admin` / `admin123456`
3. Alterne o idioma com o botão **ZH / EN / PT** no canto superior direito

### Upload de Documento
1. Clique em **Upload** na barra lateral
2. Selecione um arquivo PDF
3. Escolha **Upload & Parse** ou **Upload Only**
4. Para **Upload & Parse**: aguarde ~10–30 segundos para conclusão

### Rastreamento do Processo de Liberação
1. Clique em **Process** na barra lateral
2. Navegue pela lista de registros (filtrável por nº BL, status)
3. Clique em um registro → kanban de 10 etapas mostra PENDENTE/CONCLUÍDO
4. Clique em **Edit** em uma etapa → defina status + data de conclusão → Save
5. Status geral deriva automaticamente: EM PROCESSO → EM VISTORIA → LIBERADO

### Análise de Custos
1. Clique em **Cost** na barra lateral
2. Insira: taxa aduaneira, reembolso, valor em USD, taxa de câmbio, outras taxas, quantidade
3. Clique em **Calculate** → veja taxa líquida, conversão BRL, custo total/unitário
4. Clique em **Save Record** para persistir no histórico

### Auditoria de IA
1. Abra detalhes de um registro de negócio ou custo
2. Clique em **AI Audit** ou **Finance Review**
3. Resultados: nível de risco/saúde, pontuação, descobertas com severidade, evidências, sugestões

### Admin
1. Clique em **Admin** (visível apenas para SUPER_ADMIN e ADMIN)
2. Gerencie usuários: criar, atualizar, desativar, redefinir senhas, atribuir funções

---

## Módulos do Sistema

9 módulos funcionais. Veja `docs/系统模块流程图.md` para diagramas de fluxo Mermaid:

| # | Módulo | Descrição |
|---|---|---|
| 1 | Autenticação | Autenticação JWT, RBAC com 5 funções |
| 2 | Upload de Documentos | Upload de PDF, deduplicação SHA-256 |
| 3 | Análise de Documentos | Análise de PDF via Zhipu AI, extração de campos |
| 4 | Auditoria e Revisão | Auditoria de negócios por IA + revisão financeira |
| 5 | Contabilidade de Custos | Cálculo de custos com conversão de câmbio |
| 6 | Rastreamento de Processo | Ciclo de vida de 10 etapas de liberação |
| 7 | Gerenciamento de Tarefas | Rastreamento assíncrono de tarefas de análise |
| 8 | Painel Estatístico | Kanban da página inicial, feed de atividades |
| 9 | Administração do Sistema | CRUD de usuários, atribuição de funções |

---

## Segurança

- **Tokens JWT Bearer** em todos os endpoints protegidos
- **Hash de senha**: SHA-256 com atualização automática de senhas legadas
- **CORS**: aberto em desenvolvimento; restringir em produção
- **Injeção SQL**: todas as consultas usam instruções parametrizadas
- **Proteção SUPER_ADMIN**: contas super admin não podem ser modificadas/desativadas via API
- **Prevenção de auto-desativação**: usuários não podem desativar sua própria conta
- **Prevenção de escalação de função**: não-super-admins não podem atribuir a função SUPER_ADMIN

---

## Desenvolvimento

### Adicionar Nova Rota
1. Crie `app/routes/my_resource.py`
2. Registre em `app/factory.py`:
   ```python
   from app.routes.my_resource import bp as my_resource_bp
   app.register_blueprint(my_resource_bp, url_prefix='/api/my-resource')
   ```
3. Use `@jwt_required` para rotas protegidas e `api_response()` para respostas JSON

### Adicionar Nova View
1. Crie `src/views/MyView.jsx`
2. Exporte de `src/views/index.js`
3. Adicione em `menuItems` e no `switch renderContent()` em `App.jsx`

### Executar Testes
1. `cd Portabrasil-server && uv run flask --app main run --port 5001 --debug`
2. `cd Portabrasil-web/customs-dashboard && npm run dev`
3. Abra `http://localhost:5173`

---

*PortaBrasil — Simplificando as Operações Aduaneiras Brasileiras.*
