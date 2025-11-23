<template>
  <div
    class="flex items-center justify-between py-3 group cursor-pointer"
    @click="emit('update:checked', !checked)"
  >
    <span class="text-sm font-medium text-neutral-600 group-hover:text-neutral-900 transition-colors">
      {{ label }}
    </span>
    <div
      class="w-11 h-6 rounded-full p-1 transition-colors duration-300 ease-out"
      :class="checked ? 'bg-black' : 'bg-neutral-200'"
    >
      <div
        class="bg-white w-4 h-4 rounded-full shadow-sm transition-transform duration-300 ease-[cubic-bezier(0.34,1.56,0.64,1)]"
        :class="checked ? 'translate-x-5' : 'translate-x-0'"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  label: string
  checked: boolean
}>()

const emit = defineEmits<{
  'update:checked': [value: boolean]
}>()
</script>
