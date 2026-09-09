## Why

用户输入 "Harness Engineering（驾驭工程）是2026年兴起的AI工程化核心范式..." 时，搜索返回的全是"线束工程"(wire harness) 的结果，AI 被多数错误结果误导，生成了完全无关的题目。

更难的情况：用户只输入 "Harness Engineering"，没有任何上下文，搜索结果跨多个领域（线束工程 vs AI工程化），AI 无法判断用户想学什么。

需要两种消歧策略：
1. **有上下文时**：利用用户输入中的描述构造精确搜索词
2. **无上下文时**：检测到搜索结果跨多个领域，返回澄清选项让用户选择

## What Changes

- 修改 **planner prompt**：上下文提取 + 上下文优先原则
- 修改 **planner prompt**：搜索结果跨多个领域时，输出澄清选项而非盲目生成
- 修改 **ResearchPlan schema**：新增 `ambiguous` 和 `domain_options` 字段
- 修改 **GenerateResponse schema**：新增 `needs_clarification` 和 `domain_options` 字段
- 修改 **generate 路由**：检测到澄清需求时，直接返回澄清响应
- 修改 **generate chain prompt**：参考内容与用户描述冲突时，以用户输入为准
- 修改 **前端**：处理澄清响应，展示领域选项

## Capabilities

### New Capabilities
- `improve-domain-disambiguation`: 领域消歧——有上下文时利用上下文搜索；无上下文时检测跨领域结果并返回澄清选项

### Modified Capabilities
（无）

## Impact

- **后端代码**：`server/chains/research_chain.py`、`server/chains/generate_chain.py`、`server/models/schemas.py`、`server/routers/generate.py`
- **前端代码**：`src/services/api.ts`、`src/pages/index/index.tsx`（展示澄清选项）、`src/types/quiz.ts`（新增类型）
- **API 行为**：generate 接口可能返回澄清响应（新行为）
- **依赖**：无新增
