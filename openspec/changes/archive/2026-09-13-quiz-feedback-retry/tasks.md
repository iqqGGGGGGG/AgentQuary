## 1. 后端改动

- [x] 1.1 修改 `server/models/schemas.py`：`GenerateRequest` 新增 `feedback: str = ""` 和 `previous_questions: list[str] = Field(default_factory=list)` 字段
- [x] 1.2 修改 `server/chains/generate_chain.py`：prompt 增加反馈处理规则，user message 增加 feedback 和 previous_questions 参数
- [x] 1.3 修改 `server/routers/generate.py`：将 feedback 和 previous_questions 传递给 chain

## 2. 前端改动

- [x] 2.1 修改 `src/types/quiz.ts`：GenerateRequest 类型新增 feedback 和 previous_questions 字段
- [x] 2.2 修改 `src/services/api.ts`：generate 函数新增 feedback 和 previousQuestions 参数
- [x] 2.3 修改 `src/pages/report/report.tsx`：点击"再来一关"前弹出反馈面板，用户选择预设反馈或输入自定义反馈后调用 generate

## 3. 验证

- [x] 3.1 运行测试确认通过
- [x] 3.2 前端编译无报错
