import { useState, useCallback } from 'react'
import Taro, { useDidShow } from '@tarojs/taro'
import { View, Text, Image, Button, Input, ScrollView } from '@tarojs/components'
import { getUserState, setUserState } from '../../store/user'
import { getPendingAchievements, clearPendingAchievements } from '../../store/quiz'
import { api } from '../../services/api'
import type {
  UserStats,
  LevelInfo,
  LearningCalendar,
  Achievement,
  TrendDay,
  DomainStat,
  GoalData,
} from '../../types/quiz'
import { formatAccuracy, formatLevel, formatXpProgress, formatDate } from '../../utils/format'
import { computeLocalStats } from '../../utils/storage'
import knowledgeRobot from '../../assets/mascot/knowledge-robot.png'
import './profile.scss'

const WEEKDAYS = ['日', '一', '二', '三', '四', '五', '六']

const DOMAIN_COLORS: Record<string, string> = {
  '历史': 'var(--spell)',
  '科学': 'var(--correct)',
  '心理': 'var(--ember)',
  '生活': '#4A90D9',
  '数学': '#7C5CFC',
  '地理': '#3EC9A0',
  '文学': '#B8A9FF',
  '科技': '#4A90D9',
  '艺术': '#FF8C42',
  '其他': 'var(--ink-light)',
}

export default function Profile() {
  const [user, setUser] = useState(getUserState())
  const [stats, setStats] = useState<UserStats | null>(null)
  const [nicknameDraft, setNicknameDraft] = useState(getUserState().nickname)
  const [savingProfile, setSavingProfile] = useState(false)
  const [editingName, setEditingName] = useState(false)

  const [levelInfo, setLevelInfo] = useState<LevelInfo | null>(null)
  const [calendar, setCalendar] = useState<LearningCalendar | null>(null)
  const [achievements, setAchievements] = useState<Achievement[]>([])
  const [unlockedCount, setUnlockedCount] = useState(0)
  const [trends, setTrends] = useState<TrendDay[]>([])
  const [domains, setDomains] = useState<DomainStat[]>([])
  const [goal, setGoal] = useState<GoalData | null>(null)
  const [wrongCount, setWrongCount] = useState(0)
  const [trendRange, setTrendRange] = useState<7 | 30>(7)
  const now = new Date()
  const [calendarYear, setCalendarYear] = useState(now.getFullYear())
  const [calendarMonth, setCalendarMonth] = useState(now.getMonth() + 1)
  const [modalQueue, setModalQueue] = useState<Achievement[]>([])
  const [currentAchievement, setCurrentAchievement] = useState<Achievement | null>(null)

  const loadData = useCallback(() => {
    const currentUser = getUserState()
    setUser(currentUser)

    if (currentUser.isLoggedIn) {
      Promise.all([
        api.getProfile().catch(() => null),
        api.getStats().catch(() => null),
        api.getLevel().catch(() => null),
        api.getLearningCalendar(calendarYear, calendarMonth).catch(() => null),
        api.getAchievements().catch(() => null),
        api.getTrends(trendRange).catch(() => null),
        api.getDomains().catch(() => null),
        api.getGoal().catch(() => null),
        api.getWrongQuestions(50).catch(() => null),
      ]).then(([profile, statsData, levelData, calData, achData, trendData, domainData, goalData, wqData]) => {
        if (profile) {
          setUserState({ nickname: profile.nickname, avatar_url: profile.avatar_url })
          setUser(getUserState())
          setNicknameDraft(profile.nickname)
        }
        setStats(statsData || computeLocalStats())
        if (levelData) setLevelInfo(levelData)
        if (calData) setCalendar(calData)
        if (achData) {
          setAchievements(achData.items)
          setUnlockedCount(achData.unlocked_count)
        }
        if (trendData) setTrends(trendData.days)
        if (domainData) setDomains(domainData.domains)
        if (goalData) setGoal(goalData)
        if (wqData) setWrongCount(wqData.total)
      })
    } else {
      setStats(computeLocalStats())
    }
  }, [trendRange, calendarYear, calendarMonth])

  useDidShow(() => {
    loadData()
    const pending = getPendingAchievements()
    if (pending.length > 0) {
      clearPendingAchievements()
      const queue = [...pending]
      setCurrentAchievement(queue.shift()!)
      setModalQueue(queue)
    }
  })

  const readAvatarAsBase64 = (filePath: string): Promise<string> => new Promise((resolve, reject) => {
    Taro.getFileSystemManager().readFile({
      filePath,
      encoding: 'base64',
      success: result => typeof result.data === 'string' ? resolve(result.data) : reject(new Error('头像读取失败')),
      fail: reject,
    })
  })

  const uploadAvatar = async (filePath: string) => {
    if (!user.isLoggedIn || savingProfile) return
    const match = filePath.toLowerCase().match(/\.(png|jpe?g|webp)(?:\?|$)/)
    const fileType = (match?.[1] || 'jpg') as 'png' | 'jpg' | 'jpeg' | 'webp'
    setSavingProfile(true)
    Taro.showLoading({ title: '正在上传头像...' })
    try {
      const data = await readAvatarAsBase64(filePath)
      const profile = await api.uploadAvatar({ data, file_type: fileType })
      setUserState({ avatar_url: profile.avatar_url })
      setUser(getUserState())
      Taro.hideLoading()
      Taro.showToast({ title: '头像已更新', icon: 'success' })
    } catch (err) {
      Taro.hideLoading()
      Taro.showToast({ title: err instanceof Error ? err.message : '头像更新失败', icon: 'none' })
    } finally {
      setSavingProfile(false)
    }
  }

  const handleChooseAvatar = (event: { detail?: { avatarUrl?: string } }) => {
    const avatarUrl = event.detail?.avatarUrl
    if (avatarUrl) uploadAvatar(avatarUrl)
  }

  const handleAvatarFallback = async () => {
    if (Taro.getEnv() === Taro.ENV_TYPE.WEAPP) return
    try {
      const res = await Taro.chooseImage({ count: 1, sizeType: ['compressed'] })
      if (res.tempFilePaths[0]) await uploadAvatar(res.tempFilePaths[0])
    } catch {}
  }

  const handleSaveNickname = async () => {
    const nickname = nicknameDraft.trim()
    if (!nickname) {
      Taro.showToast({ title: '昵称不能为空', icon: 'none' })
      return
    }
    if (nickname.length > 64 || savingProfile) return
    setSavingProfile(true)
    try {
      const profile = await api.updateProfile({ nickname })
      setUserState({ nickname: profile.nickname })
      setUser(getUserState())
      setNicknameDraft(profile.nickname)
      Taro.showToast({ title: '昵称已保存', icon: 'success' })
    } catch (err) {
      Taro.showToast({ title: err instanceof Error ? err.message : '昵称保存失败', icon: 'none' })
    } finally {
      setSavingProfile(false)
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

  const handleAdjustGoal = () => {
    Taro.showActionSheet({
      itemList: ['每日 1 次', '每日 2 次', '每日 3 次', '每日 5 次'],
      success: async (res) => {
        const goals = [1, 2, 3, 5]
        const selected = goals[res.tapIndex]
        try {
          const data = await api.updateGoal(selected)
          setGoal(data)
          Taro.showToast({ title: '目标已更新', icon: 'success' })
        } catch {
          Taro.showToast({ title: '更新失败', icon: 'none' })
        }
      },
    })
  }

  const handleCalendarPrev = () => {
    const prevMonth = calendarMonth === 1 ? 12 : calendarMonth - 1
    const prevYear = calendarMonth === 1 ? calendarYear - 1 : calendarYear
    setCalendarYear(prevYear)
    setCalendarMonth(prevMonth)
  }

  const handleCalendarNext = () => {
    const nextMonth = calendarMonth === 12 ? 1 : calendarMonth + 1
    const nextYear = calendarMonth === 12 ? calendarYear + 1 : calendarYear
    setCalendarYear(nextYear)
    setCalendarMonth(nextMonth)
  }

  const defaultStats: UserStats = { total_quizzes: 0, total_questions: 0, avg_accuracy: 0, best_streak: 0, learning_days: 0 }
  const s = stats || defaultStats

  const calYear = calendar?.year || calendarYear
  const calMonth = calendar?.month || calendarMonth
  const firstDayOfWeek = new Date(calYear, calMonth - 1, 1).getDay()
  const calendarCells = [
    ...Array(firstDayOfWeek).fill(null),
    ...(calendar?.days || []),
  ]

  const maxTrendCount = Math.max(...trends.map(t => t.count), 1)
  const trendLabels = trends.map(t => {
    const parts = t.date.split('-')
    return `${parseInt(parts[2])}/${parseInt(parts[1])}`
  })

  const previewAchievements = achievements.slice(0, 5)

  const handleDismissAchievement = () => {
    if (modalQueue.length > 0) {
      const next = [...modalQueue]
      setCurrentAchievement(next.shift()!)
      setModalQueue(next)
    } else {
      setCurrentAchievement(null)
      setModalQueue([])
    }
  }

  return (
    <ScrollView className='profile-page' scrollY>
      {/* ── User card with level badge ── */}
      <View className='user-card'>
        <View className='avatar-container'>
          {user.isLoggedIn ? (
            <Button
              className='avatar-button'
              openType='chooseAvatar'
              onChooseAvatar={handleChooseAvatar}
              onClick={handleAvatarFallback}
              disabled={savingProfile}
            >
              <View className='avatar-wrap'>
                {user.avatar_url ? (
                  <Image className='avatar-image' src={user.avatar_url} mode='aspectFill' />
                ) : (
                  <View className='avatar-placeholder'>
                    <Image className='avatar-robot' src={knowledgeRobot} mode='aspectFit' />
                  </View>
                )}
                <View className='avatar-camera-overlay'>
                  <Text className='avatar-camera-icon'>📷</Text>
                </View>
              </View>
            </Button>
          ) : (
            <View className='avatar-wrap'>
              <View className='avatar-placeholder'>
                <Image className='avatar-robot' src={knowledgeRobot} mode='aspectFit' />
              </View>
            </View>
          )}
          {levelInfo && <View className='level-badge'>{levelInfo.level}</View>}
        </View>
        {user.isLoggedIn ? (
          <>
            {editingName ? (
              <View className='name-edit-bar'>
                <Input
                  className='name-edit-input'
                  type='nickname'
                  value={nicknameDraft}
                  maxlength={64}
                  focus
                  placeholder='输入新昵称'
                  onInput={event => setNicknameDraft(event.detail.value)}
                />
                <View
                  className={`name-save-btn ${savingProfile ? 'name-save-btn-disabled' : ''}`}
                  onClick={async () => {
                    await handleSaveNickname()
                    setEditingName(false)
                  }}
                >
                  <Text className='name-save-btn-text'>保存</Text>
                </View>
              </View>
            ) : (
              <View className='user-name-row' onClick={() => setEditingName(true)}>
                <Text className='user-name'>{user.nickname}</Text>
                <Text className='user-name-edit-icon'>✏️</Text>
              </View>
            )}
            {levelInfo && (
              <View className='xp-bar-wrap'>
                <View className='xp-bar-label'>
                  <Text className='xp-level-text'>{formatLevel(levelInfo.level, levelInfo.level_name)}</Text>
                  <Text className='xp-num-text'>{formatXpProgress(levelInfo.xp - levelInfo.current_level_xp, levelInfo.next_level_xp - levelInfo.current_level_xp)}</Text>
                </View>
                <View className='xp-bar-track'>
                  <View className='xp-bar-fill' style={{ width: `${Math.round(levelInfo.progress * 100)}%` }} />
                </View>
              </View>
            )}
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

      {/* ── Stats grid with colored gradient tops ── */}
      <View className='stats-section'>
        <View className='stats-grid'>
          <View className='stat-card stat-card-purple'>
            <Text className='stat-number'>{s.total_quizzes}</Text>
            <Text className='stat-label'>答题次数</Text>
          </View>
          <View className='stat-card stat-card-green'>
            <Text className='stat-number'>{s.total_questions}</Text>
            <Text className='stat-label'>答题总数</Text>
          </View>
          <View className='stat-card stat-card-orange'>
            <Text className='stat-number'>{formatAccuracy(s.avg_accuracy)}</Text>
            <Text className='stat-label'>平均正确率</Text>
          </View>
          <View className='stat-card stat-card-blue'>
            <Text className='stat-number'>{s.learning_days}</Text>
            <Text className='stat-label'>学习天数</Text>
          </View>
        </View>
      </View>

      {/* ── Daily goal ── */}
      {user.isLoggedIn && goal && (
        <View className='goal-row'>
          <View className='goal-ring' style={{ background: `conic-gradient(var(--spell) 0 ${Math.min(Math.round((goal.today_count / goal.daily_goal) * 100), 100)}%, rgba(124, 92, 252, 0.12) 0)` }}>
            <Text className='goal-ring-text'>{goal.today_count}/{goal.daily_goal}</Text>
          </View>
          <View className='goal-info'>
            <Text className='goal-title'>每日目标</Text>
            <Text className='goal-desc'>今日已完成 {goal.today_count} / {goal.daily_goal} 次闯关</Text>
          </View>
          <View className='goal-adjust' onClick={handleAdjustGoal}>
            <Text className='goal-adjust-text'>调整</Text>
          </View>
        </View>
      )}

      {/* ── Streak card ── */}
      {s.best_streak > 0 && (
        <View className='streak-card'>
          <Text className='streak-icon'>🔥</Text>
          <View className='streak-info'>
            <Text className='streak-title'>最佳连对纪录</Text>
            <Text className='streak-value'>连续答对 {s.best_streak} 题</Text>
          </View>
        </View>
      )}

      {/* ── Learning calendar ── */}
      {user.isLoggedIn && calendar && (
        <View className='calendar-card'>
          <View className='calendar-header'>
            <Text className='calendar-title'>📅 学习日历</Text>
            <View className='calendar-nav'>
              <Text className='calendar-nav-btn' onClick={handleCalendarPrev}>◀</Text>
              <Text className='calendar-nav-text'>{calYear}年{calMonth}月</Text>
              <Text className='calendar-nav-btn' onClick={handleCalendarNext}>▶</Text>
            </View>
          </View>
          <View className='calendar-weekdays'>
            {WEEKDAYS.map(d => <Text key={d} className='calendar-weekday'>{d}</Text>)}
          </View>
          <View className='calendar-days'>
            {calendarCells.map((cell, idx) => {
              if (!cell) return <View key={`e${idx}`} className='calendar-day empty' />
              const isToday = cell.date === `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`
              return (
                <View key={cell.date} className={`calendar-day ${cell.count > 0 ? 'has-learned' : ''} ${cell.high ? 'high' : ''} ${isToday ? 'today' : ''}`}>
                  <Text className='calendar-day-num'>{parseInt(cell.date.split('-')[2])}</Text>
                  {cell.count > 0 && <View className='calendar-dot' />}
                </View>
              )
            })}
          </View>
          <View className='calendar-streak'>
            <Text className='calendar-streak-text'>当前连续学习 <Text className='calendar-streak-num'>{calendar.current_streak}</Text> 天</Text>
          </View>
        </View>
      )}

      {/* ── Trends chart ── */}
      {user.isLoggedIn && trends.length > 0 && (
        <View className='trends-card'>
          <View className='trends-header'>
            <Text className='trends-title'>📊 学习趋势</Text>
            <View className='trends-toggle'>
              <Text className={`trends-toggle-item ${trendRange === 7 ? 'active' : ''}`} onClick={() => setTrendRange(7)}>7天</Text>
              <Text className={`trends-toggle-item ${trendRange === 30 ? 'active' : ''}`} onClick={() => setTrendRange(30)}>30天</Text>
            </View>
          </View>
          <View className='trends-chart'>
            {trends.map((t, i) => (
              <View key={t.date} className='trend-bar-wrap'>
                <View className={`trend-bar ${t.count === 0 ? 'empty-bar' : ''}`} style={{ height: `${Math.max((t.count / maxTrendCount) * 100, 5)}%` }} />
                <Text className='trend-label'>{trendLabels[i]}</Text>
              </View>
            ))}
          </View>
        </View>
      )}

      {/* ── Achievement preview ── */}
      {user.isLoggedIn && previewAchievements.length > 0 && (
        <View className='achievement-preview'>
          <View className='achievement-preview-header'>
            <Text className='achievement-preview-title'>🏅 成就徽章</Text>
            <Text className='achievement-preview-link' onClick={() => Taro.navigateTo({ url: '/pages/achievements/achievements' })}>查看全部 →</Text>
          </View>
          <View className='achievement-icons'>
            {previewAchievements.map(a => (
              <View key={a.id} className={`achievement-icon ${a.unlocked ? 'unlocked' : 'locked'}`}>
                <Text className='achievement-icon-text'>{a.icon}</Text>
              </View>
            ))}
          </View>
        </View>
      )}

      {/* ── Domain distribution ── */}
      {user.isLoggedIn && domains.length > 0 && (
        <View className='domain-card'>
          <Text className='domain-title'>🧠 知识领域分布</Text>
          {domains.map(d => (
            <View key={d.domain} className='domain-row'>
              <View className='domain-icon-wrap' style={{ background: `${DOMAIN_COLORS[d.domain] || 'var(--ink-light)'}1a` }}>
                <Text className='domain-icon-text'>{d.icon}</Text>
              </View>
              <Text className='domain-name'>{d.domain}</Text>
              <View className='domain-bar-track'>
                <View className='domain-bar-fill' style={{ width: `${Math.round(d.accuracy * 100)}%`, background: DOMAIN_COLORS[d.domain] || 'var(--ink-light)' }} />
              </View>
              <Text className='domain-pct'>{Math.round(d.accuracy * 100)}%</Text>
            </View>
          ))}
        </View>
      )}

      {/* ── Menu ── */}
      <View className='menu-section'>
        <View className='menu-item' onClick={() => Taro.switchTab({ url: '/pages/history/history' })}>
          <Text className='menu-icon'>📖</Text>
          <Text className='menu-text'>学习记录</Text>
          <Text className='menu-arrow'>→</Text>
        </View>
        <View className='menu-item' onClick={() => Taro.navigateTo({ url: '/pages/wrong-book/wrong-book' })}>
          <Text className='menu-icon'>❌</Text>
          <Text className='menu-text'>错题本</Text>
          {wrongCount > 0 && <View className='menu-badge'><Text className='menu-badge-text'>{wrongCount}</Text></View>}
          <Text className='menu-arrow'>→</Text>
        </View>
        <View className='menu-item' onClick={() => Taro.navigateTo({ url: '/pages/preferences/preferences' })}>
          <Text className='menu-icon'>🎨</Text>
          <Text className='menu-text'>兴趣偏好</Text>
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

      <View className='bottom-spacer' />

      {/* ── Achievement unlock modal ── */}
      {currentAchievement && (
        <View className='ach-modal-overlay' onClick={handleDismissAchievement}>
          <View className='ach-modal' onClick={e => e.stopPropagation()}>
            <Text className='ach-modal-emoji'>🎉</Text>
            <Text className='ach-modal-label'>解锁新成就</Text>
            <Text className='ach-modal-icon'>{currentAchievement.icon}</Text>
            <Text className='ach-modal-name'>{currentAchievement.name}</Text>
            <Text className='ach-modal-desc'>{currentAchievement.description}</Text>
            <View className='ach-modal-btn' onClick={handleDismissAchievement}>
              <Text className='ach-modal-btn-text'>太棒了！</Text>
            </View>
          </View>
        </View>
      )}
    </ScrollView>
  )
}
