export type ChatActorType = 'client' | 'executor' | 'system'
export type ChatMessageType = 'text' | 'media' | 'offer' | 'system'

export interface ChatAttachment {
  id: number
  url: string
  content_type: string
  size: number
  width: number | null
  height: number | null
  created_at: string
}

export interface ChatMessage {
  id: number
  conversation_id: number
  sender_type: ChatActorType
  sender_client_id: number | null
  sender_executor_id: number | null
  type: ChatMessageType
  body: string | null
  offer_id: number | null
  attachments: ChatAttachment[]
  created_at: string
}

export interface ChatConversation {
  id: number
  order_id: number
  peer: {
    id: number
    name: string
    image_url: string | null
  }
  order: {
    id: number
    origin_address: string
    destination_address: string
    cargo_type: string
  }
  last_message: ChatMessage | null
  unread_count: number
  last_message_at: string | null
  created_at: string
}

export interface CreateChatMessage {
  type: 'text' | 'media'
  body?: string | null
  attachment_ids?: number[]
  idempotency_key?: string
}

export interface CreateOrderOffer {
  price: number
}

export interface OrderOffer {
  id: number
  conversation_id: number
  price: string
  currency: string
  terms: string | null
  status: 'pending' | 'accepted' | 'declined' | 'countered' | 'withdrawn' | 'expired'
  created_at: string
}
