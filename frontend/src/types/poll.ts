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
