<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'

// ── State ──────────────────────────────────────────────────────────
const isOpen       = ref(false)
const isExpanded   = ref(false)
const selectedText = ref('')
const mode         = ref('explain')   // 'explain' | 'translate' | 'flashcard'
const response     = ref('')
const isStreaming   = ref(false)
const chatHistory  = ref([])
const chatInput    = ref('')
const drawerRef    = ref(null)
const chatEndRef   = ref(null)

const modes = [
  { id: 'explain',   label: 'Giải thích' },
  { id: 'translate', label: 'Dịch thuật' },
  { id: 'flashcard', label: 'Flashcard'  },
]

// ── Text selection listener ────────────────────────────────────────
function onSelectionChange() {
  const sel = window.getSelection()
  const text = sel?.toString().trim()
  if (text && text.length > 3 && text.length < 1000) {
    selectedText.value = text
    isOpen.value = true
    response.value = ''
  }
}

// ── Simulated AI stream (fallback when backend offline) ────────────
const MOCK_RESPONSES = {
  explain: (t) => `**Giải thích: "${t.slice(0, 40)}..."**\n\nĐây là một khái niệm quan trọng trong lĩnh vực học thuật và công nghệ. Nội dung này đề cập đến các nguyên lý cốt lõi mà bạn cần nắm vững để tiến xa hơn trong lộ trình học tập.\n\n**Ứng dụng thực tế:**\n- Áp dụng trong các dự án thực tế\n- Nền tảng cho các khái niệm nâng cao hơn\n- Thường xuất hiện trong phỏng vấn kỹ thuật`,
  translate: (t) => `**Bản dịch:**\n\n"${t.slice(0, 60)}..."\n\n**Tiếng Việt:** Đây là bản dịch của đoạn văn bản được chọn. Ngôn ngữ gốc được phát hiện tự động và dịch sang tiếng Việt một cách tự nhiên, giữ nguyên ý nghĩa và ngữ cảnh của văn bản gốc.\n\n**Từ khóa chính:** học tập, công nghệ, thực hành`,
  flashcard: (t) => `**Flashcard:**\n\n**Mặt trước:**\n${t.slice(0, 60)}${t.length > 60 ? '...' : ''}\n\n**Mặt sau:**\nĐây là định nghĩa và giải thích ngắn gọn về khái niệm trên. Ghi nhớ bằng cách liên kết với ví dụ thực tế mà bạn đã gặp.\n\n**Mẹo nhớ:** Liên tưởng đến một tình huống cụ thể trong cuộc sống hàng ngày.`,
}

async function streamText(fullText) {
  response.value = ''
  isStreaming.value = true
  const words = fullText.split(' ')
  for (let i = 0; i < words.length; i++) {
    await new Promise(r => setTimeout(r, 28 + Math.random() * 20))
    response.value += (i === 0 ? '' : ' ') + words[i]
    chatEndRef.value?.scrollIntoView({ behavior: 'smooth' })
  }
  isStreaming.value = false
}

async function askAI(text, actionMode) {
  if (!text || isStreaming.value) return
  response.value = ''

  try {
    const config = useRuntimeConfig()
    const res = await fetch(`${config.public.apiBase}/api/ai-companion`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, mode: actionMode }),
      signal: AbortSignal.timeout(4000),
    })
    if (!res.ok || !res.body) throw new Error('No stream')

    isStreaming.value = true
    const reader = res.body.getReader()
    const decoder = new TextDecoder()
    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      response.value += decoder.decode(value, { stream: true })
      chatEndRef.value?.scrollIntoView({ behavior: 'smooth' })
    }
    isStreaming.value = false
  } catch {
    // Fallback to mock stream
    await streamText(MOCK_RESPONSES[actionMode]?.(text) ?? MOCK_RESPONSES.explain(text))
  }
}

function runMode(m) {
  mode.value = m
  askAI(selectedText.value, m)
}

// ── Chat ───────────────────────────────────────────────────────────
async function sendChat() {
  const msg = chatInput.value.trim()
  if (!msg || isStreaming.value) return
  chatInput.value = ''
  chatHistory.value.push({ role: 'user', text: msg })

  const mockChat = `Câu hỏi của bạn rất hay! Dựa trên ngữ cảnh "${selectedText.value?.slice(0,30)}...", tôi có thể giải thích thêm rằng: ${msg.length > 10 ? 'Đây là một chủ đề phức tạp cần được phân tích từ nhiều góc độ khác nhau.' : 'Vui lòng cung cấp thêm thông tin để tôi có thể hỗ trợ tốt hơn.'} Hãy thử áp dụng vào bài tập thực hành để củng cố kiến thức!`

  chatHistory.value.push({ role: 'ai', text: '' })
  isStreaming.value = true
  const words = mockChat.split(' ')
  const last = chatHistory.value[chatHistory.value.length - 1]
  for (let i = 0; i < words.length; i++) {
    await new Promise(r => setTimeout(r, 30))
    last.text += (i === 0 ? '' : ' ') + words[i]
    chatEndRef.value?.scrollIntoView({ behavior: 'smooth' })
  }
  isStreaming.value = false
}

// ── Parsed markdown (minimal) ──────────────────────────────────────
function parseMarkdown(text) {
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\n/g, '<br>')
}

// ── Lifecycle ─────────────────────────────────────────────────────
onMounted(() => {
  document.addEventListener('mouseup', onSelectionChange)
})
onUnmounted(() => {
  document.removeEventListener('mouseup', onSelectionChange)
})

// ── Close on outside click ────────────────────────────────────────
function onOverlayClick(e) {
  if (drawerRef.value && !drawerRef.value.contains(e.target)) {
    isOpen.value = false
  }
}
</script>

<template>
  <!-- Floating trigger button (always visible) -->
  <button
    class="ai-fab"
    :class="{ open: isOpen }"
    @click="isOpen = !isOpen"
    title="AI Study Companion"
  >
    <span class="ai-fab-icon">{{ isOpen ? '×' : 'AI' }}</span>
    <span class="ai-fab-pulse"></span>
  </button>

  <!-- Backdrop -->
  <Transition name="backdrop">
    <div v-if="isOpen" class="ai-backdrop" @click="onOverlayClick"></div>
  </Transition>

  <!-- Drawer -->
  <Transition name="drawer-slide">
    <div
      v-if="isOpen"
      ref="drawerRef"
      class="ai-drawer"
      :class="{ expanded: isExpanded }"
    >
      <!-- Header -->
      <div class="ai-header">
        <div class="ai-header-left">
          <div class="ai-avatar">AI</div>
          <div>
            <div class="ai-title">Study Companion</div>
            <div class="ai-subtitle">{{ isStreaming ? 'Đang suy nghĩ...' : 'Sẵn sàng hỗ trợ' }}</div>
          </div>
        </div>
        <div class="ai-header-actions">
          <button class="ai-ctrl-btn" @click="isExpanded = !isExpanded" :title="isExpanded ? 'Thu nhỏ' : 'Mở rộng'">
            {{ isExpanded ? '⊡' : '⊞' }}
          </button>
          <button class="ai-ctrl-btn" @click="isOpen = false" title="Đóng">×</button>
        </div>
      </div>

      <!-- Selected text chip -->
      <div v-if="selectedText" class="ai-selection-chip">
        <span class="chip-label">Đoạn đã chọn</span>
        <span class="chip-text">"{{ selectedText.slice(0, 80) }}{{ selectedText.length > 80 ? '...' : '' }}"</span>
      </div>
      <div v-else class="ai-empty-hint">
        Bôi đen bất kỳ đoạn văn nào trên trang để nhận hỗ trợ từ AI.
      </div>

      <!-- Mode selector -->
      <div v-if="selectedText" class="ai-mode-tabs">
        <button
          v-for="m in modes"
          :key="m.id"
          :class="['ai-mode-tab', { active: mode === m.id }]"
          @click="runMode(m.id)"
        >
          {{ m.label }}
        </button>
      </div>

      <!-- AI Response -->
      <div class="ai-response-area" v-if="selectedText">
        <div v-if="!response && !isStreaming" class="ai-response-placeholder">
          Chọn chế độ phía trên để bắt đầu
        </div>
        <div
          v-else
          class="ai-response-text"
          v-html="parseMarkdown(response)"
        ></div>
        <span v-if="isStreaming" class="ai-cursor">|</span>
      </div>

      <!-- Divider -->
      <div class="ai-divider"></div>

      <!-- Chat history -->
      <div class="ai-chat-history" v-if="chatHistory.length">
        <div
          v-for="(msg, i) in chatHistory"
          :key="i"
          :class="['ai-chat-msg', msg.role]"
        >
          <div class="msg-bubble" v-html="parseMarkdown(msg.text || '...')"></div>
        </div>
      </div>

      <!-- Chat input -->
      <div class="ai-chat-input-wrap">
        <input
          v-model="chatInput"
          class="ai-chat-input"
          placeholder="Hỏi thêm về nội dung này..."
          @keydown.enter.prevent="sendChat"
          :disabled="isStreaming"
        />
        <button
          class="ai-send-btn"
          @click="sendChat"
          :disabled="isStreaming || !chatInput.trim()"
        >
          {{ isStreaming ? '...' : 'Gửi' }}
        </button>
      </div>

      <div ref="chatEndRef"></div>
    </div>
  </Transition>
</template>

<style lang="scss" scoped>
// ── FAB Button ────────────────────────────────────────────────────
.ai-fab {
  position: fixed;
  right: 24px;
  bottom: 24px;
  z-index: 9990;
  width: 56px;
  height: 56px;
  border-radius: 50%;
  border: none;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: white;
  font-weight: 900;
  font-size: 0.85rem;
  cursor: pointer;
  box-shadow: 0 8px 32px rgba(99,102,241,0.5);
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
  display: flex;
  align-items: center;
  justify-content: center;
  position: fixed;

  &:hover { transform: scale(1.1); box-shadow: 0 12px 40px rgba(99,102,241,0.65); }
  &.open  { background: linear-gradient(135deg, #4f46e5, #7c3aed); }
}

.ai-fab-icon { position: relative; z-index: 1; font-size: 1rem; font-weight: 900; }

.ai-fab-pulse {
  position: absolute;
  inset: -4px;
  border-radius: 50%;
  border: 2px solid rgba(99,102,241,0.4);
  animation: pulse-ring 2s ease-out infinite;
}

@keyframes pulse-ring {
  0%   { transform: scale(1);   opacity: 0.6; }
  100% { transform: scale(1.5); opacity: 0; }
}

// ── Backdrop ──────────────────────────────────────────────────────
.ai-backdrop {
  position: fixed;
  inset: 0;
  z-index: 9991;
  background: rgba(0,0,0,0.15);
  backdrop-filter: blur(2px);
}

// ── Drawer ────────────────────────────────────────────────────────
.ai-drawer {
  position: fixed;
  right: 0;
  top: 0;
  bottom: 0;
  z-index: 9992;
  width: 380px;
  display: flex;
  flex-direction: column;
  gap: 0;
  overflow: hidden;

  // Glassmorphism
  background: rgba(255, 255, 255, 0.72);
  backdrop-filter: blur(28px) saturate(180%);
  -webkit-backdrop-filter: blur(28px) saturate(180%);
  border-left: 1px solid rgba(255,255,255,0.5);
  box-shadow:
    -20px 0 60px rgba(99,102,241,0.12),
    -4px 0 20px rgba(0,0,0,0.08);

  transition: width 0.35s cubic-bezier(0.4, 0, 0.2, 1);

  &.expanded { width: 560px; }
}

// ── Header ────────────────────────────────────────────────────────
.ai-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 20px 16px;
  border-bottom: 1px solid rgba(99,102,241,0.1);
  background: linear-gradient(135deg, rgba(99,102,241,0.08), rgba(139,92,246,0.06));
  flex-shrink: 0;
}

.ai-header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.ai-avatar {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 900;
  font-size: 0.75rem;
  box-shadow: 0 4px 12px rgba(99,102,241,0.35);
}

.ai-title    { font-weight: 800; font-size: 0.95rem; color: #1e1b4b; letter-spacing: -0.02em; }
.ai-subtitle { font-size: 0.72rem; color: #6366f1; font-weight: 600; margin-top: 1px; }

.ai-header-actions { display: flex; gap: 6px; }

.ai-ctrl-btn {
  width: 30px; height: 30px;
  border-radius: 8px;
  border: 1px solid rgba(99,102,241,0.15);
  background: rgba(99,102,241,0.06);
  color: #6366f1;
  font-size: 1.1rem;
  cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: all 0.2s ease;

  &:hover { background: rgba(99,102,241,0.15); border-color: rgba(99,102,241,0.35); }
}

// ── Selection chip ────────────────────────────────────────────────
.ai-selection-chip {
  margin: 16px;
  padding: 12px 14px;
  border-radius: 12px;
  background: linear-gradient(135deg, rgba(99,102,241,0.08), rgba(139,92,246,0.06));
  border: 1px solid rgba(99,102,241,0.18);
  flex-shrink: 0;
}

.chip-label {
  display: block;
  font-size: 0.68rem;
  font-weight: 800;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: #6366f1;
  margin-bottom: 4px;
}

.chip-text {
  font-size: 0.82rem;
  color: #374151;
  line-height: 1.5;
  font-style: italic;
}

.ai-empty-hint {
  margin: 20px 16px;
  padding: 20px;
  border-radius: 12px;
  background: rgba(99,102,241,0.04);
  border: 1px dashed rgba(99,102,241,0.2);
  text-align: center;
  font-size: 0.85rem;
  color: #6b7280;
  line-height: 1.6;
  flex-shrink: 0;
}

// ── Mode tabs ─────────────────────────────────────────────────────
.ai-mode-tabs {
  display: flex;
  gap: 6px;
  padding: 0 16px;
  flex-shrink: 0;
}

.ai-mode-tab {
  flex: 1;
  padding: 8px;
  border-radius: 8px;
  border: 1px solid rgba(99,102,241,0.15);
  background: transparent;
  color: #6b7280;
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover { background: rgba(99,102,241,0.06); color: #6366f1; }

  &.active {
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    color: white;
    border-color: transparent;
    box-shadow: 0 4px 12px rgba(99,102,241,0.3);
  }
}

// ── Response area ─────────────────────────────────────────────────
.ai-response-area {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  min-height: 0;

  &::-webkit-scrollbar       { width: 4px; }
  &::-webkit-scrollbar-track { background: transparent; }
  &::-webkit-scrollbar-thumb { background: rgba(99,102,241,0.2); border-radius: 999px; }
}

.ai-response-placeholder {
  text-align: center;
  color: #9ca3af;
  font-size: 0.83rem;
  padding: 32px 16px;
}

.ai-response-text {
  font-size: 0.875rem;
  color: #1f2937;
  line-height: 1.7;
  padding: 16px;
  background: rgba(255,255,255,0.7);
  border-radius: 12px;
  border: 1px solid rgba(99,102,241,0.1);
}

.ai-cursor {
  display: inline-block;
  animation: blink 0.7s step-end infinite;
  color: #6366f1;
  font-weight: 900;
}

@keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0; } }

// ── Divider ───────────────────────────────────────────────────────
.ai-divider {
  height: 1px;
  background: rgba(99,102,241,0.1);
  margin: 0 16px;
  flex-shrink: 0;
}

// ── Chat history ──────────────────────────────────────────────────
.ai-chat-history {
  overflow-y: auto;
  padding: 12px 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-height: 200px;

  &::-webkit-scrollbar       { width: 4px; }
  &::-webkit-scrollbar-thumb { background: rgba(99,102,241,0.15); border-radius: 999px; }
}

.ai-chat-msg {
  display: flex;

  &.user  { justify-content: flex-end; }
  &.ai    { justify-content: flex-start; }
}

.msg-bubble {
  max-width: 80%;
  padding: 10px 14px;
  border-radius: 14px;
  font-size: 0.82rem;
  line-height: 1.5;

  .user & {
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    color: white;
    border-bottom-right-radius: 4px;
  }

  .ai & {
    background: rgba(255,255,255,0.8);
    border: 1px solid rgba(99,102,241,0.12);
    color: #1f2937;
    border-bottom-left-radius: 4px;
  }
}

// ── Chat input ────────────────────────────────────────────────────
.ai-chat-input-wrap {
  display: flex;
  gap: 8px;
  padding: 16px;
  border-top: 1px solid rgba(99,102,241,0.1);
  background: rgba(255,255,255,0.5);
  flex-shrink: 0;
}

.ai-chat-input {
  flex: 1;
  padding: 10px 14px;
  border-radius: 10px;
  border: 1px solid rgba(99,102,241,0.2);
  background: rgba(255,255,255,0.8);
  font-size: 0.85rem;
  color: #1f2937;
  outline: none;
  transition: border-color 0.2s;

  &:focus { border-color: rgba(99,102,241,0.5); box-shadow: 0 0 0 3px rgba(99,102,241,0.08); }
  &::placeholder { color: #9ca3af; }
  &:disabled { opacity: 0.6; }
}

.ai-send-btn {
  padding: 10px 18px;
  border-radius: 10px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: white;
  font-size: 0.82rem;
  font-weight: 700;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;

  &:hover:not(:disabled) { box-shadow: 0 4px 16px rgba(99,102,241,0.4); transform: translateY(-1px); }
  &:disabled { opacity: 0.5; cursor: not-allowed; }
}

// ── Transitions ───────────────────────────────────────────────────
.drawer-slide-enter-active,
.drawer-slide-leave-active {
  transition: transform 0.38s cubic-bezier(0.4, 0, 0.2, 1),
              opacity 0.3s ease;
}
.drawer-slide-enter-from,
.drawer-slide-leave-to {
  transform: translateX(100%);
  opacity: 0;
}

.backdrop-enter-active, .backdrop-leave-active { transition: opacity 0.3s ease; }
.backdrop-enter-from, .backdrop-leave-to       { opacity: 0; }

// ── Mobile ────────────────────────────────────────────────────────
@media (max-width: 768px) {
  .ai-drawer { width: 100% !important; }
  .ai-fab    { right: 16px; bottom: 16px; }
}
</style>
