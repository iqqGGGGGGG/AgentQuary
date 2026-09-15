## 1. 依赖与配置

- [ ] 1.1 修改 `server/requirements.txt`：添加 `dashscope>=1.20.0`
- [ ] 1.2 修改 `server/config.py`：添加 `image_gen_enabled: bool = False`、`image_gen_model: str = "qwen-image-3.0-pro"` 配置项
- [ ] 1.3 在 `.gitignore` 中确认 `server/uploads/images/` 已排除

## 2. 图片生成服务

- [ ] 2.1 新建 `server/services/image_gen.py`：实现 `async def generate_image(prompt: str, save_path: str) -> bool` 函数，调用百炼图片生成 API，保存图片到指定路径

## 3. 图片静态服务

- [ ] 3.1 修改 `server/main.py`：挂载 `server/uploads/images/` 为静态文件目录 `/api/images`

## 4. 集成到生成流程

- [ ] 4.1 修改 `server/models/schemas.py`：`Question` 新增 `image_url: str | None = None` 字段
- [ ] 4.2 修改 `server/routers/generate.py`：新增 `generate_images: bool = False` 请求参数；题目生成后，如果启用图片生成，为每道题异步生成图片并设置 image_url

## 5. 前端改动

- [ ] 5.1 修改 `src/types/quiz.ts`：`Question` 新增 `image_url` 字段
- [ ] 5.2 修改 `src/pages/index/index.tsx`：增加「生成图片」开关，传递给 generate API
- [ ] 5.3 修改 `src/pages/quiz/quiz.tsx`：题目有 image_url 时展示配图

## 6. 验证

- [ ] 6.1 运行测试确认通过
- [ ] 6.2 前端编译无报错
