# PortaBrasil Flask 后端

这个后端负责 PDF 上传、智谱 PDF 解析、解析文本规则化、写入 `portabrasil.sql` 中的业务表，以及基础查询接口。

## 0. 工程化结构

当前后端已按模块拆分，入口与路由职责分离：

```text
Portabrasil-server/
├── main.py                  # 启动入口（仅 create_app + run）
├── app/
│   ├── factory.py           # Flask app factory（配置、CORS、错误处理、蓝图注册）
│   ├── core/
│   │   ├── auth.py          # JWT、密码哈希、鉴权装饰器、用户查询
│   │   └── responses.py     # 统一 JSON 响应与序列化
│   └── routes/
│       ├── health.py        # 健康检查
│       ├── auth.py          # 登录/注册/忘记密码/用户管理
│       ├── files.py         # 文件上传、解析、查询
│       ├── documents.py     # 文本入库
│       ├── business.py      # 业务与费用查询
│       ├── tasks.py         # 任务查询
│       ├── dashboard.py     # 首页仪表盘数据
│       ├── process.py       # 清关流程跟踪
│       ├── reports.py       # 报表列表
│       └── cost.py          # 成本分析（汇率/计算/记录）
├── database.py              # 数据库连接与初始化（MySQL/SQLite）
└── services.py              # PDF 解析与业务入库服务逻辑
```

## 1. 安装依赖

```bash
cd Portabrasil-server
uv sync
```

如果不用 `uv`，也可以用 Python 3.11 创建虚拟环境后安装 `pyproject.toml` 里的依赖。

## 2. 初始化数据库

MySQL 版本使用根目录的 SQL：

```bash
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS portabrasil DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
mysql -u root -p portabrasil < ../portabrasil.sql
```

> 服务只通过 `os.getenv` 读取系统环境变量，不会自动读取 `.env` 文件。开发阶段推荐直接在终端导出变量：

```bash
export DATABASE_URL='mysql://root:password@127.0.0.1:3306/portabrasil?charset=utf8mb4'
export ZHIPU_API_KEY='你的智谱APIKey'
export UPLOAD_DIR='./uploads'
export JWT_SECRET='请换成你自己的长随机字符串'
export JWT_EXPIRES_MINUTES='120'
```

`.env.example` 只作为字段模板，不要把真实密钥写进仓库。如果你仍然想在本地保留 `.env` 给 IDE 使用，根目录 `.gitignore` 已经忽略 `.env`、`*.env` 和 `Portabrasil-server/.env`。

如果没有配置 `DATABASE_URL`，服务会自动使用本地 SQLite：`instance/portabrasil.db`，方便先跑通接口。

## 3. 启动服务

```bash
cd Portabrasil-server
uv run flask --app main run --host 0.0.0.0 --port 5001 --debug
```

或：

```bash
uv run python main.py
```

## 4. 核心接口

### 健康检查

```http
GET /api/health
```

### 登录获取 JWT

```bash
curl -X POST http://127.0.0.1:5001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123456"}'
```

默认管理员账号（来自 `portabrasil.sql`）：

- 用户名：`admin`
- 密码：`admin123456`

登录成功后会返回 `access_token`，后续请求要带：

```http
Authorization: Bearer <access_token>
```

除 `GET /api/health` 和 `POST /api/auth/login` 之外，其他 API 默认都需要登录。

### 注册账号（公开）

```bash
curl -X POST http://127.0.0.1:5001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"newuser","password":"123456","email":"newuser@example.com"}'
```

注册成功会直接返回 `access_token`。默认分配角色由环境变量 `DEFAULT_REGISTER_ROLE` 控制，默认是 `FORWARDER`。

### 忘记密码（重置）

```bash
curl -X POST http://127.0.0.1:5001/api/auth/forgot-password \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","email":"admin@portabrasil.local","new_password":"newpass123"}'
```

### 上传 PDF 并立即解析入库

```bash
curl -X POST http://127.0.0.1:5001/api/files/upload \
  -F "file=@p2s.pdf" \
  -F "parse=true"
```

处理流程：

1. 保存文件到 `uploads/YYYYMMDD/`
2. 写入 `pdf_file`
3. 创建 `pdf_parse_task`
4. 调用智谱 PDF parser 得到文本
5. 规则解析字段和费用明细
6. 写入 `customs_business` 和 `customs_business_fee_item`
7. 更新文件和任务状态

### 上传但暂不解析

```bash
curl -X POST http://127.0.0.1:5001/api/files/upload \
  -F "file=@p2s.pdf" \
  -F "parse=false"
```

之后再触发：

```http
POST /api/files/{file_id}/parse
```

### 已有解析文本直接入库

适合把智谱返回的 `content` 或你已有的解析结果直接写入数据库：

```bash
curl -X POST http://127.0.0.1:5001/api/documents/from-text \
  -H "Content-Type: application/json" \
  -d '{"raw_text":"LOGIMEX COMERCIO EXTERIOR LTDA ..."}'
```

### 查询

```http
GET /api/files
GET /api/files/{file_id}
GET /api/business?q=20250528000158
GET /api/business/{business_id}
GET /api/business/{business_id}/fees
GET /api/tasks/{task_id}
```

### 仪表盘与流程（对齐前端页面）

```http
GET /api/dashboard/overview
GET /api/process/records
GET /api/process/records/{record_id}
PUT /api/process/records/{record_id}/steps/{step_no}
GET /api/reports/records
GET /api/cost/overview
GET /api/cost/exchange-rate?base=USD&quote=BRL
POST /api/cost/calculate
POST /api/cost/records
GET /api/cost/records
GET /api/cost/records/{record_id}
```

### 用户与角色管理

```http
GET /api/auth/me
POST /api/auth/register
POST /api/auth/forgot-password
POST /api/auth/users   # 仅 SUPER_ADMIN / ADMIN 可调用
```

`POST /api/auth/users` 请求体示例：

```json
{
  "username": "zhangsan",
  "password": "123456",
  "real_name": "张三",
  "email": "zhangsan@example.com",
  "role_codes": ["CUSTOMS"]
}
```

## 5. 解析规则说明

解析器会先清理 OCR 常见异常字符，例如 `а`、`EndereE`、`MunicM`，再提取：

- 主业务字段：`S/Ref`、`No. Processo`、客户信息、税号、提单号、发票号、DI、到港/清关/装载日期、船名、重量、件数、CIF/FOB/FRETE、汇率、总计、余额。
- 费用明细：按 `日期 + 代码 + 名称 + 金额` 切分。
- 贷借方向：`ADIANTAMENTO` 或费用代码 `200` 进入 `credit_amount`，其他费用进入 `debit_amount`，负数会按原值保存。

同一个 `S/Ref` 再次入库会更新 `customs_business`，并重建对应费用明细。

## 6. 新增数据表（流程模块）

为了支持你当前前端的首页看板、流程跟踪和报表列表，本次后端新增了 3 张表（MySQL 与 SQLite 均已支持）：

- `customs_process_record`：流程主记录（提单号、货物、港口、整体状态）
- `customs_process_step`：10 步流程节点状态（PENDING/COMPLETE、完成时间、描述）
- `customs_activity`：首页“最新动态”数据

## 7. 新增数据表（成本模块）

为了支持成本分析页面的后端化能力（汇率、计算结果落库、历史记录），新增了 3 张表：

- `fx_rate_cache`：汇率缓存（当前主要存 USD/BRL）
- `customs_cost_record`：成本计算主记录（费用输入、总量、总成本、单件成本）
- `customs_cost_item`：每条成本记录下的商品明细（数量、分摊成本、单件成本）
