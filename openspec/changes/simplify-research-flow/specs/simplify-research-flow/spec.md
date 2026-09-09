## Purpose

简化研究流程，去掉不可靠的 Planner LLM 调用，直接调用 Tavily 工具获取搜索结果。

## ADDED Requirements

### Requirement: 直接搜索
系统 SHALL 在用户输入为短文本（≤2000字且非 URL）时，直接调用 TavilySearch 搜索，不需要 LLM 决定是否搜索。

#### Scenario: 短文本直接搜索
- **WHEN** 用户输入 "Harness Engineering"
- **THEN** 系统直接调用 TavilySearch(query="Harness Engineering", max_results=10, search_depth="advanced")

#### Scenario: 中文输入搜索
- **WHEN** 用户输入 "太阳系基础知识"
- **THEN** 系统直接调用 TavilySearch(query="太阳系基础知识", max_results=10, search_depth="advanced")

### Requirement: URL 直接提取
系统 SHALL 在用户输入为 URL 时，直接调用 TavilyExtract 提取内容。

#### Scenario: URL 输入
- **WHEN** 用户输入 "https://example.com/article"
- **THEN** 系统直接调用 TavilyExtract(urls=["https://example.com/article"])

### Requirement: 长文本跳过
系统 SHALL 在用户输入超过 2000 字时跳过搜索。

#### Scenario: 长文本输入
- **WHEN** 用户输入超过 2000 字的详细内容
- **THEN** 系统直接使用原始内容，不调用搜索工具

### Requirement: 搜索失败降级
系统 SHALL 在搜索失败时静默降级。

#### Scenario: 搜索失败
- **WHEN** TavilySearch 调用失败
- **THEN** 系统使用原始内容继续生成题目
