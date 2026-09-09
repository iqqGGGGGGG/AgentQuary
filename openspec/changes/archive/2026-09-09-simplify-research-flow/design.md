## Context

当前 `research_content` 函数通过 Planner LLM 决定搜索策略，但 MiMo 可能不遵循复杂指令，导致搜索不执行。

## Goals / Non-Goals

**Goals:**
- 去掉 Planner LLM 调用，直接调用 Tavily 工具
- 阈值从 200 字提升到 2000 字
- 保持搜索失败降级

**Non-Goals:**
- 不保留 Planner（删除相关代码）
- 不保留跨领域检测（简化）

## Decisions

### Decision 1: 直接调用，去掉 Planner

**选择**: 短文本直接调用 TavilySearch，URL 直接调用 TavilyExtract，不经过 LLM 决策

**理由**: Planner 是不可靠的中间层，去掉后流程更简单、更可靠、更快

### Decision 2: 阈值 2000 字

**选择**: 输入 ≤2000 字时触发搜索，>2000 字跳过

**理由**: 200 字太小，用户可能输入一段中等长度的文本仍然需要搜索补充

## Risks / Trade-offs

**[失去智能搜索词优化]** → 去掉 Planner 后，搜索词就是用户原始输入，不会被优化。缓解：用户输入本身就是最直接的搜索意图。
