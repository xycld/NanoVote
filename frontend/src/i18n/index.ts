import { createI18n } from 'vue-i18n'
import en from './locales/en'
import zh from './locales/zh'

// 获取浏览器语言或本地存储的语言偏好
function getLocale(): string {
  const stored = localStorage.getItem('locale')
  if (stored && ['en', 'zh'].includes(stored)) {
    return stored
  }

  const browserLang = navigator.language.toLowerCase()
  if (browserLang.startsWith('zh')) {
    return 'zh'
  }
  return 'en'
}

const i18n = createI18n({
  legacy: false, // 使用 Composition API 模式
  locale: getLocale(),
  fallbackLocale: 'en',
  messages: {
    en,
    zh,
  },
})

// 切换语言并保存到本地存储
export function setLocale(locale: 'en' | 'zh') {
  i18n.global.locale.value = locale
  localStorage.setItem('locale', locale)
}

export default i18n
