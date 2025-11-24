<template>
  <div class="w-full h-full flex flex-col animate-fade-in-up">
    <div
      class="bg-white/70 backdrop-blur-2xl rounded-[2.5rem] p-8 border border-white/60 shadow-[0_20px_40px_-12px_rgba(0,0,0,0.05)] ring-1 ring-black/[0.03] transition-all duration-700 h-full flex flex-col"
      :class="voted ? 'scale-[1.01]' : ''"
    >
      <!-- 固定部分：标题 -->
      <div class="flex-shrink-0 mb-6 space-y-2 text-center">
        <!-- 多选标识 -->
        <div v-if="!loading && poll?.allow_multiple" class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-neutral-100/80 border border-neutral-200/50 mb-2">
          <span class="relative flex h-2 w-2">
            <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-black opacity-20"></span>
            <span class="relative inline-flex rounded-full h-2 w-2 bg-black"></span>
          </span>
          <span class="text-[10px] font-bold uppercase tracking-widest text-neutral-500">
            {{ t('poll.multipleChoice') }}
          </span>
        </div>

        <h1 class="text-2xl font-semibold text-neutral-900 tracking-tight leading-tight break-words">
          {{ loading ? t('common.loading') : poll?.title || '' }}
        </h1>

        <p v-if="!loading && poll && !poll.allow_multiple" class="mt-2 text-xs text-neutral-400 uppercase tracking-wider">
          {{ expiresText }}
        </p>

        <!-- 多选描述 -->
        <p v-if="!loading && poll?.allow_multiple" class="text-sm text-neutral-500">
          {{ getMultipleChoiceDesc() }}
          <span class="text-black font-medium">({{ selectedIds.length }}/{{ poll.max_selection }})</span>
        </p>
      </div>

      <!-- 滚动部分：加载状态 + 选项列表 -->
      <div class="flex-1 overflow-y-auto min-h-0 mb-6 px-1">
        <!-- 加载状态 -->
        <div v-if="loading" class="text-center py-8 text-neutral-400">
          <svg class="animate-spin w-5 h-5 mx-auto mb-2" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
        </div>

        <!-- 单选模式 -->
        <div v-if="!loading && poll && !poll.allow_multiple" class="space-y-3 py-1">
          <button
            v-for="opt in poll.options"
            :key="opt.id"
            @click="voteSingle(opt.id)"
            :disabled="voted"
            class="group relative w-full h-[72px] rounded-[1.2rem] overflow-hidden transition-all duration-500 ease-[cubic-bezier(0.23,1,0.32,1)] flex items-center px-1 outline-none focus-visible:ring-2 focus-visible:ring-black/20"
            :class="[
              selectedId === opt.id ? 'bg-black shadow-lg scale-[1.02]' : 'bg-white hover:bg-[#F9F9F9] shadow-sm border border-neutral-100',
              voted && selectedId !== opt.id ? 'opacity-40 scale-[0.98]' : 'opacity-100',
              voted ? 'cursor-default' : 'cursor-pointer'
            ]"
          >
            <!-- 进度条 -->
            <div
              v-if="showResults"
              class="absolute inset-0 z-0 transition-all duration-1000 ease-out origin-left progress-bar"
              :class="selectedId === opt.id ? 'bg-white/20' : 'bg-neutral-100'"
              :style="'--target-width: ' + Math.round(opt.votes / (poll.total_votes || 1) * 100) + '%'"
            ></div>

            <!-- 内容 -->
            <div class="relative z-10 w-full h-full flex items-center justify-between pl-6 pr-5">
              <span
                class="text-[15px] font-medium tracking-normal transition-colors duration-300 text-left"
                :class="selectedId === opt.id ? 'text-white' : 'text-neutral-900'"
              >
                {{ opt.text }}
              </span>

              <!-- 状态区 -->
              <div class="flex items-center">
                <!-- 未投票时的箭头 -->
                <div
                  v-if="!voted"
                  class="w-8 h-8 rounded-full flex items-center justify-center opacity-0 scale-50 group-hover:opacity-100 group-hover:scale-100 transition-all duration-300 ease-out"
                  :class="selectedId === opt.id ? 'bg-white/20' : 'bg-neutral-100'"
                >
                  <svg
                    class="w-4 h-4"
                    :class="selectedId === opt.id ? 'text-white' : 'text-neutral-900'"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
                  </svg>
                </div>

                <!-- 投票后显示百分比和票数 -->
                <div v-if="showResults" class="flex items-center gap-2">
                  <span
                    class="text-base font-medium tracking-tight tabular-nums"
                    :class="selectedId === opt.id ? 'text-white' : 'text-neutral-900'"
                  >
                    {{ Math.round(opt.votes / (poll.total_votes || 1) * 100) }}%
                  </span>
                  <span
                    class="text-xs text-opacity-70"
                    :class="selectedId === opt.id ? 'text-white' : 'text-neutral-500'"
                  >
                    ({{ opt.votes }})
                  </span>
                </div>

                <!-- 选中但未显示结果时的勾 -->
                <div v-if="voted && !showResults && selectedId === opt.id" class="animate-scale-in text-white">
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7"></path>
                  </svg>
                </div>
              </div>
            </div>

            <!-- 选中态光泽 -->
            <div
              v-if="selectedId === opt.id && !showResults"
              class="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent -skew-x-12 animate-shimmer pointer-events-none"
            ></div>
          </button>
        </div>

        <!-- 多选模式 -->
        <div v-if="!loading && poll && poll.allow_multiple" class="space-y-3 py-1">
          <button
            v-for="opt in poll.options"
            :key="opt.id"
            @click="toggleOption(opt.id)"
            :disabled="voted"
            class="group relative w-full p-4 min-h-[72px] rounded-[1.2rem] flex items-center justify-between overflow-hidden transition-all duration-300 ease-[cubic-bezier(0.23,1,0.32,1)] outline-none focus-visible:ring-2 focus-visible:ring-black/20"
            :class="[
              shakeId === opt.id ? 'animate-shake' : '',
              selectedIds.includes(opt.id)
                ? 'bg-black text-white shadow-[0_8px_20px_-6px_rgba(0,0,0,0.3)] scale-[1.02] z-10'
                : 'bg-white hover:bg-[#FAFAFA] text-neutral-900 shadow-sm border border-neutral-100 hover:border-neutral-200',
              !selectedIds.includes(opt.id) && selectedIds.length >= (poll.max_selection || 1) && !voted ? 'opacity-50 hover:opacity-100 cursor-not-allowed' : 'opacity-100',
              voted && !selectedIds.includes(opt.id) ? 'opacity-40 scale-[0.98]' : '',
              voted ? 'cursor-default' : ''
            ]"
          >
            <!-- 进度条（投票后显示）-->
            <div
              v-if="showResults"
              class="absolute inset-0 z-0 transition-all duration-1000 ease-out origin-left progress-bar"
              :class="selectedIds.includes(opt.id) ? 'bg-white/20' : 'bg-neutral-100'"
              :style="'--target-width: ' + Math.round(opt.votes / (poll.total_votes || 1) * 100) + '%'"
            ></div>

            <div class="flex items-center gap-4 relative z-10">
              <!-- 复选框指示器 -->
              <div
                class="w-6 h-6 rounded-full flex items-center justify-center transition-all duration-300"
                :class="selectedIds.includes(opt.id)
                  ? 'bg-white text-black scale-100'
                  : 'bg-transparent border border-neutral-200 group-hover:border-neutral-300 scale-90'
                "
              >
                <Check
                  class="w-3.5 h-3.5 transition-transform duration-300"
                  :class="selectedIds.includes(opt.id) ? 'scale-100' : 'scale-0'"
                  :stroke-width="3"
                />
              </div>

              <span
                class="text-[15px] font-medium text-left"
                :class="selectedIds.includes(opt.id) ? 'text-white' : 'text-neutral-700'"
              >
                {{ opt.text }}
              </span>
            </div>

            <!-- 投票后显示百分比和票数 -->
            <div v-if="showResults" class="flex items-center gap-2 relative z-10">
              <span
                class="text-base font-medium tracking-tight tabular-nums"
                :class="selectedIds.includes(opt.id) ? 'text-white' : 'text-neutral-900'"
              >
                {{ Math.round(opt.votes / (poll.total_votes || 1) * 100) }}%
              </span>
              <span
                class="text-xs text-opacity-70"
                :class="selectedIds.includes(opt.id) ? 'text-white' : 'text-neutral-500'"
              >
                ({{ opt.votes }})
              </span>
            </div>
          </button>
        </div>
      </div>

      <!-- 固定部分：底部信息 / 多选提交按钮 -->
      <div v-if="!loading" class="flex-shrink-0">
        <!-- 多选模式：提交按钮 -->
        <div
          v-if="poll?.allow_multiple"
          class="grid transition-[grid-template-rows,opacity,margin] duration-500 ease-[cubic-bezier(0.2,0.8,0.2,1)]"
          :class="selectedIds.length > 0 && !voted ? 'grid-rows-[1fr] opacity-100 mb-6' : 'grid-rows-[0fr] opacity-0 mb-0'"
        >
          <div class="overflow-hidden">
            <button
              @click="voteMultiple"
              :disabled="!isMultipleValid || isSubmitting"
              class="w-full h-14 rounded-[1.2rem] font-medium text-base flex items-center justify-center gap-2 transition-all duration-300 ease-out"
              :class="
                isMultipleValid
                  ? 'bg-black text-white shadow-lg hover:shadow-xl hover:scale-[1.02]'
                  : 'bg-neutral-100 text-neutral-400 cursor-not-allowed'
              "
            >
              <template v-if="isSubmitting">
                <div class="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              </template>
              <template v-else-if="isMultipleValid">
                <span>{{ t('poll.submitVotes', { count: selectedIds.length }, selectedIds.length) }}</span>
                <ArrowRight class="w-4 h-4" />
              </template>
              <template v-else>
                <span class="text-xs font-medium uppercase tracking-wider">
                  {{ t('poll.selectAtLeast', { count: minRequired }, minRequired) }}
                </span>
              </template>
            </button>

            <!-- 错误提示 -->
            <div
              v-if="!isMultipleValid && selectedIds.length > 0"
              class="mt-3 text-center text-xs text-neutral-400 flex items-center justify-center gap-1.5 animate-in fade-in slide-in-from-top-1"
            >
              <AlertCircle class="w-3 h-3" />
              <span>
                {{ t('poll.pickMore', { count: remainingToMin }, remainingToMin) }}
              </span>
            </div>
          </div>
        </div>

        <!-- 底部元信息 -->
        <div class="pt-6 flex items-center justify-between text-[10px] uppercase tracking-[0.2em] text-neutral-400 font-medium border-t border-neutral-100">
          <span class="flex items-center gap-2">
            <span
              class="w-1.5 h-1.5 rounded-full transition-colors duration-500"
              :class="voted ? 'bg-indigo-600' : 'bg-neutral-300'"
            ></span>
            <span>{{ voted ? t('poll.voteRecorded') : t('poll.anonymous') }}</span>
          </span>
          <button
            @click="share"
            class="hover:text-neutral-900 cursor-pointer transition-colors"
          >
            {{ shareText }}
          </button>
        </div>
      </div>
    </div>
    <ShareModal
      :open="isShareOpen"
      :url="shareUrl"
      @close="isShareOpen = false"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { Check, ArrowRight, AlertCircle } from 'lucide-vue-next'
import { pollApi } from '@/utils/api'
import { useWebSocket } from '@/composables/useWebSocket'
import ShareModal from '@/components/ShareModal.vue'
import type { Poll } from '@/types/poll'
import type { VoteUpdatePayload } from '@/composables/useWebSocket'

const route = useRoute()
const router = useRouter()
const { t } = useI18n()

const poll = ref<Poll | null>(null)
const loading = ref(true)
const voted = ref(false)
const selectedId = ref<number | null>(null) // 单选
const selectedIds = ref<number[]>([]) // 多选
const shakeId = ref<number | null>(null) // 震动动画
const showResults = ref(false)
const shareText = computed(() => t('common.share'))
const isSubmitting = ref(false)
const isShareOpen = ref(false)
const shareUrl = ref('')

// WebSocket
const { connect, disconnect, joinPoll, leavePoll, onVoteUpdate, offVoteUpdate } = useWebSocket()

const pollId = computed(() => route.params.id as string)
const minRequired = computed(() => poll.value?.min_selection || 1)
const remainingToMin = computed(() => Math.max(minRequired.value - selectedIds.value.length, 0))

// 多选验证
const isMultipleValid = computed(() => {
  if (!poll.value?.allow_multiple) return false
  const min = poll.value.min_selection || 1
  const max = poll.value.max_selection || poll.value.options.length
  return selectedIds.value.length >= min && selectedIds.value.length <= max
})

// 截止时间文本
const expiresText = computed(() => {
  if (!poll.value) return ''
  const expiresAt = new Date(poll.value.expires_at * 1000)
  const now = new Date()
  const remaining = expiresAt.getTime() - now.getTime()

  if (remaining <= 0) return t('poll.expired')

  const days = Math.floor(remaining / 86400000)
  const hours = Math.floor((remaining % 86400000) / 3600000)
  const minutes = Math.floor((remaining % 3600000) / 60000)

  if (days > 0) return t('poll.expiresIn', { time: t('poll.days', days) })
  if (hours > 0) return t('poll.expiresIn', { time: t('poll.hours', hours) })
  return t('poll.expiresIn', { time: t('poll.minutes', minutes) })
})

// 多选描述
const getMultipleChoiceDesc = () => {
  if (!poll.value) return ''
  const min = poll.value.min_selection || 1
  const max = poll.value.max_selection || poll.value.options.length

  if (min === max) {
    return t('poll.selectExactly', { count: min }, min)
  } else {
    return t('poll.selectBetween', { min, max })
  }
}

// 加载投票数据
const loadPoll = async () => {
  loading.value = true

  try {
    const data = await pollApi.getPoll(pollId.value)
    poll.value = data

    // 检查是否已投票（从服务器返回的状态）
    if (data.has_voted && data.voted_for) {
      voted.value = true

      if (data.allow_multiple && Array.isArray(data.voted_for)) {
        // 多选模式
        selectedIds.value = data.voted_for
      } else {
        // 单选模式
        selectedId.value = Array.isArray(data.voted_for) ? data.voted_for[0] : data.voted_for
      }
      showResults.value = true
    }

    // 连接WebSocket
    connect()
    joinPoll(pollId.value)

    // 监听实时更新
    onVoteUpdate((update: VoteUpdatePayload) => {
      if (poll.value && poll.value.options) {
        const option = poll.value.options.find(o => o.id === update.option_id)
        if (option) {
          option.votes = update.votes
        }
        poll.value.total_votes = update.total_votes
      }
    })

  } catch (err) {
    console.error('Poll load failed:', err)
    router.replace({ name: 'not-found' })
  } finally {
    loading.value = false
  }
}

// 单选投票
const voteSingle = async (optionId: number) => {
  if (voted.value || !poll.value) return

  selectedId.value = optionId
  voted.value = true

  // 乐观更新
  const opt = poll.value.options.find(o => o.id === optionId)
  if (opt) {
    opt.votes++
    poll.value.total_votes++
  }

  // 延迟显示结果
  setTimeout(() => {
    showResults.value = true
  }, 600)

  try {
    const response = await pollApi.vote(pollId.value, { option_id: optionId })

    // 同步服务器数据
    if (poll.value) {
      poll.value.options = response.options
      poll.value.total_votes = response.total_votes
    }

  } catch (err) {
    console.error('Vote submission failed:', err)
    // 回滚乐观更新
    if (opt) {
      opt.votes--
      if (poll.value) {
        poll.value.total_votes--
      }
    }
    voted.value = false
    selectedId.value = null
    showResults.value = false
    const message = err instanceof Error ? err.message : t('poll.voteFailed')
    alert(message)
  }
}

// 多选：切换选项
const toggleOption = (id: number) => {
  if (voted.value) return

  if (selectedIds.value.includes(id)) {
    // 取消选择
    selectedIds.value = selectedIds.value.filter(i => i !== id)
  } else {
    // 尝试选择
    const max = poll.value?.max_selection || poll.value?.options.length || 1
    if (selectedIds.value.length < max) {
      selectedIds.value = [...selectedIds.value, id]
    } else {
      // 超过最大限制：触发震动反馈
      triggerShake(id)
    }
  }
}

// 触发震动动画
const triggerShake = (id: number) => {
  shakeId.value = id
  setTimeout(() => {
    shakeId.value = null
  }, 500)
}

// 多选投票提交
const voteMultiple = async () => {
  if (!isMultipleValid.value || voted.value || !poll.value || isSubmitting.value) return

  isSubmitting.value = true

  try {
    const response = await pollApi.vote(pollId.value, { option_ids: selectedIds.value })

    // 更新状态
    voted.value = true
    if (poll.value) {
      poll.value.options = response.options
      poll.value.total_votes = response.total_votes
    }

    // 延迟显示结果
    setTimeout(() => {
      showResults.value = true
    }, 600)

  } catch (err) {
    console.error('Vote submission failed:', err)
    const message = err instanceof Error ? err.message : t('poll.voteFailed')
    alert(message)
  } finally {
    isSubmitting.value = false
  }
}

// 分享
const share = () => {
  if (typeof window !== 'undefined') {
    shareUrl.value = window.location.href
  }
  isShareOpen.value = true
}

onMounted(() => {
  if (typeof window !== 'undefined') {
    shareUrl.value = window.location.href
  }
  loadPoll()
})

onUnmounted(() => {
  if (poll.value) {
    leavePoll(pollId.value)
  }
  offVoteUpdate()
  disconnect()
})
</script>

<style scoped>
.progress-bar {
  animation: expandWidth 1.2s cubic-bezier(0.22, 1, 0.36, 1) forwards;
}

@keyframes expandWidth {
  from {
    width: 0%;
    opacity: 0;
  }
  to {
    width: var(--target-width);
    opacity: 1;
  }
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  20% { transform: translateX(-4px); }
  40% { transform: translateX(4px); }
  60% { transform: translateX(-2px); }
  80% { transform: translateX(2px); }
}

.animate-shake {
  animation: shake 0.4s cubic-bezier(.36,.07,.19,.97) both;
}
</style>
