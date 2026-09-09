## Why

当前知识库是独立页面，用户需要额外跳转才能使用。需要将知识库功能整合到"我的"页面，让用户可以在个人中心直接管理文档并快速开始闯关。

## What Changes

- 在"我的"页面新增 **知识库卡片**：展示已上传文档数量、上传按钮、文档列表、一键开始闯关
- 移除独立的 **知识库页面**（`src/pages/knowledge/`）
- 移除 **app.config.ts** 中的知识库路由

## Capabilities

### New Capabilities
- `knowledge-in-profile`: 知识库整合到"我的"页面

### Modified Capabilities
- `knowledge-base`: 页面位置变更

## Impact

- **前端代码**：`src/pages/profile/profile.tsx`（新增知识库卡片）、`src/pages/profile/profile.scss`（新增样式）、`src/app.config.ts`（移除路由）
- **后端代码**：无变更
