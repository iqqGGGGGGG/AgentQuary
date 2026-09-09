## 1. 修改 ResearchPlan schema

- [x] 1.1 修改 `server/chains/research_chain.py` 的 `ResearchPlan` 类：新增 `ambiguous: bool = False` 和 `domain_options: list[str] = Field(default_factory=list)` 字段

## 2. 修改 planner prompt

- [x] 2.1 修改 `server/chains/research_chain.py` 的 `RESEARCH_SYSTEM_PROMPT`：增加"上下文提取"规则——从用户输入中提取领域描述融入搜索 query；增加"上下文优先"规则——用户描述了主题含义时以用户描述为准；增加"跨领域检测"规则——搜索结果跨多个不同领域且用户无上下文时，设置 `ambiguous=true` 并列出 `domain_options`

## 3. 修改 GenerateResponse schema

- [x] 3.1 修改 `server/models/schemas.py` 的 `GenerateResponse` 类：新增 `needs_clarification: bool = False` 和 `domain_options: list[str] = Field(default_factory=list)` 字段

## 4. 修改 generate 路由

- [x] 4.1 修改 `server/routers/generate.py`：在调用 `research_content` 后，如果返回的 plan 标记为 ambiguous，直接返回澄清响应（`needs_clarification=true, domain_options=[...]`），不调用 chain_generate

## 5. 修改 generate prompt

- [x] 5.1 修改 `server/chains/generate_chain.py` 的 `system_prompt`：增加规则"如果参考内容与用户输入的主题领域明显不一致，应以用户输入的领域为准生成题目"

## 6. 修改前端

- [x] 6.1 修改 `src/types/quiz.ts`：`GenerateResponse` 新增 `needs_clarification` 和 `domain_options` 字段
- [x] 6.2 修改 `src/pages/index/index.tsx`：generate 返回 `needs_clarification=true` 时，展示领域选项列表，用户选择后将选择结果拼入 content 重新调用 generate

## 7. 验证

- [x] 7.1 运行 `pytest server/tests/ -v` 确认所有测试通过
