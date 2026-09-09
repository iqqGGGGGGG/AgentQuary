## Why

Word 和 PDF 文件解析不稳定（编码问题、复杂格式不支持），导致用户上传后看到乱码或解析失败。MVP 阶段应限制为可靠的文件格式。

## What Changes

- 限制上传文件格式为 **TXT 和 MD**（纯文本，解析100%可靠）
- 移除 PDF 和 Word 解析依赖（PyPDF2、python-docx）
- 更新前端提示文案

## Capabilities

### New Capabilities
- `restrict-file-types`: 限制文件格式为 TXT/MD

### Modified Capabilities
- `knowledge-base`: 文件格式限制变更

## Impact

- **后端代码**：`server/services/document_parser.py`（移除 PDF/Word 解析）、`server/routers/documents.py`（更新允许的扩展名）、`server/requirements.txt`（移除依赖）
- **前端代码**：`src/pages/knowledge/index.tsx`（更新 extension 和提示文案）
