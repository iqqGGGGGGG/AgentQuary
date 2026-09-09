## Context

当前项目已有文件上传目录 `server/uploads/`（已在 .gitignore 中），但没有文档上传和解析功能。需要新增文档上传 API、解析服务、数据库表和前端页面。

## Goals / Non-Goals

**Goals:**
- 支持 PDF、Word、TXT、MD 文件上传
- 自动解析文档文本内容
- 知识库管理（列表、删除、预览）
- 基于文档生成题目

**Non-Goals:**
- 不支持图片 OCR 识别
- 不支持文档在线编辑
- 不支持文档共享
- 不实现向量搜索（纯文本方案）

## Decisions

### Decision 1: 文件存储方案

**选择**: 本地文件系统存储，路径 `server/uploads/{user_id}/{timestamp}_{sanitized_filename}`

**理由**: MVP 阶段本地存储足够，后续可迁移到 OSS

### Decision 2: 文档解析库

**选择**: 
- PDF: `PyPDF2`（轻量、纯 Python）
- Word: `python-docx`（官方库）
- TXT/MD: 直接读取

**理由**: 这些库成熟稳定，满足基本需求

### Decision 3: 数据库设计

**选择**: 新增 `documents` 表，存储文档元数据和解析后的文本

**字段**: id, user_id, filename, original_filename, file_type, file_size, text_content, text_length, created_at

### Decision 4: 前端页面

**选择**: 新增知识库页面，作为底部 Tab 的第三个选项

**理由**: 方便用户管理文档和快速生成题目

## Risks / Trade-offs

**[大文件解析耗时]** → 大 PDF 解析可能需要数秒。缓解：限制文件大小 10MB，异步解析。

**[PDF 解析质量]** → 某些 PDF（扫描件、加密）无法提取文本。缓解：解析失败时给出明确提示。

**[存储空间]** → 本地存储会占用服务器空间。缓解：限制单用户文档数量（后续可扩展）。
