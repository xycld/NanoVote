export interface PollOption {
  id: number
  text: string
  votes: number
}

export interface Poll {
  poll_id: string
  title: string
  options: PollOption[]
  total_votes: number
  expires_at: number
  has_voted: boolean
  voted_for: number | null | number[]
  allow_multiple?: boolean
  min_selection?: number
  max_selection?: number
}

export interface CreatePollRequest {
  title: string
  options: string[]
  duration: DurationOption
  allow_multiple?: boolean
  min_selection?: number
  max_selection?: number
}

export interface CreatePollResponse {
  poll_id: string
  url: string
  expires_at: number
}

export interface VoteRequest {
  option_id?: number
  option_ids?: number[]
}

export interface VoteResponse {
  success: boolean
  options: PollOption[]
  total_votes: number
}

export type DurationOption = '3m' | '30m' | '1h' | '6h' | '1d' | '3d' | '7d' | '10d'

export const DURATION_OPTIONS: { value: DurationOption; label: string }[] = [
  { value: '3m', label: '3分钟' },
  { value: '30m', label: '30分钟' },
  { value: '1h', label: '1小时' },
  { value: '6h', label: '6小时' },
  { value: '1d', label: '1天' },
  { value: '3d', label: '3天' },
  { value: '7d', label: '7天' },
  { value: '10d', label: '10天' }
]
