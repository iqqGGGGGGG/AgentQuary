## Why

联网搜索功能上线后发现：当用户用中文提问英文主题（如 "Harness Engineering 是什么？"）时，Tavily 搜索返回英文内容，LLM 直接基于英文内容生成了全英文的题目、选项和讲解。这对中文用户非常不友好。

根本原因：题目生成 chain 的 prompt 没有明确要求输出语言，LLM 会跟随参考内容的语言。需要在 prompt 中强制要求使用中文输出。

## What Changes

- 修改 **题目生成 prompt**：在 system prompt 中增加中文输出要求，无论参考内容是什么语言，题目、选项、讲解必须使用中文
- 修改 **研究阶段 planner prompt**：引导 AI 在用户输入包含中文时，优先搜索中文来源或在 query 中加入中文关键词

## Capabilities

### New Capabilities
- `question-language`: 题目语言一致性——确保生成的题目、选项、讲解始终使用中文

### Modified Capabilities
（无）

## Impact

- **后端代码**：`server/chains/generate_chain.py`（prompt 修改）、`server/chains/research_chain.py`（planner prompt 修改）
- **API 行为**：无变更
- **依赖**：无新增
