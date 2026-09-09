## Why

真实搜索测试发现两个问题：

1. **搜索结果太少导致 AI 误判**：当前默认搜索 3-5 条结果，对于 "Harness Engineering" 这种冷门词，搜索结果可能来自错误领域（如建筑工程而非线束工程），AI 无法通过少数结果判断正确含义。需要增加搜索条数和搜索轮数，让 AI 通过多数结果判断正确领域。

2. **前端请求超时不足**：当前所有请求统一 150 秒超时。联网搜索 + AI 规划 + 题目生成的总耗时可能超过 150 秒，导致前端超时失败。generate 和 report 接口需要更长的超时时间。

## What Changes

- 修改 **搜索参数**：max_results 默认从 3 提升到 10，始终使用 `search_depth="advanced"`
- 修改 **planner prompt**：引导 AI 对冷门主题进行多轮搜索（不同关键词），通过多数结果判断正确领域
- 修改 **前端超时**：generate 和 report 接口单独设置 300 秒超时，其他接口保持 150 秒

## Capabilities

### New Capabilities
- `enhance-search-quality`: 提升搜索质量和前端超时——增加搜索条数、多轮搜索、长超时

### Modified Capabilities
（无）

## Impact

- **后端代码**：`server/chains/research_chain.py`（max_results、planner prompt）
- **前端代码**：`src/services/api.ts`（超时配置）
- **依赖**：无新增
