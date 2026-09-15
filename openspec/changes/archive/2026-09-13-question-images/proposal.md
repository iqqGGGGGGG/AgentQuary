## Why

当前题目只有文字，缺乏视觉辅助。对于英语单词、动植物、历史地理等知识，配图能显著提升记忆效果。需要在 AI 生成题目的同时，为每道题生成一张相关配图。

## What Changes

- 新增 **图片生成服务**：调用阿里云百炼图片生成 API，根据题目内容生成配图
- 新增 **图片存储**：本地存储生成的图片，通过 FastAPI 静态文件服务
- 修改 **题目生成流程**：支持可选的图片生成步骤
- 修改 **首页**：增加「生成图片」开关
- 修改 **答题页**：展示题目配图
- 修改 **数据模型**：Question 新增 image_url 字段

## Capabilities

### New Capabilities
- `question-images`: 题目配图生成——AI 为每道题生成相关图片，辅助记忆

### Modified Capabilities
（无）

## Impact

- **后端新增**：`server/services/image_gen.py`（图片生成服务）、`server/routers/images.py`（图片静态服务）
- **后端修改**：`server/routers/generate.py`（集成图片生成）、`server/models/schemas.py`（Question 新增字段）、`server/config.py`（新增配置）、`server/main.py`（挂载静态文件）
- **前端修改**：`src/pages/index/index.tsx`（开关）、`src/pages/quiz/quiz.tsx`（展示图片）、`src/types/quiz.ts`（类型更新）
- **新增依赖**：`dashscope`（阿里云百炼 SDK）
