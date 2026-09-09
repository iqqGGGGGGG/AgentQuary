## Purpose

在开发模式下输出详细的 DEBUG 日志，帮助开发者观察 AI 请求、响应、工具调用的完整过程。

## ADDED Requirements

### Requirement: 开发模式 DEBUG 日志
系统 SHALL 在 `DEV_MODE=true` 时将日志级别设为 DEBUG，输出 AI 调用的详细信息。

#### Scenario: 开发模式日志
- **WHEN** `DEV_MODE=true` 且启动后端
- **THEN** 控制台输出 DEBUG 级别日志，包含 planner 输入/输出、工具调用参数、搜索结果摘要、content 长度等

#### Scenario: 生产模式日志
- **WHEN** `DEV_MODE=false`
- **THEN** 日志级别保持 INFO，不输出 DEBUG 信息

### Requirement: LangChain verbose
系统 SHALL 在开发模式下启用 LangChain verbose，输出 LLM 调用细节。

#### Scenario: LangChain 调用日志
- **WHEN** `DEV_MODE=true` 且调用 LLM chain
- **THEN** LangChain 输出 prompt 内容、模型响应、耗时等详细信息
