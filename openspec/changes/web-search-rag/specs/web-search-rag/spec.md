## Purpose

为题目生成流程引入 AI 驱动的联网研究能力。系统将 TavilySearch（关键词搜索）和 TavilyExtract（URL 内容提取）作为工具提供给 AI，由 AI 自主判断用户输入类型并决定调用哪些工具、使用什么参数，获取的内容作为生成题目的参考上下文。

## ADDED Requirements

### Requirement: AI 自主工具选择
系统 SHALL 将 TavilySearch 和 TavilyExtract 作为工具提供给 AI，由 AI 根据用户输入自主决定调用哪个工具。

#### Scenario: 关键词输入触发搜索
- **WHEN** 用户输入 "Harness Engineering"
- **THEN** AI 判断为关键词输入，调用 TavilySearch 搜索相关知识

#### Scenario: URL 输入触发内容提取
- **WHEN** 用户输入 "https://example.com/harness-guide"
- **THEN** AI 判断为 URL 输入，调用 TavilyExtract 提取该网页的完整内容

#### Scenario: 长文本输入跳过工具
- **WHEN** 用户输入超过 200 字的详细文本
- **THEN** AI 判断已有足够信息，不调用任何工具，直接使用原始文本

#### Scenario: 混合输入
- **WHEN** 用户输入 "根据 https://example.com/article 的内容出题，再搜索一下最新的进展"
- **THEN** AI 同时调用 TavilyExtract 提取指定 URL 和 TavilySearch 搜索最新进展

### Requirement: 动态参数调整
系统 SHALL 根据内容复杂度和语言特征动态调整工具参数。

#### Scenario: 复杂/专业主题使用高级搜索
- **WHEN** 用户输入涉及专业术语或冷门知识领域
- **THEN** AI 设置 `search_depth="advanced"`、`max_results=5`、`include_raw_content=True` 获取更详细的内容

#### Scenario: 简单/常见主题使用基础搜索
- **WHEN** 用户输入为常见知识主题（如 "太阳系基础知识"）
- **THEN** AI 设置 `search_depth="basic"`、`max_results=3`，仅获取摘要即可

#### Scenario: 中文内容优先中文来源
- **WHEN** 用户输入为中文主题
- **THEN** AI 可通过 `include_domains` 参数优先搜索中文网站

#### Scenario: URL 提取深度动态调整
- **WHEN** 用户输入一个 URL
- **THEN** AI 根据 URL 类型设置 `extract_depth`：简单页面用 `"basic"`，结构复杂的页面用 `"advanced"`

### Requirement: 搜索结果作为上下文
系统 SHALL 将工具获取的内容与用户原始输入合并，作为 LLM 生成题目的参考上下文。

#### Scenario: 搜索结果注入 prompt
- **WHEN** 工具成功获取到相关内容
- **THEN** LLM 收到的 prompt 中包含用户原始主题和获取到的参考内容，题目基于参考内容生成

#### Scenario: 内容长度限制
- **WHEN** 获取的内容超过系统限制
- **THEN** 内容被截断到最大限制长度，不报错

### Requirement: 研究失败降级
系统 SHALL 在工具调用失败时优雅降级，不阻断题目生成流程。

#### Scenario: 网络不可用降级
- **WHEN** Tavily API 因网络问题无法访问
- **THEN** 系统使用用户原始输入直接调用 LLM 生成题目，不报错

#### Scenario: 工具调用超时降级
- **WHEN** 工具调用超过 15 秒未返回结果
- **THEN** 系统放弃工具调用，使用用户原始输入直接调用 LLM 生成题目

#### Scenario: 搜索无结果降级
- **WHEN** TavilySearch 返回空结果
- **THEN** 系统使用用户原始输入直接调用 LLM 生成题目

#### Scenario: URL 提取失败降级
- **WHEN** TavilyExtract 无法提取指定 URL 的内容
- **THEN** 系统回退到 TavilySearch 搜索该 URL 的标题/关键词，或直接使用原始输入

### Requirement: 研究来源标记
系统 SHALL 在生成结果中标记是否使用了联网研究，便于前端展示和调试。

#### Scenario: 使用了搜索标记
- **WHEN** 题目生成过程中使用了 TavilySearch
- **THEN** 响应中包含 `search_used: true`

#### Scenario: 使用了提取标记
- **WHEN** 题目生成过程中使用了 TavilyExtract
- **THEN** 响应中包含 `search_used: true`

#### Scenario: 未使用任何工具标记
- **WHEN** 题目生成过程中未使用任何工具（长文本或降级）
- **THEN** 响应中包含 `search_used: false`

### Requirement: 系统配置
系统 SHALL 支持通过环境变量配置研究行为。

#### Scenario: 启用/禁用联网研究
- **WHEN** 环境变量 `SEARCH_ENABLED=false`
- **THEN** 系统不调用任何 Tavily 工具，直接使用用户输入

#### Scenario: API Key 缺失降级
- **WHEN** `TAVILY_API_KEY` 未配置或为空
- **THEN** 系统跳过所有工具调用，直接使用用户输入生成题目

### Requirement: 内容安全
系统 SHALL 对工具获取的内容进行基本的安全过滤。

#### Scenario: 内容截断
- **WHEN** 工具获取的内容过长
- **THEN** 内容被截断到最大限制，不超出 LLM 上下文窗口
