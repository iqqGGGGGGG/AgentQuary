import { useState, useEffect } from 'react'
import Taro, { useRouter, useShareAppMessage } from '@tarojs/taro'
import { Button, View, Text, Image } from '@tarojs/components'
import { getQuizResult, setCurrentQuiz, setQuizResult, setPendingAchievements } from '../../store/quiz'
import { api } from '../../services/api'
import { clearQuizProgress, getHistory, saveHistory, saveQuizProgress } from '../../utils/storage'
import { formatDuration, formatAccuracy } from '../../utils/format'
import type { ReportResponse } from '../../types/quiz'
import { isLoggedIn } from '../../store/user'
import knowledgeRobot from '../../assets/mascot/knowledge-robot.png'
import './report.scss'

export default function Report() {
  const [result] = useState(getQuizResult())
  const [report, setReport] = useState<ReportResponse | null>(null)
  const [showWrongReview, setShowWrongReview] = useState(false)
  const [retrying, setRetrying] = useState(false)
  const [summaryLoading, setSummaryLoading] = useState(true)
  const router = useRouter()
  const fromHistory = router.params.from === 'history'

  useShareAppMessage(() => ({
    title: result ? `我完成了「${result.topic}」知识闯关，正确率 ${formatAccuracy(result.accuracy)}` : '知识闯关',
    path: '/pages/index/index',
  }))

  useEffect(() => {
    if (!result) {
      Taro.navigateBack()
      return
    }

    const masteredQuestions = result.user_answers
      .filter(a => a.is_correct)
      .map(a => result.questions.find(q => q.id === a.question_id)?.question || '')

    const weakQuestions = result.user_answers
      .filter(a => !a.is_correct)
      .map(a => result.questions.find(q => q.id === a.question_id)?.question || '')

    const stored = getHistory().find(item => item.session_id === result.session_id)
    const localReport: ReportResponse = {
      accuracy: result.accuracy,
      correct_count: result.correct_count,
      total_count: result.total_count,
      mastered: masteredQuestions,
      weak: weakQuestions,
      summary: fromHistory ? stored?.summary || '' : '',
      encouragement: '',
    }
    setReport(localReport)

    if (fromHistory) {
      setSummaryLoading(false)
      return
    }

    const persistHistory = (summary = '') => {
      saveHistory({
        session_id: result.session_id,
        topic: result.topic,
        timestamp: Date.now(),
        accuracy: result.accuracy,
        total_questions: result.total_count,
        correct_count: result.correct_count,
        duration_seconds: result.duration_seconds,
        quiz: { session_id: result.session_id, topic: result.topic, questions: result.questions },
        result,
        summary,
      })

      if (isLoggedIn()) {
        api.saveHistory({
          session_id: result.session_id,
          topic: result.topic,
          accuracy: result.accuracy,
          total_questions: result.total_count,
          correct_count: result.correct_count,
          duration_seconds: result.duration_seconds,
          questions: result.questions,
          user_answers: result.user_answers,
          summary,
        }).then(res => {
          if (res.new_achievements?.length) {
            setPendingAchievements(res.new_achievements)
          }
        }).catch(() => {})
      }
    }
    persistHistory()

    api.report({
      topic: result.topic,
      questions: result.questions,
      user_answers: result.user_answers.map(a => a.selected),
      duration_seconds: result.duration_seconds,
    }).then(res => {
      setReport(prev => prev ? { ...prev, summary: res.summary, encouragement: res.encouragement } : res)
      setSummaryLoading(false)
      persistHistory(res.summary)
    }).catch(() => { setSummaryLoading(false) })
  }, [])

  const handleRetry = async () => {
    if (!result || retrying) return
    setRetrying(true)
    Taro.showLoading({ title: '正在生成新题...' })
    try {
      const sourceContent = result.source_content?.trim() || result.topic
      const generated = await api.generate(
        sourceContent,
        result.total_count,
        result.questions.map(question => question.question),
      )
      const quiz = { ...generated, source_content: sourceContent }
      setCurrentQuiz(quiz)
      setQuizResult(null)
      clearQuizProgress()
      saveQuizProgress({
        quiz,
        current_index: 0,
        selected_option: -1,
        status: 'selecting',
        user_answers: [],
        streak: 0,
        start_time: Date.now(),
      })
      Taro.hideLoading()
      Taro.redirectTo({ url: '/pages/quiz/quiz' })
    } catch (err) {
      Taro.hideLoading()
      Taro.showModal({
        title: '新题生成失败',
        content: err instanceof Error ? err.message : '请稍后重试',
        showCancel: false,
      })
    } finally {
      setRetrying(false)
    }
  }

  const handleHome = () => {
    setCurrentQuiz(null)
    setQuizResult(null)
    Taro.reLaunch({ url: '/pages/index/index' })
  }

  if (!result || !report) return null

  const accuracyPercent = Math.round(report.accuracy * 100)
  const circumference = 2 * Math.PI * 52
  const offset = circumference * (1 - report.accuracy)

  return (
    <View className='report-page'>
      {/* Navbar */}
      <View className='report-navbar'>
        <Text className='navbar-icon'>🏆</Text>
        <Text className='navbar-title'>闯关完成！</Text>
      </View>

      {/* Mascot celebrate */}
      <View className='mascot-celebrate'>
        <View className='celebrate-mascot'>
          <Image className='celebrate-mascot-image' src={knowledgeRobot} mode='aspectFit' />
          <View className='confetti confetti-1' />
          <View className='confetti confetti-2' />
          <View className='confetti confetti-3' />
        </View>
      </View>

      {/* Accuracy Ring */}
      <View className='accuracy-ring-wrap'>
        <View className='accuracy-ring'>
          <svg viewBox='0 0 120 120' style={{ width: '100%', height: '100%', transform: 'rotate(-90deg)' }}>
            <circle cx='60' cy='60' r='52' fill='none' stroke='rgba(124,92,252,0.1)' strokeWidth='8' />
            <circle
              cx='60' cy='60' r='52'
              fill='none'
              stroke='url(#ring-grad)'
              strokeWidth='8'
              strokeLinecap='round'
              strokeDasharray={circumference}
              strokeDashoffset={offset}
            />
            <defs>
              <linearGradient id='ring-grad' x1='0%' y1='0%' x2='100%'>
                <stop offset='0%' stopColor='#7C5CFC' />
                <stop offset='100%' stopColor='#B8A9FF' />
              </linearGradient>
            </defs>
          </svg>
          <View className='ring-text'>
            <Text className='ring-number'>{accuracyPercent}%</Text>
            <Text className='ring-label'>正确率</Text>
          </View>
        </View>
      </View>

      {/* Stats */}
      <View className='report-stats'>
        <View className='stat-item'>
          <Text className='stat-icon'>⏱️</Text>
          <Text className='stat-text'>用时 {formatDuration(result.duration_seconds)}</Text>
        </View>
        <View className='stat-item'>
          <Text className='stat-icon'>📝</Text>
          <Text className='stat-text'>{result.total_count} 题</Text>
        </View>
      </View>

      {/* AI Summary */}
      {summaryLoading && (
        <View className='summary-card summary-loading'>
          <Text className='summary-label'>AI 总结</Text>
          <Text className='summary-loading-text'>AI 正在生成总结...</Text>
        </View>
      )}
      {!summaryLoading && report.summary && (
        <View className='summary-card'>
          <Text className='summary-label'>AI 总结</Text>
          <Text className='summary-text'>{report.summary}</Text>
        </View>
      )}
      {report.encouragement && <Text className='encouragement'>{report.encouragement}</Text>}

      {/* Mastered */}
      {report.mastered.length > 0 && (
        <View className='report-section'>
          <View className='section-title-row'>
            <Text className='section-icon'>✓</Text>
            <Text className='section-title' style={{ color: 'var(--correct)' }}>已掌握</Text>
          </View>
          {report.mastered.map((item, idx) => (
            <View key={idx} className='mastered-item'>
              <Text className='mastered-icon'>✓</Text>
              <Text className='item-text'>{item}</Text>
            </View>
          ))}
        </View>
      )}

      {/* Weak */}
      {report.weak.length > 0 && (
        <View className='report-section'>
          <View className='section-title-row'>
            <Text className='section-icon'>💡</Text>
            <Text className='section-title' style={{ color: 'var(--ember)' }}>需要复习</Text>
          </View>
          {report.weak.map((item, idx) => (
            <View key={idx} className='weak-item'>
              <Text className='weak-icon'>💡</Text>
              <Text className='item-text'>{item}</Text>
            </View>
          ))}
        </View>
      )}

      {result.user_answers.some(answer => !answer.is_correct) && (
        <View className='wrong-review-section'>
          <View className='wrong-review-toggle' onClick={() => setShowWrongReview(value => !value)}>
            <Text className='wrong-review-title'>错题回顾</Text>
            <Text className='wrong-review-action'>{showWrongReview ? '收起 ↑' : '展开 ↓'}</Text>
          </View>
          {showWrongReview && result.user_answers.filter(answer => !answer.is_correct).map(answer => {
            const question = result.questions.find(item => item.id === answer.question_id)
            if (!question) return null
            return (
              <View key={answer.question_id} className='wrong-review-card'>
                <Text className='wrong-question'>{question.question}</Text>
                <Text className='wrong-answer'>你的答案：{question.options[answer.selected] || '未作答'}</Text>
                <Text className='right-answer'>正确答案：{question.options[question.answer]}</Text>
                <Text className='wrong-explanation'>💡 {question.explanation}</Text>
              </View>
            )
          })}
        </View>
      )}

      {/* Actions */}
      <View className='report-actions'>
        <View className={`btn-primary ${retrying ? 'btn-disabled' : ''}`} onClick={handleRetry}>
          <Text>{retrying ? '正在生成新题...' : '🔄 再来一关'}</Text>
        </View>
        <View className='btn-secondary' onClick={handleHome}>
          <Text>🏠 回到首页</Text>
        </View>
        <Button className='btn-text-link share-button' openType='share'>
          <Text>📤 分享成绩给朋友</Text>
        </Button>
      </View>
    </View>
  )
}
