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
  source_content?: string
  search_used?: boolean
  needs_clarification?: boolean
  domain_options?: string[]
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
  source_content?: string
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
  access_token: string
  token_type: 'bearer'
  expires_in: number
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
  access_token: string | null
  nickname: string
  avatar_url: string | null
  isLoggedIn: boolean
}

// ── Level Types ──

export interface LevelInfo {
  xp: number
  level: number
  level_name: string
  current_level_xp: number
  next_level_xp: number
  progress: number
}

// ── Calendar Types ──

export interface CalendarDay {
  date: string
  count: number
  high: boolean
}

export interface LearningCalendar {
  year: number
  month: number
  days: CalendarDay[]
  current_streak: number
}

// ── Achievement Types ──

export interface Achievement {
  id: number
  key: string
  name: string
  description: string
  icon: string
  condition_type: string
  condition_value: number
  sort_order: number
  unlocked: boolean
  unlocked_at: string | null
}

export interface AchievementList {
  items: Achievement[]
  unlocked_count: number
  total_count: number
}

// ── Wrong Question Types ──

export interface WrongQuestion {
  record_id: number
  question_id: number
  topic: string
  question: string
  your_answer: string
  correct_answer: string
  explanation: string
  created_at: string
}

export interface WrongQuestionList {
  items: WrongQuestion[]
  total: number
  topic_count: number
}

// ── Trends Types ──

export interface TrendDay {
  date: string
  count: number
  accuracy: number
}

export interface TrendsData {
  days: TrendDay[]
}

// ── Domain Types ──

export interface DomainStat {
  domain: string
  icon: string
  accuracy: number
  count: number
}

export interface DomainsData {
  domains: DomainStat[]
}

// ── Preferences Types ──

export interface PreferencesData {
  preferences: string[]
}

// ── Goal Types ──

export interface GoalData {
  daily_goal: number
  today_count: number
}

// ── History Save Response ──

export interface HistorySaveResult {
  id: number
  session_id: string
  topic: string
  accuracy: number
  total_questions: number
  correct_count: number
  duration_seconds: number
  summary: string | null
  created_at: string
  xp_earned: number
  new_level: number | null
  new_achievements: Achievement[]
}
