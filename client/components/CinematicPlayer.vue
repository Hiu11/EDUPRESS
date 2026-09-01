<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'

const props = defineProps({
  course: { type: Object, required: true }
})
const emit = defineEmits(['close'])

// ── Real educational YouTube videos per course ──
const videoIds = {
  ai:       'aircAruvnKk',  // 3Blue1Brown: "But what is a neural network?"
  oop:      'pTB0EiLXUC8',  // Mosh: Object-oriented Programming in 7 minutes
  web:      'ysEN5RaKOlA',  // FreeCodeCamp: Web Dev for Beginners
  cloud:    'M988_fsOSWo',  // Google Cloud: Cloud Computing Basics
  mobile:   'VPvVD8t02U8',  // Flutter Crash Course
  data:     'LHBE0FaFmss',  // Python for Data Science
  security: 'hpObD2Hrai8',  // Web Security crash course
  ui:       '_W3R2VwPdzI',  // UI/UX Design fundamentals
}

// ── Fetch real captions from YouTube timedtext API ──
// Falls back to hardcoded notes if CORS blocks it
const fallbackTranscripts = {
  ai: [
    { time: 0,   text: 'Giới thiệu: Mạng nơ-ron là gì?' },
    { time: 15,  text: 'Mỗi lớp nơ-ron học một tính năng khác nhau của dữ liệu.' },
    { time: 40,  text: 'Hàm kích hoạt (activation function) quyết định nơ-ron có "bật" không.' },
    { time: 70,  text: 'Backpropagation: lan truyền ngược để điều chỉnh trọng số.' },
    { time: 100, text: 'Gradient descent: thuật toán tối ưu hóa trọng số theo từng bước.' },
    { time: 130, text: 'Ví dụ thực tế: nhận diện chữ viết tay với MNIST dataset.' },
  ],
  oop: [
    { time: 0,   text: 'OOP giải quyết vấn đề gì trong lập trình truyền thống?' },
    { time: 20,  text: '4 Pillars: Encapsulation — gói dữ liệu vào trong class.' },
    { time: 50,  text: 'Abstraction — ẩn chi tiết, chỉ lộ ra interface cần thiết.' },
    { time: 90,  text: 'Inheritance — class con kế thừa tính năng của class cha.' },
    { time: 130, text: 'Polymorphism — cùng phương thức, hành vi khác nhau theo object.' },
    { time: 170, text: 'Demo: xây class Animal, Dog, Cat với override method speak().' },
  ],
  web: [
    { time: 0,   text: 'HTML5 — cấu trúc trang với semantic elements.' },
    { time: 25,  text: 'CSS Flexbox và Grid — bố cục responsive hiện đại.' },
    { time: 55,  text: 'JavaScript ES6+: arrow functions, destructuring, async/await.' },
    { time: 90,  text: 'React/Vue component model — tái sử dụng UI.' },
    { time: 130, text: 'REST API — giao tiếp giữa client và server.' },
    { time: 170, text: 'Deploy: Vercel, Netlify — CI/CD tự động khi push code.' },
  ],
  default: [
    { time: 0,   text: 'Bắt đầu bài học — hãy chuẩn bị ghi chú!' },
    { time: 20,  text: 'Khái niệm nền tảng và ứng dụng thực tế.' },
    { time: 50,  text: 'Ví dụ minh họa từng bước.' },
    { time: 80,  text: 'Bài tập thực hành cuối module.' },
  ]
}

const lines      = ref([])
const captionSrc = ref('fallback')  // 'youtube' | 'fallback'

async function loadCaptions(vid) {
  try {
    // Gọi qua backend của mình để vừa fetch vừa dịch sang Tiếng Việt
    const config = useRuntimeConfig()
    const res = await fetch(`${config.public.apiBase}/api/captions/${vid}`)
    if (!res.ok) throw new Error('HTTP ' + res.status)
    const data = await res.json()
    if (!data.length) throw new Error('No captions')
    
    lines.value = data
    captionSrc.value = 'youtube'
  } catch (err) {
    console.error('Lỗi khi tải phụ đề:', err)
    // Fallback nếu có lỗi
    lines.value = fallbackTranscripts[props.course.id] || fallbackTranscripts.default
    captionSrc.value = 'fallback'
  }
}


const videoId  = computed(() => videoIds[props.course.id] || videoIds.ai)
const thumbUrl = computed(() => `https://img.youtube.com/vi/${videoId.value}/maxresdefault.jpg`)

// Preload captions immediately on mount
onMounted(() => loadCaptions(videoId.value))

// ── Player state ──
const started     = ref(false)
const isPlaying   = ref(false)
const currentTime = ref(0)
const duration    = ref(0)
const playerReady = ref(false)
let ytPlayer      = null
let rafId         = null  // requestAnimationFrame ID for time sync

const activeIndex = computed(() => {
  let idx = 0
  for (let i = 0; i < lines.value.length; i++) {
    if (currentTime.value >= lines.value[i].time) idx = i
  }
  return idx
})

const ambientPalette = [
  'rgba(220, 38, 38, 0.45)',
  'rgba(234, 88, 12, 0.4)',
  'rgba(99, 102, 241, 0.35)',
  'rgba(16, 185, 129, 0.3)',
  'rgba(245, 158, 11, 0.35)',
]
const ambientColor = computed(() => {
  const idx = Math.floor(currentTime.value / 15) % ambientPalette.length
  return ambientPalette[idx]
})

const progressPct = computed(() =>
  duration.value ? Math.min(100, (currentTime.value / duration.value) * 100) : 0
)

function fmt(s) {
  const sec = Math.floor(s || 0)
  return `${String(Math.floor(sec / 60)).padStart(2,'0')}:${String(sec % 60).padStart(2,'0')}`
}

function startPolling() {
  function poll() {
    if (ytPlayer && typeof ytPlayer.getCurrentTime === 'function') {
      currentTime.value = ytPlayer.getCurrentTime()
      if (!duration.value && ytPlayer.getDuration) {
        duration.value = ytPlayer.getDuration()
      }
    }
    rafId = requestAnimationFrame(poll)
  }
  rafId = requestAnimationFrame(poll)
}

function stopPolling() {
  if (rafId) { cancelAnimationFrame(rafId); rafId = null }
}

function initYTPlayer() {
  if (!window.YT || !window.YT.Player) return
  ytPlayer = new window.YT.Player('yt-player-target', {
    videoId: videoId.value,
    playerVars: {
      autoplay: 1,
      rel: 0,
      modestbranding: 1,
      enablejsapi: 1,
      controls: 0, // Disable native controls and CC
      disablekb: 1,
      origin: window.location.origin,
    },
    events: {
      onReady(e) {
        playerReady.value = true
        duration.value = e.target.getDuration()
        startPolling()
      },
      onStateChange(e) {
        // YT.PlayerState: PLAYING=1, PAUSED=2, ENDED=0
        isPlaying.value = e.data === 1
        if (e.data === 0) stopPolling()  // ended
      },
    },
  })
}

function loadYTApi() {
  if (window.YT && window.YT.Player) { initYTPlayer(); return }
  if (window._ytApiLoading) {
    const prev = window.onYouTubeIframeAPIReady
    window.onYouTubeIframeAPIReady = () => { prev?.(); initYTPlayer() }
    return
  }
  window._ytApiLoading = true
  window.onYouTubeIframeAPIReady = initYTPlayer
  const s = document.createElement('script')
  s.src = 'https://www.youtube.com/iframe_api'
  document.head.appendChild(s)
}

async function startVideo() {
  started.value = true
  await nextTick()
  loadYTApi()
  if (!lines.value.length) loadCaptions(videoId.value)
}

function togglePlay() {
  if (!ytPlayer) return
  if (isPlaying.value) { ytPlayer.pauseVideo() }
  else { ytPlayer.playVideo() }
}

function seek(e) {
  if (!ytPlayer || !duration.value) return
  const rect = e.currentTarget.getBoundingClientRect()
  const ratio = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width))
  ytPlayer.seekTo(ratio * duration.value, true)
}

function seekToTime(time) {
  if (!ytPlayer) return
  ytPlayer.seekTo(time, true)
  if (!isPlaying.value) {
    ytPlayer.playVideo()
  }
}

function handleKeydown(e) {
  if (e.code === 'Space') {
    e.preventDefault()
    togglePlay()
  } else if (e.code === 'ArrowRight') {
    e.preventDefault()
    if (ytPlayer && ytPlayer.getCurrentTime) {
      ytPlayer.seekTo(Math.min(duration.value, ytPlayer.getCurrentTime() + 5), true)
    }
  } else if (e.code === 'ArrowLeft') {
    e.preventDefault()
    if (ytPlayer && ytPlayer.getCurrentTime) {
      ytPlayer.seekTo(Math.max(0, ytPlayer.getCurrentTime() - 5), true)
    }
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
  stopPolling()
  if (ytPlayer) { ytPlayer.destroy(); ytPlayer = null }
  if (document.fullscreenElement) document.exitFullscreen()
})
</script>

<template>
  <div class="cinema-overlay" @click.self="emit('close')">
    <div class="cinema-shell">
      <button class="cinema-close" type="button" @click="emit('close')" title="Đóng">Đóng</button>

      <!-- ── VIDEO STAGE ── -->
      <div class="cinema-stage" :style="{ '--ambient': ambientColor }">
        <div class="ambient-glow"></div>
        <canvas ref="canvasRef" width="1" height="1" style="display:none"></canvas>

        <!-- Thumbnail + Play prompt (before player init) -->
        <div v-if="!started" class="play-prompt" @click="startVideo">
          <img :src="thumbUrl" class="video-poster" :alt="course.title" />
          <div class="play-prompt-overlay">
            <button class="play-prompt-icon" type="button" @click.stop="startVideo">▶</button>
            <p>Nhấn để xem bài học</p>
          </div>
        </div>

        <!-- YT Player mounts here after startVideo() -->
        <div v-show="started" id="yt-player-target" class="cinema-video"></div>

        <!-- Loading indicator -->
        <div v-if="started && !playerReady" class="player-loading">
          <div class="loading-spinner"></div>
          <p>Đang tải video…</p>
        </div>

        <!-- ── CONTROL BAR ── -->
        <div v-if="started && playerReady" class="cinema-controls">
          <div class="seek-bar" @click="seek">
            <div class="seek-fill" :style="{ width: progressPct + '%' }"></div>
            <div class="seek-thumb" :style="{ left: progressPct + '%' }"></div>
          </div>
          <div class="controls-row">
            <div class="controls-left">
              <button class="ctrl-btn play-btn" type="button" @click="togglePlay">
                {{ isPlaying ? '⏸' : '▶' }}
              </button>
              <span class="ctrl-time">{{ fmt(currentTime) }} / {{ fmt(duration) }}</span>
            </div>
            <div class="controls-right">
              <span class="ctrl-label">{{ course.category }} · {{ course.level }}</span>
              <span class="ctrl-badge">Live</span>
            </div>
          </div>
        </div>
      </div>

      <!-- ── TRANSCRIPT PANEL ── -->
      <div class="transcript-panel">
        <div class="transcript-header">
          <span class="eyebrow" style="margin-bottom:0">Phụ đề trực tiếp</span>
          <span class="transcript-status" :class="{ active: isPlaying }">
            {{ isPlaying ? 'Đang phát' : (captionSrc === 'youtube' ? 'YT Caption' : 'Ghi chú') }}
          </span>
        </div>
        <div class="transcript-body">
          <div
            v-for="(line, i) in lines"
            :key="i"
            :class="['transcript-line', {
              'is-active': i === activeIndex && started,
              'is-past':   i < activeIndex
            }]"
            @click="seekToTime(line.time)"
            style="cursor: pointer;"
          >
            <span class="transcript-ts">{{ fmt(line.time) }}</span>
            <span class="transcript-text">{{ line.text }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
