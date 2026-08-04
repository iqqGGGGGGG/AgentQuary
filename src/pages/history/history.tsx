import { useState, useEffect } from 'react'
import Taro from '@tarojs/taro'
import { View, Text, Input } from '@tarojs/components'
import { clearHistory, clearQuizProgress, deleteHistory, getHistory, saveQuizProgress } from '../../utils/storage'
import { setCurrentQuiz, setQuizResult } from '../../store/quiz'
import { formatDuration, formatAccuracy } from '../../utils/format'
import type { HistoryItem } from '../../types/quiz'
import './history.scss'

export default function History() {
  const [history, setHistory] = useState<HistoryItem[]>([])
  const [search, setSearch] = useState('')

  useEffect(() => {
    setHistory(getHistory())
  }, [])

  const filtered = search.trim()
    ? history.filter(h => h.topic.includes(search.trim()))
    : history

  const grouped = filtered.reduce<Record<string, HistoryItem[]>>((acc, item) => {
    const date = new Date(item.timestamp)
    const today = new Date()
    const yesterday = new Date(today)
    yesterday.setDate(yesterday.getDate() - 1)

    let label: string
    if (date.toDateString() === today.toDateString()) {
      label = '今天'
    } else if (date.toDateString() === yesterday.toDateString()) {
      label = '昨天'
    } else {
      label = `${date.getMonth() + 1}月${date.getDate()}日`
    }

    if (!acc[label]) acc[label] = []
    acc[label].push(item)
    return acc
  }, {})

  const handleClear = () => {
    Taro.showModal({
      title: '确认清空',
      content: '将清空所有学习记录',
      success(res) {
        if (res.confirm) {
          clearHistory()
          setHistory([])
        }
      },
    })
  }

  const handleRetry = (item: HistoryItem) => {
    if (!item.quiz) {
      Taro.showToast({ title: '旧记录未保存题目，无法重试', icon: 'none' })
      return
    }
    const quiz = { ...item.quiz, session_id: `${item.session_id}-retry-${Date.now()}` }
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
    Taro.navigateTo({ url: '/pages/quiz/quiz' })
  }

  const handleViewReport = (item: HistoryItem) => {
    if (!item.result) {
      Taro.showToast({ title: '旧记录没有完整报告', icon: 'none' })
      return
    }
    setQuizResult(item.result)
    Taro.navigateTo({ url: '/pages/report/report?from=history' })
  }

  const handleDelete = (item: HistoryItem) => {
    Taro.showModal({
      title: '删除这条记录？',
      content: item.topic,
      success(res) {
        if (res.confirm) setHistory(deleteHistory(item.session_id))
      },
    })
  }

  const getAccuracyColor = (accuracy: number) => {
    if (accuracy >= 0.8) return 'var(--correct)'
    if (accuracy >= 0.6) return 'var(--ember)'
    return 'var(--wrong)'
  }

  return (
    <View className='history-page'>
      {/* Search */}
      <View className='search-box'>
        <Text className='search-icon'>🔍</Text>
        <Input
          className='search-input'
          placeholder='搜索学过的主题…'
          value={search}
          onInput={e => setSearch(e.detail.value)}
        />
      </View>

      {history.length === 0 ? (
        <View className='empty-state'>
          <Text className='empty-icon'>📖</Text>
          <Text className='empty-title'>还没有学习记录</Text>
          <Text className='empty-sub'>输入一个主题，开始你的第一次闯关吧</Text>
        </View>
      ) : filtered.length === 0 ? (
        <View className='empty-state'>
          <Text className='empty-icon'>🔍</Text>
          <Text className='empty-title'>没有找到相关记录</Text>
          <Text className='empty-sub'>换个关键词试试</Text>
        </View>
      ) : (
        Object.entries(grouped).map(([label, items]) => (
          <View key={label}>
            <Text className='date-header'>{label}</Text>
            {items.map(item => (
              <View key={item.session_id} className='history-card'>
                <View className='card-top'>
                  <Text className='card-trophy'>🏆</Text>
                  <Text className='card-topic'>{item.topic}</Text>
                  <Text className='card-accuracy' style={{ color: getAccuracyColor(item.accuracy) }}>
                    {formatAccuracy(item.accuracy)}
                  </Text>
                </View>
                <View className='card-stats'>
                  <Text className='stat'>📝 {item.total_questions} 题</Text>
                  <Text className='stat'>⏱️ {formatDuration(item.duration_seconds)}</Text>
                </View>
                <View className='card-divider' />
                <View className='card-actions'>
                  <Text className='action-text' onClick={() => handleViewReport(item)}>查看报告</Text>
                  <Text className='action-text' onClick={() => handleRetry(item)}>再次挑战 🔄</Text>
                  <Text className='delete-text' onClick={() => handleDelete(item)}>删除</Text>
                </View>
              </View>
            ))}
          </View>
        ))
      )}

      {history.length > 0 && (
        <View className='clear-btn' onClick={handleClear}>
          <Text className='clear-text'>清空记录</Text>
        </View>
      )}
    </View>
  )
}
