## Why

三个问题需要修复：
1. **生图质量差**：当前使用硅基流动 Kolors 免费模型，质量不稳定。切换到百炼 qwen-image-3.0-pro 提升质量
2. **图片位置错误**：图片在题目文字上方，但题干说"下图"，应将图片移到题目文字下方
3. **缺少自定义反馈**：反馈面板只有预设选项，没有自定义输入框

## What Changes

- 修改 **图片生成服务**：从硅基流动切换到百炼 qwen-image-3.0-pro
- 修改 **答题页**：图片移到题目文字下方
- 修改 **报告页反馈面板**：增加自定义输入框

## Capabilities

### New Capabilities
- `fix-image-and-feedback`: 修复生图质量、图片位置、自定义反馈

### Modified Capabilities
（无）

## Impact

- **后端代码**：`server/services/image_gen.py`（切换到百炼 API）、`server/config.py`（更新配置）
- **前端代码**：`src/pages/quiz/quiz.tsx`（图片位置）、`src/pages/report/report.tsx`（自定义反馈）
