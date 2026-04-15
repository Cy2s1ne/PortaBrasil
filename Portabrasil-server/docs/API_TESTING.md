# PortaBrasil 接口测试说明

## Apifox 导入

在 Apifox 中选择：

```text
导入数据 -> OpenAPI/Swagger -> 选择文件
```

导入文件：

```text
Portabrasil-server/docs/apifox-openapi.json
```

文档内默认服务地址是：

```text
http://127.0.0.1:5001
```

## 推荐测试顺序

1. 健康检查

```http
GET /api/health
```

期望返回：

```json
{
  "status": "ok",
  "database": "mysql"
}
```

如果没有配置 `DATABASE_URL`，`database` 会返回 `sqlite`。

2. 文本直接入库

```http
POST /api/documents/from-text
```

Body 选择 JSON：

```json
{
  "raw_text": "LOGIMEX COMERCIO EXTERIOR LTDA ... S/Ref.: 20250528000158 ... TOTAL => 228.389,13 200.897,37 ...",
  "source_page_no": 1
}
```

这个接口不需要真实 PDF，也不需要调用智谱接口，适合先验证规则解析和数据库写入。

3. 查询业务列表

```http
GET /api/business?q=20250528000158
```

4. 查询业务详情

把上一步返回的 `id` 填到路径：

```http
GET /api/business/{business_id}
```

5. 查询费用明细

```http
GET /api/business/{business_id}/fees
```

6. 上传 PDF

```http
POST /api/files/upload
```

Body 选择 `multipart/form-data`：

```text
file: 选择 PDF 文件
parse: true
```

如果 `parse=true`，需要先在启动服务的终端配置：

```bash
export ZHIPU_API_KEY='你的智谱APIKey'
```

如果只想测试上传文件入库，不想调用智谱解析：

```text
parse: false
```

7. 解析已上传文件

把上传接口返回的 `file.id` 填到路径：

```http
POST /api/files/{file_id}/parse
```

8. 查询文件和任务

```http
GET /api/files
GET /api/files/{file_id}
GET /api/tasks/{task_id}
```

## 常见错误

- `ZHIPU_API_KEY 未配置`：上传 PDF 且 `parse=true` 时没有配置智谱 API Key。
- `当前只支持 PDF 文件`：上传了非 `.pdf` 文件。
- `file_id 不存在`：`/api/documents/from-text` 传了不存在的 `file_id`。
- `无法从文本中识别 S/Ref、Invoice 或单据号`：文本里没有能作为业务唯一编号的字段。
