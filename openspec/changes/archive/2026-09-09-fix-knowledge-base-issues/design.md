## Context

三个独立问题，互不影响。

## Decisions

### Decision 1: 文本清理

**选择**: 在 `parse_docx` 中添加文本清理逻辑

**理由**: python-docx 提取的文本可能包含控制字符

### Decision 2: 清空 API

**选择**: 新增 DELETE /api/documents（无 ID）清空所有文档

**理由**: 比逐个删除更高效

### Decision 3: 前端数据优化

**选择**: 文档列表只显示元数据，生成题目时再获取完整文本

**理由**: 减少 state 中的数据量
