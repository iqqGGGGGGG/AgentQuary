## 1. 后端依赖与配置

- [x] 1.1 在 `server/requirements.txt` 中添加 `PyPDF2>=3.0.0` 和 `python-docx>=1.0.0`
- [x] 1.2 确认 `server/uploads/` 目录存在且在 `.gitignore` 中

## 2. 数据库模型

- [x] 2.1 修改 `server/models/orm.py`：新增 `Document` 表
- [x] 2.2 修改 `server/models/schemas.py`：新增 `DocumentResponse`、`DocumentListResponse` Pydantic 模型

## 3. 文档解析服务

- [x] 3.1 新建 `server/services/document_parser.py`

## 4. 文档 API 路由

- [x] 4.1 新建 `server/routers/documents.py`
- [x] 4.2 修改 `server/main.py`

## 5. 前端类型与 API

- [x] 5.1 修改 `src/types/quiz.ts`：新增 `Document`、`DocumentListResponse` 类型
- [x] 5.2 修改 `src/services/api.ts`：新增 `uploadDocument`、`getDocuments`、`getDocument`、`deleteDocument` API 方法

## 6. 前端知识库页面

- [x] 6.1 新建 `src/pages/knowledge/` 页面
- [x] 6.2 修改 `src/app.config.ts`

## 7. 集成题目生成

- [x] 7.1 修改 `src/pages/knowledge/index.tsx`

## 8. 验证

- [x] 8.1 运行 `pytest server/tests/ -v` 确认后端测试通过
- [x] 8.2 前端编译无报错
