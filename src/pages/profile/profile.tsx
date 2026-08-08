import { useState } from 'react'
import Taro, { useDidShow } from '@tarojs/taro'
import { View, Text, Image } from '@tarojs/components'
import { getUserState, setUserState } from '../../store/user'
import { api } from '../../services/api'
import type { UserStats } from '../../types/quiz'
import { formatAccuracy } from '../../utils/format'
import { computeLocalStats } from '../../utils/storage'
import knowledgeRobot from '../../assets/mascot/knowledge-robot.png'
import './profile.scss'

export default function Profile() {
  const [user, setUser] = useState(getUserState())
  const [stats, setStats] = useState<UserStats | null>(null)

  const loadData = () => {
    const currentUser = getUserState()
    setUser(currentUser)

    if (currentUser.isLoggedIn) {
      Promise.all([
        api.getProfile().catch(() => null),
        api.getStats().catch(() => null),
      ]).then(([profile, statsData]) => {
        if (profile) {
          setUserState({ nickname: profile.nickname, avatar_url: profile.avatar_url })
          setUser(getUserState())
        }
        if (statsData) {
          setStats(statsData)
        } else {
          setStats(computeLocalStats())
        }
      })
    } else {
      setStats(computeLocalStats())
    }
  }

  useDidShow(() => { loadData() })

  const handleChooseAvatar = async () => {
    try {
      const res = await Taro.chooseImage({ count: 1, sizeType: ['compressed'] })
      if (res.tempFilePaths[0]) {
        await api.updateProfile({ avatar_url: res.tempFilePaths[0] })
        setUserState({ avatar_url: res.tempFilePaths[0] })
        setUser(getUserState())
        Taro.showToast({ title: '头像已更新', icon: 'success' })
      }
    } catch {
      // User cancelled
    }
  }

  const handleLogin = () => {
    Taro.login({
      success(loginRes) {
        if (loginRes.code) {
          api.login(loginRes.code).then(res => {
            setUserState({
              openid: res.openid,
              access_token: res.access_token,
              nickname: res.nickname,
              avatar_url: res.avatar_url,
              isLoggedIn: true,
            })
            Taro.setStorageSync('access_token', res.access_token)
            Taro.removeStorageSync('user_openid')
            setUser(getUserState())
            loadData()
          }).catch(() => {
            Taro.showToast({ title: '登录失败', icon: 'none' })
          })
        }
      },
    })
  }

  const defaultStats: UserStats = {
    total_quizzes: 0,
    total_questions: 0,
    avg_accuracy: 0,
    best_streak: 0,
    learning_days: 0,
  }
  const s = stats || defaultStats

  return (
    <View className='profile-page'>
      <View className='user-card'>
        <View className='avatar-wrap' onClick={user.isLoggedIn ? handleChooseAvatar : undefined}>
          {user.avatar_url ? (
            <Image className='avatar-image' src={user.avatar_url} mode='aspectFill' />
          ) : (
            <View className='avatar-placeholder'>
              <Image className='avatar-robot' src={knowledgeRobot} mode='aspectFit' />
            </View>
          )}
        </View>
        {user.isLoggedIn ? (
          <>
            <Text className='user-name'>{user.nickname}</Text>
            <Text className='user-hint'>点击头像可更换</Text>
          </>
        ) : (
          <>
            <Text className='user-name'>未登录</Text>
            <View className='login-btn' onClick={handleLogin}>
              <Text className='login-btn-text'>一键登录</Text>
            </View>
          </>
        )}
      </View>

      <View className='stats-section'>
        <View className='stats-grid'>
          <View className='stat-card'>
            <Text className='stat-number'>{s.total_quizzes}</Text>
            <Text className='stat-label'>答题次数</Text>
          </View>
          <View className='stat-card'>
            <Text className='stat-number'>{s.total_questions}</Text>
            <Text className='stat-label'>答题总数</Text>
          </View>
          <View className='stat-card'>
            <Text className='stat-number'>{formatAccuracy(s.avg_accuracy)}</Text>
            <Text className='stat-label'>平均正确率</Text>
          </View>
          <View className='stat-card'>
            <Text className='stat-number'>{s.learning_days}</Text>
            <Text className='stat-label'>学习天数</Text>
          </View>
        </View>
      </View>

      {s.best_streak > 0 && (
        <View className='streak-card'>
          <Text className='streak-icon'>🔥</Text>
          <View className='streak-info'>
            <Text className='streak-title'>最佳连对纪录</Text>
            <Text className='streak-value'>连续答对 {s.best_streak} 题</Text>
          </View>
        </View>
      )}

      <View className='menu-section'>
        <View className='menu-item' onClick={() => Taro.switchTab({ url: '/pages/history/history' })}>
          <Text className='menu-icon'>📖</Text>
          <Text className='menu-text'>学习记录</Text>
          <Text className='menu-arrow'>→</Text>
        </View>
        <View className='menu-item' onClick={() => {
          Taro.showModal({
            title: '关于知识闯关',
            content: '一款把任何知识变成轻松问答闯关的 AI 学习工具。v2.0',
            showCancel: false,
          })
        }}>
          <Text className='menu-icon'>💡</Text>
          <Text className='menu-text'>关于</Text>
          <Text className='menu-arrow'>→</Text>
        </View>
      </View>
    </View>
  )
}
