## Why

当用户输入一个 AI 模型训练数据未覆盖的新知识主题（如 "Harness Engineering"）时，模型会给出错误或无关的题目。原因是 LLM 训练数据有截止日期，无法覆盖最新知识。需要引入联网搜索能力，在生成题目之前先获取相关网页内容作为上下文，确保题目基于真实信息生成。

用户输入可能是一个关键词（如 "Harness Engineering"），也可能是一个网址（如某篇技术博客链接）。两种场景需要不同的处理方式：关键词需要搜索，网址需要提取页面内容。系统应让 AI 自动判断输入类型并选择合适的工具。

## What Changes

- 新增 **Research Agent**：在题目生成前增加"内容研究"阶段，AI 分析用户输入后自主决定调用搜索（TavilySearch）还是提取网页（TavilyExtract），并动态设置参数
- 新增 **两个 Tavily 工具**：`TavilySearch`（关键词搜索）和 `TavilyExtract`（URL 内容提取），均通过 `langchain-tavily` 包集成
- 修改 **题目生成流程**：从"直接生成"变为"研究 → 拼接 → 生成"三步，研究阶段获取的内容作为 LLM 生成题目的参考上下文
- 新增 **动态参数策略**：根据内容复杂度自动调整搜索深度、结果数量、是否获取完整内容等参数
- 新增 **配置项**：Tavily API Key、搜索开关、超时时间等
- 新增 **依赖**：`langchain-tavily`（Tavily 搜索+提取工具，LangChain 原生集成）
- 搜索失败时 **优雅降级**：不阻断现有流程，回退到纯 LLM 生成

## Capabilities

### New Capabilities
- `web-search-rag`: 联网搜索增强题目生成能力——AI 自主判断输入类型，调用 TavilySearch 或 TavilyExtract 获取内容，动态调整参数，作为 LLM 上下文生成题目，含降级策略

### Modified Capabilities
（无现有 spec 需要修改）

## Impact

- **后端代码**：新增 `server/chains/research_chain.py`（Research Agent）、修改 `server/routers/generate.py`（流程集成）、修改 `server/config.py`（配置项）、修改 `server/requirements.txt`（依赖）
- **API 行为**：`POST /api/generate` 响应新增 `search_used` 字段，其他不变
- **新增依赖**：`langchain-tavily`（Tavily 搜索+提取，需 API Key）
- **配置**：`.env` 需新增 `TAVILY_API_KEY` 等配置项
