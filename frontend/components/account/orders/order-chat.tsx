'use client'

import Image from 'next/image'
import { ArrowLeft, Check, CircleAlert, LoaderCircle, Paperclip, Send, X } from 'lucide-react'
import { useEffect, useRef, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import {
  createChatMessage,
  getChatAttachmentUrl,
  getChatConversations,
  getChatMessages,
  getChatWebSocketUrl,
  markChatRead,
  uploadChatAttachment,
} from '@/lib/api/chat'
import type { ChatAttachment, ChatMessage } from '@/types/chat'

interface OrderChatProps {
  orderId: number
  isOpen: boolean
}

interface ChatSocketEvent {
  type: string
  data?: {
    conversation_id?: number
  }
}

const CONVERSATIONS_KEY = (orderId: number) => ['chat', 'conversations', orderId] as const
const MESSAGES_KEY = (conversationId: number) => ['chat', 'messages', conversationId] as const
const EMPTY_MESSAGES: ChatMessage[] = []

const formatTime = (value: string) =>
  new Intl.DateTimeFormat('ru-RU', { hour: '2-digit', minute: '2-digit' }).format(new Date(value))

const getInitials = (name: string) =>
  name
    .split(/\s+/)
    .slice(0, 2)
    .map(part => part[0])
    .join('')
    .toUpperCase()

const getLastMessageLabel = (message: ChatMessage | null) => {
  if (!message) return 'Переписка началась'
  if (message.body) return message.body
  if (message.type === 'media') return 'Вложение'
  if (message.type === 'offer') return 'Предложение по заказу'
  return 'Системное сообщение'
}

export default function OrderChat({ orderId, isOpen }: OrderChatProps) {
  const queryClient = useQueryClient()
  const [selectedConversationId, setSelectedConversationId] = useState<number | null>(null)
  const [draft, setDraft] = useState('')
  const [files, setFiles] = useState<File[]>([])
  const [sendError, setSendError] = useState<string | null>(null)
  const [liveStatus, setLiveStatus] = useState<'connecting' | 'connected' | 'disconnected'>(
    'connecting'
  )
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const conversationsQuery = useQuery({
    queryKey: CONVERSATIONS_KEY(orderId),
    queryFn: async () => (await getChatConversations()).filter(item => item.order_id === orderId),
    enabled: isOpen,
  })
  const conversations = conversationsQuery.data ?? []
  const selectedConversation = conversations.find(item => item.id === selectedConversationId)

  const messagesQuery = useQuery({
    queryKey: MESSAGES_KEY(selectedConversationId ?? 0),
    queryFn: () => getChatMessages(selectedConversationId!),
    enabled: isOpen && selectedConversationId !== null,
  })
  const messages = messagesQuery.data ?? EMPTY_MESSAGES

  const sendMutation = useMutation({
    mutationFn: async () => {
      if (selectedConversationId === null) throw new Error('Не выбрана беседа')

      const uploadedAttachments = []
      for (const file of files) {
        uploadedAttachments.push(await uploadChatAttachment(file))
      }

      const body = draft.trim()
      return createChatMessage(selectedConversationId, {
        type: uploadedAttachments.length ? 'media' : 'text',
        body: body || undefined,
        attachment_ids: uploadedAttachments.map(attachment => attachment.id),
        idempotency_key: crypto.randomUUID(),
      })
    },
    onSuccess: message => {
      queryClient.setQueryData<ChatMessage[]>(MESSAGES_KEY(message.conversation_id), current => {
        if (!current || current.some(item => item.id === message.id)) return current
        return [...current, message]
      })
      void queryClient.invalidateQueries({ queryKey: CONVERSATIONS_KEY(orderId) })
      setDraft('')
      setFiles([])
      setSendError(null)
    },
    onError: error => {
      setSendError(error instanceof Error ? error.message : 'Не удалось отправить сообщение')
    },
  })

  useEffect(() => {
    if (!isOpen || !selectedConversationId) return
    if (selectedConversation && selectedConversation.unread_count > 0 && messages.length > 0) {
      void markChatRead(selectedConversationId, messages[messages.length - 1].id)
        .then(() => queryClient.invalidateQueries({ queryKey: CONVERSATIONS_KEY(orderId) }))
        .catch(() => undefined)
    }
  }, [isOpen, selectedConversationId, selectedConversation, messages, orderId, queryClient])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, selectedConversationId])

  useEffect(() => {
    if (!isOpen) return

    let shouldReconnect = true
    let authRetryAttempted = false
    let reconnectDelay = 1000
    let reconnectTimer: number | undefined
    let socket: WebSocket | undefined

    const connect = () => {
      setLiveStatus('connecting')
      socket = new WebSocket(getChatWebSocketUrl())

      socket.onopen = () => {
        reconnectDelay = 1000
        setLiveStatus('connected')
        socket?.send('ping')
        void queryClient.invalidateQueries({ queryKey: CONVERSATIONS_KEY(orderId) })
        void queryClient.invalidateQueries({ queryKey: ['chat', 'messages'] })
      }

      socket.onmessage = event => {
        try {
          const payload = JSON.parse(event.data) as ChatSocketEvent
          if (payload.type === 'pong') {
            authRetryAttempted = false
          } else if (payload.type === 'message.created' && payload.data?.conversation_id) {
            void queryClient.invalidateQueries({
              queryKey: MESSAGES_KEY(payload.data.conversation_id),
            })
            void queryClient.invalidateQueries({ queryKey: CONVERSATIONS_KEY(orderId) })
          } else if (payload.type === 'offer.updated') {
            void queryClient.invalidateQueries({ queryKey: CONVERSATIONS_KEY(orderId) })
            void queryClient.invalidateQueries({ queryKey: ['chat', 'messages'] })
          }
        } catch {
          // Ignore malformed or unrelated socket payloads.
        }
      }

      socket.onclose = event => {
        if (!shouldReconnect) return
        setLiveStatus('disconnected')
        if (event.code === 1008) {
          if (authRetryAttempted) return
          authRetryAttempted = true
          void getChatConversations()
            .then(() => {
              if (shouldReconnect) connect()
            })
            .catch(() => undefined)
          return
        }
        reconnectTimer = window.setTimeout(connect, reconnectDelay)
        reconnectDelay = Math.min(reconnectDelay * 2, 30000)
      }
    }

    connect()
    const heartbeatTimer = window.setInterval(() => {
      if (socket?.readyState === WebSocket.OPEN) socket.send('ping')
    }, 25000)

    return () => {
      shouldReconnect = false
      if (reconnectTimer !== undefined) window.clearTimeout(reconnectTimer)
      if (heartbeatTimer !== undefined) window.clearInterval(heartbeatTimer)
      socket?.close()
    }
  }, [isOpen, orderId, queryClient])

  const handleFilesSelected = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = Array.from(event.target.files ?? [])
    setFiles(current => [...current, ...selectedFiles].slice(0, 10))
    event.target.value = ''
  }

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if ((!draft.trim() && files.length === 0) || sendMutation.isPending) return
    sendMutation.mutate()
  }

  const liveLabel =
    liveStatus === 'connected'
      ? 'Онлайн'
      : liveStatus === 'connecting'
        ? 'Подключение…'
        : liveStatus === 'disconnected'
          ? 'Нет соединения'
          : 'Переподключение…'

  return (
    <section className="border-t border-gray-100 pt-5">
      <div className="flex items-center justify-between gap-3">
        <h3 className="text-text flex items-center gap-2 text-base font-semibold">
          <span>Чаты по заказу</span>
          {conversations.length > 0 && (
            <span className="rounded-full bg-gray-100 px-2 py-0.5 text-xs font-medium text-gray-600">
              {conversations.length}
            </span>
          )}
        </h3>
        <span
          className={`text-xs ${liveStatus === 'connected' ? 'text-green-700' : 'text-gray-400'}`}
          aria-live="polite"
        >
          {liveLabel}
        </span>
      </div>

      <div className="mt-3 grid min-h-80 overflow-hidden rounded-xl border border-gray-200 md:grid-cols-[minmax(13rem,0.8fr)_minmax(0,1.5fr)]">
        <div
          className={`border-gray-100 md:border-r ${selectedConversationId ? 'hidden md:block' : 'block'}`}
        >
          {conversationsQuery.isPending ? (
            <div className="flex h-40 items-center justify-center text-gray-400">
              <LoaderCircle size={22} className="animate-spin" />
            </div>
          ) : conversationsQuery.isError ? (
            <div className="flex items-start gap-2 p-4 text-sm text-red-700">
              <CircleAlert size={18} className="mt-0.5 shrink-0" />
              <p>Не удалось загрузить чаты. Закройте и снова откройте заказ.</p>
            </div>
          ) : conversations.length === 0 ? (
            <p className="p-4 text-sm text-gray-500">По этому заказу пока нет переписок.</p>
          ) : (
            <div className="divide-y divide-gray-100">
              {conversations.map(conversation => (
                <button
                  key={conversation.id}
                  type="button"
                  onClick={() => setSelectedConversationId(conversation.id)}
                  className={`flex w-full items-center gap-3 p-3 text-left transition-colors hover:bg-gray-50 ${selectedConversationId === conversation.id ? 'bg-orange-50' : 'bg-white'}`}
                >
                  <PeerAvatar
                    name={conversation.peer.name}
                    imageUrl={conversation.peer.image_url}
                  />
                  <span className="min-w-0 flex-1">
                    <span className="flex items-center justify-between gap-2">
                      <span className="text-text truncate text-sm font-medium">
                        {conversation.peer.name}
                      </span>
                      {conversation.last_message_at && (
                        <span className="shrink-0 text-xs text-gray-400">
                          {formatTime(conversation.last_message_at)}
                        </span>
                      )}
                    </span>
                    <span className="mt-1 flex items-center justify-between gap-2">
                      <span className="truncate text-xs text-gray-500">
                        {getLastMessageLabel(conversation.last_message)}
                      </span>
                      {conversation.unread_count > 0 && (
                        <span className="bg-orange flex size-5 shrink-0 items-center justify-center rounded-full text-[10px] font-semibold text-white">
                          {conversation.unread_count > 9 ? '9+' : conversation.unread_count}
                        </span>
                      )}
                    </span>
                  </span>
                </button>
              ))}
            </div>
          )}
        </div>

        <div className={`min-w-0 flex-col ${selectedConversationId ? 'flex' : 'hidden md:flex'}`}>
          {selectedConversation ? (
            <>
              <div className="flex items-center gap-3 border-b border-gray-100 px-3 py-2.5">
                <button
                  type="button"
                  onClick={() => setSelectedConversationId(null)}
                  className="rounded-md p-1 text-gray-500 hover:bg-gray-100 md:hidden"
                  aria-label="К списку чатов"
                >
                  <ArrowLeft size={18} />
                </button>
                <PeerAvatar
                  name={selectedConversation.peer.name}
                  imageUrl={selectedConversation.peer.image_url}
                />
                <p className="text-text truncate text-sm font-semibold">
                  {selectedConversation.peer.name}
                </p>
              </div>

              <div className="flex min-h-48 flex-1 flex-col gap-3 overflow-y-auto bg-gray-50/60 p-3">
                {messagesQuery.isPending ? (
                  <div className="flex flex-1 items-center justify-center text-gray-400">
                    <LoaderCircle size={22} className="animate-spin" />
                  </div>
                ) : messagesQuery.isError ? (
                  <p className="m-auto text-sm text-red-700">Не удалось загрузить сообщения.</p>
                ) : messages.length === 0 ? (
                  <p className="m-auto text-sm text-gray-500">Начните переписку.</p>
                ) : (
                  messages.map(message => <ChatMessageItem key={message.id} message={message} />)
                )}
                <div ref={messagesEndRef} />
              </div>

              <form onSubmit={handleSubmit} className="border-t border-gray-100 p-3">
                {files.length > 0 && (
                  <div className="mb-2 flex flex-wrap gap-2">
                    {files.map((file, index) => (
                      <span
                        key={`${file.name}-${file.lastModified}-${index}`}
                        className="flex max-w-full items-center gap-1 rounded-md bg-gray-100 py-1 pr-1 pl-2 text-xs text-gray-600"
                      >
                        <span className="max-w-40 truncate">{file.name}</span>
                        <button
                          type="button"
                          onClick={() => setFiles(current => current.filter((_, i) => i !== index))}
                          className="rounded p-1 hover:bg-gray-200"
                          aria-label={`Убрать файл ${file.name}`}
                        >
                          <X size={14} />
                        </button>
                      </span>
                    ))}
                  </div>
                )}
                {sendError && <p className="mb-2 text-xs text-red-700">{sendError}</p>}
                <div className="flex items-end gap-2">
                  <label className="cursor-pointer rounded-md p-2 text-gray-500 transition-colors hover:bg-gray-100 hover:text-gray-800 has-disabled:pointer-events-none has-disabled:opacity-50">
                    <Paperclip size={18} />
                    <span className="sr-only">Добавить фото или видео</span>
                    <input
                      type="file"
                      accept="image/*,video/*"
                      multiple
                      disabled={sendMutation.isPending || files.length >= 10}
                      onChange={handleFilesSelected}
                      className="sr-only"
                    />
                  </label>
                  <textarea
                    value={draft}
                    onChange={event => setDraft(event.target.value)}
                    maxLength={4000}
                    rows={1}
                    placeholder="Написать сообщение…"
                    className="focus:border-orange max-h-28 min-h-10 min-w-0 flex-1 resize-y rounded-lg border border-gray-200 px-3 py-2 text-sm outline-none"
                    disabled={sendMutation.isPending}
                  />
                  <button
                    type="submit"
                    disabled={sendMutation.isPending || (!draft.trim() && files.length === 0)}
                    className="bg-orange flex size-10 shrink-0 items-center justify-center rounded-lg text-white transition-colors hover:bg-[#e65322] disabled:cursor-not-allowed disabled:opacity-50"
                    aria-label="Отправить сообщение"
                  >
                    {sendMutation.isPending ? (
                      <LoaderCircle size={18} className="animate-spin" />
                    ) : (
                      <Send size={17} />
                    )}
                  </button>
                </div>
              </form>
            </>
          ) : (
            <p className="m-auto hidden px-4 text-center text-sm text-gray-500 md:block">
              Выберите чат, чтобы посмотреть сообщения.
            </p>
          )}
        </div>
      </div>
    </section>
  )
}

function PeerAvatar({ name, imageUrl }: { name: string; imageUrl: string | null }) {
  if (imageUrl) {
    return (
      <Image
        src={imageUrl}
        alt=""
        width={40}
        height={40}
        unoptimized
        className="size-10 shrink-0 rounded-full object-cover"
      />
    )
  }

  return (
    <span className="text-orange flex size-10 shrink-0 items-center justify-center rounded-full bg-orange-50 text-sm font-semibold">
      {getInitials(name)}
    </span>
  )
}

function ChatMessageItem({ message }: { message: ChatMessage }) {
  const isMine = message.sender_type === 'client'

  if (message.type === 'system') {
    return (
      <p className="mx-auto max-w-[90%] rounded-full bg-gray-100 px-3 py-1.5 text-center text-xs text-gray-500">
        {message.body ?? 'Системное сообщение'}
      </p>
    )
  }

  return (
    <div className={`flex ${isMine ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-[85%] rounded-xl px-3 py-2 ${isMine ? 'rounded-br-sm bg-orange-500 text-white' : 'rounded-bl-sm bg-white text-gray-800 shadow-sm'}`}
      >
        {message.type === 'offer' ? (
          <p className="text-sm font-medium">
            Предложение по заказу{message.offer_id ? ` #${message.offer_id}` : ''}
          </p>
        ) : null}
        {message.body && (
          <p className="text-sm wrap-break-word whitespace-pre-wrap">{message.body}</p>
        )}
        {message.attachments.map(attachment => (
          <ChatAttachmentItem key={attachment.id} attachment={attachment} isMine={isMine} />
        ))}
        <p
          className={`mt-1 flex items-center justify-end gap-1 text-[10px] ${isMine ? 'text-white/75' : 'text-gray-400'}`}
        >
          {formatTime(message.created_at)}
          {isMine && <Check size={12} />}
        </p>
      </div>
    </div>
  )
}

function ChatAttachmentItem({
  attachment,
  isMine,
}: {
  attachment: ChatAttachment
  isMine: boolean
}) {
  const [url, setUrl] = useState<string | null>(null)

  useEffect(() => {
    let isActive = true
    getChatAttachmentUrl(attachment.id)
      .then(result => {
        if (isActive) setUrl(new URL(result.url, process.env.NEXT_PUBLIC_API_URL).toString())
      })
      .catch(() => undefined)

    return () => {
      isActive = false
    }
  }, [attachment.id])

  if (!url) {
    return (
      <p className={`mt-2 text-xs ${isMine ? 'text-white/80' : 'text-gray-500'}`}>
        Загрузка вложения…
      </p>
    )
  }

  if (attachment.content_type.startsWith('image/')) {
    return (
      <a href={url} target="_blank" rel="noreferrer" className="mt-2 block">
        <Image
          src={url}
          alt="Вложение из чата"
          width={attachment.width ?? 640}
          height={attachment.height ?? 480}
          unoptimized
          className="max-h-64 w-auto rounded-lg object-contain"
        />
      </a>
    )
  }

  if (attachment.content_type.startsWith('video/')) {
    return <video src={url} controls className="mt-2 max-h-64 max-w-full rounded-lg" />
  }

  return (
    <a
      href={url}
      target="_blank"
      rel="noreferrer"
      className={`mt-2 flex items-center gap-2 text-xs underline ${isMine ? 'text-white' : 'text-orange'}`}
    >
      <Paperclip size={14} />
      Открыть вложение
    </a>
  )
}
