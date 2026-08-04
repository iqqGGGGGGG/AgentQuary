import { View, Text } from '@tarojs/components'
import { formatAccuracy } from '../../utils/format'
import './index.scss'

interface ResultCardProps {
  topic: string
  accuracy: number
  correctCount: number
  totalCount: number
  duration: number
}

export default function ResultCard({ topic, accuracy, correctCount, totalCount, duration }: ResultCardProps) {
  const minutes = Math.floor(duration / 60)
  const seconds = duration % 60

  return (
    <View className='result-card'>
      <Text className='result-topic'>{topic}</Text>
      <Text className='result-accuracy'>{formatAccuracy(accuracy)}</Text>
      <Text className='result-label'>正确率</Text>
      <View className='result-stats'>
        <Text className='stat'>{correctCount}/{totalCount} 题</Text>
        <Text className='stat'>{minutes}分{seconds}秒</Text>
      </View>
    </View>
  )
}
