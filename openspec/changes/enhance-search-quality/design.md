## Context

当前搜索默认 3 条结果，planner prompt 建议简单主题 3 条、复杂主题 5 条。前端所有请求统一 150 秒超时。

## Goals / Non-Goals

**Goals:**
- 增加搜索结果数量到 10 条
- 引导 AI 多轮搜索冷门主题
- generate/report 接口 300 秒超时

**Non-Goals:**
- 不修改 Tavily API 限制（最大 10 条）
- 不修改后端 LLM 超时（已有 120 秒）

## Decisions

### Decision 1: max_results 默认 10

**选择**: ToolAction.max_results 默认从 3 改为 10

**理由**: Tavily 最大支持 10 条，越多结果越能帮助 AI 判断正确领域

### Decision 2: 始终使用 advanced 搜索

**选择**: search_depth 默认改为 "advanced"，移除 "basic" 选项

**理由**: advanced 搜索返回更详细的内容，对题目生成质量更有帮助

### Decision 3: 多轮搜索策略

**选择**: 在 planner prompt 中引导 AI 对冷门/专业主题生成多组搜索词

**理由**: 单一搜索词可能返回错误领域的结果，多组关键词交叉验证更可靠

### Decision 4: 前端分接口超时

**选择**: request 函数接受可选 timeout 参数，generate/report 传 300000，其他默认 150000

**理由**: 不同接口耗时差异大，分接口设置更合理

## Risks / Trade-offs

**[Tavily 额度消耗加快]** → 10 条结果 + 多轮搜索会消耗更多额度。缓解：MVP 阶段用量可控，后续可调整。
