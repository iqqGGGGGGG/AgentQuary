import type { GenerateResponse, QuizResult, Achievement } from '../types/quiz'

let currentQuiz: GenerateResponse | null = null
let quizResult: QuizResult | null = null
let pendingAchievements: Achievement[] = []

export function setCurrentQuiz(data: GenerateResponse | null) { currentQuiz = data }
export function getCurrentQuiz() { return currentQuiz }

export function setQuizResult(data: QuizResult | null) { quizResult = data }
export function getQuizResult() { return quizResult }

export function setPendingAchievements(list: Achievement[]) { pendingAchievements = [...list] }
export function getPendingAchievements() { return pendingAchievements }
export function clearPendingAchievements() { pendingAchievements = [] }
