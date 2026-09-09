## Purpose

实现完整的向量 RAG + Agentic RAG 系统，支持用户上传文档构建离线知识库，结合联网搜索，智能决策检索策略。

## Requirements

### Requirement: 文档上传与向量化
系统 SHALL 支持用户上传 PDF/Word/MD/TXT 文档，自动解析、分块、向量化并存入向量数据库。

#### Scenario: 上传文档
- **WHEN** 用户上传一个 PDF 文件
- **THEN** 系统解析文本 → 按 500 字分块（重叠 50 字）→ 生成 embedding → 存入 Chroma

#### Scenario: 用户知识库隔离
- **WHEN** 用户 A 上传文档
- **THEN** 用户 B 无法检索到用户 A 的文档（按 user_id 隔离）

#### Scenario: 删除文档
- **WHEN** 用户删除一个文档
- **THEN** 系统同时删除 Chroma 中对应的向量数据

### Requirement: 向量检索
系统 SHALL 支持根据用户问题检索最相关的文档片段。

#### Scenario: 语义检索
- **WHEN** 用户输入 "什么是 Harness Engineering"
- **THEN** 系统从该用户的向量库中检索最相关的 5 个文档片段

#### Scenario: 知识库为空
- **WHEN** 用户知识库没有文档
- **THEN** 跳过向量检索，直接走联网搜索

### Requirement: Agentic RAG 决策
系统 SHALL 使用 AI Agent 智能决策检索策略。

#### Scenario: 短主题查询
- **WHEN** 用户输入 "太阳系基础知识"
- **THEN** Agent 决策：先检索本地知识库，再联网搜索，合并结果

#### Scenario: 知识库有相关内容
- **WHEN** 用户知识库包含相关文档
- **THEN** Agent 优先使用本地知识库内容，联网搜索作为补充

#### Scenario: 知识库无相关内容
- **WHEN** 用户知识库无相关内容
- **THEN** Agent 主要依赖联网搜索

### Requirement: 联网搜索集成
系统 SHALL 将现有 Tavily 联网搜索集成到 Agentic RAG 流程中。

#### Scenario: 联网搜索
- **WHEN** Agent 决策需要联网搜索
- **THEN** 调用 TavilySearch 获取最新信息

#### Scenario: 混合检索
- **WHEN** Agent 决策同时需要本地和联网
- **THEN** 合并向量检索结果和联网搜索结果

### Requirement: 恢复 PDF/Word 支持
系统 SHALL 恢复 PDF 和 Word 文档解析能力。

#### Scenario: 上传 PDF
- **WHEN** 用户上传 PDF 文件
- **THEN** 系统使用 PyPDF2 解析文本

#### Scenario: 上传 Word
- **WHEN** 用户上传 Word 文件
- **THEN** 系统使用 python-docx 解析文本

### Requirement: Embedding 模型
系统 SHALL 使用阿里云百炼 Embedding API 生成向量。

#### Scenario: API Embedding
- **WHEN** 系统需要生成文本向量
- **THEN** 调用阿里云百炼 `text-embedding-v4` API，不依赖本地模型
