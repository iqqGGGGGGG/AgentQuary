## Context

当前项目使用纯文本拼接方案，需要升级为完整的向量 RAG 系统。项目已使用 LangChain 框架和小米 MiMo 2.5 Pro（通过 OpenAI 兼容 API）。需要集成 Chroma 向量数据库和阿里云百炼 Embedding 模型。

## Goals / Non-Goals

**Goals:**
- 文档上传 → 解析 → 分块 → 向量化 → Chroma 存储
- Agentic RAG：智能决策本地检索 vs 联网搜索
- 用户知识库隔离
- 恢复 PDF/Word 支持

**Non-Goals:**
- 不实现多模态 RAG（图片、音频）
- 不实现文档在线编辑
- 不实现跨用户文档共享

## Decisions

### Decision 1: 向量数据库 — Chroma

**选择**: Chroma（本地轻量级向量数据库）

**理由**:
- pip install chromadb，零配置
- 内置持久化（存储到本地目录）
- LangChain 原生集成（langchain-chroma）
- 适合单机部署的 MVP

**备选方案**:
- FAISS：更快但无内置持久化
- Milvus：生产级但部署复杂

### Decision 2: Embedding 模型 — 阿里云百炼

**选择**: 阿里云百炼 `text-embedding-v4`（API 调用）

**理由**:
- **中文支持优秀**（原生中文训练，比 sentence-transformers 好得多）
- 无需下载模型文件（API 调用，启动即用）
- 与项目已有的 API 调用模式一致（MiMo 也是 API 调用）
- 阿里云百炼有免费额度，MVP 阶段够用
- 质量高（text-embedding-v4 是最新版本）

**备选方案**:
- sentence-transformers（本地）：免费但中文支持一般，需下载80MB模型
- OpenAI Embedding：质量好但贵，国内访问不稳定

**调用方式**: 通过 OpenAI 兼容 API 调用（百炼支持 OpenAI 格式）

### Decision 3: 文档分块策略

**选择**: `RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)`

**理由**:
- 500 字/块适合生成题目（每块包含1-2个知识点）
- 50 字重叠保持上下文连贯
- LangChain 内置分块器

### Decision 4: Agentic RAG 架构

**选择**: LangChain Agent + 自定义工具

**工具集**:
1. `vector_search` — 从 Chroma 检索相关文档片段
2. `web_search` — Tavily 联网搜索

**Agent 决策逻辑**:
- 短文本输入 → 先 vector_search，再 web_search，合并
- URL 输入 → tavily_extract
- 长文本输入 → 跳过检索

**理由**:
- 复用现有 LangChain 基础设施
- Agent 可以智能决策，无需硬编码规则
- 工具可扩展（后续可加更多数据源）

### Decision 5: 用户隔离

**选择**: Chroma collection 按 `user_{user_id}` 命名

**理由**:
- 每个用户独立的 collection，天然隔离
- 删除用户文档时删除对应 collection 中的向量

### Decision 6: 恢复 PDF/Word 支持

**选择**: 重新添加 PyPDF2 和 python-docx 依赖

**理由**:
- 向量存储方案下，解析后内容不再直接传给 LLM
- 而是分块后存入 Chroma，检索时只返回相关片段
- 避免了之前"整篇传入导致乱码/截断"的问题

## Risks / Trade-offs

**[百炼 API 依赖]** → Embedding 依赖外部 API。缓解：API 调用稳定，失败时可降级为不使用向量检索。

**[百炼免费额度]** → 需关注使用量。缓解：MVP 阶段用量小，可监控。

**[Chroma 性能]** → 大量文档时检索可能变慢。缓解：MVP 阶段文档量小，后续可优化索引。

**[存储空间]** → 向量数据会占用磁盘。缓解：限制每用户文档数量和总大小。
