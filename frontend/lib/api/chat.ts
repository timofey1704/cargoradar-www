import { apiRequest } from '@/lib/api'

import type { ChatAttachment, ChatConversation, ChatMessage, CreateChatMessage } from '@/types/chat'

export const getChatConversations = (skip = 0, limit = 100) => {
  const params = new URLSearchParams({ skip: String(skip), limit: String(limit) })
  return apiRequest<ChatConversation[]>(`/conversations?${params.toString()}`)
}

export const getChatMessages = (conversationId: number, afterId?: number) => {
  const params = new URLSearchParams({ limit: '100' })
  if (afterId !== undefined) params.set('after_id', String(afterId))

  return apiRequest<ChatMessage[]>(`/conversations/${conversationId}/messages?${params.toString()}`)
}

export const createChatMessage = (conversationId: number, data: CreateChatMessage) => {
  return apiRequest<ChatMessage>(`/conversations/${conversationId}/messages`, {
    method: 'POST',
    body: data,
  })
}

export const markChatRead = (conversationId: number, lastReadId: number) => {
  return apiRequest<{ conversation_id: number; unread_count: number }>(
    `/conversations/${conversationId}/read`,
    {
      method: 'POST',
      body: { last_read_id: lastReadId },
    }
  )
}

export const uploadChatAttachment = (file: File) => {
  const body = new FormData()
  body.append('file', file)

  return apiRequest<ChatAttachment>('/attachments', {
    method: 'POST',
    body,
  })
}

export const getChatAttachmentUrl = (attachmentId: number) => {
  return apiRequest<{ url: string }>(`/attachments/${attachmentId}/url`)
}

export const getChatWebSocketUrl = () => {
  const url = new URL('/ws', process.env.NEXT_PUBLIC_API_URL)
  url.protocol = url.protocol === 'https:' ? 'wss:' : 'ws:'
  return url.toString()
}
