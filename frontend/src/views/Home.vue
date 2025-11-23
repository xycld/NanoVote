<template>
  <div class="w-full h-full flex flex-col animate-fade-in-up">
    <div class="bg-white/80 backdrop-blur-2xl rounded-[2.5rem] p-8 border border-white/60 shadow-[0_20px_40px_-12px_rgba(0,0,0,0.05)] ring-1 ring-black/[0.03] transition-all duration-500 h-full flex flex-col">

      <!-- 固定部分：错误提示 + 问题输入 -->
      <div class="flex-shrink-0">
        <!-- 错误提示 -->
        <Transition
          enter-active-class="transition ease-out duration-300"
          enter-from-class="opacity-0 -translate-y-2"
          enter-to-class="opacity-100 translate-y-0"
        >
          <div v-if="error" class="mb-6 p-3 bg-rose-50 text-rose-600 text-sm rounded-xl border border-rose-100">
            {{ error }}
          </div>
        </Transition>

        <!-- 问题输入 -->
        <div class="mb-6 group">
          <label class="block text-xs font-medium text-neutral-400 uppercase tracking-wider mb-2 ml-1 group-focus-within:text-black transition-colors duration-300">
            {{ t('home.questionLabel') }}
          </label>
          <div class="relative">
            <input
              v-model="title"
              type="text"
              maxlength="100"
              :placeholder="t('home.questionPlaceholder')"
              class="w-full bg-[#F9F9F9] text-xl font-medium text-neutral-900 placeholder:text-neutral-300/80 rounded-2xl px-5 py-4 border border-transparent outline-none focus:bg-white focus:shadow-[0_8px_30px_-4px_rgba(0,0,0,0.04)] focus:ring-1 focus:ring-black/5 transition-all duration-300 ease-out"
              autofocus
            >
          </div>
        </div>
      </div>

      <!-- 滚动部分：选项列表 -->
      <div class="flex-1 overflow-y-auto mb-6 min-h-0 px-1">
        <label class="block text-xs font-medium text-neutral-400 uppercase tracking-wider mb-3">
          {{ t('home.optionsLabel') }}
        </label>

        <div class="w-full options-scroll py-1">
          <div
            v-for="(opt, index) in options"
            :key="opt.id"
            :ref="el => { if (el && opt.isNew) { initNewOption(el, opt) } }"
            class="grid-animate overflow-hidden"
            :class="opt.deleting ? 'hidden' : (opt.isNew ? 'hidden' : 'visible')"
          >
            <div class="overflow-hidden">
              <div class="relative group">
                  <div class="absolute left-4 top-1/2 -translate-y-1/2 text-neutral-300 font-mono text-xs pointer-events-none transition-colors group-focus-within:text-neutral-400">
                    {{ String(index + 1).padStart(2, '0') }}
                  </div>

                  <input
                    v-model="opt.text"
                    type="text"
                    maxlength="50"
                    :placeholder="t('home.optionPlaceholder', { n: index + 1 })"
                    @keydown.enter.prevent="addOption"
                    class="w-full bg-white border border-neutral-200/60 text-neutral-800 text-sm font-medium rounded-xl pl-12 pr-10 py-3.5 outline-none focus:border-neutral-300 focus:ring-4 focus:ring-neutral-100 transition-all duration-200 placeholder:text-neutral-300"
                  >

                  <button
                    v-if="!opt.deleting && options.filter(o => !o.deleting).length > 2"
                    @click="removeOption(opt.id)"
                    class="absolute right-3 top-1/2 -translate-y-1/2 p-1.5 rounded-full text-neutral-300 hover:text-red-500 hover:bg-red-50 transition-all duration-200 opacity-0 group-hover:opacity-100 focus:opacity-100"
                  >
                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                    </svg>
                  </button>
                </div>
              </div>
            </div>

          <!-- 添加按钮 -->
          <button
            v-if="options.length < 20"
            @click="addOption"
            class="w-full mt-1 py-3.5 rounded-xl border border-dashed border-neutral-300 text-neutral-400 text-sm font-medium hover:border-neutral-400 hover:text-neutral-600 hover:bg-white/40 active:bg-neutral-50 transition-all duration-200 flex items-center justify-center gap-2 group"
          >
            <div class="w-5 h-5 rounded-full bg-neutral-100 flex items-center justify-center group-hover:bg-neutral-200 transition-colors">
              <svg class="w-3 h-3 text-neutral-500 group-hover:text-neutral-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
              </svg>
            </div>
            {{ t('home.addOption') }}
          </button>
        </div>
      </div>

      <!-- 固定部分：持续时间 + 提交按钮 -->
      <div class="flex-shrink-0">
        <!-- 持续时间选择 - 极致平滑下拉菜单 -->
        <div class="mb-4 relative group" ref="selectContainer">
          <label class="block text-xs font-medium text-neutral-400 uppercase tracking-wider mb-2 ml-1 group-focus-within:text-black transition-colors duration-300">
            {{ t('home.durationLabel') }}
          </label>

          <button
            @click="toggleDropdown"
            class="w-full bg-[#F9F9F9] text-left rounded-2xl px-5 py-4 flex items-center justify-between border border-transparent outline-none transition-all duration-300 ease-out"
            :class="isOpen
              ? 'bg-white shadow-[0_8px_30px_-4px_rgba(0,0,0,0.08)] ring-1 ring-black/5 scale-[1.01]'
              : 'hover:bg-white hover:shadow-[0_4px_20px_-4px_rgba(0,0,0,0.02)]'
            "
          >
            <span class="text-sm font-medium text-neutral-900 flex items-center gap-2">
              <svg class="w-4 h-4 text-neutral-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              {{ selectedLabel }}
            </span>
            <svg
              class="w-4 h-4 text-neutral-400 transition-transform duration-500 ease-[cubic-bezier(0.34,1.56,0.64,1)]"
              :class="isOpen ? 'rotate-180' : ''"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
            </svg>
          </button>

          <!-- 下拉选项列表 -->
          <div
            class="absolute left-0 w-full z-50 transition-[opacity,transform] duration-500 ease-[cubic-bezier(0.32,0.72,0,1)] will-change-transform"
            :class="[
              shouldOpenUpward ? 'bottom-full mb-2 origin-bottom' : 'top-full mt-2 origin-top',
              isOpen
                ? 'opacity-100 translate-y-0 scale-100 pointer-events-auto'
                : shouldOpenUpward
                  ? 'opacity-0 translate-y-4 scale-95 pointer-events-none'
                  : 'opacity-0 -translate-y-4 scale-95 pointer-events-none'
            ]"
          >
            <div
              ref="listRef"
              @mouseleave="handleMouseLeaveList"
              class="bg-white/95 rounded-2xl p-1.5 overflow-hidden relative antialiased border border-white/20 ring-1 ring-black/[0.04] shadow-[0_20px_40px_-12px_rgba(0,0,0,0.1),0_0_0_1px_rgba(255,255,255,0.5)_inset]"
            >
              <!-- 魔法悬浮光标 -->
              <div
                class="absolute left-1.5 right-1.5 rounded-xl bg-neutral-300 transition-all duration-300 ease-[cubic-bezier(0.2,0.8,0.2,1)] pointer-events-none"
                :style="{
                  top: `${hoverStyle.top}px`,
                  height: `${hoverStyle.height}px`,
                  opacity: hoverStyle.opacity,
                  zIndex: -1
                }"
              />

              <button
                v-for="option in DURATION_OPTIONS"
                :key="option.value"
                @click="selectOption(option.value)"
                @mouseenter="handleMouseEnter"
                class="w-full flex items-center justify-between px-4 py-3 rounded-xl text-sm font-medium transition-colors duration-200 relative z-10"
                :class="option.value === duration ? 'text-black' : 'text-neutral-600'"
              >
                <span :class="option.value === duration ? 'font-semibold' : ''">{{ option.label }}</span>
                <svg
                  v-if="option.value === duration"
                  class="w-3.5 h-3.5 animate-in zoom-in spin-in-45 duration-300"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
              </button>
            </div>
          </div>
        </div>

        <!-- 多选配置 -->
        <div class="mb-4">
          <Toggle
            label="Allow Multiple Choices"
            :checked="allowMultiple"
            @update:checked="allowMultiple = $event"
          />

          <!-- 平滑展开的步进器配置区域 -->
          <div
            class="grid transition-[grid-template-rows,opacity,margin] duration-500 ease-[cubic-bezier(0.2,0.8,0.2,1)]"
            :class="allowMultiple ? 'grid-rows-[1fr] opacity-100 mt-4' : 'grid-rows-[0fr] opacity-0 mt-0'"
          >
            <div class="overflow-hidden space-y-3 pl-1">
              <!-- 分割线装饰 -->
              <div class="w-full h-px bg-neutral-100 mb-4" />

              <NumberStepper
                label="Min Selection"
                :value="minSelection"
                @update:value="minSelection = $event"
                :min="1"
                :max="activeOptionCount"
              />

              <NumberStepper
                label="Max Selection"
                :value="maxSelection"
                @update:value="maxSelection = $event"
                :min="minSelection"
                :max="activeOptionCount"
              />
            </div>
          </div>
        </div>

        <!-- 提交按钮 -->
        <button
          @click="submit"
          :disabled="loading || !isFormValid"
          class="w-full h-14 rounded-[1.2rem] font-medium text-base flex items-center justify-center gap-2 transition-all duration-300 ease-out bg-black text-white shadow-[0_8px_20px_-6px_rgba(0,0,0,0.2)] hover:shadow-[0_12px_25px_-8px_rgba(0,0,0,0.3)] hover:scale-[1.02] active:scale-[0.98] disabled:opacity-50 disabled:hover:scale-100 disabled:shadow-none disabled:cursor-not-allowed"
        >
          <span v-if="!loading">{{ t('home.createPoll') }}</span>
          <svg v-if="!loading" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
          </svg>
          <svg v-if="loading" class="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { pollApi } from '@/utils/api'
import type { DurationOption } from '@/types/poll'
import Toggle from '@/components/Toggle.vue'
import NumberStepper from '@/components/NumberStepper.vue'

const router = useRouter()
const { t } = useI18n()

interface Option {
  id: number
  text: string
  isNew: boolean
  deleting: boolean
}

const options = ref<Option[]>([
  { id: 1, text: '', isNew: false, deleting: false },
  { id: 2, text: '', isNew: false, deleting: false }
])
const nextId = ref(3)
const title = ref('')
const duration = ref<DurationOption>('1d')
const loading = ref(false)
const error = ref('')

// 多选配置
const allowMultiple = ref(false)
const minSelection = ref(1)
const maxSelection = ref(2)

// 下拉菜单状态
const isOpen = ref(false)
const selectContainer = ref<HTMLElement | null>(null)
const listRef = ref<HTMLElement | null>(null)
const hoverStyle = ref({ top: 0, height: 0, opacity: 0 })
const shouldOpenUpward = ref(false)

// 持续时间选项
const DURATION_VALUES: DurationOption[] = ['3m', '30m', '1h', '6h', '1d', '3d', '7d', '10d']

const DURATION_OPTIONS = computed(() =>
  DURATION_VALUES.map(value => ({
    label: t(`home.duration.${value}`),
    value,
  }))
)

const selectedLabel = computed(() => {
  return t(`home.duration.${duration.value}`)
})

const isFormValid = computed(() => {
  const validOptions = options.value.filter(o => !o.deleting && o.text.trim())
  return title.value.trim().length > 0 && validOptions.length >= 2
})

// 有效选项数量（用于 NumberStepper 的 max 限制）
const activeOptionCount = computed(() => {
  return options.value.filter(o => !o.deleting).length
})

// 自动调整 max_selection 当它小于 min_selection 时
watch(minSelection, (newMin) => {
  if (newMin > maxSelection.value) {
    maxSelection.value = newMin
  }
})

const initNewOption = (el: Element | unknown, opt: Option) => {
  if (!(el instanceof Element)) return
  requestAnimationFrame(() => {
    el.classList.remove('hidden')
    el.classList.add('visible')
    opt.isNew = false
  })
}

const addOption = () => {
  if (options.value.length < 20) {
    options.value.push({
      id: nextId.value++,
      text: '',
      isNew: true,
      deleting: false
    })
  }
}

const removeOption = (id: number) => {
  const activeCount = options.value.filter(o => !o.deleting).length
  if (activeCount > 2) {
    const opt = options.value.find(o => o.id === id)
    if (opt) {
      opt.deleting = true
      setTimeout(() => {
        options.value = options.value.filter(o => o.id !== id)
      }, 500)
    }
  }
}

// 下拉菜单事件处理
const handleMouseEnter = (e: Event) => {
  if (!listRef.value) return
  const target = e.currentTarget as HTMLElement
  const listRect = listRef.value.getBoundingClientRect()
  const itemRect = target.getBoundingClientRect()

  // 修复：计算相对于列表容器的位置，并考虑 padding
  hoverStyle.value = {
    top: itemRect.top - listRect.top,
    height: itemRect.height,
    opacity: 1
  }
}

const handleMouseLeaveList = () => {
  hoverStyle.value = { ...hoverStyle.value, opacity: 0 }
}

const selectOption = (value: DurationOption) => {
  duration.value = value
  isOpen.value = false
}

// 检测是否需要向上展开（防止超出屏幕底部）
const checkDropdownPosition = () => {
  if (!selectContainer.value) return

  const rect = selectContainer.value.getBoundingClientRect()
  const dropdownHeight = 400 // 预估下拉菜单高度
  const spaceBelow = window.innerHeight - rect.bottom
  const spaceAbove = rect.top

  // 如果下方空间不足，且上方空间更多，则向上展开
  shouldOpenUpward.value = spaceBelow < dropdownHeight && spaceAbove > spaceBelow
}

// 打开下拉菜单时检测位置
const toggleDropdown = () => {
  if (!isOpen.value) {
    checkDropdownPosition()
  }
  isOpen.value = !isOpen.value
}

// 点击外部关闭下拉菜单
const handleClickOutside = (event: MouseEvent) => {
  if (selectContainer.value && !selectContainer.value.contains(event.target as Node)) {
    isOpen.value = false
  }
}

onMounted(() => {
  document.addEventListener('mousedown', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('mousedown', handleClickOutside)
})

const submit = async () => {
  const validOptions = options.value
    .filter(o => !o.deleting)
    .map(o => o.text.trim())
    .filter(text => text.length > 0)

  if (!title.value.trim() || validOptions.length < 2) return

  loading.value = true
  error.value = ''

  try {
    const requestData: any = {
      title: title.value.trim(),
      options: validOptions,
      duration: duration.value
    }

    // 如果启用了多选，添加多选配置
    if (allowMultiple.value) {
      requestData.allow_multiple = true
      requestData.min_selection = minSelection.value
      requestData.max_selection = maxSelection.value
    }

    const response = await pollApi.createPoll(requestData)

    // 跳转到投票页面
    router.push(`/p/${response.poll_id}`)
  } catch (err) {
    error.value = err instanceof Error ? err.message : t('home.createError')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.grid-animate {
  display: grid;
  transition: grid-template-rows 0.5s cubic-bezier(0.2,0.8,0.2,1), opacity 0.5s, margin 0.5s;
}

.grid-animate.visible {
  grid-template-rows: 1fr;
  opacity: 1;
  margin-bottom: 0.75rem;
}

.grid-animate.hidden {
  grid-template-rows: 0fr;
  opacity: 0;
  margin-bottom: 0;
}

/* 自定义滚动条样式 */
.options-scroll::-webkit-scrollbar {
  width: 6px;
}

.options-scroll::-webkit-scrollbar-track {
  background: transparent;
}

.options-scroll::-webkit-scrollbar-thumb {
  background: #d4d4d4;
  border-radius: 3px;
}

.options-scroll::-webkit-scrollbar-thumb:hover {
  background: #a3a3a3;
}

/* Firefox 滚动条样式 */
.options-scroll {
  scrollbar-width: thin;
  scrollbar-color: #d4d4d4 transparent;
}

.list-move,
.list-enter-active,
.list-leave-active {
  transition: all 0.5s ease;
}

.list-enter-from,
.list-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

.list-leave-active {
  position: absolute;
}
</style>
