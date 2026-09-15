## Context

需要在报告页增加反馈面板，并将反馈传递给后端用于优化下一轮题目。

## Decisions

### Decision 1: 反馈面板 UI

**选择**: 使用 Taro.showActionSheet + 自定义弹窗组合

**理由**: 预设选项用 ActionSheet 快速选择，自定义反馈用弹窗输入

### Decision 2: 反馈传递方式

**选择**: GenerateRequest 新增 `feedback` 和 `previous_questions` 字段

**理由**: 后端需要知道上一轮题目才能结合反馈优化

### Decision 3: Prompt 集成

**选择**: 在 prompt 中增加反馈处理规则，将 feedback 和 previous_questions 作为额外上下文

**理由**: LLM 理解自然语言反馈，可以直接调整出题策略
