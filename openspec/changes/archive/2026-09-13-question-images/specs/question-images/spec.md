## Purpose

为题目生成配图，辅助用户记忆。用户可选择是否启用图片生成。

## Requirements

### Requirement: 图片生成开关
系统 SHALL 支持用户在闯关前选择是否生成配图。

#### Scenario: 启用图片生成
- **WHEN** 用户在首页勾选「生成图片」
- **THEN** 系统在生成题目时同时为每道题生成配图

#### Scenario: 禁用图片生成
- **WHEN** 用户未勾选「生成图片」
- **THEN** 系统只生成文字题目，不生成图片

### Requirement: 题目配图生成
系统 SHALL 根据题目内容生成相关配图。

#### Scenario: 生成配图
- **WHEN** 系统生成了一道关于「太阳系」的题目
- **THEN** 系统调用图片生成 API，生成一张太阳系相关的图片

#### Scenario: 图片生成失败
- **WHEN** 图片生成 API 调用失败
- **THEN** 该题不显示图片，不影响其他题目

### Requirement: 图片展示
系统 SHALL 在答题页面展示题目配图。

#### Scenario: 答题页展示图片
- **WHEN** 用户查看一道有配图的题目
- **THEN** 在题目文字上方展示配图

#### Scenario: 历史记录展示图片
- **WHEN** 用户回看历史学习记录
- **THEN** 仍然能看到当时的配图

### Requirement: 图片存储
系统 SHALL 将生成的图片存储在本地服务器。

#### Scenario: 图片存储路径
- **WHEN** 图片生成成功
- **THEN** 图片保存到 `server/uploads/images/{session_id}_{question_id}.png`

#### Scenario: 图片访问
- **WHEN** 前端需要展示图片
- **THEN** 通过 `/api/images/{filename}` 访问图片
