<template>
  <div class="w-full h-full flex flex-col animate-fade-in-up">
    <div
      class="bg-white/70 backdrop-blur-2xl rounded-[2.5rem] p-8 border border-white/60 shadow-[0_20px_40px_-12px_rgba(0,0,0,0.05)] ring-1 ring-black/[0.03] transition-all duration-700 h-full flex flex-col"
      :class="voted ? 'scale-[1.01]' : ''"
    >
      <!-- 固定部分：标题 -->
      <div class="flex-shrink-0 mb-6 text-center">
        <h1 class="text-xl font-medium text-neutral-900 tracking-tight leading-tight break-words">
          {{ loading ? '加载中...' : poll?.title || '' }}
        </h1>
        <p v-if="!loading && poll" class="mt-2 text-xs text-neutral-400 uppercase tracking-wider">
          {{ expiresText }}
        </p>
      </div>

      <!-- 滚动部分：加载状态 + 选项列表 -->
      <div class="flex-1 overflow-y-auto min-h-0 mb-6">
        <!-- 加载状态 -->
        <div v-if="loading" class="text-center py-8 text-neutral-400">
          <svg class="animate-spin w-5 h-5 mx-auto mb-2" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
        </div>

        <!-- 选项列表 -->
        <div v-if="!loading && poll" class="space-y-3 px-1">
          <button
            v-for="opt in poll.options"
            :key="opt.id"
            @click="vote(opt.id)"
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
      </div>

      <!-- 固定部分：底部信息 -->
      <div v-if="!loading" class="flex-shrink-0 pt-6 flex items-center justify-between text-[10px] uppercase tracking-[0.2em] text-neutral-400 font-medium border-t border-neutral-100">
        <span class="flex items-center gap-2">
          <span
            class="w-1.5 h-1.5 rounded-full transition-colors duration-500"
            :class="voted ? 'bg-indigo-600' : 'bg-neutral-300'"
          ></span>
          <span>{{ voted ? 'Vote Recorded' : 'Anonymous' }}</span>
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
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { pollApi } from '@/utils/api'
import { useWebSocket } from '@/composables/useWebSocket'
import type { Poll } from '@/types/poll'
import type { VoteUpdatePayload } from '@/composables/useWebSocket'

const route = useRoute()
const router = useRouter()

const poll = ref<Poll | null>(null)
const loading = ref(true)
const voted = ref(false)
const selectedId = ref<number | null>(null)
const showResults = ref(false)
const shareText = ref('SHARE')

// WebSocket
const { connect, disconnect, joinPoll, leavePoll, onVoteUpdate, offVoteUpdate } = useWebSocket()

const pollId = computed(() => route.params.id as string)

// 截止时间文本
const expiresText = computed(() => {
  if (!poll.value) return ''
  const expiresAt = new Date(poll.value.expires_at * 1000)
  const now = new Date()
  const remaining = expiresAt.getTime() - now.getTime()

  if (remaining <= 0) return 'Expired'

  const days = Math.floor(remaining / 86400000)
  const hours = Math.floor((remaining % 86400000) / 3600000)
  const minutes = Math.floor((remaining % 3600000) / 60000)

  if (days > 0) return `Expires in ${days} day${days > 1 ? 's' : ''}`
  if (hours > 0) return `Expires in ${hours} hour${hours > 1 ? 's' : ''}`
  return `Expires in ${minutes} minute${minutes > 1 ? 's' : ''}`
})

// 加载投票数据
const loadPoll = async () => {
  loading.value = true

  try {
    const data = await pollApi.getPoll(pollId.value)
    poll.value = data

    // 检查是否已投票（从服务器返回的状态）
    if (data.has_voted && data.voted_for) {
      voted.value = true
      selectedId.value = data.voted_for
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
    console.error('加载失败:', err)
    alert('投票不存在或已过期')
    router.push('/')
  } finally {
    loading.value = false
  }
}

// 投票
const vote = async (optionId: number) => {
  if (voted.value || !poll.value) return

  selectedId.value = optionId
  voted.value = true

  // 乐观更新
  const opt = poll.value.options.find(o => o.id === optionId)
  if (opt) {
    opt.votes++
    poll.value.total_votes++
  }

  // 延迟显示结果（匹配原设计的600ms延迟）
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
    console.error('投票失败:', err)
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
    alert('投票失败，请重试')
  }
}

// 分享
const share = async () => {
  const url = window.location.href
  try {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(url)
      shareText.value = 'COPIED'
    } else {
      // 降级方案
      const ta = document.createElement('textarea')
      ta.value = url
      ta.style.position = 'fixed'
      ta.style.left = '-9999px'
      document.body.appendChild(ta)
      ta.select()
      document.execCommand('copy')
      document.body.removeChild(ta)
      shareText.value = 'COPIED'
    }
    setTimeout(() => {
      shareText.value = 'SHARE'
    }, 2000)
  } catch {
    alert('复制失败，请手动复制链接')
  }
}

onMounted(() => {
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
</style>
