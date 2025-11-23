import { watch } from 'vue'
import { useI18n } from 'vue-i18n'

export function useMeta() {
  const { t, locale } = useI18n()

  const updateMeta = () => {
    // 更新 title
    document.title = t('meta.title')

    // 更新 html lang 属性
    document.documentElement.lang = locale.value === 'zh' ? 'zh-CN' : 'en'

    // 更新 meta description
    const metaDesc = document.querySelector('meta[name="description"]')
    if (metaDesc) {
      metaDesc.setAttribute('content', t('meta.description'))
    }

    // 更新 OG tags
    const ogTitle = document.querySelector('meta[property="og:title"]')
    if (ogTitle) {
      ogTitle.setAttribute('content', t('meta.ogTitle'))
    }

    const ogDesc = document.querySelector('meta[property="og:description"]')
    if (ogDesc) {
      ogDesc.setAttribute('content', t('meta.ogDescription'))
    }

    // 更新 OG locale
    const ogLocale = document.querySelector('meta[property="og:locale"]')
    if (ogLocale) {
      ogLocale.setAttribute('content', locale.value === 'zh' ? 'zh_CN' : 'en_US')
    }

    // 更新 Twitter tags
    const twitterTitle = document.querySelector('meta[name="twitter:title"]')
    if (twitterTitle) {
      twitterTitle.setAttribute('content', t('meta.ogTitle'))
    }

    const twitterDesc = document.querySelector('meta[name="twitter:description"]')
    if (twitterDesc) {
      twitterDesc.setAttribute('content', t('meta.ogDescription'))
    }
  }

  // 监听语言变化
  watch(locale, updateMeta, { immediate: true })

  return { updateMeta }
}
