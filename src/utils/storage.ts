import Taro from '@tarojs/taro'
import type { HistoryItem, QuizProgress } from '../types/quiz'

const HISTORY_KEY = 'learning_history'
const MAX_HISTORY = 50
const PROGRESS_KEY = 'active_quiz_progress'

export function saveHistory(item: HistoryItem): void {
  const list = getHistory().filter(existing => existing.session_id !== item.session_id)
  list.unshift(item)
  if (list.length > MAX_HISTORY) list.pop()
  Taro.setStorageSync(HISTORY_KEY, JSON.stringify(list))
}

export function deleteHistory(sessionId: string): HistoryItem[] {
  const list = getHistory().filter(item => item.session_id !== sessionId)
  Taro.setStorageSync(HISTORY_KEY, JSON.stringify(list))
  return list
}

export function saveQuizProgress(progress: QuizProgress): void {
  Taro.setStorageSync(PROGRESS_KEY, JSON.stringify(progress))
}

export function getQuizProgress(): QuizProgress | null {
  try {
    const raw = Taro.getStorageSync(PROGRESS_KEY)
    return raw ? JSON.parse(raw) : null
  } catch {
    return null
  }
}

export function clearQuizProgress(): void {
  Taro.removeStorageSync(PROGRESS_KEY)
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
