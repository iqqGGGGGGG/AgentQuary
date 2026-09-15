## Purpose

为题目生成配图，使用硅基流动 Kolors 免费模型 + 腾讯云 COS 存储。

## Requirements

### Requirement: 图片生成开关
系统 SHALL 支持用户选择是否为题目配图。

### Requirement: 图片生成
系统 SHALL 使用 Kolors 免费模型为每道题生成配图。

#### Scenario: 生成配图
- **WHEN** 系统生成了一道关于「太阳系」的题目
- **THEN** LLM 提取关键词，调用 Kolors 生成太阳系相关图片

#### Scenario: 生成失败
- **WHEN** 图片生成失败
- **THEN** 该题不显示图片，不影响其他题目

### Requirement: COS 存储
系统 SHALL 将图片上传到腾讯云 COS。

### Requirement: 图片展示
系统 SHALL 在答题页展示配图。
