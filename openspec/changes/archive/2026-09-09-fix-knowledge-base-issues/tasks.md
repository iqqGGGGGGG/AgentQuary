## 1. 后端修复

- [x] 1.1 修改 `server/routers/documents.py`：新增 GET /api/documents/{id}/text 返回完整文本内容；新增 DELETE /api/documents（清空当前用户所有文档）
- [x] 1.2 修改 `src/services/api.ts`：新增 `getDocumentText` 和 `clearDocuments` API 方法

## 2. 前端修复

- [x] 2.1 修改 `src/pages/knowledge/index.tsx`：handleGenerateQuiz 使用 getDocumentText 获取完整文本；添加"清空全部"按钮

## 3. 验证

- [x] 3.1 运行测试确认通过
- [x] 3.2 前端编译无报错
