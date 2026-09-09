## 1. 日志配置

- [x] 1.1 修改 `server/main.py`：根据 `settings.dev_mode` 动态设置 `logging.basicConfig(level=logging.DEBUG if settings.dev_mode else logging.INFO)`；开发模式下设置 `os.environ["LANGCHAIN_VERBOSE"] = "true"`

## 2. AI 调用日志

- [x] 2.1 修改 `server/chains/research_chain.py` 的 `research_content` 函数：在 planner 调用前后增加 DEBUG 日志（输入 content 长度、计划输出 actions）、工具调用时增加 DEBUG 日志（工具名、参数、结果摘要）、降级时增加 WARNING 日志（原因）
- [x] 2.2 修改 `server/routers/generate.py` 的 `generate_quiz` 函数：在 research_content 调用后增加 DEBUG 日志（enriched content 长度、search_used 标记）

## 3. 验证

- [x] 3.1 启动后端 `DEV_MODE=true`，确认控制台输出 DEBUG 日志
