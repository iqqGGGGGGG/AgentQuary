import { useState, useEffect } from 'react'
import Taro, { useDidShow } from '@tarojs/taro'
import { View, Text, Textarea, Image } from '@tarojs/components'
import { setCurrentQuiz } from '../../store/quiz'
import { api } from '../../services/api'
import { clearQuizProgress, getHistory, getQuizProgress, saveQuizProgress } from '../../utils/storage'
import { formatTime, formatAccuracy } from '../../utils/format'
import type { ExampleTopic, HistoryItem, QuizProgress } from '../../types/quiz'
import graduationCapIcon from '../../assets/topic-icons/graduation-cap.png'
import orbitIcon from '../../assets/topic-icons/orbit.png'
import brainIcon from '../../assets/topic-icons/brain.png'
import coffeeIcon from '../../assets/topic-icons/coffee.png'
import knowledgeRobot from '../../assets/mascot/knowledge-robot.png'
import bookOpenHero from '../../assets/hero-icons/book-open.png'
import atomHero from '../../assets/hero-icons/atom.png'
import globeHero from '../../assets/hero-icons/globe.png'
import lightbulbHero from '../../assets/hero-icons/lightbulb.png'
import searchIcon from '../../assets/ui-icons/search.png'
import fileIcon from '../../assets/ui-icons/file-text.png'
import linkIcon from '../../assets/ui-icons/link.png'
import sparklesIcon from '../../assets/ui-icons/sparkles.png'
import './index.scss'

const DEFAULT_EXAMPLES: ExampleTopic[] = [
  { id: 1, title: '十分钟搞懂三国人物关系', category: '历史', description: '人物关系一网打尽' },
  { id: 2, title: '太阳系的八大行星', category: '科学', description: '基础天文速览' },
  { id: 3, title: '常见心理学效应', category: '心理', description: '看完更懂自己' },
  { id: 4, title: '从种子到一杯咖啡', category: '生活', description: '咖啡入门必修' },
]

const TOPIC_ICONS = [graduationCapIcon, orbitIcon, brainIcon, coffeeIcon]

function TopicIcon({ index }: { index: number }) {
  const iconType = index % TOPIC_ICONS.length
  return (
    <View className={`topic-icon topic-icon-${iconType}`} aria-hidden>
      <Image className='topic-icon-image' src={TOPIC_ICONS[iconType]} mode='aspectFit' />
    </View>
  )
}

export default function Index() {
  const [content, setContent] = useState('')
  const [examples, setExamples] = useState<ExampleTopic[]>(DEFAULT_EXAMPLES)
  const [history, setHistory] = useState<HistoryItem[]>([])
  const [loading, setLoading] = useState(false)
  const [inputMode, setInputMode] = useState<'text' | 'link' | 'file'>('text')
  const [activeProgress, setActiveProgress] = useState<QuizProgress | null>(null)

  useEffect(() => {
    api.examples().then(res => setExamples(res.examples)).catch(() => setExamples(DEFAULT_EXAMPLES))
    setHistory(getHistory().slice(0, 2))
    setActiveProgress(getQuizProgress())
  }, [])

  useDidShow(() => {
    setHistory(getHistory().slice(0, 2))
    setActiveProgress(getQuizProgress())
  })

  const handleStart = async () => {
    if (!content.trim()) {
      Taro.showToast({ title: '请输入学习内容', icon: 'none' })
      return
    }
    setLoading(true)
    Taro.showLoading({ title: '正在生成题目...' })
    try {
      const cleanContent = content.trim()
      if (cleanContent.length > 12000) {
        throw new Error('内容超过 12000 字，请截取最需要学习的部分')
      }
      const data = await api.generate(cleanContent)
      setCurrentQuiz(data)
      clearQuizProgress()
      saveQuizProgress({
        quiz: data,
        current_index: 0,
        selected_option: -1,
        status: 'selecting',
        user_answers: [],
        streak: 0,
        start_time: Date.now(),
      })
      Taro.hideLoading()
      Taro.navigateTo({ url: '/pages/quiz/quiz' })
    } catch (err) {
      Taro.hideLoading()
      Taro.showModal({
        title: '生成失败',
        content: err instanceof Error ? err.message : '请稍后重试',
        showCancel: false,
      })
    } finally {
      setLoading(false)
    }
  }

  const handleExampleClick = (title: string) => {
    setContent(title)
    setInputMode('text')
  }

  const handleChooseFile = async () => {
    try {
      const response = await Taro.chooseMessageFile({ count: 1, type: 'file', extension: ['txt', 'md'] })
      const file = response.tempFiles[0]
      if (!file) return
      if (file.size > 200 * 1024) {
        Taro.showToast({ title: '文件不能超过 200KB', icon: 'none' })
        return
      }
      const fs = Taro.getFileSystemManager()
      fs.readFile({
        filePath: file.path,
        encoding: 'utf8',
        success: res => {
          if (typeof res.data !== 'string') return
          setContent(res.data)
          setInputMode('file')
          Taro.showToast({ title: '文档已读取', icon: 'success' })
        },
        fail: () => Taro.showToast({ title: '文件读取失败', icon: 'none' }),
      })
    } catch {
      // 用户取消选择时不打断当前输入。
    }
  }

  const handleResume = () => {
    if (!activeProgress) return
    setCurrentQuiz(activeProgress.quiz)
    Taro.navigateTo({ url: '/pages/quiz/quiz' })
  }

  return (
    <View className='index-page'>
      {/* Mascot */}
      <View className='mascot-wrap'>
        <View className='knowledge-stage' aria-hidden>
          <View className='knowledge-orbit knowledge-orbit-outer' />
          <View className='knowledge-orbit knowledge-orbit-inner' />
          <View className='knowledge-badge knowledge-badge-book'>
            <Image className='knowledge-badge-icon' src={bookOpenHero} mode='aspectFit' />
          </View>
          <View className='knowledge-badge knowledge-badge-atom'>
            <Image className='knowledge-badge-icon' src={atomHero} mode='aspectFit' />
          </View>
          <View className='knowledge-badge knowledge-badge-globe'>
            <Image className='knowledge-badge-icon' src={globeHero} mode='aspectFit' />
          </View>
          <View className='knowledge-badge knowledge-badge-idea'>
            <Image className='knowledge-badge-icon' src={lightbulbHero} mode='aspectFit' />
          </View>
          <View className='knowledge-spark knowledge-spark-1' />
          <View className='knowledge-spark knowledge-spark-2' />
          <View className='knowledge-spark knowledge-spark-3' />
          <View className='mascot-core'>
            <View className='mascot-halo' />
            <Image className='mascot-image' src={knowledgeRobot} mode='aspectFit' />
          </View>
        </View>
      </View>

      {/* Hero */}
      <View className='hero'>
        <Text className='greeting'>想学点什么？丢进来就好</Text>
        <Text className='subtitle'>AI 自动出题，答完就能记住</Text>
      </View>

      {/* Input */}
      <View className='input-area'>
        <View className='input-box'>
          <Image className='input-icon' src={searchIcon} mode='aspectFit' />
          <Textarea
            className='input-field'
            placeholder={inputMode === 'link' ? '粘贴公开网页链接（http/https）' : '输入主题，或粘贴一段学习内容…'}
            value={content}
            onInput={e => setContent(e.detail.value)}
            disabled={loading}
            maxlength={12000}
            autoHeight
          />
        </View>
        <View className='input-actions'>
          <View className={`input-action ${inputMode === 'file' ? 'input-action-active' : ''}`} onClick={handleChooseFile}>
            <Image className='input-action-icon' src={fileIcon} mode='aspectFit' />
            <Text>选择 .txt / .md</Text>
          </View>
          <View className={`input-action ${inputMode === 'link' ? 'input-action-active' : ''}`} onClick={() => setInputMode('link')}>
            <Image className='input-action-icon' src={linkIcon} mode='aspectFit' />
            <Text>输入网页链接</Text>
          </View>
        </View>
        <Text className='input-note'>网页会读取公开正文；私人链接与内网地址不会访问</Text>
      </View>

      {activeProgress && (
        <View className='resume-card' onClick={handleResume}>
          <View className='resume-copy'>
            <Text className='resume-eyebrow'>未完成的闯关</Text>
            <Text className='resume-title'>{activeProgress.quiz.topic}</Text>
            <Text className='resume-meta'>已完成 {activeProgress.user_answers.length} / {activeProgress.quiz.questions.length} 题</Text>
          </View>
          <Text className='resume-action'>继续 →</Text>
        </View>
      )}

      {/* Start Button */}
      <View className='btn-primary' onClick={handleStart}>
        <Image className='btn-icon' src={sparklesIcon} mode='aspectFit' />
        <Text>开始闯关</Text>
      </View>

      {/* Examples */}
      {examples.length > 0 && (
        <View className='section'>
          <View className='section-header'>
            <View className='section-line' />
            <Text className='section-title'>翻一页试试</Text>
            <View className='section-line' />
          </View>
          <View className='topic-grid'>
            {examples.slice(0, 4).map((ex, idx) => (
              <View
                key={ex.id}
                className={`topic-card topic-card-${idx}`}
                onClick={() => handleExampleClick(ex.title)}
              >
                <View className='topic-card-top'>
                  <TopicIcon index={idx} />
                  <Text className={`topic-category topic-category-${idx % 4}`}>{ex.category}</Text>
                </View>
                <Text className='topic-title'>{ex.title}</Text>
                <Text className='topic-meta'>{ex.description}</Text>
              </View>
            ))}
          </View>
        </View>
      )}

      {/* History */}
      {history.length > 0 && (
        <View className='section'>
          <View className='section-header'>
            <View className='section-line' />
            <Text className='section-title'>上次看到这里</Text>
            <View className='section-line' />
          </View>
          {history.map((item, idx) => (
            <View key={item.session_id} className='history-item'>
              <View className={`history-icon history-icon-${idx % 2}`}>
                <Image className='history-icon-image' src={idx % 2 === 0 ? bookOpenHero : orbitIcon} mode='aspectFit' />
              </View>
              <View className='history-info'>
                <Text className='history-topic'>{item.topic}</Text>
                <Text className='history-meta'>{item.total_questions} 题 · {formatTime(item.timestamp)}</Text>
              </View>
              <Text className='history-accuracy'>{formatAccuracy(item.accuracy)}</Text>
            </View>
          ))}
        </View>
      )}
    </View>
  )
}
