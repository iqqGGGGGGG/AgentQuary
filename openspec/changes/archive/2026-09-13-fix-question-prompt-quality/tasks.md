## 1. 重写题目生成 prompt

- [x] 1.1 修改 `server/chains/generate_chain.py`：重写 system prompt，增加题目设计原则（好的题目 vs 坏的题目）、图片-题目强关联规则、不同主题类型的出题策略、具体示例

## 2. 默认题目数量改为5

- [x] 2.1 修改 `server/models/schemas.py`：`GenerateRequest.question_count` 默认值从10改为5
- [x] 2.2 修改 `src/services/api.ts`：`generate` 函数 count 参数默认值从10改为5
- [x] 2.3 修改 `src/pages/index/index.tsx`：传递给 generate 的 count 从10改为5

## 3. 验证

- [x] 3.1 运行测试确认通过
- [x] 3.2 前端编译无报错
