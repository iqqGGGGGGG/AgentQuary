## 1. 依赖与配置

- [x] 1.1 修改 `server/requirements.txt`：添加 `chromadb>=0.4.0`、`langchain-chroma>=0.1.0`、`PyPDF2>=3.0.0`、`python-docx>=1.0.0`
- [x] 1.2 修改 `server/config.py`：添加 `chroma_persist_dir`、`embedding_base_url`、`embedding_model`、`embedding_api_key`
- [x] 1.3 在 `.gitignore` 中添加 `server/chroma_data/`

## 2. Embedding 服务

- [x] 2.1 新建 `server/services/embedding.py`

## 3. 向量存储服务

- [x] 3.1 新建 `server/services/vector_store.py`

## 4. 恢复 PDF/Word 解析

- [x] 4.1 修改 `server/services/document_parser.py`
- [x] 4.2 修改 `server/routers/documents.py`

## 5. Agentic RAG Agent

- [x] 5.1 新建 `server/chains/rag_agent.py`

## 6. 集成到生成流程

- [x] 6.1 修改 `server/chains/research_chain.py`
- [x] 6.2 修改 `server/routers/generate.py`
- [x] 6.3 修改 `server/routers/documents.py`

## 7. 前端更新

- [x] 7.1 修改 `src/pages/knowledge/index.tsx`

## 8. 验证

- [x] 8.1 运行测试确认通过
- [x] 8.2 前端编译无报错
