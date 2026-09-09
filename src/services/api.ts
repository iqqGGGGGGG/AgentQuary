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
  LevelInfo,
  LearningCalendar,
  AchievementList,
  WrongQuestionList,
  TrendsData,
  DomainsData,
  PreferencesData,
  GoalData,
  HistorySaveResult,
} from '../types/quiz'
import { getAccessToken } from '../store/user'

const BASE_URL = (process.env.TARO_APP_API_BASE_URL || 'http://127.0.0.1:8000').replace(/\/$/, '')

async function request<T>(method: 'GET' | 'POST' | 'PUT' | 'DELETE', path: string, data?: unknown, timeout = 150000): Promise<T> {
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
      timeout,
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
  generate: (content: string, count = 10, excludedQuestions: string[] = []) =>
    request<GenerateResponse>('POST', '/api/generate', {
      content,
      question_count: count,
      excluded_questions: excludedQuestions,
    }, 300000),

  report: (data: ReportRequest) =>
    request<ReportResponse>('POST', '/api/report', data, 300000),

  examples: () =>
    request<{ examples: ExampleTopic[] }>('GET', '/api/examples'),

  login: (code: string) =>
    request<LoginResponse>('POST', '/api/login', { code }),

  getProfile: () =>
    request<UserProfile>('GET', '/api/user/profile'),

  updateProfile: (data: { nickname?: string; avatar_url?: string }) =>
    request<UserProfile>('PUT', '/api/user/profile', data),

  uploadAvatar: (data: { data: string; file_type: 'png' | 'jpg' | 'jpeg' | 'webp' }) =>
    request<UserProfile>('POST', '/api/user/profile/avatar', data),

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
    request<HistorySaveResult>('POST', '/api/user/history', data),

  getHistory: () =>
    request<{ items: HistoryItem[]; total: number }>('GET', '/api/user/history'),

  deleteHistory: (id: number) =>
    request<{ detail: string }>('DELETE', `/api/user/history/${id}`),

  getLevel: () =>
    request<LevelInfo>('GET', '/api/user/level'),

  getLearningCalendar: (year: number, month: number) =>
    request<LearningCalendar>('GET', `/api/user/learning-calendar?year=${year}&month=${month}`),

  getAchievements: () =>
    request<AchievementList>('GET', '/api/user/achievements'),

  getWrongQuestions: (limit = 50) =>
    request<WrongQuestionList>('GET', `/api/user/wrong-questions?limit=${limit}`),

  removeWrongQuestion: (recordId: number, questionId: number) =>
    request<{ detail: string }>('DELETE', `/api/user/wrong-questions/${recordId}/${questionId}`),

  getWrongQuiz: (questionId?: number) =>
    request<GenerateResponse>('GET', questionId ? `/api/user/wrong-questions/quiz?question_id=${questionId}` : '/api/user/wrong-questions/quiz'),

  getTrends: (days = 7) =>
    request<TrendsData>('GET', `/api/user/trends?days=${days}`),

  getDomains: () =>
    request<DomainsData>('GET', '/api/user/domains'),

  getPreferences: () =>
    request<PreferencesData>('GET', '/api/user/preferences'),

  updatePreferences: (preferences: string[]) =>
    request<PreferencesData>('PUT', '/api/user/preferences', { preferences }),

  getGoal: () =>
    request<GoalData>('GET', '/api/user/goal'),

  updateGoal: (dailyGoal: number) =>
    request<GoalData>('PUT', '/api/user/goal', { daily_goal: dailyGoal }),
}
