import { useState, useCallback } from 'react'
import Taro, { useDidShow } from '@tarojs/taro'
import { View, Text, ScrollView } from '@tarojs/components'
import { api } from '../../services/api'
import { setCurrentQuiz } from '../../store/quiz'
import { clearQuizProgress } from '../../utils/storage'
import type { WrongQuestion } from '../../types/quiz'
import './wrong-book.scss'

export default function WrongBook() {
  const [questions, setQuestions] = useState<WrongQuestion[]>([])
  const [total, setTotal] = useState(0)
  const [topicCount, setTopicCount] = useState(0)
  const [topics, setTopics] = useState<string[]>([])
  const [activeFilter, setActiveFilter] = useState('全部')

  const loadData = useCallback(async () => {
    try {
      const data = await api.getWrongQuestions(100)
      setQuestions(data.items)
      setTotal(data.total)
      setTopicCount(data.topic_count)
      const uniqueTopics = Array.from(new Set(data.items.map(q => q.topic)))
      setTopics(uniqueTopics)
    } catch {
      Taro.showToast({ title: '加载失败', icon: 'none' })
    }
  }, [])

  useDidShow(() => { loadData() })

  const filtered = activeFilter === '全部'
    ? questions
    : questions.filter(q => q.topic === activeFilter)

  const handleRemove = async (recordId: number, questionId: number) => {
    try {
      await api.removeWrongQuestion(recordId, questionId)
      setQuestions(prev => prev.filter(q => !(q.record_id === recordId && q.question_id === questionId)))
      setTotal(prev => prev - 1)
      Taro.showToast({ title: '已移除', icon: 'success' })
    } catch {
      Taro.showToast({ title: '移除失败', icon: 'none' })
    }
  }

  const handlePracticeAll = async () => {
    try {
      Taro.showLoading({ title: '加载错题中...' })
      const data = await api.getWrongQuiz()
      if (!data.questions || data.questions.length === 0) {
        Taro.hideLoading()
        Taro.showToast({ title: '没有错题可练习', icon: 'none' })
        return
      }
      clearQuizProgress()
      setCurrentQuiz(data)
      Taro.hideLoading()
      Taro.navigateTo({ url: '/pages/quiz/quiz' })
    } catch {
      Taro.hideLoading()
      Taro.showToast({ title: '加载失败', icon: 'none' })
    }
  }

  const handlePracticeOne = async (questionId: number) => {
    try {
      Taro.showLoading({ title: '加载题目中...' })
      const data = await api.getWrongQuiz(questionId)
      if (!data.questions || data.questions.length === 0) {
        Taro.hideLoading()
        Taro.showToast({ title: '题目未找到', icon: 'none' })
        return
      }
      clearQuizProgress()
      setCurrentQuiz(data)
      Taro.hideLoading()
      Taro.navigateTo({ url: '/pages/quiz/quiz' })
    } catch {
      Taro.hideLoading()
      Taro.showToast({ title: '加载失败', icon: 'none' })
    }
  }

  return (
    <View className='wrong-book-page'>
      <View className='wq-stats'>
        <View className='wq-stat'>
          <Text className='wq-stat-num'>{total}</Text>
          <Text className='wq-stat-label'>错题总数</Text>
        </View>
        <View className='wq-stat'>
          <Text className='wq-stat-num'>{topicCount}</Text>
          <Text className='wq-stat-label'>涉及主题</Text>
        </View>
      </View>

      <ScrollView className='wq-filters' scrollX enableFlex>
        <Text
          className={`wq-filter ${activeFilter === '全部' ? 'active' : ''}`}
          onClick={() => setActiveFilter('全部')}
        >全部</Text>
        {topics.map(t => (
          <Text
            key={t}
            className={`wq-filter ${activeFilter === t ? 'active' : ''}`}
            onClick={() => setActiveFilter(t)}
          >{t}</Text>
        ))}
      </ScrollView>

      <ScrollView className='wq-list' scrollY>
        {filtered.length === 0 ? (
          <View className='wq-empty'>
            <Text className='wq-empty-icon'>🎉</Text>
            <Text className='wq-empty-text'>没有错题，继续保持！</Text>
          </View>
        ) : (
          filtered.map(q => (
            <View key={`${q.record_id}-${q.question_id}`} className='wq-card'>
              <View className='wq-card-tag-wrap'>
                <Text className='wq-card-tag'>{q.topic}</Text>
              </View>
              <Text className='wq-card-question'>{q.question}</Text>
              <Text className='wq-card-answer wrong'>你的答案：{q.your_answer}</Text>
              <Text className='wq-card-answer correct'>✓ 正确答案：{q.correct_answer}</Text>
              {q.explanation && (
                <View className='wq-card-explain'>
                  <Text className='wq-card-explain-text'>💡 {q.explanation}</Text>
                </View>
              )}
              <View className='wq-card-actions'>
                <Text className='wq-card-action practice' onClick={() => handlePracticeOne(q.question_id)}>🔄 重新练习</Text>
                <Text className='wq-card-action' onClick={() => handleRemove(q.record_id, q.question_id)}>✕ 移除</Text>
              </View>
            </View>
          ))
        )}
      </ScrollView>

      {total > 0 && (
        <View className='wq-bottom'>
          <View className='wq-practice-btn' onClick={handlePracticeAll}>
            <Text className='wq-practice-text'>🔄 重新练习全部错题</Text>
          </View>
        </View>
      )}
    </View>
  )
}
