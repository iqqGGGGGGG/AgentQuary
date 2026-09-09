## Context

三个独立的 CSS/布局问题，互不影响。

## Goals / Non-Goals

**Goals:**
- 修复文字溢出
- 按钮等宽
- AI 总结前置 + loading 状态

**Non-Goals:**
- 不改变 AI 总结的生成逻辑（后端不变）
- 不改变按钮功能

## Decisions

### Decision 1: overflow-wrap: break-word

**选择**: 在错题本卡片的文字元素上添加 `overflow-wrap: break-word`

**理由**: 最简单的修复方式，让长单词/长文本自动换行

### Decision 2: 按钮等宽用 flex: 1

**选择**: 两个按钮都设置 `flex: 1`，让它们平分宽度

**理由**: 简单且自适应屏幕宽度

### Decision 3: AI 总结位置和 loading

**选择**: 
- 将 summary-card 从 mastered/weak 之后移到之前
- 新增 `summaryLoading` state，API 返回前显示 loading 文案

**理由**: 用户最关心的是 AI 总结，应该优先展示
