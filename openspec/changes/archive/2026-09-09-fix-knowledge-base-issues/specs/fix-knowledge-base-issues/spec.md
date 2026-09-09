## Purpose

修复知识库的三个问题：生成题目只用前500字、无法一键清空、前端性能警告。

## Requirements

### Requirement: 完整文本获取
系统 SHALL 提供获取文档完整文本的 API，用于生成题目。

#### Scenario: 获取完整文本
- **WHEN** 前端需要基于文档生成题目
- **THEN** 调用 GET /api/documents/{id}/text 获取完整文本，而非截断的 preview

### Requirement: 一键清空知识库
系统 SHALL 提供一键清空所有文档的功能。

#### Scenario: 清空所有文档
- **WHEN** 用户点击"清空全部"按钮
- **THEN** 系统删除该用户的所有文档和文件

### Requirement: 文本清理
系统 SHALL 对提取的文本进行清理。

#### Scenario: 控制字符清理
- **WHEN** 提取的文本包含控制字符
- **THEN** 系统去除控制字符，保留正常文本
