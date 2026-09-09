## Why

三个前端 UI 问题需要修复：
1. 错题本页面文字溢出屏幕（长题目、长答案没有换行处理）
2. 闯关完成页"再来一关"和"回到首页"按钮长度不一致
3. AI 总结位置太靠后，应该先看到总结再看掌握/错误记录；且加载时无提示

## What Changes

- 修改 **错题本样式**：添加 `overflow-wrap: break-word` 防止文字溢出
- 修改 **报告页按钮样式**：两个按钮等宽
- 修改 **报告页布局**：AI 总结移到掌握/错误记录之前，加载时显示 loading 状态

## Capabilities

### New Capabilities
- `fix-report-and-wrong-book-ui`: 修复报告页和错题本的三个 UI 问题

### Modified Capabilities
（无）

## Impact

- **前端代码**：`src/pages/wrong-book/wrong-book.scss`、`src/pages/report/report.tsx`、`src/pages/report/report.scss`
- **后端代码**：无
