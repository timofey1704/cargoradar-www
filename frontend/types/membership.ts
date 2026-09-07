export interface MembershipInfo {
  subscription: SubscriptionRead | null
  days_left: number | null
  plans: Membership[]
}

export interface MembershipRead {
  id: number
  name: string
  description: string
}

export interface SubscriptionRead {
  id: number
  status: string
  subscription_start: string
  subscription_end: string
  auto_renewal: boolean
  membership: MembershipRead
}

export interface Membership {
  id: number
  name: string
  description: string
  price: number
  is_popular: boolean
  is_available: boolean
  is_trial: boolean
  features: Feature[]
}

interface Feature {
  id: number
  name: string
}
