## Why

当前研究流程依赖一个 Planner LLM 调用来"决定要不要搜索、搜什么"。这导致：
1. **搜索根本没执行**：MiMo 可能没遵循复杂指令，返回 `actions: []` 或 `tool: "none"`
2. **额外延迟**：每次搜索前多一次 LLM 调用（5-15秒）
3. **不可靠**：Planner 的输出质量取决于 LLM 对复杂 prompt 的理解能力

**根本解决方案：去掉 Planner，直接搜索。** 短文本输入时，直接用用户输入作为搜索词调用 TavilySearch。URL 输入时直接调用 TavilyExtract。不需要 LLM 先"决定"。

## What Changes

- **重写 `research_content` 函数**：去掉 Planner LLM 调用，改为直接判断输入类型并调用对应工具
- **短文本（≤2000字）**：直接调用 TavilySearch，query = 用户输入
- **URL 输入**：直接调用 TavilyExtract
- **长文本（>2000字）**：跳过搜索
- **保留澄清逻辑**：如果搜索结果跨多个领域，在生成阶段由 LLM 判断是否需要澄清
- **删除 Planner 相关代码**：`planner_chain`、`RESEARCH_SYSTEM_PROMPT`、`ResearchPlan`、`ToolAction` 等

## Capabilities

### New Capabilities
- `simplify-research-flow`: 简化研究流程——去掉 Planner LLM，直接调用 Tavily 工具

### Modified Capabilities
（无）

## Impact

- **后端代码**：`server/chains/research_chain.py`（重写）
- **前端代码**：无变更
- **依赖**：无新增
