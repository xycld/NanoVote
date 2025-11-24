import axios from 'axios'
import type {
  CreatePollRequest,
  CreatePollResponse,
  Poll,
  VoteRequest,
  VoteResponse
} from '@/types/poll'
import i18n from '@/i18n'

type ErrorDetail = {
  code?: string
  message?: string
  count?: number
  min?: number
  max?: number
}

const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

const codeKeyMap: Record<string, string> = {
  POLL_NOT_FOUND: 'errors.pollNotFound',
  ALREADY_VOTED: 'errors.alreadyVoted',
  INVALID_OPTION: 'errors.invalidOption',
  POLL_EXPIRED: 'errors.pollExpired',
  MULTIPLE_NOT_ALLOWED: 'errors.multipleNotAllowed',
  MIN_SELECTION: 'errors.minSelection',
  MAX_SELECTION: 'errors.maxSelection',
  MISSING_OPTION: 'errors.missingOption',
  CREATE_FAILED: 'errors.createFailed',
  VOTE_FAILED: 'errors.voteFailed'
}

const legacyMatchers: Array<{
  regex: RegExp
  key: string
  getParams?: (matches: RegExpMatchArray) => Record<string, unknown>
}> = [
  { regex: /投票不存在或已过期/, key: 'errors.pollNotFound' },
  { regex: /已经投过票/, key: 'errors.alreadyVoted' },
  { regex: /投票已过期/, key: 'errors.pollExpired' },
  { regex: /不允许多选/, key: 'errors.multipleNotAllowed' },
  {
    regex: /至少需要选择\s*(\d+)/,
    key: 'errors.minSelection',
    getParams: (m) => ({ count: Number(m[1]) || undefined })
  },
  {
    regex: /最多只能选择\s*(\d+)/,
    key: 'errors.maxSelection',
    getParams: (m) => ({ count: Number(m[1]) || undefined })
  },
  { regex: /无效的选项/, key: 'errors.invalidOption' },
  { regex: /必须提供 option_id/i, key: 'errors.missingOption' }
]

function translateApiError(detail: unknown): string {
  if (!detail) {
    return i18n.global.t('errors.network')
  }

  if (typeof detail === 'string') {
    for (const matcher of legacyMatchers) {
      const matches = detail.match(matcher.regex)
      if (matches) {
        const params = matcher.getParams ? matcher.getParams(matches) || {} : {}
        return i18n.global.t(matcher.key, params)
      }
    }
    return detail
  }

  if (typeof detail === 'object') {
    const { code, message, count, min, max } = detail as ErrorDetail

    if (code && codeKeyMap[code]) {
      const params = {
        count: count ?? min ?? max,
        min,
        max
      }
      return i18n.global.t(codeKeyMap[code], params)
    }

    if (message) {
      return message
    }
  }

  return i18n.global.t('errors.network')
}

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    const message = translateApiError(error.response?.data?.detail) || error.message || i18n.global.t('errors.network')
    console.error('API Error:', message)
    return Promise.reject(new Error(message))
  }
)

export const pollApi = {
  // 创建投票
  createPoll: (data: CreatePollRequest) =>
    api.post<CreatePollRequest, CreatePollResponse>('/polls', data),

  // 获取投票详情
  getPoll: (pollId: string) =>
    api.get<void, Poll>(`/polls/${pollId}`),

  // 投票
  vote: (pollId: string, data: VoteRequest) =>
    api.post<VoteRequest, VoteResponse>(`/polls/${pollId}/vote`, data)
}

export default api
