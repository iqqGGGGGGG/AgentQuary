export function formatDuration(seconds: number): string {
  if (seconds < 60) return `${seconds} 秒`
  const min = Math.floor(seconds / 60)
  const sec = seconds % 60
  return sec > 0 ? `${min} 分 ${sec} 秒` : `${min} 分钟`
}

export function formatAccuracy(accuracy: number): string {
  return `${Math.round(accuracy * 100)}%`
}

export function formatTime(timestamp: number): string {
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)

  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes} 分钟前`
  if (hours < 24) return `${hours} 小时前`
  return `${date.getMonth() + 1}月${date.getDate()}日`
}

export function formatLevel(level: number, levelName: string): string {
  return `Lv.${level} ${levelName}`
}

export function formatXpProgress(current: number, needed: number): string {
  return `${current} / ${needed} XP`
}

export function formatDate(dateStr: string): string {
  const parts = dateStr.split('-')
  if (parts.length === 3) return `${parseInt(parts[1])}月${parseInt(parts[2])}日`
  return dateStr
}
