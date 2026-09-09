## 1. 依赖与配置

- [x] 1.1 在 `server/requirements.txt` 中添加 `langchain-tavily>=0.1.0`，验证 `pip install -r requirements.txt` 安装成功
- [x] 1.2 在 `server/config.py` 的 `Settings` 类中添加：`search_enabled: bool = True`、`tavily_api_key: str = ""`、`search_timeout: int = 15`，验证配置加载无报错
- [x] 1.3 在 `server/.env.example` 中添加：`SEARCH_ENABLED=true`、`TAVILY_API_KEY=your-tavily-api-key`、`SEARCH_TIMEOUT=15`

## 2. Research Agent 实现

- [x] 2.1 在 `server/chains/` 下新建 `research_chain.py`，定义 `ResearchPlan` 和 `ToolAction` Pydantic schema（计划结构：input_type、reasoning、actions 列表，每个 action 包含 tool 名称和对应参数），验证 schema 校验逻辑正确
- [x] 2.2 在 `research_chain.py` 中实现 research planner prompt（system prompt 描述工具能力、参数调整策略、输出格式；user prompt 接收用户输入），使用 `ChatPromptTemplate` + `JsonOutputParser(pydantic_object=ResearchPlan)` 组成 planner chain，验证 chain 可调用
- [x] 2.3 在 `research_chain.py` 中实现 `async def research_content(content: str, search_enabled: bool) -> tuple[str, bool]` 函数：调用 planner chain 获取计划 → 根据计划中的 actions 调用 `TavilySearch` 或 `TavilyExtract` → 拼接获取的内容与用户输入 → 返回 (enriched_content, search_used)；任何异常时静默降级返回 (original_content, False)

## 3. 集成到题目生成流程

- [x] 3.1 修改 `server/models/schemas.py` 的 `GenerateResponse` 类：添加 `search_used: bool = False` 字段，验证现有 API 响应兼容
- [x] 3.2 修改 `server/routers/generate.py` 的 `generate_quiz` 函数：在 `normalize_content` 之后、`chain_generate` 之前调用 `research_content`；将返回的 `search_used` 传入 `GenerateResponse`，验证返回值正确
- [x] 3.3 验证：运行 `pytest server/tests/test_generate.py -v`，确认现有测试全部通过

## 4. 测试

- [x] 4.1 编写 `server/tests/test_research.py`：mock TavilySearch 和 TavilyExtract 返回，测试 research_content 的正常流程、降级流程（API 异常/超时/空结果）、以及 search_used 标记的正确性
- [ ] 4.2 启动后端，Swagger UI 手动测试：输入 "Harness Engineering"，验证 `search_used: true` 且题目基于搜索结果
- [ ] 4.3 手动测试：输入一个 URL，验证 AI 选择 TavilyExtract 而非 TavilySearch
- [ ] 4.4 手动测试：设置 `SEARCH_ENABLED=false`，验证 `search_used: false`，题目仍正常生成
- [ ] 4.5 手动测试：输入超过 200 字的长文本，验证不触发研究阶段（`search_used: false`）
