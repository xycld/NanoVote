import { createRouter, createWebHistory } from 'vue-router'
import i18n from '@/i18n'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('@/views/Home.vue'),
      meta: {
        robots: 'index, follow'
      }
    },
    {
      path: '/p/:id',
      name: 'poll',
      component: () => import('@/views/PollView.vue'),
      meta: {
        robots: 'noindex, nofollow'
      }
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: () => import('@/views/NotFound.vue'),
      meta: {
        robots: 'noindex, nofollow'
      }
    }
  ]
})

// 路由守卫 - SEO和标题设置
router.afterEach((to) => {
  // 设置页面标题（使用i18n）
  const routeName = to.name as string
  const titleKey = `routes.${routeName === 'not-found' ? 'notFound' : routeName}.title`
  document.title = i18n.global.t(titleKey) || 'NanoVote'

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
