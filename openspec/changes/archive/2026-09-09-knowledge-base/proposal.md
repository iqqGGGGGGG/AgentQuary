## Why

当前产品只能通过输入文字、粘贴链接或联网搜索来获取学习内容。用户无法上传自己的文档（如课件、笔记、教材）来生成题目。需要实现文档上传和知识库管理功能，让用户可以：

1. 上传 PDF、Word、TXT、MD 等格式的文档
2. 系统自动解析文档内容并存储
3. 基于上传的文档生成问答题目
4. 管理已上传的文档（查看、删除、重新生成题目）

## What Changes

- 新增 **文档上传 API**：支持 PDF、Word、TXT、MD 文件上传
- 新增 **文档解析服务**：自动提取文档中的文本内容
- 新增 **知识库数据表**：存储文档元数据和解析后的文本
- 新增 **知识库管理 API**：查看、删除已上传的文档
- 新增 **知识库页面**：前端文档上传和管理界面
- 修改 **题目生成流程**：支持从知识库选择文档作为题目来源

## Capabilities

### New Capabilities
- `knowledge-base`: 文档上传与知识库管理——用户上传文档、系统解析存储、基于文档生成题目

### Modified Capabilities
（无）

## Impact

- **后端代码**：新增 `server/routers/documents.py`、`server/services/document_parser.py`、修改 `server/models/orm.py`、`server/models/schemas.py`、`server/main.py`、`server/requirements.txt`
- **前端代码**：新增 `src/pages/knowledge/` 页面、修改 `src/services/api.ts`、`src/types/quiz.ts`、`src/app.config.ts`
- **依赖**：新增 `PyPDF2`（PDF解析）、`python-docx`（Word解析）
- **配置**：`server/uploads/` 目录用于存储上传文件
