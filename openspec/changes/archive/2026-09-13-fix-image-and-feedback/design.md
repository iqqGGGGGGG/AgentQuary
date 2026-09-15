## Context

三个独立问题。

## Decisions

### Decision 1: 百炼生图

**选择**: 切换到百炼 qwen-image-3.0-pro

**理由**: 质量更好，与项目已有的百炼 Embedding 同平台

### Decision 2: 图片在题目下方

**选择**: 将 Image 组件移到 Text 组件下方

**理由**: 题干说"下图"时，图片应在文字下方

### Decision 3: 自定义反馈输入框

**选择**: 在预设选项下方添加 TextInput

**理由**: 让用户可以输入更具体的反馈
