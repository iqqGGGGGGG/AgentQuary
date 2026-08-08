import Taro from '@tarojs/taro'
import type {
  GenerateResponse,
  ReportRequest,
  ReportResponse,
  ExampleTopic,
  LoginResponse,
  UserProfile,
  UserStats,
  HistoryItem,
} from '../types/quiz'
import { getAccessToken } from '../store/user'

const BASE_URL = (process.env.TARO_APP_API_BASE_URL || 'http://127.0.0.1:8000').replace(/\/$/, '')

async function request<T>(method: 'GET' | 'POST' | 'PUT' | 'DELETE', path: string, data?: unknown): Promise<T> {
  const headers: Record<string, string> = { 'Content-Type': 'application/json' }
  const accessToken = getAccessToken()
  if (accessToken) {
    headers.Authorization = `Bearer ${accessToken}`
  }

  try {
    const res = await Taro.request({
      url: `${BASE_URL}${path}`,
      method,
      data,
      header: headers,
      timeout: 150000,
    })
    if (res.statusCode >= 200 && res.statusCode < 300) {
      return res.data as T
    }
    throw new Error((res.data as Record<string, string>)?.detail || `请求失败 (${res.statusCode})`)
  } catch (err) {
    if (err instanceof Error) {
      throw err
    }
    throw new Error('网络请求失败，请检查网络连接')
  }
}

export const api = {
  generate: (content: string, count = 10) =>
    request<GenerateResponse>('POST', '/api/generate', { content, question_count: count }),

  report: (data: ReportRequest) =>
    request<ReportResponse>('POST', '/api/report', data),

  examples: () =>
    request<{ examples: ExampleTopic[] }>('GET', '/api/examples'),

  login: (code: string) =>
    request<LoginResponse>('POST', '/api/login', { code }),

  getProfile: () =>
    request<UserProfile>('GET', '/api/user/profile'),

  updateProfile: (data: { nickname?: string; avatar_url?: string }) =>
    request<UserProfile>('PUT', '/api/user/profile', data),

  getStats: () =>
    request<UserStats>('GET', '/api/user/stats'),

  saveHistory: (data: {
    session_id: string
    topic: string
    accuracy: number
    total_questions: number
    correct_count: number
    duration_seconds: number
    questions?: unknown[]
    user_answers?: unknown[]
    summary?: string
  }) =>
    request<{ id: number; session_id: string }>('POST', '/api/user/history', data),

  getHistory: () =>
    request<{ items: HistoryItem[]; total: number }>('GET', '/api/user/history'),

  deleteHistory: (id: number) =>
    request<{ detail: string }>('DELETE', `/api/user/history/${id}`),
}
