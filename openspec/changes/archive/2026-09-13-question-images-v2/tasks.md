## 1. 依赖与配置

- [ ] 1.1 修改 `server/requirements.txt`：添加 `cos-python-sdk-v5>=1.9.0`
- [ ] 1.2 修改 `server/config.py`：添加 `cos_bucket: str = "gqq-agent-1310553153"`、`cos_region: str = "ap-beijing"`、`cos_secret_id: str = ""`、`cos_secret_key: str = ""` 配置项
- [ ] 1.3 在 `server/.env` 中添加 COS 配置

## 2. COS 上传服务

- [ ] 2.1 新建 `server/services/cos_upload.py`：实现 `async def upload_image(image_bytes: bytes, key: str) -> str` 函数，上传图片到 COS 并返回 CDN URL

## 3. 图片搜索服务

- [ ] 3.1 新建 `server/services/image_search.py`：实现 `async def search_image(query: str) -> str | None` 函数，用 Unsplash API 搜索图片，下载后上传到 COS，返回 COS URL

## 4. 集成到生成流程

- [ ] 4.1 修改 `server/models/schemas.py`：`Question` 新增 `image_url: str | None = None` 字段
- [ ] 4.2 修改 `server/routers/generate.py`：新增 `generate_images: bool = False` 参数；题目生成后并行搜索图片

## 5. 前端改动

- [ ] 5.1 修改 `src/types/quiz.ts`：`Question` 新增 `image_url` 字段
- [ ] 5.2 修改 `src/pages/index/index.tsx`：增加「生成图片」开关
- [ ] 5.3 修改 `src/pages/quiz/quiz.tsx`：展示配图

## 6. 验证

- [ ] 6.1 运行测试确认通过
- [ ] 6.2 前端编译无报错
