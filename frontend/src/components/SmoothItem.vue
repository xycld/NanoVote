<template>
  <div
    class="grid transition-[grid-template-rows,opacity,margin] duration-500 ease-[cubic-bezier(0.2,0.8,0.2,1)]"
    :class="isVisible ? 'grid-rows-[1fr] opacity-100 mb-3' : 'grid-rows-[0fr] opacity-0 mb-0'"
  >
    <div class="overflow-hidden">
      <slot />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'

const props = defineProps<{
  isNew?: boolean
  isDeleted?: boolean
}>()

const isVisible = ref(!props.isNew)

onMounted(() => {
  if (props.isNew) {
    requestAnimationFrame(() => {
      isVisible.value = true
    })
  }
})

watch(() => props.isDeleted, (deleted) => {
  if (deleted) {
    isVisible.value = false
  }
})
</script>
