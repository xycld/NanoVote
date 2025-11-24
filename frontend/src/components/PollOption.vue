<template>
  <div
    class="poll-option"
    :class="{
      'opacity-50': disabled,
      'cursor-not-allowed': disabled,
      'cursor-pointer hover:border-primary-500 hover:shadow-md': !disabled && !showResults,
      'border-primary-600 bg-primary-50': isSelected && showResults
    }"
    @click="handleClick"
  >
    <div class="flex items-center justify-between mb-2">
      <span class="font-medium text-gray-800">{{ option.text }}</span>
      <span v-if="showResults" class="text-sm font-semibold text-primary-700">
        {{ percentage }}%
      </span>
    </div>

    <!-- 投票数和进度条 -->
    <div v-if="showResults" class="space-y-2">
      <div class="flex items-center justify-between text-sm text-gray-600">
        <span>{{ t('poll.votesCount', { count: option.votes }, option.votes) }}</span>
      </div>

      <!-- 进度条 -->
      <div class="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
        <div
          class="h-full rounded-full transition-all duration-600 ease-out"
          :class="isSelected ? 'bg-primary-600' : 'bg-primary-400'"
          :style="{ width: percentage + '%' }"
        />
      </div>
    </div>

    <!-- 选中标记 -->
    <div v-if="isSelected && showResults" class="absolute top-3 right-3">
      <svg class="w-6 h-6 text-primary-600" fill="currentColor" viewBox="0 0 20 20">
        <path
          fill-rule="evenodd"
          d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
          clip-rule="evenodd"
        />
      </svg>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { PollOption as PollOptionType } from '@/types/poll'

interface Props {
  option: PollOptionType
  totalVotes: number
  showResults?: boolean
  isSelected?: boolean
  disabled?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  showResults: false,
  isSelected: false,
  disabled: false
})

const emit = defineEmits<{
  vote: [optionId: number]
}>()

const { t } = useI18n()

const percentage = computed(() => {
  if (props.totalVotes === 0) return 0
  return Math.round((props.option.votes / props.totalVotes) * 100)
})

const handleClick = () => {
  if (!props.disabled && !props.showResults) {
    emit('vote', props.option.id)
  }
}
</script>

<style scoped>
.poll-option {
  @apply relative p-4 border-2 border-gray-200 rounded-xl
         transition-all duration-200
         bg-white;
}
</style>
