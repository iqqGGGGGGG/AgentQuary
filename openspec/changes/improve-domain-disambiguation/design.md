## Context

当前 planner 只输出搜索计划。需要增加"检测到跨领域结果时输出澄清选项"的能力。

## Goals / Non-Goals

**Goals:**
- 有上下文时利用上下文消歧
- 无上下文时检测跨领域结果，返回澄清选项
- 前端展示澄清选项，用户选择后重新生成

**Non-Goals:**
- 不实现自动领域分类器
- 不限制搜索结果来源

## Decisions

### Decision 1: ResearchPlan 新增澄清字段

**选择**: `ResearchPlan` 增加 `ambiguous: bool` 和 `domain_options: list[str]` 字段

**理由**: 让 planner 可以在检测到跨领域结果时输出澄清选项，而不是强制选择一个领域

### Decision 2: GenerateResponse 新增澄清字段

**选择**: `GenerateResponse` 增加 `needs_clarification: bool` 和 `domain_options: list[str]` 字段

**理由**: 前端需要知道是否需要展示澄清选项

### Decision 3: 两阶段流程

**选择**:
1. 第一次请求：planner 搜索后检测到跨领域 → 返回澄清响应
2. 用户选择领域后，前端将用户选择作为额外上下文拼入 content，重新调用 generate
3. 第二次请求：planner 有了用户选择的上下文，搜索结果不再跨领域 → 正常生成

**理由**: 不需要新增 API 端点，复用现有 generate 接口

### Decision 4: generate prompt 增加领域对齐规则

**选择**: 当参考内容与用户输入的领域描述冲突时，以用户输入为准

**理由**: 作为兜底，即使搜索返回了错误内容，生成阶段也能正确处理

## Risks / Trade-offs

**[误判跨领域]** → 可能将单一领域的不同子主题误判为跨领域。缓解：planner 应区分"不同领域"和"同一领域的不同方面"。

**[用户体验]** → 用户可能不想被问澄清问题。缓解：只在搜索结果明确跨多个不同领域时才触发澄清，同领域不同子主题不触发。
