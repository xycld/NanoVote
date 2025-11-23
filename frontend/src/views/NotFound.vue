<template>
  <div class="w-full h-full flex flex-col items-center justify-center animate-fade-in-up">
    <div
      class="relative bg-white/80 backdrop-blur-2xl rounded-[2.5rem] p-10 border border-white/60 shadow-[0_20px_40px_-12px_rgba(0,0,0,0.05)] ring-1 ring-black/[0.03] flex flex-col items-center text-center max-w-[400px] w-full"
    >

      <!-- 1. 视觉核心：虚空图标 -->
      <div class="relative mb-8 group cursor-default">
        <!-- 脉冲光环 -->
        <div class="absolute inset-0 bg-neutral-100 rounded-full blur-xl animate-pulse-slow opacity-50" />

        <!-- 图标容器：凹陷质感 -->
        <div class="relative w-24 h-24 rounded-full bg-[#F0F0F2] shadow-[inset_0_2px_4px_rgba(0,0,0,0.06)] flex items-center justify-center border border-white/50">
          <div class="relative z-10">
            <!-- SearchX Icon (lucide) -->
            <svg class="w-10 h-10 text-neutral-400/80 group-hover:scale-110 transition-transform duration-500 ease-out" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" viewBox="0 0 24 24">
              <circle cx="11" cy="11" r="8" />
              <path d="m21 21-4.3-4.3" />
              <path d="m8.5 8.5 5 5" />
              <path d="m13.5 8.5-5 5" />
            </svg>
          </div>

          <!-- 装饰性粒子 -->
          <svg class="absolute top-5 right-5 w-3 h-3 text-neutral-300 animate-bounce-slow" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
          </svg>
          <svg class="absolute bottom-5 left-5 w-3 h-3 text-neutral-300 animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
        </div>
      </div>

      <!-- 2. 状态文本 -->
      <div class="space-y-3 mb-10 max-w-[280px]">
        <h1 class="text-3xl font-semibold text-neutral-900 tracking-tight">
          {{ t('notFound.title') }}
        </h1>
        <p class="text-sm text-neutral-500 leading-relaxed">
          {{ t('notFound.description') }}
        </p>
      </div>

      <!-- 3. 行动按钮 -->
      <div class="w-full">
        <button
          @click="$router.push('/')"
          class="w-full h-14 rounded-[1.2rem] font-medium text-base flex items-center justify-center gap-2 transition-all duration-300 ease-out bg-black text-white shadow-[0_8px_20px_-6px_rgba(0,0,0,0.2)] hover:shadow-[0_12px_25px_-8px_rgba(0,0,0,0.3)] hover:scale-[1.02] active:scale-[0.98] group"
        >
          <span>{{ t('notFound.createNew') }}</span>
          <svg class="w-4 h-4 group-hover:translate-x-0.5 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
          </svg>
        </button>
      </div>

      <!-- 底部装饰：条形码风格 -->
      <div class="mt-8 flex gap-1 opacity-20">
        <div
          v-for="i in 5"
          :key="i"
          class="h-1 rounded-full bg-neutral-900 animate-pulse"
          :style="{ width: `${Math.random() * 20 + 4}px`, animationDelay: `${i * 0.1}s` }"
        />
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
</script>

<style scoped>
@keyframes pulse-slow {
  0%, 100% {
    opacity: 0.3;
    transform: scale(1);
  }
  50% {
    opacity: 0.6;
    transform: scale(1.05);
  }
}

@keyframes bounce-slow {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-3px);
  }
}

.animate-pulse-slow {
  animation: pulse-slow 4s ease-in-out infinite;
}

.animate-bounce-slow {
  animation: bounce-slow 3s ease-in-out infinite;
}
</style>
