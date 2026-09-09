import { useState, useCallback } from 'react'
import Taro, { useDidShow } from '@tarojs/taro'
import { View, Text, ScrollView } from '@tarojs/components'
import { api } from '../../services/api'
import { setCurrentQuiz } from '../../store/quiz'
import { clearQuizProgress } from '../../utils/storage'
import type { Document } from '../../types/quiz'
import './index.scss'

export default function Knowledge() {
  const [documents, setDocuments] = useState<Document[]>([])
  const [uploading, setUploading] = useState(false)

  const loadDocuments = useCallback(async () => {
    try {
      const data = await api.getDocuments()
      setDocuments(data.items)
    } catch {
      Taro.showToast({ title: '加载失败', icon: 'none' })
    }
  }, [])

  useDidShow(() => { loadDocuments() })

  const handleUpload = async () => {
    try {
      const res = await Taro.chooseMessageFile({
        count: 1,
        type: 'file',
        extension: ['pdf', 'docx', 'txt', 'md'],
      })

      const file = res.tempFiles[0]
      if (!file) return

      setUploading(true)
      Taro.showLoading({ title: '正在上传解析...' })

      await api.uploadDocument(file.path, file.name)

      Taro.hideLoading()
      Taro.showToast({ title: '上传成功', icon: 'success' })
      loadDocuments()
    } catch (err) {
      Taro.hideLoading()
      Taro.showModal({
        title: '上传失败',
        content: err instanceof Error ? err.message : '请稍后重试',
        showCancel: false,
      })
    } finally {
      setUploading(false)
    }
  }

  const handleDelete = async (doc: Document) => {
    const confirmed = await Taro.showModal({
      title: '删除文档',
      content: `确定删除「${doc.original_filename}」？`,
    })
    if (!confirmed.confirm) return

    try {
      await api.deleteDocument(doc.id)
      setDocuments(prev => prev.filter(d => d.id !== doc.id))
      Taro.showToast({ title: '已删除', icon: 'success' })
    } catch {
      Taro.showToast({ title: '删除失败', icon: 'none' })
    }
  }

  const handleClearAll = async () => {
    if (documents.length === 0) return

    const confirmed = await Taro.showModal({
      title: '清空知识库',
      content: `确定删除全部 ${documents.length} 个文档？此操作不可恢复。`,
    })
    if (!confirmed.confirm) return

    try {
      Taro.showLoading({ title: '正在清空...' })
      await api.clearDocuments()
      setDocuments([])
      Taro.hideLoading()
      Taro.showToast({ title: '已清空', icon: 'success' })
    } catch {
      Taro.hideLoading()
      Taro.showToast({ title: '清空失败', icon: 'none' })
    }
  }

  const handleGenerateQuiz = async (doc: Document) => {
    try {
      Taro.showLoading({ title: '正在生成题目...' })
      const textData = await api.getDocumentText(doc.id)
      if (!textData.text_content || textData.text_content.length < 50) {
        Taro.hideLoading()
        Taro.showToast({ title: '文档内容过少', icon: 'none' })
        return
      }

      const content = textData.text_content.slice(0, 12000)
      const generated = await api.generate(content)
      const data = { ...generated, source_content: content }
      setCurrentQuiz(data)
      clearQuizProgress()
      Taro.hideLoading()
      Taro.navigateTo({ url: '/pages/quiz/quiz' })
    } catch (err) {
      Taro.hideLoading()
      Taro.showModal({
        title: '生成失败',
        content: err instanceof Error ? err.message : '请稍后重试',
        showCancel: false,
      })
    }
  }

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes}B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)}KB`
    return `${(bytes / (1024 * 1024)).toFixed(1)}MB`
  }

  const getFileTypeIcon = (type: string) => {
    const icons: Record<string, string> = {
      '.pdf': '📕',
      '.docx': '📘',
      '.txt': '📄',
      '.md': '📝',
    }
    return icons[type] || '📄'
  }

  return (
    <View className='knowledge-page'>
      <View className='kb-header'>
        <Text className='kb-title'>我的知识库</Text>
        <Text className='kb-subtitle'>上传文档，基于自己的资料生成题目</Text>
      </View>

      <View className='kb-upload-area' onClick={handleUpload}>
        <Text className='kb-upload-icon'>{uploading ? '⏳' : '📤'}</Text>
        <Text className='kb-upload-text'>{uploading ? '上传中...' : '点击上传文档'}</Text>
        <Text className='kb-upload-hint'>支持 PDF、Word、TXT、MD 格式，最大10MB</Text>
      </View>

      {documents.length > 0 && (
        <View className='kb-toolbar'>
          <Text className='kb-toolbar-count'>{documents.length} 个文档</Text>
          <Text className='kb-toolbar-clear' onClick={handleClearAll}>清空全部</Text>
        </View>
      )}

      <ScrollView className='kb-list' scrollY>
        {documents.length === 0 ? (
          <View className='kb-empty'>
            <Text className='kb-empty-icon'>📚</Text>
            <Text className='kb-empty-text'>还没有上传文档</Text>
            <Text className='kb-empty-hint'>上传课件、笔记或教材，开始学习</Text>
          </View>
        ) : (
          documents.map(doc => (
            <View key={doc.id} className='kb-card'>
              <View className='kb-card-header'>
                <Text className='kb-card-icon'>{getFileTypeIcon(doc.file_type)}</Text>
                <View className='kb-card-info'>
                  <Text className='kb-card-name'>{doc.original_filename}</Text>
                  <Text className='kb-card-meta'>
                    {formatFileSize(doc.file_size)} · {doc.text_length}字 · {doc.file_type}
                  </Text>
                </View>
              </View>
              <View className='kb-card-actions'>
                <Text
                  className='kb-action kb-action-primary'
                  onClick={() => handleGenerateQuiz(doc)}
                >🎯 生成题目</Text>
                <Text
                  className='kb-action kb-action-danger'
                  onClick={() => handleDelete(doc)}
                >🗑️ 删除</Text>
              </View>
            </View>
          ))
        )}
      </ScrollView>
    </View>
  )
}
