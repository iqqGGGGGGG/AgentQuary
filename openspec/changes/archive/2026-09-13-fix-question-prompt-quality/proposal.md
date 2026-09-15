## Why

当前题目生成 prompt 存在两个核心问题：
1. **题目质量差**：缺乏具体的题目设计指导，AI 生成的题目过于泛泛，如"二次元人物有哪些"这种列举题不适合闯关模式
2. **图片与题目脱节**：image_prompt 生成的是通用插图，而非直接服务于题目内容的图片

需要重新设计 prompt，让 AI 理解什么是好的闯关题目，以及如何让图片与题目紧密配合。

## What Changes

- 重写 **题目生成 prompt**：增加题目设计原则、图片-题目配合规则、具体示例
- 新增 **题目类型指导**：识别题、判断题、场景题等多种出题方式

## Capabilities

### New Capabilities
- `fix-question-prompt-quality`: 优化题目生成 prompt，提升题目质量和图片关联性

### Modified Capabilities
（无）

## Impact

- **后端代码**：`server/chains/generate_chain.py`（prompt 重写）
- **无新增依赖**
