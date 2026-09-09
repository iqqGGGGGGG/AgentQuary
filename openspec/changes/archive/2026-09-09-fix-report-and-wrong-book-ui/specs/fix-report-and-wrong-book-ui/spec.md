## Purpose

修复报告页和错题本的三个 UI 问题。

## ADDED Requirements

### Requirement: 错题本文字不溢出
系统 SHALL 确保错题本卡片中的长文字正确换行，不溢出屏幕。

#### Scenario: 长题目文字
- **WHEN** 错题卡片中包含很长的题目文本
- **THEN** 文字自动换行，不超出卡片边界

### Requirement: 报告页按钮等宽
系统 SHALL 确保"再来一关"和"回到首页"两个按钮宽度一致。

#### Scenario: 两个按钮等宽
- **WHEN** 用户查看闯关完成报告页
- **THEN** "再来一关"和"回到首页"按钮宽度相同

### Requirement: AI 总结优先显示
系统 SHALL 将 AI 总结放在掌握/错误记录之前显示，并在加载时显示 loading 状态。

#### Scenario: AI 总结位置
- **WHEN** 用户查看闯关完成报告
- **THEN** 先看到正确率 → AI 总结 → 掌握的 → 需要复习的 → 错题回顾

#### Scenario: AI 总结加载中
- **WHEN** AI 总结正在加载
- **THEN** 显示"AI 正在生成总结..."的加载提示
