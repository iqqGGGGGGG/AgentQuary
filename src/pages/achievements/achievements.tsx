import { useState, useCallback } from 'react'
import Taro, { useDidShow } from '@tarojs/taro'
import { View, Text, ScrollView } from '@tarojs/components'
import { api } from '../../services/api'
import type { Achievement } from '../../types/quiz'
import './achievements.scss'

export default function Achievements() {
  const [achievements, setAchievements] = useState<Achievement[]>([])
  const [unlockedCount, setUnlockedCount] = useState(0)
  const [totalCount, setTotalCount] = useState(0)

  const loadData = useCallback(async () => {
    try {
      const data = await api.getAchievements()
      setAchievements(data.items)
      setUnlockedCount(data.unlocked_count)
      setTotalCount(data.total_count)
    } catch {
      Taro.showToast({ title: '加载失败', icon: 'none' })
    }
  }, [])

  useDidShow(() => { loadData() })

  return (
    <ScrollView className='ach-page' scrollY>
      <View className='ach-header'>
        <Text className='ach-header-icon'>🏅</Text>
        <Text className='ach-header-title'>成就徽章</Text>
        <Text className='ach-header-count'>已解锁 {unlockedCount} / {totalCount}</Text>
      </View>

      <View className='ach-progress-bar'>
        <View className='ach-progress-fill' style={{ width: `${totalCount > 0 ? Math.round((unlockedCount / totalCount) * 100) : 0}%` }} />
      </View>

      <View className='ach-grid'>
        {achievements.map(a => {
          const unlockDate = a.unlocked && a.unlocked_at
            ? (() => { const d = new Date(a.unlocked_at); return `${d.getMonth() + 1}月${d.getDate()}日解锁` })()
            : null
          return (
            <View key={a.id} className={`ach-item ${a.unlocked ? 'unlocked' : 'locked'}`}>
              <Text className='ach-item-icon'>{a.icon}</Text>
              <Text className='ach-item-name'>{a.name}</Text>
              <Text className='ach-item-desc'>{a.description}</Text>
              {unlockDate && <Text className='ach-item-date'>{unlockDate}</Text>}
            </View>
          )
        })}
      </View>

      <View className='bottom-spacer' />
    </ScrollView>
  )
}
