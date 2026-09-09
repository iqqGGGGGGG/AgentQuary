## Purpose

将知识库功能整合到"我的"页面，用户可以在个人中心直接管理文档和开始闯关。

## Requirements

### Requirement: 知识库卡片
系统 SHALL 在"我的"页面展示知识库卡片。

#### Scenario: 展示知识库
- **WHEN** 用户进入"我的"页面
- **THEN** 展示知识库卡片，包含文档数量、上传按钮、文档列表

### Requirement: 上传文档
系统 SHALL 支持在"我的"页面直接上传文档。

#### Scenario: 上传文档
- **WHEN** 用户点击上传按钮
- **THEN** 弹出文件选择器，选择后上传并刷新列表

### Requirement: 开始闯关
系统 SHALL 支持从知识库直接开始闯关。

#### Scenario: 基于文档闯关
- **WHEN** 用户点击文档的"开始闯关"按钮
- **THEN** 使用该文档内容生成题目并进入答题页

### Requirement: 删除文档
系统 SHALL 支持删除知识库中的文档。

#### Scenario: 删除文档
- **WHEN** 用户点击删除按钮
- **THEN** 删除文档并刷新列表
