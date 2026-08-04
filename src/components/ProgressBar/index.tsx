import { View, Text } from '@tarojs/components'
import './index.scss'

interface ProgressBarProps {
  current: number
  total: number
}

export default function ProgressBar({ current, total }: ProgressBarProps) {
  const percent = total > 0 ? (current / total) * 100 : 0

  return (
    <View className='progress-bar'>
      <Text className='progress-text'>第 {current} 关 / 共 {total} 关</Text>
      <View className='bar-wrap'>
        <View className='bar-fill' style={{ width: `${percent}%` }} />
      </View>
    </View>
  )
}
