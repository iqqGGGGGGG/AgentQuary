# enhance-search-quality Specification

## Purpose
提升搜索结果数量和质量，确保 AI 通过足够多的搜索结果正确理解用户主题；增加前端超时避免请求失败。

## Requirements

### Requirement: 增加搜索结果数量
系统 SHALL 将默认搜索结果数从 3 条提升到 10 条。

#### Scenario: 默认搜索 10 条
- **WHEN** AI 决定搜索一个主题
- **THEN** 默认搜索 10 条结果（Tavily 最大值），确保覆盖足够多的信息来源

### Requirement: 多轮搜索
系统 SHALL 支持 AI 对同一主题进行多轮搜索，使用不同关键词。

#### Scenario: 冷门主题多轮搜索
- **WHEN** 用户输入 "Harness Engineering"
- **THEN** AI 生成多组搜索词（如 "Harness Engineering 线束工程"、"Harness Engineering automotive wiring"），分别搜索后合并结果

### Requirement: 前端长超时
系统 SHALL 为 generate 和 report 接口设置 300 秒超时。

#### Scenario: generate 接口超时
- **WHEN** 前端调用 generate 接口
- **THEN** 超时时间为 300 秒，不因搜索+生成耗时而超时

#### Scenario: 其他接口超时不变
- **WHEN** 前端调用其他接口（login、history 等）
- **THEN** 超时时间保持 150 秒
