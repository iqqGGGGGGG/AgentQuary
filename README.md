<div align="center">
  <img src="src/assets/mascot/knowledge-robot.png" width="120" alt="AgentQuary 知识机器人">
  <h1>AgentQuary</h1>
  <p>把主题、网页或学习材料转换为一局可完成、可复盘的 AI 知识闯关。</p>
</div>

## 项目简介

AgentQuary 是一个面向微信小程序的 AI 泛知识问答应用。用户可以输入学习主题、公开网页链接，或上传 `.txt` / `.md` 文件；后端调用兼容 OpenAI Responses API 的模型生成题目，前端完成逐题作答、即时反馈、学习报告和历史复盘。

当前版本在原有 MVP 闭环上增加了三栏 TabBar、个人中心、开发态微信登录、MySQL 数据模型、用户统计和学习记录云端写入：

> 输入学习内容 → AI 生成题目 → 逐题闯关 → 即时解析 → 成绩报告 → 本地历史与错题复盘 → 登录用户统计

项目仍处于开发验证阶段。当前身份校验、头像持久化和跨设备历史恢复尚未达到生产可用标准，不能把这一版本等同于完整账号与云同步系统。

## 当前能力

- 支持主题文本、公开网页链接和 `.txt` / `.md` 文件输入。
- 生成单选题与判断题，并校验题目、选项和答案结构。
- 支持逐题作答、即时反馈、答案解析、连续答对统计和中途续玩。
- 自动生成正确率、掌握点、薄弱点和 AI 学习总结。
- 本地历史保留完整题目与报告，支持查看、重试和删除。
- 首页、记录、我的三栏导航，包含统一的普通态与选中态图标。
- 个人中心展示答题次数、答题总数、平均正确率和学习天数。
- 开发模式下可使用模拟 openid；配置微信 AppID/Secret 后可调用 `jscode2session`。
- 登录用户的学习记录可写入 MySQL，并由后端聚合个人统计。
- 服务端包含基础 SSRF 防护、内容类型检查和响应大小限制。
- 支持微信小程序构建、H5 本地预览和无真实模型的 Mock API 演示。

## 技术栈

| 模块 | 技术 |
| --- | --- |
| 微信小程序 / H5 | Taro 4、React 18、TypeScript、SCSS |
| 后端 API | FastAPI、Pydantic 2、Uvicorn |
| AI 调用 | LangChain、OpenAI-compatible Responses API |
| 数据存储 | Taro 本地存储、SQLAlchemy Async、MySQL |
| 测试与构建 | Pytest、TypeScript Compiler、Taro Build |

## 目录结构

```text
AgentQuary/
├─ src/                  # Taro 前端源码
│  ├─ pages/             # 首页、闯关、报告、记录、个人中心
│  ├─ components/        # 答题选项、进度条、结果卡片
│  ├─ services/          # 前端 API 封装
│  ├─ store/             # 闯关与用户状态
│  ├─ utils/             # 本地历史、进度和统计
│  └─ assets/            # TabBar、主题图标与知识机器人素材
├─ server/               # FastAPI 后端
│  ├─ chains/            # 题目和报告生成链
│  ├─ models/            # Pydantic schema 与 SQLAlchemy ORM
│  ├─ routers/           # 生成、报告、登录和用户 API
│  ├─ services/          # 网页抽取与安全校验
│  └─ tests/             # 后端自动化测试
├─ prototypes/           # 产品原型页面
├─ scripts/              # Mock API、静态预览和图标生成脚本
├─ doc/                  # 需求、技术方案和实现状态文档
└─ config/               # Taro 构建配置
```

## 环境要求

- Node.js 18 或更高版本
- npm
- Python 3.10 或更高版本
- MySQL 8.x（运行真实后端时需要）
- 微信开发者工具
- 一个兼容 OpenAI Responses API 的模型服务密钥

## 快速开始

### 1. 安装前端依赖

```powershell
git clone https://github.com/iqqGGGGGGG/AgentQuary.git
cd AgentQuary
npm install
```

### 2. 配置前端 API 地址

复制根目录 `.env.example` 为 `.env`：

```env
TARO_APP_API_BASE_URL=http://127.0.0.1:8000
```

真机调试时，`127.0.0.1` 指向手机自身，需要改为电脑在同一局域网中的 IP，并正确配置小程序合法域名或开发调试选项。

### 3. 准备 MySQL

创建 UTF-8 数据库：

```sql
CREATE DATABASE agentquary CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

后端启动时会根据 SQLAlchemy 模型创建当前缺失的数据表；正式环境仍应补充数据库迁移工具。

### 4. 配置并运行后端

复制 `server/.env.example` 为 `server/.env`，按实际环境填写：

```env
AI_API_KEY=your-api-key

DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your-password
DB_NAME=agentquary

WX_APPID=
WX_SECRET=
DEV_MODE=true
```

模型地址和模型名可通过 `AI_BASE_URL`、`AI_MODEL` 覆盖；默认值见 `server/config.py`。生产或真机微信登录时必须配置 `WX_APPID`、`WX_SECRET` 并设置 `DEV_MODE=false`。

```powershell
cd server
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

启动后可访问：

- API 根地址：`http://127.0.0.1:8000/`
- Swagger：`http://127.0.0.1:8000/docs`

### 5. 运行微信小程序

在项目根目录执行：

```powershell
npm run dev:weapp
```

随后用微信开发者工具导入项目根目录；构建产物位于 `dist/weapp/`。

## H5 本地演示

不接入真实模型时，可以分别启动 Mock API、构建和预览服务：

```powershell
npm run dev:mock-api
npm run build:h5
npm run preview:h5
```

浏览器访问 `http://127.0.0.1:4175/`。

## 常用命令

| 命令 | 作用 |
| --- | --- |
| `npm run dev:weapp` | 监听并编译微信小程序 |
| `npm run build:weapp` | 单次构建微信小程序 |
| `npm run build:h5` | 构建 H5 版本 |
| `npm run preview:h5` | 预览 H5 构建产物 |
| `npm run dev:mock-api` | 启动本地 Mock API |
| `node_modules\.bin\tsc.cmd --noEmit` | TypeScript 类型检查 |
| `python -m pytest -q` | 在 `server` 目录运行后端测试 |
| `powershell -ExecutionPolicy Bypass -File scripts\render-tab-icons.ps1` | 重新生成 TabBar PNG |

## API 概览

| 方法 | 路径 | 用途 |
| --- | --- | --- |
| `GET` | `/api/examples` | 获取首页示例题材 |
| `POST` | `/api/generate` | 根据主题、网页或文本生成题目 |
| `POST` | `/api/report` | 根据答题结果生成学习报告 |
| `POST` | `/api/login` | 微信 code 或开发 code 登录 |
| `GET/PUT` | `/api/user/profile` | 查询或修改个人资料 |
| `GET` | `/api/user/stats` | 获取用户学习统计 |
| `GET/POST` | `/api/user/history` | 查询或保存云端学习记录 |
| `DELETE` | `/api/user/history/{record_id}` | 删除指定云端记录 |

具体请求和响应结构以后端 Swagger 为准。

## 当前验证状态

- TypeScript 类型检查通过。
- 微信小程序构建通过。
- H5 构建通过。
- 后端自动化测试：`35 passed`。
- TabBar 六张 PNG 已验证为 81×81 透明资源，并正确复制到微信构建产物。

## 已知限制

- `X-User-Openid` 当前只是开发期身份传递，客户端可以伪造；生产环境必须改为服务端签发并验证的会话或令牌。
- 个人中心选择的头像目前保存的是小程序临时文件路径，尚未接入对象存储，不保证跨会话或跨设备可用。
- 登录后会把新学习记录写入数据库，但记录页仍以本地历史为主，尚未实现完整的跨设备拉取、合并与冲突处理。
- 数据库使用 `create_all` 初始化，尚未接入 Alembic 等正式迁移机制。
- 真实微信登录、分享卡片和真机网络环境仍需在真实设备上验收。
- 文件解析只支持纯文本，不支持 PDF、Word 和图片 OCR。
- 动态网页、登录墙、反爬页面及复杂正文抽取可能失败。
- 真实模型的稳定性、费用、限流和失败重试仍需持续压测。
- H5 入口体积仍有优化空间。

更完整的实现状态和下一阶段建议见 [MVP 实现状态](doc/MVP实现状态.md)。

## 安全说明

- 不要提交根目录 `.env`、`server/.env` 或任何真实 API Key、微信 Secret、数据库密码。
- 仓库通过 `.gitignore` 排除本地密钥、虚拟环境、依赖目录和构建产物。
- 正式部署前仍需补充可靠鉴权、限流、日志脱敏、出站网络策略、数据库迁移和生产级 CORS 配置。

## 素材许可

- 界面图标来自 [Lucide](https://lucide.dev/)，TabBar 来源说明见 `src/assets/tab-icons/README.md`。
- 知识机器人素材来自 Microsoft Fluent Emoji，许可说明位于 `src/assets/mascot/`。
