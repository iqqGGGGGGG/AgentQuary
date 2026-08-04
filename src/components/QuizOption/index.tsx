import { View, Text } from '@tarojs/components'
import './index.scss'

interface QuizOptionProps {
  letter: string
  text: string
  selected?: boolean
  correct?: boolean
  wrong?: boolean
  onClick?: () => void
}

export default function QuizOption({ letter, text, selected, correct, wrong, onClick }: QuizOptionProps) {
  let className = 'quiz-option'
  if (selected) className += ' selected'
  if (correct) className += ' correct'
  if (wrong) className += ' wrong'

  return (
    <View className={className} onClick={onClick}>
      <View className='option-letter'>
        <Text className='letter'>{letter}</Text>
      </View>
      <Text className='option-text'>{text}</Text>
      {correct && <View className='check'>✓</View>}
      {wrong && <View className='check-wrong'>✗</View>}
      {selected && !correct && !wrong && <View className='check'>✓</View>}
    </View>
  )
}
