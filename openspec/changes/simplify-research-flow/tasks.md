## 1. 重写 research_chain.py

- [x] 1.1 重写 `server/chains/research_chain.py`：删除 `ToolAction`、`ResearchPlan`、`planner_chain`、`RESEARCH_SYSTEM_PROMPT` 等 Planner 相关代码；重写 `research_content` 函数——短文本（≤2000字）直接调用 TavilySearch(query=用户输入, max_results=10, search_depth="advanced")，URL 直接调用 TavilyExtract，长文本跳过；保留 `ResearchResult` 返回类型和降级逻辑

## 2. 验证

- [x] 2.1 运行 `pytest server/tests/test_research.py tests/test_generate.py -v` 确认测试通过
