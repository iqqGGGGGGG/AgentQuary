## Context

当前 `main.py` 固定使用 `logging.INFO` 级别。LangChain 默认不输出调用细节。

## Goals / Non-Goals

**Goals:**
- 开发模式下能看到 AI 完整调用链路
- 不影响生产环境日志

**Non-Goals:**
- 不实现日志文件持久化
- 不实现日志采样或过滤

## Decisions

### Decision 1: 根据 DEV_MODE 动态设置日志级别

**选择**: `DEV_MODE=true` 时 `logging.basicConfig(level=logging.DEBUG)`，否则 `INFO`

**理由**: 复用现有配置，无需新增环境变量

### Decision 2: LangChain verbose 通过环境变量控制

**选择**: 开发模式设置 `LANGCHAIN_VERBOSE=true` 环境变量

**理由**: LangChain 原生支持此环境变量，无需改代码

## Risks / Trade-offs

**[DEBUG 日志量大]** → 开发模式日志较多。缓解：仅在开发环境使用。
