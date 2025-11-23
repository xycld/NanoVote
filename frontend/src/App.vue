<template>
  <div class="h-screen w-full bg-[#F5F5F7] text-neutral-900 antialiased flex flex-col items-center justify-center p-4 sm:p-6 relative overflow-hidden">
    <!-- 极简氛围光 -->
    <div class="absolute top-[-10%] left-[10%] md:left-[20%] w-[400px] md:w-[800px] h-[400px] md:h-[800px] bg-white rounded-full blur-[80px] md:blur-[120px] mix-blend-overlay pointer-events-none"></div>
    <div class="absolute bottom-[-10%] right-[10%] md:right-[20%] w-[300px] md:w-[600px] h-[300px] md:h-[600px] bg-indigo-100/40 rounded-full blur-[60px] md:blur-[100px] mix-blend-multiply pointer-events-none"></div>

    <main class="relative z-10 w-full max-w-[420px] max-h-[calc(100vh-2rem)] sm:max-h-[calc(100vh-3rem)] flex flex-col">
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
import { useMeta } from '@/composables/useMeta'

// 初始化元信息国际化
useMeta()
</script>
