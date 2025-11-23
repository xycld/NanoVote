<template>
  <div class="flex items-center justify-between py-1">
    <span class="text-xs font-medium text-neutral-400 uppercase tracking-wider pl-1">
      {{ label }}
    </span>
    <div class="flex items-center gap-3 bg-[#F9F9F9] rounded-xl p-1 border border-transparent hover:border-neutral-200 transition-colors duration-200">
      <button
        @click.stop="handleDecrement"
        :disabled="value <= min"
        class="w-8 h-8 flex items-center justify-center rounded-lg bg-white shadow-[0_1px_2px_rgba(0,0,0,0.05)] border border-neutral-100 text-neutral-600 hover:text-black disabled:opacity-30 disabled:cursor-not-allowed disabled:hover:text-neutral-600 transition-all active:scale-95 active:shadow-none"
      >
        <Minus class="w-3.5 h-3.5" />
      </button>
      <span class="w-5 text-center text-sm font-bold text-neutral-900 tabular-nums">
        {{ value }}
      </span>
      <button
        @click.stop="handleIncrement"
        :disabled="value >= max"
        class="w-8 h-8 flex items-center justify-center rounded-lg bg-white shadow-[0_1px_2px_rgba(0,0,0,0.05)] border border-neutral-100 text-neutral-600 hover:text-black disabled:opacity-30 disabled:cursor-not-allowed disabled:hover:text-neutral-600 transition-all active:scale-95 active:shadow-none"
      >
        <Plus class="w-3.5 h-3.5" />
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Plus, Minus } from 'lucide-vue-next'

const props = defineProps<{
  label: string
  value: number
  min: number
  max: number
}>()

const emit = defineEmits<{
  'update:value': [value: number]
}>()

const handleDecrement = () => {
  if (props.value > props.min) {
    emit('update:value', props.value - 1)
  }
}

const handleIncrement = () => {
  if (props.value < props.max) {
    emit('update:value', props.value + 1)
  }
}
</script>
