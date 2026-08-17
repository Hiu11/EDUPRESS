<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import confetti from 'canvas-confetti'

const props = defineProps({
  course: { type: Object, required: false }
})
const emit = defineEmits(['close'])

// Dữ liệu mẫu (Có thể thay bằng API fetch theo props.course)
const initialCards = [
  { id: 1, front: 'Hàm nào dùng để chuyển chuỗi thành số nguyên trong JavaScript?', back: 'parseInt()' },
  { id: 2, front: 'CSS Flexbox: Thuộc tính nào để căn giữa theo trục chéo (cross-axis)?', back: 'align-items' },
  { id: 3, front: 'Khác biệt chính giữa Let và Var?', back: 'Let có block scope, Var có function scope' },
  { id: 4, front: 'Lifecycle hook nào trong Vue 3 chạy sau khi component đã được mount vào DOM?', back: 'onMounted' },
  { id: 5, front: 'Virtual DOM là gì?', back: 'Bản sao nhẹ của DOM thực tế, giúp tối ưu hóa việc cập nhật UI' }
]

// ── State ────────────────────────────────────────────────────────
const totalCardsCount = ref(initialCards.length)
const cards = ref([...initialCards].reverse())
const currentCard = computed(() => cards.value[cards.value.length - 1])
const isFlipped = ref(false)
const isFinished = computed(() => cards.value.length === 0)

// Progress Bar
const progressPercent = computed(() => {
  if (totalCardsCount.value === 0) return 0
  return ((totalCardsCount.value - cards.value.length) / totalCardsCount.value) * 100
})

// ── Web Audio API ──────────────────────────────────────────────────
let audioCtx = null
function playSound(type) {
  try {
    if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)()
    const osc = audioCtx.createOscillator()
    const gainNode = audioCtx.createGain()
    osc.connect(gainNode)
    gainNode.connect(audioCtx.destination)
    
    const now = audioCtx.currentTime
    if (type === 'flip') {
      osc.type = 'triangle'
      osc.frequency.setValueAtTime(400, now)
      osc.frequency.exponentialRampToValueAtTime(800, now + 0.05)
      gainNode.gain.setValueAtTime(0.05, now)
      gainNode.gain.exponentialRampToValueAtTime(0.01, now + 0.05)
      osc.start(now)
      osc.stop(now + 0.05)
    } else if (type === 'right') { 
      osc.type = 'sine'
      osc.frequency.setValueAtTime(880, now)
      osc.frequency.exponentialRampToValueAtTime(1760, now + 0.15)
      gainNode.gain.setValueAtTime(0.08, now)
      gainNode.gain.exponentialRampToValueAtTime(0.01, now + 0.3)
      osc.start(now)
      osc.stop(now + 0.3)
    } else if (type === 'left') { 
      osc.type = 'sawtooth'
      osc.frequency.setValueAtTime(150, now)
      osc.frequency.exponentialRampToValueAtTime(100, now + 0.15)
      gainNode.gain.setValueAtTime(0.05, now)
      gainNode.gain.exponentialRampToValueAtTime(0.01, now + 0.2)
      osc.start(now)
      osc.stop(now + 0.2)
    }
  } catch(e) { }
}

// ── Swipe Physics ──────────────────────────────────────────────────
const isDragging = ref(false)
const isAnimatingOut = ref(false)
const startX = ref(0)
const startY = ref(0)
const offsetX = ref(0)
const offsetY = ref(0)
const swipeThreshold = 100

const cardTransform = computed(() => {
  if (!currentCard.value || isFinished.value) return ''
  const rotateY = isFlipped.value ? 180 : 0
  const rotateZ = offsetX.value * 0.04
  return `translate(${offsetX.value}px, ${offsetY.value}px) rotateZ(${rotateZ}deg) rotateY(${rotateY}deg)`
})

const labelRightOpacity = computed(() => Math.max(0, Math.min(1, offsetX.value / swipeThreshold)))
const labelLeftOpacity  = computed(() => Math.max(0, Math.min(1, -offsetX.value / swipeThreshold)))

function onPointerDown(e) {
  if (isAnimatingOut.value) return
  isDragging.value = true
  startX.value = e.clientX || (e.touches && e.touches[0].clientX)
  startY.value = e.clientY || (e.touches && e.touches[0].clientY)
  offsetX.value = 0
  offsetY.value = 0
  if (e.target.setPointerCapture) e.target.setPointerCapture(e.pointerId)
}

function onPointerMove(e) {
  if (!isDragging.value) return
  const currentX = e.clientX || (e.touches && e.touches[0].clientX)
  const currentY = e.clientY || (e.touches && e.touches[0].clientY)
  offsetX.value = currentX - startX.value
  offsetY.value = currentY - startY.value
}

function onPointerUp(e) {
  if (!isDragging.value) return
  isDragging.value = false
  
  if (Math.abs(offsetX.value) > swipeThreshold) {
    swipeOut(offsetX.value > 0 ? 'right' : 'left')
  } else {
    offsetX.value = 0
    offsetY.value = 0
  }
}

function toggleFlip() {
  if (Math.abs(offsetX.value) > 5) return 
  isFlipped.value = !isFlipped.value
  playSound('flip')
}

// ── VIP Feature: Spaced Repetition Logic ─────────────────────────
function swipeOut(direction) {
  if (isAnimatingOut.value || isFinished.value) return
  isAnimatingOut.value = true
  
  // Animation exit
  offsetX.value = direction === 'right' ? window.innerWidth * 1.5 : -window.innerWidth * 1.5
  offsetY.value = offsetX.value * 0.2
  playSound(direction)
  
  setTimeout(() => {
    const card = cards.value.pop()
    
    if (direction === 'left') {
      // Nhét lại vào giữa bộ bài để ôn lại
      // Nếu chỉ còn 1-2 thẻ thì nhét xuống đáy, nếu nhiều thì nhét ngẫu nhiên vào nửa sau
      const insertIndex = Math.max(0, Math.floor(Math.random() * (cards.value.length / 2)))
      cards.value.splice(insertIndex, 0, card)
      // Tăng tổng số thẻ cần học (penalty)
      totalCardsCount.value += 1
    }

    offsetX.value = 0
    offsetY.value = 0
    isFlipped.value = false
    isAnimatingOut.value = false
    
    if (cards.value.length === 0) triggerConfetti()
  }, 350)
}

// ── Keyboard Controls ────────────────────────────────────────────
function onKeyDown(e) {
  if (isFinished.value) return
  if (e.key === 'ArrowLeft') swipeOut('left')
  if (e.key === 'ArrowRight') swipeOut('right')
  if (e.key === ' ' || e.key === 'ArrowUp' || e.key === 'ArrowDown') {
    e.preventDefault()
    toggleFlip()
  }
}

onMounted(() => {
  window.addEventListener('keydown', onKeyDown)
})
onUnmounted(() => {
  window.removeEventListener('keydown', onKeyDown)
})

// ── Confetti ─────────────────────────────────────────────────────
function triggerConfetti() {
  const duration = 2.5 * 1000
  const animationEnd = Date.now() + duration
  const defaults = { startVelocity: 30, spread: 360, ticks: 60, zIndex: 10000 }
  
  function randomInRange(min, max) { return Math.random() * (max - min) + min }
  
  const interval = setInterval(function() {
    const timeLeft = animationEnd - Date.now()
    if (timeLeft <= 0) return clearInterval(interval)
    const particleCount = 50 * (timeLeft / duration)
    confetti(Object.assign({}, defaults, { particleCount, origin: { x: randomInRange(0.1, 0.3), y: Math.random() - 0.2 } }))
    confetti(Object.assign({}, defaults, { particleCount, origin: { x: randomInRange(0.7, 0.9), y: Math.random() - 0.2 } }))
  }, 250)
}

function restart() {
  cards.value = [...initialCards].reverse()
  totalCardsCount.value = initialCards.length
  isFlipped.value = false
}
</script>

<template>
  <div class="flashcard-overlay">
    <div class="flashcard-header">
      <div class="header-left">
        <div class="stats">
          <span>Tiến độ:</span>
        </div>
        <div class="progress-bar-wrap">
          <div class="progress-fill" :style="{ width: progressPercent + '%' }"></div>
        </div>
        <span class="badge-count">{{ totalCardsCount - cards.length }}/{{ totalCardsCount }}</span>
      </div>

      <button class="close-btn" @click="emit('close')">
        <svg viewBox="0 0 24 24" width="16" height="16" stroke="currentColor" stroke-width="2.5" fill="none" stroke-linecap="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
        Đóng
      </button>
    </div>

    <div class="flashcard-container">
      <div v-if="isFinished" class="finished-state">
        <div class="trophy-icon">Hoàn thành</div>
        <h2 class="gradient-text">Đã ôn xong</h2>
        <p>Bạn đã đi hết bộ thẻ. Có thể làm lại để củng cố phần còn yếu.</p>
        <button class="premium-btn mt-4" @click="restart">Ôn tập lại</button>
      </div>

      <div class="card-stack" v-else>
        <!-- Background cards for stack effect -->
        <div class="card-bg card-bg-2" v-if="cards.length > 2"></div>
        <div class="card-bg card-bg-1" v-if="cards.length > 1"></div>

        <!-- Active Swipeable Card -->
        <div
          class="flashcard"
          :class="{ 'is-dragging': isDragging, 'is-animating': isAnimatingOut || (!isDragging && offsetX === 0) }"
          :style="{ transform: cardTransform }"
          @pointerdown="onPointerDown"
          @pointermove="onPointerMove"
          @pointerup="onPointerUp"
          @pointercancel="onPointerUp"
          @click="toggleFlip"
        >
          <!-- Front Side -->
          <div class="card-face card-front">
            <div class="card-badge">CÂU HỎI</div>
            <h3 class="card-text">{{ currentCard.front }}</h3>
            <div class="hint">Phím Space / Click để lật</div>
          </div>
          
          <!-- Back Side -->
          <div class="card-face card-back">
            <div class="card-badge answer">ĐÁP ÁN</div>
            <h3 class="card-text">{{ currentCard.back }}</h3>
            <div class="hint">Vuốt hoặc dùng Phím Mũi tên</div>
          </div>

          <!-- Overlay Feedback Labels -->
          <div class="swipe-feedback feedback-left" :style="{ opacity: labelLeftOpacity }">
            <div class="stamp stamp-left">QUÊN</div>
          </div>
          <div class="swipe-feedback feedback-right" :style="{ opacity: labelRightOpacity }">
            <div class="stamp stamp-right">ĐÃ NHỚ</div>
          </div>
        </div>
      </div>
      
      <!-- Controls -->
      <div class="controls" v-if="!isFinished">
        <div class="ctrl-wrap">
          <button class="ctrl-btn btn-left" @click="swipeOut('left')">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6L6 18M6 6l12 12"/></svg>
          </button>
          <span class="kb-hint">Trái</span>
        </div>
        
        <div class="ctrl-wrap ctrl-wrap-center">
          <button class="ctrl-btn btn-flip" @click="toggleFlip">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12a9 9 0 11-9-9c2.52 0 4.93 1 6.74 2.74L21 8"/><path d="M21 3v5h-5"/></svg>
          </button>
          <span class="kb-hint">SPACE</span>
        </div>
        
        <div class="ctrl-wrap">
          <button class="ctrl-btn btn-right" @click="swipeOut('right')">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6L9 17l-5-5"/></svg>
          </button>
          <span class="kb-hint">Phải</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.flashcard-overlay {
  position: fixed;
  inset: 0;
  z-index: 10000;
  background: #101827;
  display: flex;
  flex-direction: column;
  animation: fadeIn 0.25s ease;
  touch-action: none;
  overflow: hidden;
}

.flashcard-header {
  position: relative; z-index: 10;
  display: flex; justify-content: space-between; align-items: center;
  padding: 24px 32px; color: white;

  .header-left {
    display: flex; align-items: center; gap: 16px; flex: 1;
  }
  .stats { font-size: 0.9rem; color: #94a3b8; font-weight: 700; text-transform: uppercase; }
  
  .progress-bar-wrap {
    flex: 1; max-width: 300px; height: 8px;
    background: rgba(255,255,255,0.1); border-radius: 999px; overflow: hidden;
  }
  .progress-fill {
    height: 100%; background: #10b981;
    transition: width 0.3s ease; border-radius: 999px;
  }
  
  .badge-count { font-size: 0.95rem; font-weight: 800; color: #d1d5db; }

  .close-btn {
    display: flex; align-items: center; gap: 8px;
    background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1);
    color: white; padding: 8px 20px; border-radius: 999px; font-weight: 600;
    cursor: pointer; backdrop-filter: blur(10px); transition: all 0.25s;
    &:hover { background: rgba(255,255,255,0.15); }
  }
}

.flashcard-container {
  flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center;
  position: relative; z-index: 10; padding-bottom: 120px;
}

.finished-state {
  text-align: center; color: white; animation: slideUp 0.35s ease;
  .trophy-icon { font-size: 1rem; color: #d1d5db; margin-bottom: 16px; }
  .gradient-text { font-size: 2.4rem; margin-bottom: 12px; color: #ffffff; font-weight: 800; }
  p { color: #94a3b8; font-size: 1.1rem; }
  .premium-btn {
    margin-top: 32px; background: #ffffff; color: #111827; border: none; padding: 14px 28px; border-radius: 10px; font-size: 1rem; font-weight: 700; cursor: pointer;
    box-shadow: 0 10px 24px rgba(0, 0, 0, 0.24); transition: transform 0.2s ease, box-shadow 0.2s ease;
    &:hover { transform: translateY(-1px); box-shadow: 0 12px 28px rgba(0, 0, 0, 0.28); }
  }
}

.card-stack { position: relative; width: min(90%, 420px); aspect-ratio: 3/4; perspective: 1500px; }

.card-bg {
  position: absolute; inset: 0; border-radius: 18px; backdrop-filter: blur(10px);
  background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); box-shadow: 0 20px 40px rgba(0,0,0,0.4);
  pointer-events: none; transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}
.card-bg-1 { transform: translateY(16px) scale(0.95); z-index: 1; }
.card-bg-2 { transform: translateY(32px) scale(0.90); z-index: 0; opacity: 0.6; }

.flashcard {
  position: absolute; inset: 0; z-index: 2; border-radius: 18px; cursor: grab; transform-style: preserve-3d; touch-action: none; box-shadow: 0 18px 38px rgba(0,0,0,0.42);
  &.is-dragging { cursor: grabbing; transition: none; }
  &.is-animating { transition: transform 0.35s ease; }
}

.card-face {
  position: absolute; inset: 0; border-radius: 18px; padding: 40px; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; backface-visibility: hidden;
  background: #ffffff; border: 1px solid rgba(255,255,255,0.5); overflow: hidden;
}
.card-front { z-index: 2; }
.card-back  { transform: rotateY(180deg); background: #111827; border-color: rgba(255,255,255,0.12); color: white; }

.card-badge {
  position: absolute; top: 32px; left: 50%; transform: translateX(-50%); font-size: 0.75rem; font-weight: 800; letter-spacing: 0.08em; padding: 6px 14px; border-radius: 8px;
  background: #f3f4f6; color: #374151; border: 1px solid #e5e7eb;
}
.card-back .card-badge.answer { background: rgba(255,255,255,0.08); color: #d1d5db; border-color: rgba(255,255,255,0.12); }
.card-text { font-size: 1.8rem; font-weight: 800; color: #0f172a; line-height: 1.4; z-index: 1; }
.card-back .card-text { color: white; }
.hint { position: absolute; bottom: 32px; left: 50%; transform: translateX(-50%); font-size: 0.85rem; color: #94a3b8; font-weight: 600; pointer-events: none; }

.swipe-feedback { position: absolute; inset: 0; pointer-events: none; border-radius: 32px; display: flex; align-items: flex-start; padding: 40px; z-index: 3; }
.feedback-left  { justify-content: flex-end; }
.feedback-right { justify-content: flex-start; }
.stamp { font-size: 1.6rem; font-weight: 800; padding: 8px 18px; border-radius: 10px; border: 2px solid; text-transform: uppercase; letter-spacing: 0.06em; background: rgba(255,255,255,0.9); }
.stamp-left { color: #be123c; border-color: #be123c; transform: rotate(12deg); }
.stamp-right { color: #047857; border-color: #047857; transform: rotate(-12deg); }

.controls { position: absolute; bottom: 40px; display: flex; align-items: center; justify-content: center; gap: 24px; z-index: 5; }
.ctrl-wrap { display: flex; flex-direction: column; align-items: center; gap: 6px; }
.kb-hint { font-size: 0.7rem; font-weight: 700; color: rgba(255,255,255,0.4); letter-spacing: 0.1em; }

.ctrl-btn {
  border-radius: 50%; border: none; cursor: pointer; display: flex; align-items: center; justify-content: center; background: white; transition: transform 0.2s ease, box-shadow 0.2s ease; position: relative;
  &:hover { transform: translateY(-1px); }
  &:active { transform: scale(0.9); }
}
.btn-left { width: 68px; height: 68px; color: #be123c; box-shadow: 0 10px 24px rgba(0, 0, 0, 0.2); svg { width: 32px; height: 32px; } }
.btn-right { width: 68px; height: 68px; color: #047857; box-shadow: 0 10px 24px rgba(0, 0, 0, 0.2); svg { width: 34px; height: 34px; } }
.btn-flip { width: 54px; height: 54px; color: #374151; box-shadow: 0 10px 24px rgba(0, 0, 0, 0.18); svg { width: 26px; height: 26px; transform: scaleX(-1); } }

@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
@keyframes slideUp { from { opacity: 0; transform: translateY(40px); } to { opacity: 1; transform: translateY(0); } }
</style>
