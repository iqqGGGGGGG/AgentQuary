## Context

使用硅基流动平台的 Kolors（快手可图）免费模型生成图片，上传到腾讯云 COS。

## Decisions

### Decision 1: 图片生成 — 硅基流动 Kolors（免费）

**选择**: 硅基流动 `Kwai-Kolors/Kolors` 模型

**理由**:
- **完全免费**，无生成费用
- 快手开源模型，中文理解好
- 通过 OpenAI 兼容 API 调用
- 硅基流动平台稳定

**调用方式**: `https://api.siliconflow.cn/v1/images/generations`

### Decision 2: 图片存储 — 腾讯云 COS

**选择**: 上传到腾讯云 COS `gqq-agent-1310553153` 存储桶

**理由**: 用户已有 COS 存储桶，CDN 加速

### Decision 3: 关键词提取 — LLM 从题目提取英文 prompt

**选择**: 用 LLM 从题目中提取英文图片描述

**理由**: Kolors 英文 prompt 效果最好

### Decision 4: 异步并行生成

**选择**: 所有题目的图片生成并行执行

**理由**: 减少总耗时

## Risks / Trade-offs

**[Kolors 免费额度]** → 硅基流动免费模型可能有限制。缓解：失败时不显示图片。
