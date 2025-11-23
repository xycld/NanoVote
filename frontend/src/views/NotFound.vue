<template>
  <div class="min-h-screen flex items-center justify-center px-4">
    <div class="text-center">
      <h1 class="text-9xl font-bold text-gray-300">404</h1>
      <h2 class="text-2xl font-semibold text-gray-900 mt-4">页面未找到</h2>
      <p class="text-gray-600 mt-2">抱歉，您访问的页面不存在</p>
      <button
        class="mt-8 btn-primary"
        @click="$router.push('/')"
      >
        返回首页
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
// 404页面
</script>
