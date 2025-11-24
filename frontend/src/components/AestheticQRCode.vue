<template>
  <div
    class="w-48 h-48 bg-white/95 rounded-[1.5rem] p-4 shadow-[0_18px_40px_-12px_rgba(0,0,0,0.18)] border border-white/50 ring-1 ring-white/50 ring-inset flex items-center justify-center relative overflow-hidden transition-all duration-500 hover:shadow-[0_22px_50px_-14px_rgba(0,0,0,0.22)] mx-auto"
  >
    <div class="absolute inset-0 bg-[radial-gradient(#e5e7eb_1px,transparent_1px)] [background-size:8px_8px] opacity-40" />

    <div v-if="loading" class="w-8 h-8 border-2 border-neutral-100 border-t-neutral-300 rounded-full animate-spin" />
    <svg
      v-else-if="modules && size"
      :viewBox="`0 0 ${size} ${size}`"
      :class="[
        'w-full h-full',
        qrVisible ? 'animate-in fade-in zoom-in duration-700 ease-out opacity-100' : 'opacity-0'
      ]"
    >
      <rect :width="size" :height="size" fill="white" />

      <template v-for="(row, rIndex) in modules" :key="`row-${rIndex}`">
        <template v-for="(isDark, cIndex) in row" :key="`cell-${rIndex}-${cIndex}`">
          <circle
            v-if="isDark && !isFinderPattern(rIndex, cIndex) && !isCenterLogoZone(rIndex, cIndex)"
            :cx="cIndex + 0.5"
            :cy="rIndex + 0.5"
            r="0.45"
            class="fill-neutral-900"
          />
        </template>
      </template>

      <g v-for="(pos, idx) in finderPositions" :key="`finder-${idx}`" :transform="`translate(${pos.x}, ${pos.y})`">
        <rect x="0" y="0" width="7" height="7" rx="2" class="fill-neutral-900" />
        <rect x="1" y="1" width="5" height="5" rx="1.2" class="fill-white" />
        <rect x="2" y="2" width="3" height="3" rx="0.8" class="fill-neutral-900" />
      </g>
    </svg>

    <div class="absolute inset-0 flex items-center justify-center pointer-events-none">
      <img
        :src="faviconUrl"
        alt="Logo"
        class="w-11 h-11 object-contain animate-in zoom-in delay-200 duration-500 drop-shadow-[0_4px_12px_rgba(0,0,0,0.18)]"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'

const props = defineProps<{
  url: string
}>()

type QRMatrix = boolean[][]

type QRCodeFactory = (
  typeNumber: number,
  errorCorrectionLevel: 'L' | 'M' | 'Q' | 'H'
) => {
  addData: (data: string) => void
  make: () => void
  getModuleCount: () => number
  isDark: (row: number, col: number) => boolean
}

declare global {
  interface Window {
    qrcode?: QRCodeFactory
  }
}

const modules = ref<QRMatrix | null>(null)
const size = ref(21)
const loading = ref(true)
const centerRadius = ref(2.2)
const qrVisible = ref(false)
const faviconUrl = ref('/logo.svg')

let qrScriptPromise: Promise<void> | null = null

const loadQrEngine = async () => {
  if (window.qrcode) return

  if (!qrScriptPromise) {
    qrScriptPromise = new Promise((resolve, reject) => {
      const script = document.createElement('script')
      script.src = 'https://cdnjs.cloudflare.com/ajax/libs/qrcode-generator/1.4.4/qrcode.min.js'
      script.async = true
      script.onload = () => resolve()
      script.onerror = () => reject(new Error('QR script failed to load'))
      document.body.appendChild(script)
    })
  }

  await qrScriptPromise
}

const generateQr = async () => {
  if (!props.url) return
  loading.value = true
  qrVisible.value = false

  try {
    await loadQrEngine()
    if (!window.qrcode) throw new Error('QR engine unavailable')

    const qr = window.qrcode(0, 'H')
    qr.addData(props.url)
    qr.make()

    const count = qr.getModuleCount()
    const matrix: QRMatrix = []

    for (let r = 0; r < count; r++) {
      const row: boolean[] = []
      for (let c = 0; c < count; c++) {
        row.push(qr.isDark(r, c))
      }
      matrix.push(row)
    }

    modules.value = matrix
    size.value = count
  } catch (error) {
    console.error('QR generation failed', error)
    modules.value = null
  } finally {
    loading.value = false
    setTimeout(() => {
      qrVisible.value = true
    }, 50)
  }
}

const finderPositions = computed(() => [
  { x: 0, y: 0 },
  { x: size.value - 7, y: 0 },
  { x: 0, y: size.value - 7 },
])

const isFinderPattern = (r: number, c: number) => {
  if (r < 7 && c < 7) return true
  if (r < 7 && c > size.value - 8) return true
  if (r > size.value - 8 && c < 7) return true
  return false
}

const isCenterLogoZone = (r: number, c: number) => {
  const center = Math.floor(size.value / 2)
  const radius = centerRadius.value
  return r >= center - radius && r <= center + radius && c >= center - radius && c <= center + radius
}

onMounted(() => {
  const icon = document.querySelector<HTMLLinkElement>('link[rel~="icon"]')
  if (icon?.href) {
    faviconUrl.value = icon.href
  }
  generateQr()
})
watch(
  () => props.url,
  () => {
    generateQr()
  }
)
</script>
