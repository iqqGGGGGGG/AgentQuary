import Taro from '@tarojs/taro'
import type { HistoryItem, QuizProgress, UserStats } from '../types/quiz'

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

export function computeLocalStats(): UserStats {
  const history = getHistory()
  if (history.length === 0) {
    return { total_quizzes: 0, total_questions: 0, avg_accuracy: 0, best_streak: 0, learning_days: 0 }
  }

  const totalQuizzes = history.length
  const totalQuestions = history.reduce((sum, item) => sum + item.total_questions, 0)
  const totalCorrect = history.reduce((sum, item) => sum + item.correct_count, 0)
  const avgAccuracy = totalQuestions > 0 ? totalCorrect / totalQuestions : 0

  const bestStreak = history.reduce((max, item) => {
    if (!item.result?.user_answers) return max
    let streak = 0
    let best = 0
    for (const answer of item.result.user_answers) {
      if (answer.is_correct) {
        streak++
        best = Math.max(best, streak)
      } else {
        streak = 0
      }
    }
    return Math.max(max, best)
  }, 0)

  const uniqueDays = new Set(
    history.map(item => {
      const d = new Date(item.timestamp)
      return `${d.getFullYear()}-${d.getMonth()}-${d.getDate()}`
    })
  )

  return {
    total_quizzes: totalQuizzes,
    total_questions: totalQuestions,
    avg_accuracy: avgAccuracy,
    best_streak: bestStreak,
    learning_days: uniqueDays.size,
  }
}
