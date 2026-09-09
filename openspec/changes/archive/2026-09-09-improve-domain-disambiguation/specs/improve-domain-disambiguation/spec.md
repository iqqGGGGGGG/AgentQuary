## Purpose

利用用户输入上下文进行领域消歧；当用户无上下文且搜索结果跨多个领域时，返回澄清选项让用户选择。

## ADDED Requirements

### Requirement: 上下文感知搜索
系统 SHALL 在用户输入包含对主题的解释/描述时，将这些上下文融入搜索 query。

#### Scenario: 用户给出领域描述
- **WHEN** 用户输入 "Harness Engineering（驾驭工程）是2026年兴起的AI工程化核心范式"
- **THEN** planner 使用 "Harness Engineering AI agent 2026 驾驭工程" 而非 "Harness Engineering" 作为搜索词

#### Scenario: 用户给出中文含义
- **WHEN** 用户输入 "Harness Engineering 是什么？驾驭工程"
- **THEN** planner 使用 "Harness Engineering 驾驭工程" 搜索，而非仅 "Harness Engineering"

### Requirement: 上下文优先原则
系统 SHALL 以用户输入的领域描述为准，当搜索结果与用户描述冲突时，不被搜索结果的多数派误导。

#### Scenario: 搜索结果与用户描述冲突
- **WHEN** 搜索返回10条结果，8条是"线束工程"，但用户输入明确描述为"AI工程化范式"
- **THEN** AI 识别出用户指的是 AI 领域的 Harness Engineering，忽略线束工程的结果

### Requirement: 跨领域澄清
系统 SHALL 在检测到搜索结果跨多个不同领域且用户无上下文时，返回澄清选项而非盲目生成题目。

#### Scenario: 搜索结果跨多个领域
- **WHEN** 用户只输入 "Harness Engineering"，搜索结果同时包含"线束工程"和"AI工程化范式"两个领域
- **THEN** 系统返回 `needs_clarification: true` 和 `domain_options` 列表（如 ["线束工程(汽车/电气)", "AI工程化范式(Agent工程)"]）

#### Scenario: 搜索结果单一领域
- **WHEN** 用户输入 "太阳系基础知识"，搜索结果全部关于天文学
- **THEN** 系统正常生成题目，`needs_clarification: false`

#### Scenario: 用户有上下文时不澄清
- **WHEN** 用户输入 "Harness Engineering 是AI范式"，虽然搜索结果跨领域，但用户已明确领域
- **THEN** 系统直接生成题目，不返回澄清选项

### Requirement: 澄清后重新生成
系统 SHALL 支持用户选择领域后重新生成题目。

#### Scenario: 用户选择领域后生成
- **WHEN** 用户在澄清响应中选择了 "AI工程化范式"
- **THEN** 系统使用选定领域重新搜索并生成题目

### Requirement: 生成阶段领域对齐
系统 SHALL 在生成题目时，确保题目属于用户所描述的领域。

#### Scenario: 参考内容与用户描述不一致
- **WHEN** 搜索返回了错误领域的参考内容，但用户输入中有明确的领域描述
- **THEN** 生成的题目基于用户描述的领域，而非参考内容中的错误领域
