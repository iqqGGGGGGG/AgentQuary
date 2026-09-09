## 1. 后端修改

- [x] 1.1 修改 `server/services/document_parser.py`：移除 `parse_pdf` 和 `parse_docx` 函数，只保留 `parse_text`
- [x] 1.2 修改 `server/routers/documents.py`：`ALLOWED_EXTENSIONS` 改为 `{".txt", ".md"}`
- [x] 1.3 修改 `server/requirements.txt`：移除 `PyPDF2` 和 `python-docx`

## 2. 前端修改

- [x] 2.1 修改 `src/pages/knowledge/index.tsx`：`extension` 改为 `['txt', 'md']`，提示文案改为"支持 TXT、MD 格式"

## 3. 验证

- [x] 3.1 运行测试确认通过
- [x] 3.2 前端编译无报错
