# PortaBrasil — Brazilian Customs Clearance Management System

> A full-stack web platform for managing Brazilian customs clearance operations, including PDF document parsing, 10-step clearance process tracking, cost analysis, and AI-powered audit & financial review.

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Features](#features)
- [Quick Start](#quick-start)
  - [Prerequisites](#prerequisites)
  - [Backend Setup](#backend-setup)
  - [Frontend Setup](#frontend-setup)
- [Configuration](#configuration)
- [Database](#database)
- [API Reference](#api-reference)
- [User Guide](#user-guide)
- [System Modules](#system-modules)
- [Security](#security)
- [Development](#development)

---

## Overview

PortaBrasil is a web-based **Brazilian customs clearance management system** designed for logistics companies, customs brokers, and freight forwarders. It digitizes the end-to-end clearance workflow — from uploading raw PDF documents (bills of lading, invoices, customs declarations) through AI-assisted data extraction, financial cost analysis, and the full 10-step clearance process lifecycle.

The system supports **three languages** out of the box: Simplified Chinese, English, and Portuguese.

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
│  ┌──────────┬───────────┬───────────┬─────────────┐    │
│  │ Auth     │ PDF Parse │ Business  │ AI Audit &  │    │
│  │ Module   │ Module    │ & Cost    │ Finance Rev │    │
│  └──────────┴───────────┴───────────┴─────────────┘    │
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
│   │       ├── health.py         # GET /api/health
│   │       ├── auth.py           # Auth: login / register / forgot-password / users
│   │       ├── files.py          # PDF upload & parse triggers
│   │       ├── documents.py      # Raw text ingestion
│   │       ├── business.py        # Business record CRUD & fee query
│   │       ├── tasks.py           # Parse task status
│   │       ├── dashboard.py       # Homepage statistics
│   │       ├── process.py         # 10-step clearance tracking
│   │       ├── reports.py         # Report records
│   │       ├── cost.py            # Cost analysis & exchange rates
│   │       ├── ai_review.py       # AI audit & finance review
│   │       └── admin.py           # User management
│   ├── database.py               # DB connection & SQLite schema
│   ├── services.py               # Business logic services
│   ├── pdf_parser.py             # Zhipu AI PDF parser
│   ├── parser_rules.py           # Regex rules for field extraction
│   ├── sql/
│   │   └── migrations/           # Incremental MySQL migrations
│   └── instance/                 # SQLite DB auto-created here
│
├── Portabrasil-web/
│   └── customs-dashboard/        # React Frontend
│       ├── src/
│       │   ├── App.jsx           # Main app shell (sidebar, header, routing)
│       │   ├── LoginPage.jsx     # Login page
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
│       │       ├── auth/storage.js   # JWT storage (localStorage/sessionStorage)
│       │       ├── config/api.js     # API base URL config
│       │       ├── i18n/
│       │       │   ├── translations.js   # All UI translations (zh/en/pt)
│       │       │   └── language-context.jsx
│       │       ├── utils/
│       │       │   ├── http.js    # Authenticated fetch helper
│       │       │   └── format.js  # Number/currency formatters
│       │
│       └── package.json
│
├── portabrasil.sql                # MySQL full schema dump
└── docs/
    ├── README_zh.md              # Chinese README
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
- Upload PDF files (max 25 MB)
- SHA-256 hash deduplication
- AI-powered parsing via Zhipu AI (supports LLM / OCR / RULE parser types)
- Async task polling for parse status
- Upsert by S/Ref — re-uploading the same document updates existing records
- Raw text ingestion endpoint for direct text input

### 3. Business Data Extraction
Extracts from parsed PDFs:
- **Header fields**: S/Ref, N/Ref, Invoice No., NF No., process numbers
- **Parties**: Customer name, address, city, state, tax ID (CNPJ/CPF), issuer
- **Shipping**: MAWB/MBL, HAWB/HBL, vessel/flight name
- **Dates**: Registration, arrival, customs clearance, loading
- **Cargo**: Weight, volume count, description
- **Financials**: Freight (currency + amount), FOB, CIF, CIF-BRL, exchange rates
- **Fee items**: Date + code + name + debit/credit amounts (50 fee items per record)

### 4. 10-Step Customs Clearance Process
- Each Bill of Lading (BL) maps to one process record
- 10 sequential steps tracked per process: PENDING / COMPLETE
- Auto-derive overall status:
  - All 10 complete → **CLEARED** (green)
  - Step 6+ complete → **INSPECTION** (yellow)
  - Otherwise → **PROCESSING** (blue)
- Edit step status, completion time, and description

### 5. Cost Analysis
- Input: customs fee, refund, USD amount, exchange rate, other fees, quantity
- Calculated: net customs fee, USD-to-BRL conversion, total cost, per-unit cost
- Real-time exchange rate fetching (USD/BRL), with database cache and fallback
- Save calculation records to history with per-item product breakdown
- AI financial health review with rule-based checks

### 6. AI Audit & Financial Review
- **Business Audit** (`/api/ai-review/business/:id/run`):
  - Debit/credit balance consistency
  - Fee item summary consistency
  - Field completeness (invoice no., DI number)
  - Refund amount anomaly detection
- **Financial Review** (`/api/ai-review/cost-record/:id/review`):
  - Total quantity validity
  - Exchange rate reasonability (0 < rate ≤ 20)
  - Refund vs. customs fee ratio
  - Per-unit cost positivity
- Results stored in DB: risk level, score, findings, suggestions, evidence

### 7. Dashboard & Reports
- Homepage: total records, status breakdown, tax totals, step completion kanban, recent activity feed
- Report view: filterable/searchable list of all clearance records

### 8. Internationalization
- UI available in: **Chinese (zh)**, **English (en)**, **Portuguese (pt)**
- Language switcher in the header toolbar
- All labels, messages, and UI strings translated

---

## Quick Start

### Prerequisites

- **Python** 3.11+
- **Node.js** 18+ and **npm**
- (Optional) **MySQL 8.x** — if not provided, SQLite is used automatically
- (Optional) **Zhipu AI API Key** — required only for PDF parsing and AI review features

### Backend Setup

```bash
# 1. Navigate to the server directory
cd PortaBrasil/Portabrasil-server

# 2. Install dependencies
uv sync
# or with pip: pip install -e .

# 3. (Optional) Set environment variables
export DATABASE_URL='mysql://root:password@127.0.0.1:3306/portabrasil?charset=utf8mb4'
export ZHIPU_API_KEY='your-zhipu-api-key'
export JWT_SECRET='your-long-random-secret-here'
export JWT_EXPIRES_MINUTES='120'

# 4. Initialize MySQL database (if using MySQL)
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS portabrasil DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
mysql -u root -p portabrasil < ../portabrasil.sql

# 5. Start the server
uv run flask --app main run --host 0.0.0.0 --port 5001 --debug
```

> **Note**: If `DATABASE_URL` is not set, the server automatically uses SQLite (`instance/portabrasil.db`), which is perfect for local development.

**Default admin credentials** (seeded from `portabrasil.sql`):
- Username: `admin`
- Password: `admin123456`

### Frontend Setup

```bash
# 1. Navigate to the frontend directory
cd PortaBrasil/Portabrasil-web/customs-dashboard

# 2. Install dependencies
npm install

# 3. Start the dev server
npm run dev
```

The frontend runs at `http://localhost:5173` and proxies API requests to `http://localhost:5001`.

---

## Configuration

### Environment Variables (Backend)

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | SQLite (`instance/portabrasil.db`) | MySQL connection string |
| `ZHIPU_API_KEY` | — | Zhipu AI API key for PDF parsing |
| `JWT_SECRET` | `change-this-in-production...` | Secret key for signing JWTs |
| `JWT_EXPIRES_MINUTES` | `120` | JWT access token expiry |
| `UPLOAD_DIR` | `./uploads` | Directory for uploaded PDFs |
| `DEFAULT_REGISTER_ROLE` | `FORWARDER` | Role assigned to new registrations |

### Environment Variables (Frontend)

| Variable | Default | Description |
|---|---|---|
| `VITE_API_BASE_URL` | `http://127.0.0.1:5001` | Backend API base URL |

---

## Database

### Supported Engines

| Environment | Engine | Schema Source |
|---|---|---|
| Production | MySQL 8.x | `portabrasil.sql` (full schema dump) |
| Development | SQLite | Auto-created by `database.py` |

### Schema Migration (MySQL)

If you already have a database and want to add new tables without dropping data:

```bash
# Cost module + AI review tables
mysql -u root -p portabrasil < Portabrasil-server/sql/migrations/20260416_add_cost_module_tables.sql
mysql -u root -p portabrasil < Portabrasil-server/sql/migrations/20260416_add_ai_review_tables.sql
```

### Core Tables

| Table | Purpose |
|---|---|
| `pdf_file` | Uploaded PDF files |
| `pdf_parse_task` | Parse task status & raw results |
| `customs_business` | Core business record (one per S/Ref) |
| `customs_business_fee_item` | Fee line items per business record |
| `users` | User accounts |
| `roles` | 5 predefined roles |
| `user_role` | User-role many-to-many mapping |
| `customs_process_record` | Clearance process per Bill of Lading |
| `customs_process_step` | 10-step status per process |
| `customs_activity` | Dashboard activity feed |
| `fx_rate_cache` | Exchange rate cache |
| `customs_cost_record` | Cost analysis master record |
| `customs_cost_item` | Cost line items per record |
| `ai_audit_run` / `ai_audit_finding` | AI business audit runs & findings |
| `ai_finance_review` / `ai_finance_item` | AI financial review runs & findings |

> Note: `statement_summary` and `statement_summary_item` exist only in the MySQL schema (`portabrasil.sql`), not in the SQLite development schema.

---

## API Reference

### Public Endpoints (No Auth)

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
| `GET` | `/api/files` | List uploaded files |
| `GET` | `/api/files/{id}` | Get file detail |
| `POST` | `/api/files/{id}/parse` | Trigger parse |
| `GET` | `/api/tasks/{id}` | Get parse task status |
| `POST` | `/api/documents/from-text` | Ingest raw text |
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
2. Enter credentials (default: `admin` / `admin123456`)
3. The system redirects to the homepage dashboard
4. Switch language using the **ZH / EN / PT** button in the top-right toolbar

### Uploading a Document

1. Click **资料上传** (Upload) in the sidebar
2. Select a PDF file
3. Choose **上传并立即解析** (Upload & Parse) or **仅上传** (Upload Only)
4. For **Upload & Parse**: wait for the task to complete (~10–30 seconds)
5. Check task status via the task list or on the **资料上传** page

### Tracking a Clearance Process

1. Click **流程跟踪** (Process) in the sidebar
2. Browse the list of clearance records (filterable by BL number, goods description, status)
3. Click any record to open the detail view
4. The 10-step kanban shows: ⬜ PENDING / ✅ COMPLETE per step
5. Click **编辑** (Edit) on a step card, set status and completion date
6. Save — the overall status auto-derives (PROCESSING → INSPECTION → CLEARED)

### Cost Analysis

1. Click **成本分析** (Cost) in the sidebar
2. Enter: customs fee, refund, USD amount, exchange rate, other fees, quantity
3. Click **计算** (Calculate) — see net fee, BRL conversion, total cost, per-unit cost
4. Click **保存记录** (Save Record) to persist to history
5. Click any historical record to see the per-product cost breakdown

### Running an AI Audit

1. Navigate to a business record or cost record detail
2. Click the **AI 审计** (AI Audit) or **财务复核** (Finance Review) button
3. The system runs the audit/review and displays findings
4. Results include: risk/health level, score, individual findings with severity, evidence, and suggestions

### Admin: Managing Users

1. Click **系统管理** (Admin) — visible only to SUPER_ADMIN and ADMIN roles
2. View, create, update, or disable user accounts
3. Assign or change roles per user
4. Reset passwords

---

## System Modules

The system is composed of 9 functional modules. See `docs/系统模块流程图.md` for detailed Mermaid flow diagrams:

| # | Module | Description |
|---|---|---|
| 1 | Login Authentication | JWT auth, 5-role RBAC |
| 2 | Document Upload | PDF upload, hash deduplication |
| 3 | Document Parsing | Zhipu AI PDF parsing, field extraction |
| 4 | Audit & Review | AI business audit + financial review |
| 5 | Cost Accounting | Cost calculation with FX conversion |
| 6 | Process Tracking | 10-step clearance lifecycle |
| 7 | Task Management | Async parse task tracking |
| 8 | Statistics Dashboard | Homepage kanban, activity feed |
| 9 | System Administration | User CRUD, role assignment |

---

## Security

- **JWT Bearer tokens** on all protected endpoints (except `/api/health`, `/api/auth/login`, `/api/auth/register`, `/api/auth/forgot-password`)
- **Password hashing**: SHA-256 (with automatic upgrade of legacy plaintext passwords on login)
- **CORS**: Enabled for all origins in development; restrict in production
- **SQL injection**: All queries use parameterized statements
- **SUPER_ADMIN protection**: Super admin accounts cannot be modified or disabled via the API
- **Self-disable protection**: Users cannot disable their own account
- **Role escalation prevention**: Non-super-admins cannot assign the SUPER_ADMIN role

---

## Development

### Adding a New Route

1. Create a new file in `Portabrasil-server/app/routes/`, e.g. `my_resource.py`
2. Register the blueprint in `app/factory.py`:
   ```python
   from app.routes.my_resource import bp as my_resource_bp
   # ...
   app.register_blueprint(my_resource_bp, url_prefix='/api/my-resource')
   ```
3. Use the `@jwt_required` decorator for protected routes
4. Use `api_response()` from `app/core/responses.py` for all JSON responses

### Adding a Frontend View

1. Create a new `.jsx` file in `src/views/`
2. Export it from `src/views/index.js`
3. Add it to the `menuItems` array and `renderContent()` switch in `App.jsx`

### Running Tests

User acceptance testing (manual):
1. Start the backend: `cd Portabrasil-server && uv run flask --app main run --port 5001 --debug`
2. Start the frontend: `cd Portabrasil-web/customs-dashboard && npm run dev`
3. Open `http://localhost:5173` and follow the [User Guide](#user-guide)

---

*PortaBrasil — Simplifying Brazilian Customs Operations.*
