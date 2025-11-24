<template>
  <Teleport to="body">
    <div
      v-if="isMounted"
      :class="[
        'fixed inset-0 z-50 flex w-full h-full px-4 sm:px-6',
        isMobile ? 'items-end justify-center' : 'items-center justify-center'
      ]"
    >
      <div
        :class="[
          'absolute inset-0 bg-neutral-900/30 transition-opacity duration-500 ease-in-out',
          isVisible ? 'opacity-100' : 'opacity-0'
        ]"
        @click="close"
      />

      <div
        :class="[
          'relative z-10 w-full transition-all duration-500 ease-out',
          isMobile ? 'max-w-screen-sm' : 'max-w-[360px]'
        ]"
      >
        <div
          :class="[
            'relative bg-white/95 backdrop-blur-2xl shadow-[0_20px_50px_-12px_rgba(0,0,0,0.15)] ring-1 ring-white/50 ring-inset border border-white/20 antialiased flex flex-col items-center will-change-transform transition-all duration-500 ease-[cubic-bezier(0.2,0.8,0.2,1)]',
            isMobile
              ? [
                  'rounded-t-[1.75rem] rounded-b-none px-6 pt-4 pb-6 max-h-[78vh] w-full overflow-y-auto',
                  isVisible ? 'opacity-100 scale-100 translate-y-0' : 'opacity-0 scale-95 translate-y-8'
                ]
              : [
                  'rounded-[2.5rem] p-6',
                  isVisible ? 'opacity-100 scale-100 translate-y-0' : 'opacity-0 scale-95 translate-y-8'
                ]
          ]"
          :style="isMobile ? { paddingBottom: 'calc(env(safe-area-inset-bottom, 0px) + 20px)' } : undefined"
          role="dialog"
          aria-modal="true"
        >
          <div v-if="isMobile" class="w-12 h-1.5 rounded-full bg-neutral-200 mb-4" />

          <button
            class="absolute top-5 right-5 p-2 text-neutral-400 hover:text-neutral-900 transition-colors rounded-full hover:bg-neutral-100 active:scale-90 focus-visible:ring-2 focus-visible:ring-black/10"
            @click="close"
            :aria-label="t('common.close')"
          >
            <X class="w-5 h-5" />
          </button>

          <h2 class="text-lg font-semibold text-neutral-900 mb-8 tracking-tight">
            {{ t('poll.shareTitle') }}
          </h2>

          <div class="mb-8 w-full">
            <AestheticQRCode :url="url" />
          </div>

          <div class="w-full space-y-3">
            <div class="relative group">
              <div
                class="absolute inset-0 bg-neutral-100 rounded-2xl transform translate-y-1 transition-transform group-hover:translate-y-1.5"
                :class="isMobile ? 'rounded-3xl' : 'rounded-2xl'"
              />

              <button
                :class="copyButtonClass"
                @click="handleCopy"
              >
                <div class="flex items-center gap-3 overflow-hidden">
                  <div
                    :class="[
                      'relative w-9 h-9 shrink-0 rounded-full flex items-center justify-center transition-colors duration-500 ease-out',
                      copied ? 'bg-green-50 text-green-600' : 'bg-neutral-50 text-neutral-500'
                    ]"
                  >
                    <LinkIcon
                      class="absolute w-4 h-4 transition-all duration-500 ease-[cubic-bezier(0.34,1.56,0.64,1)]"
                      :class="copied ? 'scale-0 rotate-90 opacity-0' : 'scale-100 rotate-0 opacity-100'"
                    />
                    <Check
                      class="absolute w-4 h-4 transition-all duration-500 ease-[cubic-bezier(0.34,1.56,0.64,1)]"
                      :class="copied ? 'scale-100 rotate-0 opacity-100' : 'scale-0 -rotate-90 opacity-0'"
                    />
                  </div>

                  <div class="flex flex-col min-w-0">
                    <span class="text-[10px] font-bold uppercase tracking-wider text-neutral-400">
                      {{ t('poll.pollLink') }}
                    </span>
                    <span class="text-sm font-medium text-neutral-900 truncate pr-2 font-mono tracking-tight">
                      {{ displayUrl }}
                    </span>
                  </div>
                </div>

                <div class="relative h-7 min-w-[64px] overflow-hidden">
                  <div
                    :class="[
                      'relative w-full h-full transition-transform duration-500 ease-[cubic-bezier(0.34,1.56,0.64,1)]',
                      copied ? '-translate-y-full' : 'translate-y-0'
                    ]"
                  >
                    <div class="absolute top-0 left-0 w-full h-full flex items-center justify-center">
                      <span class="text-xs font-semibold px-2.5 py-1.5 rounded-lg bg-neutral-100 text-neutral-600 group-hover:bg-neutral-200 transition-colors">
                        {{ t('poll.copy') }}
                      </span>
                    </div>
                    <div class="absolute top-full left-0 w-full h-full flex items-center justify-center">
                      <span class="text-xs font-semibold px-2.5 py-1.5 rounded-lg bg-green-100 text-green-700">
                        {{ t('common.copied') }}
                      </span>
                    </div>
                  </div>
                </div>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { Check, Link as LinkIcon, X } from 'lucide-vue-next'

import AestheticQRCode from './AestheticQRCode.vue'

const props = defineProps<{
  open: boolean
  url: string
}>()

const emit = defineEmits<{
  (e: 'close'): void
}>()

const { t } = useI18n()

const copied = ref(false)
const isMobile = ref(false)
const isMounted = ref(false)
const isVisible = ref(false)
let copyTimer: number | undefined
let mediaQuery: MediaQueryList | null = null
let previousOverflow: string | null = null
let visibilityTimer: number | undefined
const handleMediaChange = (event: MediaQueryListEvent) => {
  syncIsMobile(event.matches)
}

const displayUrl = computed(() => props.url.replace(/^https?:\/\//, ''))
const copyButtonClass = computed(() =>
  [
    'relative w-full bg-white border border-neutral-200 flex items-center justify-between gap-3 text-left transition-transform active:translate-y-0.5 outline-none focus:ring-2 focus:ring-black/5',
    isMobile.value ? 'rounded-3xl px-5 py-4 text-base' : 'rounded-2xl px-4 py-3.5'
  ].join(' ')
)

const close = () => {
  emit('close')
}

const resetCopyTimer = () => {
  if (copyTimer) {
    window.clearTimeout(copyTimer)
  }
  copyTimer = window.setTimeout(() => {
    copied.value = false
  }, 2000)
}

const handleCopy = async () => {
  if (!props.url) return

  try {
    const ta = document.createElement('textarea')
    ta.value = props.url
    ta.style.position = 'fixed'
    ta.style.left = '-9999px'
    ta.style.top = '0'
    document.body.appendChild(ta)
    ta.focus()
    ta.select()
    document.execCommand('copy')
    document.body.removeChild(ta)

    copied.value = true
    resetCopyTimer()
  } catch {
    alert(t('poll.copyFailed'))
  }
}

const handleKeydown = (event: KeyboardEvent) => {
  if (event.key === 'Escape' && !isMobile.value) {
    close()
  }
}

const syncIsMobile = (matches: boolean) => {
  isMobile.value = matches
}

const setupMediaQuery = () => {
  if (typeof window === 'undefined') return
  mediaQuery = window.matchMedia('(max-width: 768px)')
  syncIsMobile(mediaQuery.matches)
  mediaQuery.addEventListener('change', handleMediaChange)
}

const lockScroll = () => {
  if (previousOverflow !== null) return
  previousOverflow = document.body.style.overflow
  document.body.style.overflow = 'hidden'
}

const unlockScroll = () => {
  if (previousOverflow === null) return
  document.body.style.overflow = previousOverflow
  previousOverflow = null
}

watch(
  () => props.open,
  (isOpen) => {
    if (isOpen) {
      isMounted.value = true
      if (visibilityTimer) {
        window.clearTimeout(visibilityTimer)
        visibilityTimer = undefined
      }
      window.setTimeout(() => {
        isVisible.value = true
      }, 50)
      document.addEventListener('keydown', handleKeydown)
      lockScroll()
    } else {
      isVisible.value = false
      document.removeEventListener('keydown', handleKeydown)
      unlockScroll()
      copied.value = false
      if (copyTimer) {
        window.clearTimeout(copyTimer)
        copyTimer = undefined
      }
      if (visibilityTimer) {
        window.clearTimeout(visibilityTimer)
      }
      visibilityTimer = window.setTimeout(() => {
        isMounted.value = false
        visibilityTimer = undefined
      }, 500)
    }
  }
)

onMounted(() => {
  setupMediaQuery()
})

onBeforeUnmount(() => {
  document.removeEventListener('keydown', handleKeydown)
  if (mediaQuery) {
    mediaQuery.removeEventListener('change', handleMediaChange)
  }
  unlockScroll()
  if (copyTimer) {
    window.clearTimeout(copyTimer)
    copyTimer = undefined
  }
  if (visibilityTimer) {
    window.clearTimeout(visibilityTimer)
    visibilityTimer = undefined
  }
})
</script>
