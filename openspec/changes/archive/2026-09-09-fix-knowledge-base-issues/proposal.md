## Why

知识库功能存在三个问题：
1. Word 文档解析后出现乱码（可能是 .doc 格式或编码问题）
2. Taro 警告 textarea 数据量过大（文档内容存入 state 导致性能问题）
3. 无法一键清空知识库，操作不便

## What Changes

- 修改 **文档解析**：清理 Word 文档提取的文本（去除控制字符、规范化空白）
- 修改 **前端**：限制传入 state 的数据量，避免性能警告
- 新增 **一键清空**：知识库页面增加"清空全部"按钮
- 新增 **后端 API**：DELETE /api/documents 清空所有文档

## Capabilities

### New Capabilities
- `fix-knowledge-base-issues`: 修复知识库乱码、性能警告、一键清空

### Modified Capabilities
（无）

## Impact

- **后端代码**：`server/services/document_parser.py`（文本清理）、`server/routers/documents.py`（清空 API）
- **前端代码**：`src/pages/knowledge/index.tsx`（清空按钮 + 数据优化）
