## Why

当前题目只有文字，缺乏视觉辅助。需要为题目配图，提升记忆效果。

采用**免费图库（Unsplash）+ 腾讯云 COS** 方案，而非 AI 生成图片：
- **免费**：Unsplash API 免费，无生成费用
- **快速**：搜索 <1秒，无需等待 AI 生成
- **高质量**：真实照片，适合学习场景（英语单词配实物图、历史配真实场景）
- **COS 存储**：图片上传到腾讯云 COS，CDN 加速访问

## What Changes

- 新增 **图片搜索服务**：LLM 从题目提取关键词 → Unsplash 搜索免费图片
- 新增 **COS 上传服务**：图片上传到腾讯云 COS
- 修改 **题目生成流程**：支持可选的图片搜索步骤
- 修改 **首页**：增加「生成图片」开关
- 修改 **答题页**：展示题目配图

## Capabilities

### New Capabilities
- `question-images-v2`: 题目配图——Unsplash 免费图库搜索 + 腾讯云 COS 存储

### Modified Capabilities
（无）

## Impact

- **后端新增**：`server/services/image_search.py`（图片搜索）、`server/services/cos_upload.py`（COS 上传）
- **后端修改**：`server/routers/generate.py`（集成图片搜索）、`server/models/schemas.py`（Question 新增字段）、`server/config.py`（COS 配置）
- **前端修改**：`src/pages/index/index.tsx`（开关）、`src/pages/quiz/quiz.tsx`（展示图片）
- **新增依赖**：`cos-python-sdk-v5`（腾讯云 COS SDK）
