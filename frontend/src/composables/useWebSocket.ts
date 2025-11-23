import { ref, onUnmounted } from 'vue'
import { io, Socket } from 'socket.io-client'
import { useI18n } from 'vue-i18n'

export interface VoteUpdatePayload {
  option_id: number
  votes: number
  total_votes: number
}

export function useWebSocket() {
  const { t } = useI18n()
  const socket = ref<Socket | null>(null)
  const isConnected = ref(false)
  const error = ref<string | null>(null)

  const connect = () => {
    try {
      socket.value = io({
        path: '/socket.io',
        transports: ['websocket', 'polling'],
        reconnection: true,
        reconnectionAttempts: 5,
        reconnectionDelay: 1000
      })

      socket.value.on('connect', () => {
        isConnected.value = true
        error.value = null
        console.log('WebSocket connected')
      })

      socket.value.on('disconnect', () => {
        isConnected.value = false
        console.log('WebSocket disconnected')
      })

      socket.value.on('connect_error', (err) => {
        error.value = err.message
        console.error('WebSocket connection error:', err)
      })

    } catch (err) {
      error.value = err instanceof Error ? err.message : t('errors.websocketConnection')
      console.error('WebSocket error:', err)
    }
  }

  const disconnect = () => {
    if (socket.value) {
      socket.value.disconnect()
      socket.value = null
      isConnected.value = false
    }
  }

  const joinPoll = (pollId: string) => {
    if (socket.value && isConnected.value) {
      socket.value.emit('join_poll', { poll_id: pollId })
      console.log('Joined poll:', pollId)
    }
  }

  const leavePoll = (pollId: string) => {
    if (socket.value && isConnected.value) {
      socket.value.emit('leave_poll', { poll_id: pollId })
      console.log('Left poll:', pollId)
    }
  }

  const onVoteUpdate = (callback: (data: VoteUpdatePayload) => void) => {
    if (socket.value) {
      socket.value.on('vote_update', callback)
    }
  }

  const onPollExpired = (callback: () => void) => {
    if (socket.value) {
      socket.value.on('poll_expired', callback)
    }
  }

  const offVoteUpdate = () => {
    if (socket.value) {
      socket.value.off('vote_update')
    }
  }

  const offPollExpired = () => {
    if (socket.value) {
      socket.value.off('poll_expired')
    }
  }

  // 组件卸载时自动断开连接
  onUnmounted(() => {
    disconnect()
  })

  return {
    socket,
    isConnected,
    error,
    connect,
    disconnect,
    joinPoll,
    leavePoll,
    onVoteUpdate,
    onPollExpired,
    offVoteUpdate,
    offPollExpired
  }
}
