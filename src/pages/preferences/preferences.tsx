import { useState, useEffect } from 'react'
import Taro from '@tarojs/taro'
import { View, Text } from '@tarojs/components'
import { api } from '../../services/api'
import './preferences.scss'

const ALL_PREFERENCES = [
  { label: '📖 历史', value: '历史' },
  { label: '🔬 科学', value: '科学' },
  { label: '🧠 心理学', value: '心理学' },
  { label: '📐 数学', value: '数学' },
  { label: '🌍 地理', value: '地理' },
  { label: '🎨 艺术', value: '艺术' },
  { label: '💻 科技', value: '科技' },
  { label: '☕ 生活', value: '生活' },
  { label: '🎵 音乐', value: '音乐' },
  { label: '📖 文学', value: '文学' },
  { label: '🏥 医学', value: '医学' },
  { label: '⚽ 体育', value: '体育' },
]

export default function Preferences() {
  const [selected, setSelected] = useState<string[]>([])
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    api.getPreferences().then(data => {
      setSelected(data.preferences)
    }).catch(() => {})
  }, [])

  const togglePref = (value: string) => {
    setSelected(prev =>
      prev.includes(value)
        ? prev.filter(v => v !== value)
        : [...prev, value]
    )
  }

  const handleSave = async () => {
    if (saving) return
    setSaving(true)
    try {
      await api.updatePreferences(selected)
      Taro.showToast({ title: '偏好已保存', icon: 'success' })
      setTimeout(() => Taro.navigateBack(), 1200)
    } catch {
      Taro.showToast({ title: '保存失败', icon: 'none' })
    } finally {
      setSaving(false)
    }
  }

  return (
    <View className='preferences-page'>
      <Text className='pref-desc'>选择你感兴趣的领域，我们会优先为你推荐相关主题。</Text>

      <View className='pref-grid'>
        {ALL_PREFERENCES.map(p => (
          <Text
            key={p.value}
            className={`pref-tag ${selected.includes(p.value) ? 'selected' : ''}`}
            onClick={() => togglePref(p.value)}
          >{p.label}</Text>
        ))}
      </View>

      <View className='pref-save'>
        <View className={`pref-save-btn ${saving ? 'disabled' : ''}`} onClick={handleSave}>
          <Text className='pref-save-text'>保存偏好</Text>
        </View>
      </View>
    </View>
  )
}
