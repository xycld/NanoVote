import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Poll } from '@/types/poll'

export const usePollStore = defineStore('poll', () => {
  const currentPoll = ref<Poll | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  const setPoll = (poll: Poll) => {
    currentPoll.value = poll
  }

  const updateOption = (optionId: number, votes: number) => {
    if (currentPoll.value) {
      const option = currentPoll.value.options.find(opt => opt.id === optionId)
      if (option) {
        option.votes = votes
      }
    }
  }

  const updateTotalVotes = (total: number) => {
    if (currentPoll.value) {
      currentPoll.value.total_votes = total
    }
  }

  const setVoted = (optionId: number) => {
    if (currentPoll.value) {
      currentPoll.value.has_voted = true
      currentPoll.value.voted_for = optionId
    }
  }

  const setLoading = (value: boolean) => {
    loading.value = value
  }

  const setError = (message: string | null) => {
    error.value = message
  }

  const reset = () => {
    currentPoll.value = null
    loading.value = false
    error.value = null
  }

  return {
    currentPoll,
    loading,
    error,
    setPoll,
    updateOption,
    updateTotalVotes,
    setVoted,
    setLoading,
    setError,
    reset
  }
})
