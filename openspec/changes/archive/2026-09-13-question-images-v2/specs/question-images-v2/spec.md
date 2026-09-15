## Purpose

为题目搜索配图，使用免费图库 + 腾讯云 COS 存储。

## Requirements

### Requirement: 图片搜索开关
系统 SHALL 支持用户选择是否为题目配图。

#### Scenario: 启用配图
- **WHEN** 用户勾选「生成图片」
- **THEN** 系统为每道题搜索配图

### Requirement: 图片搜索
系统 SHALL 从免费图库搜索与题目相关的图片。

#### Scenario: 搜索配图
- **WHEN** 系统生成了一道关于「太阳系」的题目
- **THEN** LLM 提取关键词 "solar system"，搜索 Unsplash 获取相关图片

#### Scenario: 搜索失败
- **WHEN** 图片搜索失败
- **THEN** 该题不显示图片，不影响其他题目

### Requirement: COS 存储
系统 SHALL 将图片上传到腾讯云 COS。

#### Scenario: 上传到 COS
- **WHEN** 图片搜索成功
- **THEN** 图片上传到 COS，返回 CDN URL

### Requirement: 图片展示
系统 SHALL 在答题页展示配图。

#### Scenario: 展示配图
- **WHEN** 题目有配图
- **THEN** 在题目文字上方展示图片
