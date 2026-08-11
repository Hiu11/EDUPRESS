<script setup>
import { ref, onMounted, onUnmounted, computed, nextTick } from 'vue'

const props = defineProps({
  courseTitle: { type: String, default: 'Bài học hiện tại' }
})
const emit = defineEmits(['close'])

const isGenerating = ref(true)
const generationStep = ref(0)
const generationLogs = ref([
  'Đang chuẩn bị nội dung bài giảng...',
  'Viết kịch bản đàm thoại 2 nhân vật (Host & Expert)...',
  'Chuẩn bị giọng đọc...',
  'Ghép luồng âm thanh & tối ưu cảm xúc giọng nói...',
  'Hoàn tất! Đang tải trình phát Podcast...'
])

const isPlaying = ref(false)
const currentLineIdx = ref(-1)
const currentWordIdx = ref(-1)
const showPlayer = ref(false)
let synth = null
let ambientAudio = null
const transcriptScroll = ref(null)

const availableVoices = ref([])
const selectedHostVoiceURI = ref('')
const selectedExpertVoiceURI = ref('')
const showSettings = ref(false)

// Split transcript into words for karaoke
const transcript = [
  { speaker: 'host', name: 'Alex', role: 'Host', text: 'Xin chào các bạn học viên! Chào mừng trở lại với EduPress Audio. Khóa học hôm nay có vẻ rất thú vị đây.' },
  { speaker: 'expert', name: 'Sarah', role: 'Chuyên gia', text: 'Chào Alex! Đúng vậy, hôm nay chúng ta sẽ nói về cách công nghệ đang thay đổi cách học tập và làm việc.' },
  { speaker: 'host', name: 'Alex', role: 'Host', text: '*cười* Wow. Nghe nói các công cụ học tập hiện nay có thể hỗ trợ review lỗi rất nhanh phải không?' },
  { speaker: 'expert', name: 'Sarah', role: 'Chuyên gia', text: 'Chính xác! Ví dụ như phần thực hành của EduPress có thể nhắc người học xem lại những lỗi JavaScript phổ biến.' },
  { speaker: 'host', name: 'Alex', role: 'Host', text: '*thở phào* Quá đỉnh! Hy vọng qua bài học này, mọi người sẽ nắm được cốt lõi của công nghệ này. Chúc các bạn học tốt nhé!' }
].map(line => ({
  ...line,
  words: line.text.split(' ')
}))

onMounted(() => {
  synth = window.speechSynthesis
  
  const loadVoices = () => {
    availableVoices.value = synth.getVoices()
    if (availableVoices.value.length > 0) {
      // Try to auto-select good defaults (e.g. Google Vietnamese or different ones)
      const viVoices = availableVoices.value.filter(v => v.lang.includes('vi'))
      if (viVoices.length > 0) {
        selectedHostVoiceURI.value = viVoices[0].voiceURI
        selectedExpertVoiceURI.value = viVoices[viVoices.length > 1 ? 1 : 0].voiceURI
      } else {
        selectedHostVoiceURI.value = availableVoices.value[0]?.voiceURI
        selectedExpertVoiceURI.value = availableVoices.value[1]?.voiceURI || availableVoices.value[0]?.voiceURI
      }
    }
  }
  
  loadVoices()
  if (synth.onvoiceschanged !== undefined) {
    synth.onvoiceschanged = loadVoices
  }
  
  // Fake Generation Process
  let step = 0
  const interval = setInterval(() => {
    generationStep.value = step
    step++
    if (step > 4) {
      clearInterval(interval)
      setTimeout(() => {
        isGenerating.value = false
        showPlayer.value = true
        initAmbientMusic()
      }, 1000)
    }
  }, 1200)
})

onUnmounted(() => {
  stopPodcast()
})

function initAmbientMusic() {
  // Free Lo-fi ambient URL from Pixabay
  ambientAudio = new Audio('https://cdn.pixabay.com/download/audio/2022/05/27/audio_1808fbf07a.mp3?filename=lofi-study-112191.mp3')
  ambientAudio.loop = true
  ambientAudio.volume = 0.05 // Very quiet background
}

function playPodcast() {
  if (isPlaying.value) return
  isPlaying.value = true
  ambientAudio?.play().catch(e => console.log('Audio autoplay blocked'))
  
  playLine(0)
}

function stopPodcast() {
  isPlaying.value = false
  synth?.cancel()
  if (ambientAudio) {
    ambientAudio.pause()
    ambientAudio.currentTime = 0
  }
  currentLineIdx.value = -1
}

function closePlayer() {
  stopPodcast()
  emit('close')
}

function playLine(index) {
  if (index >= transcript.length || !isPlaying.value) {
    stopPodcast()
    return
  }
  
  currentLineIdx.value = index
  currentWordIdx.value = -1
  scrollToActiveLine()
  
  const line = transcript[index]
  
  // Play mock sound effects
  if (line.text.includes('*cười*')) playSFX('laugh')
  if (line.text.includes('*thở phào*')) playSFX('sigh')
  
  const cleanText = line.text.replace(/\*[^*]+\*/g, '') // Remove *action* for TTS
  const utterance = new SpeechSynthesisUtterance(cleanText)
  
  // Configure voices
  const isHost = line.speaker === 'host'
  const targetURI = isHost ? selectedHostVoiceURI.value : selectedExpertVoiceURI.value
  const voice = availableVoices.value.find(v => v.voiceURI === targetURI)
  
  if (voice) {
    utterance.voice = voice
  } else {
    utterance.lang = 'vi-VN'
  }
  
  utterance.rate = 1.15 // Slightly faster
  utterance.pitch = isHost ? 0.9 : 1.3 // Keep pitch trick in case it's the same voice
  
  // Word by word highlight (Karaoke)
  utterance.onboundary = (event) => {
    if (event.name === 'word') {
      const charIndex = event.charIndex
      let charCount = 0
      for (let i = 0; i < line.words.length; i++) {
        charCount += line.words[i].length + 1 // +1 for space
        if (charCount > charIndex) {
          currentWordIdx.value = i
          // Make waveform react to word length
          triggerWaveformReact(line.words[i].length)
          break
        }
      }
    }
  }
  
  utterance.onend = () => {
    setTimeout(() => {
      playLine(index + 1)
    }, 500) // Small pause between speakers
  }
  
  synth.speak(utterance)
}

function playSFX(type) {
  // Use mock tiny base64 or public URLs for SFX
  // We can just simulate the effect visually in the UI for now
}

const waveAmplitude = ref(32)
function triggerWaveformReact(wordLength) {
  waveAmplitude.value = Math.min(80, 20 + (wordLength * 6))
  setTimeout(() => { waveAmplitude.value = 32 }, 150)
}

function scrollToActiveLine() {
  nextTick(() => {
    if (transcriptScroll.value) {
      const activeEl = transcriptScroll.value.querySelector('.active')
      if (activeEl) {
        activeEl.scrollIntoView({ behavior: 'smooth', block: 'center' })
      }
    }
  })
}
</script>

<template>
  <div class="podcast-overlay">
    
    <!-- Immersive Background -->
    <div class="ambient-bg" :class="[isPlaying ? transcript[currentLineIdx]?.speaker : 'idle']">
      <div class="bg-blob blob-1"></div>
      <div class="bg-blob blob-2"></div>
    </div>

    <div class="podcast-container">
      <div class="top-bar">
        <button class="back-btn" @click="closePlayer">Quay lại</button>
        <button class="settings-btn" v-if="showPlayer" @click="showSettings = true">Giọng đọc</button>
      </div>
      
      <!-- SETTINGS MODAL -->
      <div v-if="showSettings" class="settings-modal">
        <div class="settings-header">
          <h3>Cài đặt Giọng đọc</h3>
          <button @click="showSettings = false">Đóng</button>
        </div>
        <div class="settings-body">
          <div class="form-group">
            <label>Giọng Host (Alex)</label>
            <select v-model="selectedHostVoiceURI">
              <option v-for="voice in availableVoices" :key="voice.voiceURI" :value="voice.voiceURI">
                {{ voice.name }} ({{ voice.lang }})
              </option>
            </select>
          </div>
          <div class="form-group">
            <label>Giọng Expert (Sarah)</label>
            <select v-model="selectedExpertVoiceURI">
              <option v-for="voice in availableVoices" :key="voice.voiceURI" :value="voice.voiceURI">
                {{ voice.name }} ({{ voice.lang }})
              </option>
            </select>
          </div>
        </div>
      </div>
      
      <!-- GENERATING STATE -->
      <div v-if="isGenerating" class="gen-state">
        <div class="spinner-ring"></div>
        <h2 class="gen-title">Chuẩn bị Podcast...</h2>
        <div class="gen-steps">
          <div v-for="(log, idx) in generationLogs" :key="idx" 
               class="gen-step" 
               :class="{ active: generationStep === idx, done: generationStep > idx }">
            <span class="icon">{{ generationStep > idx ? 'Xong' : (generationStep === idx ? 'Đang làm' : 'Chờ') }}</span>
            <span class="text">{{ log }}</span>
          </div>
        </div>
      </div>

      <!-- PLAYER STATE -->
      <div v-if="showPlayer" class="player-state">
        
        <!-- Top Visualizer -->
        <div class="visualizer-section">
          <div class="header-pills">
            <span class="badge">EduPress Podcast</span>
            <span class="title-pill">{{ courseTitle }}</span>
          </div>
          
          <!-- NotebookLM / Siri Style Orbs -->
          <div class="orb-container" :class="{ active: isPlaying }" @click="isPlaying ? stopPodcast() : playPodcast()">
            <div class="orb host-orb" :class="{ speaking: isPlaying && transcript[currentLineIdx]?.speaker === 'host' }"></div>
            <div class="orb expert-orb" :class="{ speaking: isPlaying && transcript[currentLineIdx]?.speaker === 'expert' }"></div>
            
            <div class="play-overlay" v-if="!isPlaying">
              <span class="play-icon">▶</span>
            </div>
          </div>
          
          <div class="speaker-labels" v-if="isPlaying">
            <span class="label host-label" :class="{ active: transcript[currentLineIdx]?.speaker === 'host' }">Alex (Host)</span>
            <span class="label expert-label" :class="{ active: transcript[currentLineIdx]?.speaker === 'expert' }">Sarah (Chuyên gia)</span>
          </div>
        </div>

        <!-- Bottom Karaoke Lyrics -->
        <div class="lyrics-section" ref="transcriptScroll">
          <div class="lyrics-wrapper">
            <div v-for="(line, idx) in transcript" :key="idx" 
                 class="lyric-line" 
                 :class="[line.speaker, { 
                   'active': currentLineIdx === idx,
                   'past': currentLineIdx > idx 
                 }]">
              <div class="lyric-text">
                <span v-for="(word, wIdx) in line.words" :key="wIdx" 
                      class="karaoke-word"
                      :class="{ 'word-active': currentLineIdx === idx && currentWordIdx >= wIdx }">
                  {{ word }}&nbsp;
                </span>
              </div>
            </div>
            <!-- Spacer to allow scrolling past bottom -->
            <div style="height: 40vh;"></div>
          </div>
        </div>
        
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.podcast-overlay {
  position: fixed;
  inset: 0;
  background: #000;
  z-index: 10000;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: 'Inter', sans-serif;
  animation: fadeIn 0.5s ease;
  overflow: hidden;
}

/* ── Immersive Background ── */
.ambient-bg {
  position: absolute;
  inset: 0;
  z-index: 0;
  opacity: 0.6;
  filter: blur(100px);
  transition: all 1s ease;

  .bg-blob {
    position: absolute;
    border-radius: 50%;
    transition: all 1s ease;
  }
  
  .blob-1 { width: 60vw; height: 60vw; top: -10vw; left: -10vw; background: rgba(96, 165, 250, 0.2); mix-blend-mode: screen; }
  .blob-2 { width: 50vw; height: 50vw; bottom: -10vw; right: -10vw; background: rgba(192, 132, 252, 0.2); mix-blend-mode: screen; }

  &.host {
    .blob-1 { background: rgba(96, 165, 250, 0.5); transform: scale(1.2); }
    .blob-2 { opacity: 0.2; }
  }
  &.expert {
    .blob-1 { opacity: 0.2; }
    .blob-2 { background: rgba(192, 132, 252, 0.5); transform: scale(1.2); }
  }
}

.podcast-container {
  position: relative;
  z-index: 1;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  color: #fff;
}

.top-bar {
  position: absolute; top: 0; left: 0; right: 0;
  display: flex; justify-content: space-between;
  padding: 32px 40px; z-index: 20;
}

.back-btn, .settings-btn {
  background: rgba(255,255,255,0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255,255,255,0.1);
  padding: 10px 20px;
  border-radius: 100px;
  color: #fff;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  &:hover { background: rgba(255,255,255,0.2); transform: scale(1.05); }
}

/* ── SETTINGS MODAL ── */
.settings-modal {
  position: absolute; top: 90px; right: 40px;
  background: rgba(15, 23, 42, 0.9); backdrop-filter: blur(20px);
  border: 1px solid rgba(255,255,255,0.2);
  border-radius: 16px; padding: 24px; z-index: 30;
  width: 300px; box-shadow: 0 20px 40px rgba(0,0,0,0.5);
  animation: slideIn 0.2s ease;
  
  .settings-header {
    display: flex; justify-content: space-between; margin-bottom: 20px;
    h3 { font-size: 1.1rem; font-weight: 700; margin: 0; }
    button { background: transparent; border: none; color: #fff; cursor: pointer; }
  }
  
  .form-group {
    margin-bottom: 16px;
    label { display: block; font-size: 0.85rem; color: #94a3b8; margin-bottom: 8px; }
    select {
      width: 100%; padding: 8px 12px;
      background: rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.2);
      color: #fff; border-radius: 8px;
    }
  }
}

@keyframes slideIn { from { opacity: 0; transform: translateY(-10px); } to { opacity: 1; transform: translateY(0); } }

/* ── GEN STATE ── */
.gen-state {
  flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center;
  
  .spinner-ring {
    width: 80px; height: 80px; border-radius: 50%;
    border: 3px solid rgba(255,255,255,0.1);
    border-top-color: #a78bfa;
    animation: spin 1s linear infinite;
    margin-bottom: 32px;
  }
  
  .gen-title { font-size: 1.5rem; font-weight: 600; margin-bottom: 40px; letter-spacing: 0.05em; }
  
  .gen-steps { width: 100%; max-width: 400px; display: flex; flex-direction: column; gap: 16px; }
  
  .gen-step {
    display: flex; align-items: center; gap: 16px;
    font-size: 1rem; color: #64748b; opacity: 0.5; transition: all 0.3s;
    &.active { opacity: 1; color: #fff; transform: translateX(10px); }
    &.done { opacity: 1; color: #10b981; }
  }
}

@keyframes spin { to { transform: rotate(360deg); } }

/* ── PLAYER STATE ── */
.player-state {
  flex: 1; display: flex; flex-direction: column; padding-top: 80px;
}

.visualizer-section {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  flex: 1; max-height: 40vh;
}

.header-pills {
  display: flex; gap: 12px; margin-bottom: 40px;
  .badge { background: #a78bfa; color: #000; font-weight: 700; padding: 6px 12px; border-radius: 100px; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.1em; }
  .title-pill { background: rgba(255,255,255,0.1); padding: 6px 16px; border-radius: 100px; font-size: 0.85rem; }
}

/* ── Glowing Orbs ── */
.orb-container {
  position: relative; width: 160px; height: 160px; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  
  .orb {
    position: absolute; width: 100%; height: 100%;
    border-radius: 40% 60% 70% 30% / 40% 50% 60% 50%;
    mix-blend-mode: screen;
    filter: blur(10px);
    opacity: 0.7;
    transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
  }
  
  .host-orb {
    background: linear-gradient(45deg, #3b82f6, #60a5fa);
    animation: morph 8s ease-in-out infinite alternate;
  }
  
  .expert-orb {
    background: linear-gradient(45deg, #a855f7, #c084fc);
    animation: morph 8s ease-in-out infinite alternate-reverse;
  }
  
  &.active {
    .host-orb.speaking { transform: scale(1.4) rotate(45deg); opacity: 1; filter: blur(5px); box-shadow: 0 0 40px #60a5fa; }
    .expert-orb.speaking { transform: scale(1.4) rotate(-45deg); opacity: 1; filter: blur(5px); box-shadow: 0 0 40px #c084fc; }
  }
  
  .play-overlay {
    position: absolute; z-index: 10;
    width: 64px; height: 64px; border-radius: 50%;
    background: rgba(255,255,255,0.2); backdrop-filter: blur(5px);
    display: flex; align-items: center; justify-content: center;
    .play-icon { font-size: 1.5rem; margin-left: 4px; }
  }
}

@keyframes morph {
  0% { border-radius: 40% 60% 70% 30% / 40% 50% 60% 50%; }
  100% { border-radius: 60% 40% 30% 70% / 60% 30% 70% 40%; }
}

.speaker-labels {
  display: flex; gap: 32px; margin-top: 40px;
  .label { font-size: 0.85rem; font-weight: 600; opacity: 0.4; transition: all 0.3s; text-transform: uppercase; letter-spacing: 0.1em; }
  .label.active { opacity: 1; }
  .host-label.active { color: #60a5fa; text-shadow: 0 0 10px #60a5fa; }
  .expert-label.active { color: #c084fc; text-shadow: 0 0 10px #c084fc; }
}

/* ── Apple Music Style Lyrics ── */
.lyrics-section {
  flex: 1; overflow-y: auto; scroll-behavior: smooth;
  padding: 0 10%; margin-top: 40px;
  mask-image: linear-gradient(to bottom, transparent, black 10%, black 70%, transparent);
  -webkit-mask-image: linear-gradient(to bottom, transparent, black 10%, black 70%, transparent);
  
  &::-webkit-scrollbar { display: none; }
}

.lyrics-wrapper { display: flex; flex-direction: column; gap: 40px; padding-top: 20vh; }

.lyric-line {
  font-size: 2.5rem; line-height: 1.4; font-weight: 800;
  opacity: 0.15; filter: blur(2px); transform: translateY(20px) scale(0.95);
  transition: all 0.6s cubic-bezier(0.4, 0, 0.2, 1);
  text-align: center;
  
  &.past { opacity: 0.15; filter: blur(2px); transform: translateY(-20px) scale(0.95); }
  
  &.active { opacity: 1; filter: blur(0); transform: translateY(0) scale(1); }
  
  .karaoke-word {
    display: inline-block;
    transition: color 0.2s, text-shadow 0.2s;
    &.word-active { color: #fff; }
  }
  
  &.host .word-active { text-shadow: 0 0 20px rgba(96, 165, 250, 0.5); }
  &.expert .word-active { text-shadow: 0 0 20px rgba(192, 132, 252, 0.5); }
}
</style>
