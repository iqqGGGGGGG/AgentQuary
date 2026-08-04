import Taro from '@tarojs/taro'
import type { GenerateResponse, ReportRequest, ReportResponse, ExampleTopic } from '../types/quiz'

const BASE_URL = (process.env.TARO_APP_API_BASE_URL || 'http://127.0.0.1:8000').replace(/\/$/, '')

async function request<T>(method: 'GET' | 'POST', path: string, data?: unknown): Promise<T> {
  try {
    const res = await Taro.request({
      url: `${BASE_URL}${path}`,
      method,
      data,
      header: { 'Content-Type': 'application/json' },
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
}
