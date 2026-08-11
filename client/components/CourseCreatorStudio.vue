<script setup>
import { ref, watch, nextTick } from 'vue'

const emit = defineEmits(['close'])

// ── State ─────────────────────────────────────────────────────────
const courseTitle = ref(localStorage.getItem('ccs-title') || '')
const blocks = ref(JSON.parse(localStorage.getItem('ccs-blocks')) || [
  { id: generateId(), type: 'h1', content: 'Bài giảng mới...' },
  { id: generateId(), type: 'p', content: '' }
])

const isSaved = ref(true)
const slashMenu = ref({ visible: false, x: 0, y: 0, blockIndex: -1, query: '' })
const draggedBlockIndex = ref(-1)

// ── Helpers ───────────────────────────────────────────────────────
function generateId() {
  return Math.random().toString(36).substring(2, 9)
}

function saveDraft() {
  localStorage.setItem('ccs-title', courseTitle.value)
  localStorage.setItem('ccs-blocks', JSON.stringify(blocks.value))
  isSaved.value = true
  setTimeout(() => isSaved.value = false, 2000)
}

watch(blocks, () => {
  isSaved.value = false
  debouncedSave()
}, { deep: true })

watch(courseTitle, () => {
  isSaved.value = false
  debouncedSave()
})

let saveTimeout = null
function debouncedSave() {
  clearTimeout(saveTimeout)
  saveTimeout = setTimeout(saveDraft, 1000)
}

// ── Auto-resize Textarea ──────────────────────────────────────────
function autoResize(e) {
  const el = e.target
  el.style.height = 'auto'
  el.style.height = el.scrollHeight + 'px'
}

// ── Block Interactions ────────────────────────────────────────────
function handleInput(e, index) {
  autoResize(e)
  const text = blocks.value[index].content
  
  // Trigger Slash Menu
  if (text.endsWith('/') || (text.includes('/') && text.split('/').pop().length < 10)) {
    const slashIndex = text.lastIndexOf('/')
    const query = text.substring(slashIndex + 1)
    
    // Position menu near the cursor (simplified by using textarea bounds)
    const rect = e.target.getBoundingClientRect()
    slashMenu.value = {
      visible: true,
      x: rect.left,
      y: rect.bottom + window.scrollY,
      blockIndex: index,
      query: query.toLowerCase()
    }
  } else {
    slashMenu.value.visible = false
  }
}

function handleKeyDown(e, index) {
  // Menu Navigation overrides
  if (slashMenu.value.visible && (e.key === 'Escape' || e.key === 'Enter')) {
    e.preventDefault()
    if (e.key === 'Escape') slashMenu.value.visible = false
    return
  }

  // Create new block on Enter
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    const newBlock = { id: generateId(), type: 'p', content: '' }
    blocks.value.splice(index + 1, 0, newBlock)
    
    nextTick(() => {
      const el = document.getElementById(`block-${newBlock.id}`)
      if (el) { el.focus(); autoResize({ target: el }) }
    })
  } 
  // Delete block on Backspace if empty
  else if (e.key === 'Backspace' && blocks.value[index].content === '') {
    e.preventDefault()
    if (blocks.value.length > 1) {
      blocks.value.splice(index, 1)
      nextTick(() => {
        const prevBlock = blocks.value[index - 1]
        if (prevBlock) {
          const el = document.getElementById(`block-${prevBlock.id}`)
          if (el) { 
            el.focus()
            // Move cursor to end of textarea
            el.setSelectionRange(el.value.length, el.value.length)
          }
        }
      })
    }
  }
}

// ── Slash Menu Actions ────────────────────────────────────────────
const blockTypes = [
  { type: 'h1', label: 'Tiêu đề lớn (H1)', icon: 'T1' },
  { type: 'h2', label: 'Tiêu đề vừa (H2)', icon: 'T2' },
  { type: 'p', label: 'Văn bản (Text)', icon: 'TXT' },
  { type: 'image', label: 'Hình ảnh / Video', icon: 'IMG' },
  { type: 'code', label: 'Khối Code', icon: '{ }' },
  { type: 'quiz', label: 'Câu hỏi Quiz', icon: 'Q' }
]

import { computed } from 'vue'
const filteredBlockTypes = computed(() => {
  if (!slashMenu.value.query) return blockTypes
  return blockTypes.filter(b => b.label.toLowerCase().includes(slashMenu.value.query))
})

function changeBlockType(typeInfo) {
  const idx = slashMenu.value.blockIndex
  if (idx === -1) return
  
  // Remove the '/' and query
  const currentContent = blocks.value[idx].content
  const slashIndex = currentContent.lastIndexOf('/')
  blocks.value[idx].content = currentContent.substring(0, slashIndex)
  
  // Change type
  blocks.value[idx].type = typeInfo.type
  slashMenu.value.visible = false
  
  nextTick(() => {
    const el = document.getElementById(`block-${blocks.value[idx].id}`)
    if (el && el.tagName === 'TEXTAREA') {
      autoResize({ target: el })
      el.focus()
      el.setSelectionRange(el.value.length, el.value.length)
    }
  })
}

// ── Drag & Drop Blocks ────────────────────────────────────────────
function dragStart(e, index) {
  draggedBlockIndex.value = index
  e.dataTransfer.effectAllowed = 'move'
  setTimeout(() => e.target.classList.add('is-dragging'), 0)
}

function dragEnter(e, index) { e.preventDefault() }
function dragOver(e, index) { e.preventDefault(); e.dataTransfer.dropEffect = 'move' }

function drop(e, targetIndex) {
  e.preventDefault()
  if (draggedBlockIndex.value === -1 || draggedBlockIndex.value === targetIndex) return
  
  const item = blocks.value.splice(draggedBlockIndex.value, 1)[0]
  blocks.value.splice(targetIndex, 0, item)
  draggedBlockIndex.value = -1
}

function dragEnd(e) {
  draggedBlockIndex.value = -1
  e.target.classList.remove('is-dragging')
}

// ── Image Drop (Global) ───────────────────────────────────────────
function handleGlobalDrop(e) {
  e.preventDefault()
  const files = e.dataTransfer.files
  if (files && files.length > 0) {
    const file = files[0]
    if (file.type.startsWith('image/') || file.type.startsWith('video/')) {
      const reader = new FileReader()
      reader.onload = (event) => {
        blocks.value.push({ id: generateId(), type: 'image', content: event.target.result })
      }
      reader.readAsDataURL(file)
    }
  }
}
function handleGlobalDragOver(e) { e.preventDefault() }

</script>

<template>
  <div class="studio-overlay" @dragover="handleGlobalDragOver" @drop="handleGlobalDrop">
    <!-- Navbar -->
    <header class="studio-header">
      <div class="header-left">
        <button class="icon-btn" @click="emit('close')">Đóng</button>
        <span class="breadcrumbs">EduPress / <span class="highlight">Course Creator Studio</span></span>
      </div>
      <div class="header-right">
        <span class="save-status">
          <span v-if="isSaved" class="status-saved">Đã lưu nháp</span>
          <span v-else class="status-saving">Đang lưu...</span>
        </span>
        <button class="publish-btn">Xuất bản</button>
      </div>
    </header>

    <!-- Editor Canvas -->
    <main class="studio-canvas">
      <div class="editor-container">
        <!-- Title Input -->
        <textarea 
          class="title-input auto-resize" 
          placeholder="Tên bài giảng..." 
          v-model="courseTitle"
          @input="autoResize"
          rows="1"
        ></textarea>

        <!-- Block List -->
        <div class="block-list">
          <div 
            v-for="(block, index) in blocks" 
            :key="block.id"
            class="block-wrapper"
            draggable="true"
            @dragstart="dragStart($event, index)"
            @dragenter="dragEnter($event, index)"
            @dragover="dragOver($event, index)"
            @drop="drop($event, index)"
            @dragend="dragEnd"
          >
            <!-- Drag Handle -->
            <div class="drag-handle" title="Kéo để di chuyển">⋮⋮</div>

            <!-- Auto-resizing Textareas for Text Blocks (Flawless Reactivity) -->
            <textarea
              v-if="['h1', 'h2', 'p'].includes(block.type)"
              :id="`block-${block.id}`"
              class="editable-block auto-resize"
              :class="`type-${block.type}`"
              v-model="block.content"
              :placeholder="block.type === 'p' ? 'Gõ / để mở menu lệnh...' : 'Nhập tiêu đề...'"
              rows="1"
              @input="handleInput($event, index)"
              @keydown="handleKeyDown($event, index)"
              @focus="autoResize"
            ></textarea>

            <!-- Image/Video Block -->
            <div v-else-if="block.type === 'image'" class="media-block">
              <img v-if="block.content" :src="block.content" alt="Media" />
              <div v-else class="media-placeholder">
                Kéo thả file ảnh/video vào đây
              </div>
            </div>

            <!-- Code Block -->
            <div v-else-if="block.type === 'code'" class="code-block">
              <div class="block-badge">Code Snippet</div>
              <textarea v-model="block.content" placeholder="Nhập mã code vào đây..."></textarea>
            </div>

            <!-- Quiz Block -->
            <div v-else-if="block.type === 'quiz'" class="quiz-block">
              <div class="block-badge quiz">Quiz</div>
              <input type="text" v-model="block.content" placeholder="Nhập câu hỏi trắc nghiệm..." class="quiz-q" />
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- Slash Menu Floating -->
    <div 
      v-if="slashMenu.visible" 
      class="slash-menu" 
      :style="{ top: slashMenu.y + 5 + 'px', left: slashMenu.x + 'px' }"
    >
      <div class="menu-header">Thêm Block</div>
      <button 
        v-for="type in filteredBlockTypes" 
        :key="type.type"
        class="menu-item"
        @click="changeBlockType(type)"
      >
        <span class="menu-icon">{{ type.icon }}</span>
        <span class="menu-label">{{ type.label }}</span>
      </button>
      <div v-if="filteredBlockTypes.length === 0" class="menu-empty">Không tìm thấy lệnh</div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.studio-overlay {
  position: fixed; inset: 0; z-index: 10000; background: #ffffff;
  display: flex; flex-direction: column; animation: fadeIn 0.3s ease; overflow: hidden;
}

.studio-header {
  height: 56px; border-bottom: 1px solid #e2e8f0; display: flex; justify-content: space-between; align-items: center;
  padding: 0 16px; background: rgba(255, 255, 255, 0.9); backdrop-filter: blur(8px); z-index: 100;
}
.header-left { display: flex; align-items: center; gap: 12px; }
.icon-btn { background: transparent; border: none; font-size: 1.2rem; cursor: pointer; padding: 8px; border-radius: 4px; &:hover { background: #f1f5f9; } }
.breadcrumbs { font-size: 0.9rem; color: #64748b; .highlight { color: #0f172a; font-weight: 600; } }
.header-right { display: flex; align-items: center; gap: 20px; }
.save-status { font-size: 0.85rem; .status-saved { color: #10b981; } .status-saving { color: #94a3b8; font-style: italic; } }
.publish-btn { background: #3b82f6; color: white; border: none; padding: 8px 16px; border-radius: 6px; font-weight: 600; cursor: pointer; transition: all 0.2s; &:hover { background: #2563eb; } }

.studio-canvas { flex: 1; overflow-y: auto; padding: 64px 20px 200px; scroll-behavior: smooth; }
.editor-container { max-width: 800px; margin: 0 auto; }

// Auto-resizing textarea resets
.auto-resize {
  width: 100%; border: none; outline: none; background: transparent; resize: none; overflow: hidden;
  font-family: inherit; line-height: 1.5; padding: 0;
}

.title-input { font-size: 3rem; font-weight: 800; color: #0f172a; margin-bottom: 32px; &::placeholder { color: #cbd5e1; } }

.block-list { display: flex; flex-direction: column; gap: 4px; }
.block-wrapper { position: relative; display: flex; align-items: flex-start; padding: 4px 0; transition: background 0.2s; &.is-dragging { opacity: 0.4; background: #f8fafc; } }

.drag-handle {
  position: absolute; left: -32px; top: 8px; width: 24px; height: 24px; display: flex; align-items: center; justify-content: center;
  color: #cbd5e1; font-size: 1.2rem; cursor: grab; opacity: 0; transition: opacity 0.2s; user-select: none;
}
.block-wrapper:hover .drag-handle { opacity: 1; }
.drag-handle:active { cursor: grabbing; }

// Editable Text Blocks (Textareas)
.editable-block {
  flex: 1; color: #334155;
  &::placeholder { color: #cbd5e1; }
}
.type-h1 { font-size: 2rem; font-weight: 700; margin-top: 24px; margin-bottom: 8px; color: #0f172a; line-height: 1.2; }
.type-h2 { font-size: 1.5rem; font-weight: 600; margin-top: 16px; margin-bottom: 8px; color: #1e293b; line-height: 1.3; }
.type-p  { font-size: 1.1rem; line-height: 1.6; min-height: 28px; }

// Media Block
.media-block {
  width: 100%; margin: 16px 0; border-radius: 8px; overflow: hidden; background: #f1f5f9;
  img { width: 100%; height: auto; display: block; }
  .media-placeholder { padding: 64px 20px; text-align: center; color: #64748b; border: 2px dashed #cbd5e1; border-radius: 8px; }
}

// Code & Quiz Blocks
.code-block, .quiz-block {
  width: 100%; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 16px; margin: 12px 0; position: relative;
  .block-badge { position: absolute; top: -10px; left: 16px; background: #3b82f6; color: white; font-size: 0.7rem; font-weight: 700; padding: 2px 8px; border-radius: 4px; &.quiz { background: #f59e0b; } }
  textarea { width: 100%; min-height: 100px; background: #0f172a; color: #f8fafc; border: none; outline: none; border-radius: 4px; padding: 12px; font-family: monospace; font-size: 0.9rem; }
  .quiz-q { width: 100%; border: none; border-bottom: 2px solid #e2e8f0; padding: 8px 0; font-size: 1.1rem; font-weight: 600; background: transparent; outline: none; &:focus { border-bottom-color: #f59e0b; } }
}

// Slash Menu
.slash-menu {
  position: absolute; background: white; border-radius: 8px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); border: 1px solid #e2e8f0; width: 280px; z-index: 10001; overflow: hidden;
  animation: scaleIn 0.2s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}
.menu-header { font-size: 0.75rem; font-weight: 700; color: #94a3b8; padding: 12px 16px 8px; text-transform: uppercase; }
.menu-item {
  width: 100%; display: flex; align-items: center; gap: 12px; padding: 10px 16px; background: transparent; border: none; cursor: pointer; text-align: left; transition: background 0.1s;
  &:hover { background: #f1f5f9; }
  .menu-icon { width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 4px; font-weight: 700; color: #3b82f6; }
  .menu-label { font-size: 0.95rem; font-weight: 500; color: #1e293b; }
}
.menu-empty { padding: 16px; text-align: center; color: #94a3b8; font-size: 0.9rem; }

@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
@keyframes scaleIn { from { opacity: 0; transform: scale(0.95) translateY(-10px); } to { opacity: 1; transform: scale(1) translateY(0); } }
</style>
