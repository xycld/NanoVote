import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('@/views/Home.vue'),
      meta: {
        title: 'NanoVote - 极简投票系统',
        robots: 'index, follow'
      }
    },
    {
      path: '/p/:id',
      name: 'poll',
      component: () => import('@/views/PollView.vue'),
      meta: {
        title: '投票页面',
        robots: 'noindex, nofollow'
      }
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: () => import('@/views/NotFound.vue'),
      meta: {
        title: '页面未找到',
        robots: 'noindex, nofollow'
      }
    }
  ]
})

// 路由守卫 - SEO和标题设置
router.afterEach((to) => {
  // 设置页面标题
  document.title = (to.meta.title as string) || 'NanoVote'

  // 设置robots meta标签
  const robotsMeta = document.querySelector('meta[name="robots"]')
  if (robotsMeta) {
    robotsMeta.setAttribute('content', (to.meta.robots as string) || 'noindex, nofollow')
  } else {
    const meta = document.createElement('meta')
    meta.name = 'robots'
    meta.content = (to.meta.robots as string) || 'noindex, nofollow'
    document.head.appendChild(meta)
  }
})

export default router
