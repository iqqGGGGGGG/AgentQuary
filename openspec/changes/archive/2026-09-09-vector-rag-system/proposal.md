## Why

当前项目的 RAG 能力是纯文本拼接方案，存在以下问题：
1. **联网搜索**：返回 snippet（200-500字/条），内容不完整
2. **知识库文档**：整篇传入，超过12000字被截断，无语义检索
3. **无向量检索**：无法根据用户问题找到最相关的文档片段
4. **无 Agentic RAG**：无法智能决策何时搜索本地知识库、何时联网搜索

需要实现完整的 RAG 系统：
- 用户上传 PDF/Word/MD 文档 → 解析 → 分块 → 向量化 → 存入向量数据库
- 用户提问时，Agent 智能决策：检索本地知识库 / 联网搜索 / 两者结合
- 基于检索到的上下文生成高质量题目

## What Changes

- 新增 **向量数据库**：使用 Chroma（本地轻量级），存储文档向量
- 新增 **文档处理管道**：上传 → 解析 → 分块 → Embedding → 存入 Chroma
- 新增 **Embedding 模型**：使用阿里云百炼 `text-embedding-v4`（中文优秀、API 调用、无需下载模型）
- 新增 **Agentic RAG Agent**：LangChain Agent 决策检索策略
- 新增 **向量检索服务**：从 Chroma 检索相关文档片段
- 修改 **研究阶段**：集成向量检索 + 联网搜索
- 恢复 **PDF/Word 支持**：配合向量存储，解析后内容不再直接传给 LLM
- 新增 **用户知识库隔离**：每个用户独立的向量空间

## Capabilities

### New Capabilities
- `vector-rag-system`: 向量 RAG + Agentic RAG——文档上传解析分块向量化、Chroma 存储、智能检索决策

### Modified Capabilities
- `knowledge-base`: 升级为向量存储方案
- `web-search-rag`: 集成到 Agentic RAG 决策流程

## Impact

- **后端新增**：`server/services/vector_store.py`（向量存储）、`server/services/embedding.py`（Embedding 服务）、`server/chains/rag_agent.py`（Agentic RAG Agent）、`server/services/document_parser.py`（恢复 PDF/Word 解析）
- **后端修改**：`server/chains/research_chain.py`（集成向量检索）、`server/routers/documents.py`（上传流程增加向量化）、`server/config.py`（新增配置项）、`server/requirements.txt`（新增依赖）
- **新增依赖**：`chromadb`、`langchain-chroma`、`PyPDF2`、`python-docx`
- **存储**：`server/chroma_data/` 目录存储向量数据库文件
