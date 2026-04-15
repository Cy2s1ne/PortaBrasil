# PortaBrasil Flask 后端

这个后端负责 PDF 上传、智谱 PDF 解析、解析文本规则化、写入 `portabrasil.sql` 中的业务表，以及基础查询接口。

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

服务只通过 `os.getenv` 读取系统环境变量，不会自动读取 `.env` 文件。开发阶段推荐直接在终端导出变量：

```bash
export DATABASE_URL='mysql://root:password@127.0.0.1:3306/portabrasil?charset=utf8mb4'
export ZHIPU_API_KEY='你的智谱APIKey'
export UPLOAD_DIR='./uploads'
```

`.env.example` 只作为字段模板，不要把真实密钥写进仓库。如果你仍然想在本地保留 `.env` 给 IDE 使用，根目录 `.gitignore` 已经忽略 `.env`、`*.env` 和 `Portabrasil-server/.env`。

如果没有配置 `DATABASE_URL`，服务会自动使用本地 SQLite：`instance/portabrasil.db`，方便先跑通接口。

## 3. 启动服务

```bash
cd Portabrasil-server
uv run flask --app main run --host 0.0.0.0 --port 5000 --debug
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

### 上传 PDF 并立即解析入库

```bash
curl -X POST http://127.0.0.1:5000/api/files/upload \
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
curl -X POST http://127.0.0.1:5000/api/files/upload \
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
curl -X POST http://127.0.0.1:5000/api/documents/from-text \
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

## 5. 解析规则说明

解析器会先清理 OCR 常见异常字符，例如 `а`、`EndereE`、`MunicM`，再提取：

- 主业务字段：`S/Ref`、`No. Processo`、客户信息、税号、提单号、发票号、DI、到港/清关/装载日期、船名、重量、件数、CIF/FOB/FRETE、汇率、总计、余额。
- 费用明细：按 `日期 + 代码 + 名称 + 金额` 切分。
- 贷借方向：`ADIANTAMENTO` 或费用代码 `200` 进入 `credit_amount`，其他费用进入 `debit_amount`，负数会按原值保存。

同一个 `S/Ref` 再次入库会更新 `customs_business`，并重建对应费用明细。
