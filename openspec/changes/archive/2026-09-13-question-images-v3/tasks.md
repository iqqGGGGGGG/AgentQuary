## 1. 依赖与配置

- [x] 1.1 修改 `server/requirements.txt`：添加 `cos-python-sdk-v5>=1.9.0`
- [x] 1.2 修改 `server/config.py`：添加硅基流动和 COS 配置项
- [x] 1.3 在 `server/.env` 中添加硅基流动和 COS 配置

## 2. COS 上传服务

- [x] 2.1 新建 `server/services/cos_upload.py`

## 3. 图片生成服务

- [x] 3.1 新建 `server/services/image_gen.py`

## 4. 集成到生成流程

- [x] 4.1 修改 `server/models/schemas.py`
- [x] 4.2 修改 `server/routers/generate.py`

## 5. 前端改动

- [x] 5.1 修改 `src/types/quiz.ts`
- [x] 5.2 修改 `src/pages/index/index.tsx`
- [x] 5.3 修改 `src/pages/quiz/quiz.tsx`

## 6. 验证

- [x] 6.1 运行测试确认通过
- [x] 6.2 前端编译无报错
