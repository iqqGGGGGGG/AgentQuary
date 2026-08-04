export type QuestionType = 'single_choice' | 'true_false'

export interface Question {
  id: number
  type: QuestionType
  question: string
  options: string[]
  answer: number
  explanation: string
}

export interface GenerateResponse {
  session_id: string
  topic: string
  questions: Question[]
}

export interface GenerateRequest {
  content: string
  question_count?: number
}

export interface UserAnswer {
  question_id: number
  selected: number
  is_correct: boolean
}

export interface QuizResult {
  session_id: string
  topic: string
  questions: Question[]
  user_answers: UserAnswer[]
  start_time: number
  end_time: number
  duration_seconds: number
  correct_count: number
  total_count: number
  accuracy: number
}

export interface ReportRequest {
  topic: string
  questions: Question[]
  user_answers: number[]
  duration_seconds: number
}

export interface ReportResponse {
  accuracy: number
  correct_count: number
  total_count: number
  mastered: string[]
  weak: string[]
  summary: string
  encouragement: string
}

export interface ExampleTopic {
  id: number
  title: string
  category: string
  description: string
}

export interface HistoryItem {
  session_id: string
  topic: string
  timestamp: number
  accuracy: number
  total_questions: number
  correct_count: number
  duration_seconds: number
  quiz?: GenerateResponse
  result?: QuizResult
  summary?: string
}

export interface QuizProgress {
  quiz: GenerateResponse
  current_index: number
  selected_option: number
  status: 'selecting' | 'feedback'
  user_answers: UserAnswer[]
  streak: number
  start_time: number
}

// ── User Types ──

export interface LoginResponse {
  openid: string
  nickname: string
  avatar_url: string | null
  is_new: boolean
}

export interface UserProfile {
  openid: string
  nickname: string
  avatar_url: string | null
  created_at: string
}

export interface UserStats {
  total_quizzes: number
  total_questions: number
  avg_accuracy: number
  best_streak: number
  learning_days: number
}

export interface UserState {
  openid: string | null
  nickname: string
  avatar_url: string | null
  isLoggedIn: boolean
}
