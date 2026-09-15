## Why

当前题目生成质量不稳定，用户无法对生成的题目进行反馈。需要在"再来一关"前增加反馈功能，让用户可以评价上一轮题目，模型结合反馈优化下一轮题目。

## What Changes

- 修改 **报告页**：点击"再来一关"前弹出反馈面板，用户可选择预设反馈或输入自定义反馈
- 修改 **GenerateRequest**：新增 `feedback` 和 `previous_questions` 字段
- 修改 **题目生成 prompt**：增加反馈处理规则，结合用户反馈优化题目

## Capabilities

### New Capabilities
- `quiz-feedback-retry`: 答题反馈机制——用户评价上一轮题目，模型结合反馈优化下一轮

### Modified Capabilities
（无）

## Impact

- **后端代码**：`server/models/schemas.py`（GenerateRequest 新增字段）、`server/chains/generate_chain.py`（prompt 增加反馈规则）、`server/routers/generate.py`（传递反馈）
- **前端代码**：`src/pages/report/report.tsx`（反馈面板）、`src/services/api.ts`（generate 参数）、`src/types/quiz.ts`（GenerateRequest 类型）
