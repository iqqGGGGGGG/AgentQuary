## Why

开发调试时，当前后端日志只有 INFO 级别的请求/异常信息，无法看到 AI 请求的详细内容（planner 输入/输出、工具调用参数、搜索结果、最终 prompt 等）。需要增加 DEBUG 级别日志，帮助定位 AI 生成质量、搜索效果、降级原因等问题。

## What Changes

- 修改 **日志级别**：开发模式下默认 DEBUG，生产模式保持 INFO
- 在 **研究阶段** 增加 DEBUG 日志：planner 输入/输出、工具调用参数、搜索结果摘要、降级原因
- 在 **生成阶段** 增加 DEBUG 日志：最终 content 长度、是否使用搜索、LLM 调用参数
- 启用 **LangChain verbose**：开发模式下输出 LangChain 内部调用细节

## Capabilities

### New Capabilities
- `dev-logging`: 开发模式详细日志——DEBUG 级别输出 AI 请求/响应/工具调用细节

### Modified Capabilities
（无）

## Impact

- **后端代码**：`server/main.py`（日志级别）、`server/chains/research_chain.py`（DEBUG 日志）、`server/chains/llm.py`（verbose 开关）
- **API 行为**：无变更
- **依赖**：无新增
