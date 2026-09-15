## Why

当前存在四个问题：
1. **图片与题目关联性不强**：图片 prompt 太通用，生成的图片和题目内容不匹配
2. **不是所有题目都需要图片**：抽象概念、定义判断等题目配图没有意义
3. **主题理解不准确**：如"小学六年级英语学习"应生成六年级难度的单词题，而非泛泛的英语知识
4. **图片太小看不清细节**：320px 高度的图片无法展示细节，且不应出需要仔细看图的题目

## What Changes

- 修改 **题目生成 prompt**：增强用户意图理解，支持年级/难度/场景等限定词
- 修改 **图片生成流程**：用 LLM 为每道题判断是否需要图片，并生成精准的图片 prompt
- 修改 **答题页**：图片展示尺寸增大，支持点击放大
- 修改 **Question schema**：新增 `needs_image` 字段标记哪些题需要图片

## Capabilities

### New Capabilities
- `improve-question-and-image-quality`: 提升题目质量和图片相关性

### Modified Capabilities
（无）

## Impact

- **后端代码**：`server/chains/generate_chain.py`（prompt 优化）、`server/services/image_gen.py`（LLM 判断+精准 prompt）、`server/routers/generate.py`（流程调整）
- **前端代码**：`src/pages/quiz/quiz.tsx`（图片尺寸+点击放大）
