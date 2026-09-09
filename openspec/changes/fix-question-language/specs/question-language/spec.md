## Purpose

确保 AI 生成的题目、选项和讲解始终使用中文，无论参考内容的语言是什么。

## ADDED Requirements

### Requirement: 中文输出
系统 SHALL 始终使用中文生成题目、选项和讲解，无论输入内容或参考内容的语言。

#### Scenario: 英文参考内容生成中文题目
- **WHEN** 联网搜索返回英文内容作为参考
- **THEN** 生成的题目、选项、讲解全部使用中文

#### Scenario: 中文参考内容保持中文
- **WHEN** 参考内容为中文
- **THEN** 生成的题目、选项、讲解使用中文（正常情况）

#### Scenario: 中英混合输入
- **WHEN** 用户输入 "Harness Engineering 是什么？"
- **THEN** 生成的题目使用中文，专业术语可保留英文原文并附中文解释

### Requirement: 研究阶段语言适配
系统 SHALL 在研究阶段根据用户输入语言调整搜索策略。

#### Scenario: 中文输入优先中文来源
- **WHEN** 用户输入包含中文字符
- **THEN** planner 优先使用中文关键词搜索，或在 query 中附带中文翻译
