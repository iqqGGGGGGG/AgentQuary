<!--
 * @Author: Qiqi Gao
 * @Date: 2026-07-20 15:10:58
 * @LastEditors: Do not edit
 * @LastEditTime: 2026-07-20 15:10:58
 * @FilePath: \AgentQuary\doc\1784443177336-ai-quiz-challenge-tech-plan.md
-->
# AI 泛知识问答闯关产品 - 技术方案设计文档 (V3 最终版)

## 1. 技术选型 (已全部确认)

### 前端技术栈

| 类别 | 技术方案 | 说明 |
|------|----------|------|
| 框架 | **Taro 4.x + React + TypeScript** | 跨端能力，未来可扩展 H5/APP |
| UI 组件库 | **NutUI (Taro 版)** | 按钮/卡片/弹窗/进度条/Toast |
| 请求库 | **Taro.request** | 框架内置，无需额外依赖 |
| 构建工具 | **Taro CLI (Webpack 5)** | `taro build --type weapp`，Taro CLI 内置 Webpack |
| 样式方案 | **SCSS** | NutUI 主题变量 + 自定义样式 |
| 存储 | **MySQL + Taro.setStorageSync** | 登录用户云端 MySQL，未登录本地缓存 |
| IDE | **VS Code + 微信开发者工具** | VS Code 写代码，微信开发者工具预览调试 |

### 后端技术栈

| 类别 | 技术方案 | 说明 |
|------|----------|------|
| 框架 | **Python FastAPI** | 异步高性能，自带 Swagger 文档 |
| AI 编排 | **LangChain** | PromptTemplate + JsonOutputParser + Pydantic 自动校验 |
| AI 模型 | **小米 MiMo 2.5 Pro** | `https://token-plan-cn.xiaomimimo.com/v1/chat/completions`, model: `mimo-2.5-pro` |
| 配置管理 | **pydantic-settings** | 类型安全的环境变量管理，替代 python-dotenv |
| 数据库 | **MySQL 8.0+** | 关系型数据存储，aiomysql 异步驱动 |
| ORM | **SQLAlchemy 2.0 (async)** | Mapped 类型注解 + async_sessionmaker |
| 服务器 | **uvicorn** | ASGI 服务器，开发用 `--reload` 热重载 |
| 测试 | **pytest + pytest-asyncio + httpx** | pytest 跑测试，httpx.AsyncClient 测试 FastAPI 路由 |
| 日志 | **Python logging** | 内置模块，配置 JSON 格式输出 |

## 2. 系统架构 (不变)

```
┌──────────────────────────────────────────┐
│       Taro 4.x + React 小程序前端         │
│                                          │
│  src/pages/index   → 输入主题，触发生成    │
│  src/pages/quiz    → 逐题作答，本地校验    │
│  src/pages/report  → 查看报告，请求 AI 总结│
│  src/pages/history → 学习记录列表          │
│                                          │
│  状态: React useState/useContext          │
│  存储: 登录→MySQL云端  未登录→本地缓存     │
└─────────────┬────────────────────────────┘
              │ Taro.request (HTTPS)
              ▼
┌──────────────────────────────────────────┐
│    FastAPI + LangChain 后端               │
│                                          │
│  POST /api/login    → 微信登录/注册       │
│  POST /api/generate → chain_generate     │
│  POST /api/report   → chain_report       │
│  GET  /api/examples → 返回示例主题        │
│  /api/user/*        → 用户资料/历史记录   │
│                                          │
│  LangChain: PromptTemplate + JsonParser  │
│  MySQL: 用户 + 学习记录持久化             │
└──────┬──────────────────┬────────────────┘
       │                  │
       ▼                  ▼
┌─────────────┐  ┌────────────────────────┐
│ MySQL 8.0+  │  │  MiMo 2.5 Pro API     │
│ aiomysql    │  │  (小米官方)            │
│ users表     │  │  model: mimo-2.5-pro   │
│ records表   │  └────────────────────────┘
└─────────────┘
```

## 3. 前端项目结构 (Taro 4.x)

```
AgentQuary/
├── src/
│   ├── app.ts                    # 入口：globalData 定义
│   ├── app.config.ts             # 页面路由 + 窗口配置
│   ├── app.scss                  # 全局样式 (NutUI 主题变量)
│   │
│   ├── pages/
│   │   ├── index/                # 首页
│   │   │   ├── index.tsx
│   │   │   ├── index.config.ts   # 页面独立导航栏配置
│   │   │   └── index.scss
│   │   ├── quiz/                 # 答题闯关页
│   │   │   ├── quiz.tsx
│   │   │   ├── quiz.config.ts
│   │   │   └── quiz.scss
│   │   ├── report/               # 学习报告页
│   │   │   ├── report.tsx
│   │   │   ├── report.config.ts
│   │   │   └── report.scss
│   │   └── history/              # 学习记录页
│   │       ├── history.tsx
│   │       ├── history.config.ts
│   │       └── history.scss
│   │
│   ├── components/               # 可复用组件
│   │   ├── QuizOption/           # 答题选项卡片
│   │   │   ├── index.tsx
│   │   │   └── index.scss
│   │   ├── ProgressBar/          # 答题进度条
│   │   │   ├── index.tsx
│   │   │   └── index.scss
│   │   └── ResultCard/           # 结果报告卡片
│   │       ├── index.tsx
│   │       └── index.scss
│   │
│   ├── services/
│   │   └── api.ts                # 后端 API 调用封装 (Taro.request)
│   │
│   ├── types/
│   │   └── quiz.ts               # TypeScript 类型定义 (与后端对应)
│   │
│   └── utils/
│       ├── storage.ts            # 本地存储操作封装
│       └── format.ts             # 时间格式化等工具函数
│
├── config/                       # Taro 编译配置
│   ├── index.ts                  # 通用配置
│   ├── dev.ts                    # 开发环境
│   └── prod.ts                   # 生产环境
│
├── project.config.json           # 微信小程序项目配置
├── package.json
├── tsconfig.json
├── babel.config.js (或 .ts)
├── .eslintrc.js
│
└── server/                       # 后端代码 (独立目录)
    ├── main.py
    ├── config.py
    ├── requirements.txt
    ├── .env / .env.example
    ├── routers/
    ├── chains/                   # LangChain chains (替代 services/)
    ├── models/
    └── tests/
```

## 4. TypeScript 类型定义 (src/types/quiz.ts)

前后端数据结构对齐，减少联调错误：

```typescript
// 题目类型
export type QuestionType = 'single_choice' | 'true_false'

// 单道题目
export interface Question {
  id: number
  type: QuestionType
  question: string
  options: string[]
  answer: number        // 正确选项索引 (0-based)
  explanation: string
}

// /api/generate 响应
export interface GenerateResponse {
  session_id: string
  topic: string
  questions: Question[]
}

// /api/generate 请求
export interface GenerateRequest {
  content: string
  question_count?: number   // 默认 10
}

// 用户单题答题记录
export interface UserAnswer {
  question_id: number
  selected: number          // 用户选择的索引，-1 表示跳过
  is_correct: boolean
}

// 答题结果 (前端计算 + 传递给报告页)
export interface QuizResult {
  session_id: string
  topic: string
  questions: Question[]
  user_answers: UserAnswer[]
  start_time: number        // Date.now() 时间戳
  end_time: number
  duration_seconds: number
  correct_count: number
  total_count: number
  accuracy: number           // 0.0-1.0
}

// /api/report 请求
export interface ReportRequest {
  topic: string
  questions: Question[]
  user_answers: number[]     // 每题选择的索引，-1 跳过
  duration_seconds: number
}

// /api/report 响应
export interface ReportResponse {
  accuracy: number
  correct_count: number
  total_count: number
  mastered: string[]
  weak: string[]
  summary: string
  encouragement: string
}

// 示例主题
export interface ExampleTopic {
  id: number
  title: string
  category: string
  description: string
}

// 历史记录条目
export interface HistoryItem {
  id?: number              // 云端记录 ID（登录后有）
  session_id: string
  topic: string
  timestamp: number
  accuracy: number
  total_questions: number
  correct_count: number
  duration_seconds: number
  summary?: string
}

// 登录请求
export interface LoginRequest {
  code: string
}

// 登录响应
export interface LoginResponse {
  openid: string
  nickname: string
  avatar_url?: string
  is_new: boolean
}

// 用户资料
export interface UserProfile {
  openid: string
  nickname: string
  avatar_url?: string
  created_at: string
}

// 用户统计
export interface UserStats {
  total_quizzes: number
  total_questions: number
  avg_accuracy: number
  best_streak: number
  learning_days: number
}
```

## 5. 后端 API 设计 (不变，仅补充)

### 5.1 POST /api/generate

**请求**:
```python
class GenerateRequest(BaseModel):
    content: str               # 1-2000字
    question_count: int = 10   # 5-20
```

**响应**:
```python
class GenerateResponse(BaseModel):
    session_id: str
    topic: str
    questions: list[Question]
```

**后端处理 (LangChain chain)**:
1. 校验 content 非空，长度 1-2000 字符
2. question_count 限制 5-20
3. 调用 `chain_generate.invoke({"content": ..., "count": ...})`
   - ChatPromptTemplate 拼接 system + user prompt
   - ChatOpenAI 调用 MiMo API (60s timeout)
   - JsonOutputParser 解析 + Pydantic 自动校验
   - 校验失败自动重试 (max_retries=1)
4. 生成 UUID4 session_id，返回

### 5.2 POST /api/report

**请求**:
```python
class ReportRequest(BaseModel):
    topic: str
    questions: list[dict]
    user_answers: list[int]    # 索引数组，-1 表示跳过
    duration_seconds: int
```

**响应**:
```python
class ReportResponse(BaseModel):
    accuracy: float
    correct_count: int
    total_count: int
    mastered: list[str]
    weak: list[str]
    summary: str
    encouragement: str
```

**后端处理 (LangChain chain)**:
1. 后端独立计算 accuracy / correct_count / mastered / weak (不信任前端数据)
2. 调用 `chain_report.invoke({...})` — 自动 prompt + parse + validate
3. 合并统计数据 + AI 生成的 summary/encouragement
4. **降级**: chain 抛出异常时返回默认 summary / encouragement，不阻断

### 5.3 GET /api/examples

返回硬编码的 10 个示例主题，无需 AI。

## 6. 前端核心实现设计

### 6.1 状态管理策略

**不用 Redux/Zustand**，MVP 阶段用 React 原生方式：

| 数据 | 管理方式 | 生命周期 |
|------|----------|----------|
| 当前题目 | `app.ts` globalData + 页面间跳转传参 | 单次学习 |
| 答题状态 | quiz 页面 `useState` | 页面内 |
| 答题结果 | `app.ts` globalData | quiz → report 传递 |
| 历史记录 | 登录→MySQL云端 / 未登录→`Taro.setStorageSync` | 永久 |
| 用户信息 | 登录后缓存 openid + 本地存储 | 永久 |
| 示例主题 | index 页面 `useState` | 页面内 |

### 6.2 路由配置 (app.config.ts)

```typescript
export default defineAppConfig({
  pages: [
    'pages/index/index',
    'pages/quiz/quiz',
    'pages/report/report',
    'pages/history/history',
  ],
  window: {
    navigationBarTitleText: '知识闯关',
    navigationBarBackgroundColor: '#6C5CE7',
    navigationBarTextStyle: 'white',
    backgroundColor: '#F8F9FE',
  },
})
```

### 6.3 API 服务层 (src/services/api.ts)

```typescript
import Taro from '@tarojs/taro'
import type { GenerateRequest, GenerateResponse, ReportRequest, ReportResponse, ExampleTopic, LoginResponse, UserProfile, UserStats, HistoryItem } from '../types/quiz'
import { getOpenid } from '../utils/auth'

const BASE_URL = 'http://localhost:8000'  // 开发时，生产环境通过 config 切换

function request<T>(method: 'GET' | 'POST' | 'PUT' | 'DELETE', path: string, data?: any): Promise<T> {
  const openid = getOpenid()
  return new Promise((resolve, reject) => {
    Taro.request({
      url: `${BASE_URL}${path}`,
      method,
      data,
      header: {
        'Content-Type': 'application/json',
        ...(openid ? { 'X-User-Openid': openid } : {}),
      },
      timeout: 90000,
      success(res) {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data as T)
        } else {
          reject(new Error(res.data?.detail || `请求失败 (${res.statusCode})`))
        }
      },
      fail() {
        reject(new Error('网络请求失败，请检查网络连接'))
      }
    })
  })
}

export const api = {
  // 核心功能
  generate: (content: string, count = 10) =>
    request<GenerateResponse>('POST', '/api/generate', { content, question_count: count }),

  report: (data: ReportRequest) =>
    request<ReportResponse>('POST', '/api/report', data),

  examples: () =>
    request<{ examples: ExampleTopic[] }>('GET', '/api/examples'),

  // 用户系统
  login: (code: string) =>
    request<LoginResponse>('POST', '/api/login', { code }),

  getProfile: () =>
    request<UserProfile>('GET', '/api/user/profile'),

  updateProfile: (data: { nickname?: string; avatar_url?: string }) =>
    request<UserProfile>('PUT', '/api/user/profile', data),

  getStats: () =>
    request<UserStats>('GET', '/api/user/stats'),

  saveHistory: (data: any) =>
    request<HistoryItem>('POST', '/api/user/history', data),

  getHistory: () =>
    request<{ items: HistoryItem[]; total: number }>('GET', '/api/user/history'),

  deleteHistory: (id: number) =>
    request<{ detail: string }>('DELETE', `/api/user/history/${id}`),
}
```

### 6.4 本地存储封装 (src/utils/storage.ts)

未登录用户的学习记录仍使用本地缓存，登录后自动切换为云端 MySQL。

```typescript
import Taro from '@tarojs/taro'
import type { HistoryItem } from '../types/quiz'
import { getOpenid } from './auth'

const HISTORY_KEY = 'learning_history'
const MAX_HISTORY = 50

export function saveHistory(item: HistoryItem): void {
  const list = getHistory()
  list.unshift(item)
  if (list.length > MAX_HISTORY) list.pop()
  Taro.setStorageSync(HISTORY_KEY, JSON.stringify(list))
}

export function getHistory(): HistoryItem[] {
  try {
    const raw = Taro.getStorageSync(HISTORY_KEY)
    return raw ? JSON.parse(raw) : []
  } catch {
    return []
  }
}

export function clearHistory(): void {
  Taro.removeStorageSync(HISTORY_KEY)
}
```

**登录用户**的历史记录通过 `api.saveHistory()` 和 `api.getHistory()` 操作云端 MySQL，不再写入本地存储。

### 6.5 globalData 管理 (src/app.ts)

```typescript
import { PropsWithChildren } from 'react'
import type { GenerateResponse, QuizResult } from './types/quiz'
import './app.scss'

// globalData 通过模块级变量实现，各页面 import 使用
let currentQuiz: GenerateResponse | null = null
let quizResult: QuizResult | null = null

export function setCurrentQuiz(data: GenerateResponse | null) { currentQuiz = data }
export function getCurrentQuiz() { return currentQuiz }

export function setQuizResult(data: QuizResult | null) { quizResult = data }
export function getQuizResult() { return quizResult }

function App({ children }: PropsWithChildren) {
  return children
}

export default App
```

## 7. AI Prompt 工程 (LangChain ChatPromptTemplate 版)

Prompt 以 `ChatPromptTemplate` 形式定义在 chain 文件中。`JsonOutputParser` 会自动在 system prompt 末尾注入 `{format_instructions}`（包含 JSON schema 描述），无需手动编写输出格式说明。

### 7.1 题目生成 System Prompt

```
你是一个专业的知识出题助手。你的任务是根据用户提供的内容，生成一组用于学习和记忆的问答题。

规则：
1. 题目围绕内容中的核心知识点，难度从简单到深入
2. 题型随机混合使用：
   - single_choice: 单选题，必须有恰好4个选项
   - true_false: 判断题，必须有恰好2个选项 ["正确", "错误"]
3. 每道题必须附带简明讲解(explanation)，50字以内
4. 避免重复题目、避免选项明显错误、避免题目与内容无关

{format_instructions}
```

**注意**: `{format_instructions}` 由 `JsonOutputParser.get_format_instructions()` 自动注入，包含 Pydantic schema 的 JSON 结构描述。实现时 prompt 模板中必须包含此占位符。

### 7.2 题目生成 User Prompt

```
请根据以下内容生成 {count} 道问答题：

---
{content}
---
```

### 7.3 报告生成 System Prompt

```
你是一个学习辅导助手。根据用户的答题结果，生成简洁的学习报告。

规则：
1. 语言自然、口语化、有鼓励性
2. 不要使用过于正式的教育术语

{format_instructions}
```

### 7.4 报告生成 User Prompt

```
答题主题：{topic}
正确率：{accuracy}%
共 {total} 题，答对 {correct} 题

答对的题目：
{correct_list}

答错的题目（含用户答案和正确答案）：
{wrong_list}

请根据以上信息生成学习总结和鼓励语。
```

## 8. 后端项目结构 (LangChain 版)

```
server/
├── main.py                  # FastAPI 入口 + CORS + logging 配置 + lifespan init_db
├── config.py                # pydantic-settings 配置 (AI + MySQL + 微信)
├── database.py              # SQLAlchemy async engine + session + init_db
├── auth.py                  # get_current_user 鉴权依赖
├── requirements.txt
├── requirements-dev.txt     # 开发依赖 (pytest 等)
├── .env / .env.example
├── routers/
│   ├── __init__.py
│   ├── generate.py          # POST /api/generate
│   ├── report.py            # POST /api/report
│   ├── examples.py          # GET /api/examples
│   ├── auth.py              # POST /api/login (微信登录)
│   └── user.py              # 用户资料 + 统计 + 学习记录 CRUD
├── chains/                  # LangChain chains
│   ├── __init__.py
│   ├── llm.py               # ChatOpenAI 实例
│   ├── generate_chain.py    # 题目生成 chain
│   └── report_chain.py      # 报告生成 chain
├── models/
│   ├── __init__.py
│   ├── schemas.py           # Pydantic 模型 (含 User/History schemas)
│   └── orm.py               # SQLAlchemy ORM 模型 (User, LearningRecord)
├── services/
│   ├── __init__.py
│   └── content.py           # 内容处理服务
└── tests/
    ├── conftest.py           # pytest fixtures (FastAPI TestClient + DB session)
    ├── test_generate.py      # /api/generate 测试
    ├── test_report.py        # /api/report 测试
    ├── test_auth.py          # /api/login 测试
    ├── test_user.py          # /api/user/* 测试
    └── test_content.py       # 内容处理测试
```

**说明**: `prompts/` 目录不再需要。Prompt 模板以 `ChatPromptTemplate` 形式直接定义在 chain 文件中，与输出解析器和模型组成 LCEL chain。

### 8.1 配置管理 (config.py) — pydantic-settings

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    ai_base_url: str = "https://token-plan-cn.xiaomimimo.com/v1"
    ai_model: str = "mimo-v2.5-pro"
    ai_api_key: str

    db_host: str = "localhost"
    db_port: int = 3306
    db_user: str = "root"
    db_password: str = ""
    db_name: str = "agentquary"

    wx_appid: str = ""
    wx_secret: str = ""
    dev_mode: bool = True

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    @property
    def db_url(self) -> str:
        return f"mysql+aiomysql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}?charset=utf8mb4"

settings = Settings()
```

**`.env.example`**:
```
AI_API_KEY=your-mimo-api-key-here
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=
DB_NAME=agentquary
WX_APPID=
WX_SECRET=
DEV_MODE=true
```

**优势**: 类型校验 + 缺少必填字段直接报错 + 自动加载 .env。

### 8.2 LLM 实例 (chains/llm.py)

```python
from langchain_openai import ChatOpenAI
from config import settings

llm = ChatOpenAI(
    model=settings.ai_model,
    openai_api_base=settings.ai_base_url,
    openai_api_key=settings.ai_api_key,
    temperature=0.7,
    timeout=60,
    max_retries=1,
)
```

### 8.2 题目生成 Chain (chains/generate_chain.py)

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from .llm import llm

class QuestionSchema(BaseModel):
    id: int
    type: str       # "single_choice" | "true_false"
    question: str
    options: list[str]
    answer: int
    explanation: str

class QuizOutputSchema(BaseModel):
    topic: str
    questions: list[QuestionSchema]

parser = JsonOutputParser(pydantic_object=QuizOutputSchema)

system_prompt = """你是一个专业的知识出题助手...（完整 prompt 见 §7.1）
{format_instructions}"""

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "请根据以下内容生成 {count} 道问答题：\n\n---\n{content}\n---"),
])

chain_generate = prompt | llm | parser
```

**调用方式**:
```python
result = await chain_generate.ainvoke({
    "content": "太阳系基础知识",
    "count": 10,
    "format_instructions": parser.get_format_instructions(),
})
# result = {"topic": "...", "questions": [...]}  ← 已自动校验 Pydantic schema
```

**LangChain 自动处理**:
- `ChatPromptTemplate` — 模板变量注入 + format_instructions 注入
- `ChatOpenAI` — HTTP 调用 + 超时 + 重试
- `JsonOutputParser(pydantic_object=...)` — JSON 解析 + Pydantic 校验 + 格式说明注入 prompt

### 8.3 报告生成 Chain (chains/report_chain.py)

```python
class ReportOutputSchema(BaseModel):
    summary: str = Field(min_length=20, max_length=200)
    encouragement: str = Field(min_length=5, max_length=50)

parser = JsonOutputParser(pydantic_object=ReportOutputSchema)

prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个学习辅导助手...{format_instructions}"),
    ("human", "答题主题：{topic}\n正确率：{accuracy}%\n..."),
])

chain_report = prompt | llm | parser
```

### 8.5 requirements.txt

```
fastapi>=0.115.0
uvicorn[standard]>=0.34.0
langchain>=0.3.0
langchain-openai>=0.3.0
langchain-core>=0.3.0
pydantic>=2.0
pydantic-settings>=2.0
httpx>=0.28.0
sqlalchemy[asyncio]>=2.0
aiomysql>=0.2.0
pymysql>=1.1.0
```

**`requirements-dev.txt`** (开发依赖):
```
-r requirements.txt
pytest>=8.0
pytest-asyncio>=0.24.0
httpx>=0.28.0
```

**依赖说明**:
- `langchain` — 核心框架
- `langchain-openai` — `ChatOpenAI` (兼容 MiMo 的 OpenAI 格式 API)
- `langchain-core` — `ChatPromptTemplate`, `JsonOutputParser`, LCEL
- `pydantic` — 数据校验
- `pydantic-settings` — 类型安全的环境变量配置 (替代 python-dotenv)
- `fastapi` + `uvicorn` — Web 框架 + ASGI 服务器
- `sqlalchemy[asyncio]` — 异步 ORM，MySQL 数据持久化
- `aiomysql` — MySQL 异步驱动
- `pymysql` — MySQL 同步驱动（备用）
- `httpx` — HTTP 客户端（微信登录 + 测试用）
- `pytest` + `pytest-asyncio` — 测试 (仅开发依赖)

## 9. 各页面交互流程 (细化)

### 9.1 首页 (pages/index)

```
onLoad:
  → api.examples() 获取示例主题
  → setData({ examples })

用户操作:
  1. 输入框输入内容
  2. 或点击示例卡片 → 自动填入输入框
  3. 点击"开始闯关"
     → 校验: content.trim().length > 0，否则 Toast 提示
     → Taro.showLoading({ title: '正在生成题目...' })
     → api.generate(content)
     → Taro.hideLoading()
     → 成功: setCurrentQuiz(data) → Taro.navigateTo({ url: '/pages/quiz/quiz' })
     → 失败: Taro.showModal({ title: '生成失败', content: error.message })
       → 用户点击"重试" → 重新调用 generate
```

### 9.2 答题页 (pages/quiz)

```
onLoad:
  → const quiz = getCurrentQuiz()
  → if (!quiz) navigateBack (防御性编程)
  → setState({ questions: quiz.questions, currentIndex: 0, status: 'selecting' })
  → 记录 startTime = Date.now()

状态机:
  SELECTING → 用户选择选项 → setState({ selectedOption })
  SELECTING → 点击"确认答案" →
     → 比对: isCorrect = (selected === questions[currentIndex].answer)
     → 记录: userAnswers.push({ question_id, selected, is_correct })
     → setState({ status: 'feedback', isCorrect })

  FEEDBACK → 点击"下一题" →
     → if (currentIndex < total - 1):
         setState({ currentIndex++, status: 'selecting', selectedOption: -1 })
     → if (currentIndex === total - 1):  // 最后一题
         → 计算结果
         → setQuizResult({ session_id, topic, questions, user_answers, ... })
         → Taro.redirectTo({ url: '/pages/report/report' })

防重复提交:
  → 确认按钮 disabled = (status !== 'selecting' || selectedOption === -1)
```

### 9.3 报告页 (pages/report)

```
onLoad:
  → const result = getQuizResult()
  → if (!result) navigateBack
  → 先展示本地统计数据 (accuracy, correct_count, mastered, weak) — 立即可见
  → 同时异步调用 api.report(...)
     → 成功: 更新 summary, encouragement
     → 失败: 使用默认文案，不阻断
  → 保存历史:
     → 已登录: api.saveHistory({...}) 写入 MySQL
     → 未登录: saveHistory({...}) 写入本地缓存

"再来一关":
  → Taro.navigateBack({ url: '/pages/index/index' })  // 回首页重新输入

"回到首页":
  → Taro.switchTab 或 navigateBack
```

### 9.4 历史记录页 (pages/history)

```
onShow:
  → const history = getHistory()
  → setData({ history })

点击某条记录:
  → 展示摘要 (可展开详情，或跳转到报告页用缓存数据)
```

## 10. 本地开发调试方案

### 10.1 后端

```bash
cd server
pip install -r requirements-dev.txt
cp .env.example .env       # 填入 AI_API_KEY + MySQL 配置
uvicorn main:app --reload --host 0.0.0.0 --port 8000
# 启动时自动建表 (init_db)
# Swagger: http://localhost:8000/docs

# 运行测试
pytest tests/ -v
```

**MySQL 准备**:
```sql
CREATE DATABASE IF NOT EXISTS agentquary CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 10.2 前端

```bash
# 初始化 Taro 项目 (首次)
npx @tarojs/cli@4 init AgentQuary --template default --css sass --framework react --typescript

# 或在已有目录安装依赖
npm install

# 开发编译 (微信小程序)
npm run dev:weapp

# 微信开发者工具打开项目目录，即可预览
```

### 10.3 前后端联调

1. 微信开发者工具 → 设置 → 项目设置 → 勾选「不校验合法域名」
2. `src/services/api.ts` 中 BASE_URL 用电脑局域网 IP: `http://192.168.x.x:8000`
3. 真机调试: 微信开发者工具「真机调试」模式，或同一局域网

### 10.4 上线前配置

小程序后台 → 开发管理 → 服务器域名 → request 合法域名添加后端域名 (HTTPS)

## 11. 分阶段开发计划

### Phase 1: 后端核心 (LangChain chain + FastAPI)

1. 创建 `server/` 目录
2. 创建 `requirements.txt` (含 langchain/langchain-openai/langchain-core)
3. 创建 `config.py` (pydantic-settings) + `.env.example`
4. 实现 `models/schemas.py` — Pydantic 模型 (请求/响应 + AI 输出校验)
5. 实现 `chains/llm.py` — ChatOpenAI 实例 (连接 MiMo API)
6. 实现 `chains/generate_chain.py` — 题目生成 chain (prompt + llm + parser)
7. 实现 `chains/report_chain.py` — 报告生成 chain
8. 实现 `routers/examples.py` — GET /api/examples (硬编码)
9. 实现 `routers/generate.py` — POST /api/generate (调 chain + 降级)
10. 实现 `routers/report.py` — POST /api/report (调 chain + 降级)
11. 实现 `main.py` — CORS + logging 配置 + 路由挂载
12. 编写 `tests/conftest.py` + `test_generate.py` + `test_report.py` (pytest)
13. Swagger UI 手动测试 + `pytest tests/ -v` 自动测试

### Phase 2: Taro 项目初始化 + 首页

14. `npx @tarojs/cli@4 init` 初始化项目
15. 安装 NutUI: `npm install @nutui/nutui-taro`
16. 配置 NutUI 按需引入 (babel 插件)
17. 创建 `src/types/quiz.ts` — 类型定义
18. 创建 `src/services/api.ts` — API 封装 (Taro.request)
19. 创建 `src/utils/storage.ts` — 存储封装
20. 重写 `src/app.ts` + `src/app.config.ts` — globalData + 路由
21. 实现 `src/pages/index/` — 输入框 + 示例主题 + 开始按钮

### Phase 3: 答题页 + 报告页 (跑通核心流程)

22. 实现 `src/pages/quiz/` — 逐题作答 + 本地校验 + 即时反馈
23. 实现 `src/components/QuizOption/` — 选项卡片组件
24. 实现 `src/components/ProgressBar/` — 进度条组件
25. 实现 `src/pages/report/` — 结果展示 + AI 总结
26. 实现 `src/components/ResultCard/` — 结果卡片组件
27. 前后端联调: 输入 → 生成 → 答题 → 报告 (完整流程)

### Phase 4: 历史记录 + 体验优化

27. 实现 `src/pages/history/` — 学习记录列表
28. 添加 loading 状态、错误处理、空状态 UI
29. 优化样式: 动漫风格配色、圆角卡片、动画反馈
30. 删除原有 `pages/` 目录和模板代码

## 12. 关键技术决策记录

| 决策 | 选择 | 原因 |
|------|------|------|
| 前端框架 | Taro 4.x + React + TS | 跨端能力，类型安全，社区活跃 |
| 前端构建 | Taro CLI (内置 Webpack) | 官方推荐，开箱即用 |
| 前端请求 | Taro.request | 框架内置，零额外依赖 |
| UI 库 | NutUI (Taro) | 减少基础组件开发量，风格统一 |
| AI 编排 | LangChain | PromptTemplate + JsonOutputParser 自动校验重试 |
| 数据库 | MySQL 8.0+ | 关系型数据持久化，生产环境可用，支持并发和远程访问 |
| ORM | SQLAlchemy 2.0 async | 类型安全，异步兼容 FastAPI，切换数据库只需改连接字符串 |
| 登录鉴权 | 微信 wx.login + openid | 小程序原生登录，用户无感知，无需额外注册 |
| 后端配置 | pydantic-settings | 类型安全 + 缺字段报错 + 自动加载 .env |
| 后端测试 | pytest + pytest-asyncio | Python 标准测试框架，FastAPI 官方推荐 |
| 后端日志 | Python logging | 零依赖，内置模块 |
| 答案下发 | generate 返回含答案 | 学习产品不防作弊，省存储 |
| 报告混合 | 本地统计 + AI 写文案 | 统计可靠，AI 只做润色 |
| 状态管理 | React useState + 模块变量 | MVP 无需 Redux |
| 报告降级 | 默认文案 | 不因 AI 故障阻断体验 |
| 未登录存储 | Taro.setStorageSync | 低门槛体验，登录后迁移云端 |

## 13. 风险与应对

| 风险 | 概率 | 应对 |
|------|------|------|
| MiMo 不支持 response_format=json_object | 中 | LangChain JsonOutputParser 在 prompt 注入格式说明 + 自动重试 |
| AI 生成题目质量低 | 中 | prompt 迭代 + Pydantic schema 校验过滤 |
| AI 响应超时 (>60s) | 低 | ChatOpenAI timeout=60 + max_retries=1 |
| LangChain 版本兼容 | 低 | 锁定 langchain/langchain-openai/langchain-core 版本 |
| Taro 4.x 兼容性问题 | 低 | 使用最新 stable 版，参考官方示例 |
| NutUI 组件与设计稿不匹配 | 中 | 基础组件用 NutUI，自定义区域手写 SCSS |
| MySQL 连接断开 | 低 | pool_pre_ping=True 自动断线重连 |
| 微信登录接口异常 | 低 | dev_mode 开关，开发环境跳过微信验证 |

## 14. 开放问题 (实施时确认)

1. **MiMo response_format 支持**: 第一次调用即可确认
2. **MiMo token/并发限制**: 影响题目数量和并发能力
3. **UI 视觉设计稿**: 偏动漫风格的具体配色/插画资源，Phase 4 详细设计
4. **Taro 4.x 初始化模板**: 确认 `@tarojs/cli@4` 的最新 init 命令参数
