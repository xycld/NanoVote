import axios from 'axios'
import type {
  CreatePollRequest,
  CreatePollResponse,
  Poll,
  VoteRequest,
  VoteResponse
} from '@/types/poll'
import i18n from '@/i18n'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

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
    const message = error.response?.data?.detail || error.message || i18n.global.t('errors.network')
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
