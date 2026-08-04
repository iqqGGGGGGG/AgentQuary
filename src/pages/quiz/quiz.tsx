import { useState, useEffect, useRef } from 'react'
import Taro from '@tarojs/taro'
import { View, Text, Image } from '@tarojs/components'
import { getCurrentQuiz, setQuizResult } from '../../store/quiz'
import { clearQuizProgress, getQuizProgress, saveQuizProgress } from '../../utils/storage'
import type { Question, UserAnswer, QuizResult } from '../../types/quiz'
import knowledgeRobot from '../../assets/mascot/knowledge-robot.png'
import './quiz.scss'

type QuizStatus = 'selecting' | 'feedback'

export default function Quiz() {
  const [questions, setQuestions] = useState<Question[]>([])
  const [currentIndex, setCurrentIndex] = useState(0)
  const [selectedOption, setSelectedOption] = useState(-1)
  const [status, setStatus] = useState<QuizStatus>('selecting')
  const [isCorrect, setIsCorrect] = useState(false)
  const [userAnswers, setUserAnswers] = useState<UserAnswer[]>([])
  const [streak, setStreak] = useState(0)
  const startTime = useRef(Date.now())

  useEffect(() => {
    const saved = getQuizProgress()
    const quiz = getCurrentQuiz() || saved?.quiz
    if (!quiz || quiz.questions.length === 0) {
      Taro.navigateBack()
      return
    }
    setQuestions(quiz.questions)
    if (saved?.quiz.session_id === quiz.session_id) {
      const safeIndex = Math.min(saved.current_index, quiz.questions.length - 1)
      setCurrentIndex(safeIndex)
      setSelectedOption(saved.selected_option)
      setStatus(saved.status)
      setUserAnswers(saved.user_answers)
      setStreak(saved.streak)
      startTime.current = saved.start_time
      if (saved.status === 'feedback' && saved.selected_option >= 0) {
        setIsCorrect(saved.selected_option === quiz.questions[safeIndex].answer)
      }
    }
  }, [])

  const handleSelect = (idx: number) => {
    if (status !== 'selecting') return
    setSelectedOption(idx)
  }

  const handleConfirm = () => {
    if (status !== 'selecting' || selectedOption < 0) return
    const q = questions[currentIndex]
    const correct = selectedOption === q.answer
    setIsCorrect(correct)

    const answer: UserAnswer = {
      question_id: q.id,
      selected: selectedOption,
      is_correct: correct,
    }
    const newAnswers = [...userAnswers, answer]
    setUserAnswers(newAnswers)

    const nextStreak = correct ? streak + 1 : 0
    setStreak(nextStreak)

    setStatus('feedback')
    const quiz = getCurrentQuiz() || getQuizProgress()?.quiz
    if (quiz) {
      saveQuizProgress({
        quiz,
        current_index: currentIndex,
        selected_option: selectedOption,
        status: 'feedback',
        user_answers: newAnswers,
        streak: nextStreak,
        start_time: startTime.current,
      })
    }
  }

  const handleNext = () => {
    if (currentIndex < questions.length - 1) {
      setCurrentIndex(i => i + 1)
      setSelectedOption(-1)
      setStatus('selecting')
      const quiz = getCurrentQuiz() || getQuizProgress()?.quiz
      if (quiz) {
        saveQuizProgress({
          quiz,
          current_index: currentIndex + 1,
          selected_option: -1,
          status: 'selecting',
          user_answers: userAnswers,
          streak,
          start_time: startTime.current,
        })
      }
    } else {
      const quiz = getCurrentQuiz() || getQuizProgress()?.quiz
      const correctCount = userAnswers.filter(a => a.is_correct).length
      const total = questions.length
      const result: QuizResult = {
        session_id: quiz?.session_id || '',
        topic: quiz?.topic || '',
        questions,
        user_answers: userAnswers,
        start_time: startTime.current,
        end_time: Date.now(),
        duration_seconds: Math.floor((Date.now() - startTime.current) / 1000),
        correct_count: correctCount,
        total_count: total,
        accuracy: correctCount / total,
      }
      setQuizResult(result)
      clearQuizProgress()
      Taro.redirectTo({ url: '/pages/report/report' })
    }
  }

  const handleQuit = () => {
    Taro.showModal({
      title: '确认退出',
      content: '进度会自动保存，你可以稍后继续',
      success(res) {
        if (res.confirm) {
          Taro.navigateBack()
        }
      },
    })
  }

  if (questions.length === 0) return null

  const q = questions[currentIndex]
  const progress = ((currentIndex + 1) / questions.length) * 100
  const letters = ['A', 'B', 'C', 'D']

  return (
    <View className='quiz-page'>
      {/* Navbar */}
      <View className='quiz-navbar'>
        <Text className='back' onClick={handleQuit}>← 退出</Text>
        <Text className='progress-text'>第 {currentIndex + 1} 关 / 共 {questions.length} 关</Text>
        <View className='progress-bar-wrap'>
          <View className='progress-bar-fill' style={{ width: `${progress}%` }} />
        </View>
      </View>

      {/* Encourage Bar */}
      {streak >= 2 && status === 'selecting' && (
        <View className='encourage-bar'>
          <Text className='encourage-icon'>✨</Text>
          <Text>已连对 {streak} 题，保持住！</Text>
        </View>
      )}

      {/* Mascot */}
      {status === 'feedback' && (
        <View className={`mascot-feedback ${isCorrect ? 'mascot-correct' : 'mascot-wrong'}`}>
          <View className={`feedback-mascot ${isCorrect ? 'bounce' : ''}`}>
            <Image className='feedback-mascot-image' src={knowledgeRobot} mode='aspectFit' />
          </View>
        </View>
      )}

      {/* Feedback Card */}
      {status === 'feedback' && (
        <View className={`feedback-card ${isCorrect ? 'correct-fb' : 'wrong-fb'}`}>
          <Text className={`feedback-title ${isCorrect ? 'title-correct' : 'title-wrong'}`}>
            {isCorrect ? '✓ 答对了！' : '✗ 差一点！'}
          </Text>
          {!isCorrect && (
            <View className='feedback-body'>
              <Text>你的答案：<Text className='your-answer'>{q.options[selectedOption]}</Text></Text>
              <Text style={{ marginTop: '8px' }}>正确答案：<Text className='correct-answer'>{q.options[q.answer]}</Text></Text>
            </View>
          )}
          <View className='feedback-extra'>
            <Text className='feedback-extra-icon'>💡</Text>
            <Text>{q.explanation}</Text>
          </View>
        </View>
      )}

      {/* Question */}
      <View className='question-area'>
        <Text className='question-text'>{q.question}</Text>
      </View>

      {/* Options */}
      <View className='options-area'>
        {q.options.map((opt, idx) => {
          let optClass = 'option-card'
          if (status === 'feedback') {
            if (idx === q.answer) optClass += ' correct'
            else if (idx === selectedOption && !isCorrect) optClass += ' wrong'
          } else if (idx === selectedOption) {
            optClass += ' selected'
          }

          return (
            <View
              key={idx}
              className={optClass}
              onClick={() => handleSelect(idx)}
            >
              <View className='option-letter'>
                <Text className='letter-text'>{letters[idx] || idx}</Text>
              </View>
              <Text className='option-text'>{opt}</Text>
              {status === 'feedback' && idx === q.answer && (
                <View className='option-check'>
                  <Text className='check-icon'>✓</Text>
                </View>
              )}
              {status === 'feedback' && idx === selectedOption && !isCorrect && idx !== q.answer && (
                <View className='option-check-wrong'>
                  <Text className='check-icon'>✗</Text>
                </View>
              )}
              {status === 'selecting' && idx === selectedOption && (
                <View className='option-check'>
                  <Text className='check-icon'>✓</Text>
                </View>
              )}
            </View>
          )
        })}
      </View>

      {/* Bottom Button */}
      <View className='quiz-bottom'>
        {status === 'selecting' ? (
          <View
            className={`btn-primary ${selectedOption < 0 ? 'btn-disabled' : ''}`}
            onClick={handleConfirm}
          >
            <Text>✓ 确认答案</Text>
          </View>
        ) : (
          <View className='btn-primary' onClick={handleNext}>
            <Text>{currentIndex < questions.length - 1 ? '下一题 →' : '查看报告'}</Text>
          </View>
        )}
      </View>
    </View>
  )
}
