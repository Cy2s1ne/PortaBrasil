# PDF转JSON工具使用说明

## 功能概述

这是一个用于将PDF文件内容读取并转换为JSON格式的Python工具，能够保留PDF的原有格式和结构信息。

## 安装依赖

```bash
pip3 install -r requirements.txt
```

## 使用方法

### 1. 命令行直接运行

```bash
python3 pdf_to_json.py
```

这将处理默认的 `P1.pdf` 文件，并生成两个JSON文件：
- `P1_full.json` - 包含完整的格式信息（字符、线条、矩形等）
- `P1_simple.json` - 仅包含文本和表格内容

### 2. 在代码中使用

```python
from pdf_to_json import PDFToJSONConverter

# 创建转换器
converter = PDFToJSONConverter("your_file.pdf")

# 方式1: 完整转换（包含详细格式信息）
full_data = converter.convert_to_json(
    output_path="output_full.json",
    include_detailed=True  # 包含字符、线条、矩形等详细信息
)

# 方式2: 简化转换（仅文本和表格）
simple_data = converter.convert_simple(
    output_path="output_simple.json"
)

# 访问数据
print(f"总页数: {simple_data['total_pages']}")
print(f"第一页文本: {simple_data['pages'][0]['text']}")
```

## JSON输出格式

### 简化版格式 (simple)

```json
{
  "filename": "P1.pdf",
  "total_pages": 1,
  "pages": [
    {
      "page_number": 1,
      "text": "页面文本内容...",
      "tables": [
        [
          ["单元格1", "单元格2"],
          ["单元格3", "单元格4"]
        ]
      ]
    }
  ]
}
```

### 完整版格式 (full)

除了简化版的内容外，还包括：

- **chars**: 字符级别的详细信息
  - `text`: 字符内容
  - `x0, y0, x1, y1`: 字符位置坐标
  - `fontname`: 字体名称
  - `size`: 字体大小

- **lines**: 线条信息
  - `x0, y0, x1, y1`: 线条起止坐标
  - `width`: 线条宽度

- **rects**: 矩形信息
  - `x0, y0, x1, y1`: 矩形坐标
  - `width, height`: 矩形尺寸

- **images**: 图片信息
  - `x0, y0, x1, y1`: 图片位置
  - `width, height`: 图片尺寸
  - `name`: 图片名称

## 自定义处理

你可以根据需要修改 `main()` 函数来处理不同的PDF文件：

```python
def main():
    # 指定要处理的PDF文件
    pdf_file = "your_document.pdf"
    
    converter = PDFToJSONConverter(pdf_file)
    
    # 根据需要选择转换方式
    data = converter.convert_simple(output_path="output.json")
    
    # 进行后续处理...
```

## 注意事项

1. **编码问题**: 某些PDF可能包含特殊编码的字符，显示为 `(cid:0)` 等形式，这是正常现象
2. **表格识别**: pdfplumber会自动识别表格结构，但复杂表格可能需要手动调整
3. **大文件处理**: 对于大型PDF文件，完整模式可能生成较大的JSON文件
4. **字体信息**: 详细模式保留了字体和位置信息，便于后续的格式化处理

## 后续步骤

生成的JSON数据可以用于：
- 文本分析和信息提取
- 数据结构化和数据库导入
- 报表生成和格式转换
- 基于坐标的精确定位和处理

## 常见问题

**Q: 如何只提取特定页面？**
```python
with pdfplumber.open("file.pdf") as pdf:
    page = pdf.pages[0]  # 第一页
    text = page.extract_text()
```

**Q: 如何提取特定区域的文本？**
```python
# 使用crop方法裁剪特定区域
bbox = (x0, y0, x1, y1)  # 定义矩形区域
cropped = page.crop(bbox)
text = cropped.extract_text()
```

**Q: 表格提取不准确怎么办？**
```python
# 可以调整表格提取参数
tables = page.extract_tables(table_settings={
    "vertical_strategy": "lines",
    "horizontal_strategy": "lines"
})
```
