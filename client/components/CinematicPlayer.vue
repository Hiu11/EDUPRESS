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
    { time: 170, text: 'Demo: xây class Animal → Dog, Cat với override method speak().' },
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
    const res = await fetch(`http://localhost:8001/api/captions/${vid}`)
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
const videoRef    = ref(null)
const canvasRef   = ref(null)
let rafId         = null  // requestAnimationFrame ID for time sync

// Active transcript line (synced via real YT currentTime)
const activeIndex = computed(() => {
  let idx = 0
  for (let i = 0; i < lines.value.length; i++) {
    if (currentTime.value >= lines.value[i].time) idx = i
  }
  return idx
})

const ambientColor = ref('rgba(0,0,0,0.8)')
function updateAmbientColor() {
  if (!videoRef.value || !canvasRef.value) return
  const ctx = canvasRef.value.getContext('2d', { willReadFrequently: true })
  try {
    ctx.drawImage(videoRef.value, 0, 0, 1, 1)
    const [r, g, b] = ctx.getImageData(0, 0, 1, 1).data
    ambientColor.value = `rgba(${r}, ${g}, ${b}, 0.8)`
  } catch(e) {}
}

function pollAmbient() {
  if (isPlaying.value) {
    updateAmbientColor()
  }
  rafId = requestAnimationFrame(pollAmbient)
}

const progressPct = computed(() =>
  duration.value ? Math.min(100, (currentTime.value / duration.value) * 100) : 0
)

function fmt(s) {
  const sec = Math.floor(s || 0)
  return `${String(Math.floor(sec / 60)).padStart(2,'0')}:${String(sec % 60).padStart(2,'0')}`
}

async function startVideo() {
  started.value = true
  playerReady.value = true
  await nextTick()
  if (videoRef.value) {
    videoRef.value.play()
  }
  // Reload captions in case mount call failed
  if (!lines.value.length) loadCaptions(videoId.value)
  rafId = requestAnimationFrame(pollAmbient)
}

function togglePlay() {
  if (!videoRef.value) return
  if (isPlaying.value) { videoRef.value.pause() }
  else { videoRef.value.play() }
}

function seek(e) {
  if (!videoRef.value || !duration.value) return
  const rect = e.currentTarget.getBoundingClientRect()
  const ratio = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width))
  videoRef.value.currentTime = ratio * duration.value
}

function seekToTime(time) {
  if (!videoRef.value) return
  videoRef.value.currentTime = time
  if (!isPlaying.value) {
    videoRef.value.play()
  }
}

function onTimeUpdate() {
  if (videoRef.value) currentTime.value = videoRef.value.currentTime
}
function onLoadedMetadata() {
  if (videoRef.value) duration.value = videoRef.value.duration
}
function onPlay() { isPlaying.value = true }
function onPause() { isPlaying.value = false }
function onEnded() {
  isPlaying.value = false
  if (rafId) cancelAnimationFrame(rafId)
}

function handleKeydown(e) {
  if (e.code === 'Space') {
    e.preventDefault()
    togglePlay()
  } else if (e.code === 'ArrowRight') {
    e.preventDefault()
    if (videoRef.value) videoRef.value.currentTime = Math.min(duration.value, videoRef.value.currentTime + 5)
  } else if (e.code === 'ArrowLeft') {
    e.preventDefault()
    if (videoRef.value) videoRef.value.currentTime = Math.max(0, videoRef.value.currentTime - 5)
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
  if (rafId) cancelAnimationFrame(rafId)
  if (document.fullscreenElement) document.exitFullscreen()
})
</script>

<template>
  <div class="cinema-overlay" @click.self="emit('close')">
    <div class="cinema-shell">
      <button class="cinema-close" type="button" @click="emit('close')" title="Đóng">✕</button>

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

        <!-- Native HTML5 Video Player -->
        <video
          v-show="started"
          ref="videoRef"
          src="/generated-assets/sample-lesson.mp4"
          crossorigin="anonymous"
          class="cinema-video"
          @timeupdate="onTimeUpdate"
          @loadedmetadata="onLoadedMetadata"
          @play="onPlay"
          @pause="onPause"
          @ended="onEnded"
          @click="togglePlay"
        ></video>

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
            {{ isPlaying ? '● Đang phát' : (captionSrc === 'youtube' ? '✓ YT Caption' : '○ Ghi chú') }}
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
