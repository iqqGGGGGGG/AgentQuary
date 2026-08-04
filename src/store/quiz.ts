import type { GenerateResponse, QuizResult } from '../types/quiz'

let currentQuiz: GenerateResponse | null = null
let quizResult: QuizResult | null = null

export function setCurrentQuiz(data: GenerateResponse | null) { currentQuiz = data }
export function getCurrentQuiz() { return currentQuiz }

export function setQuizResult(data: QuizResult | null) { quizResult = data }
export function getQuizResult() { return quizResult }
