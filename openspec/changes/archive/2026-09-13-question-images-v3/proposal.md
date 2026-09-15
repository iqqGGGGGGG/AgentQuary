## Why

当前题目只有文字，缺乏视觉辅助。需要为题目配图，提升记忆效果。

使用**硅基流动 Kolors（免费）+ 腾讯云 COS** 方案：
- **免费**：Kolors 模型完全免费，无生成费用
- **国产**：快手开源模型，中文理解好
- **COS 存储**：图片上传到腾讯云 COS，CDN 加速访问

## What Changes

- 新增 **图片生成服务**：调用硅基流动 Kolors API 免费生成图片
- 新增 **COS 上传服务**：图片上传到腾讯云 COS
- 修改 **题目生成流程**：支持可选的图片生成步骤
- 修改 **首页**：增加「生成图片」开关
- 修改 **答题页**：展示题目配图

## Capabilities

### New Capabilities
- `question-images-v3`: 题目配图——硅基流动 Kolors 免费生成 + 腾讯云 COS 存储

### Modified Capabilities
（无）

## Impact

- **后端新增**：`server/services/image_gen.py`（图片生成）、`server/services/cos_upload.py`（COS 上传）
- **后端修改**：`server/routers/generate.py`（集成图片生成）、`server/models/schemas.py`（Question 新增字段）、`server/config.py`（配置项）
- **前端修改**：`src/pages/index/index.tsx`（开关）、`src/pages/quiz/quiz.tsx`（展示图片）
- **新增依赖**：`cos-python-sdk-v5`（腾讯云 COS SDK）
