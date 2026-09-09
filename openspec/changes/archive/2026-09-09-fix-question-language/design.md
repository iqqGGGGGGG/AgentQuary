## Context

当前 `generate_chain.py` 的 system prompt 没有指定输出语言。当联网搜索返回英文内容时，LLM 会跟随内容语言生成英文题目。

## Goals / Non-Goals

**Goals:**
- 确保所有题目输出为中文
- 研究阶段适配用户语言

**Non-Goals:**
- 不翻译搜索结果（LLM 自行理解即可）
- 不限制用户输入语言

## Decisions

### Decision 1: 在 generate chain prompt 中增加语言规则

**选择**: 在 system prompt 的规则列表中增加一条中文输出要求

**理由**: 最直接的修复方式，LLM 会严格遵循 system prompt 中的明确指令

### Decision 2: 在 research planner prompt 中增加语言适配

**选择**: 当用户输入包含中文时，引导 planner 在搜索 query 中加入中文关键词

**理由**: 中文搜索可以获取更相关的中文来源，从源头减少英文内容

## Risks / Trade-offs

**[专业术语翻译质量]** → LLM 翻译专业术语可能不准确。缓解：允许保留英文原文并附中文解释。
