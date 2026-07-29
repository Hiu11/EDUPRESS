<script setup>
import { ref, onMounted, onUnmounted, computed, watch } from 'vue'
import loader from '@monaco-editor/loader'

const emit = defineEmits(['close'])

// ── File Explorer ─────────────────────────────────────────────────
const files = ref([
  {
    name: 'index.html',
    lang: 'html',
    icon: '🌐',
    content: `<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>UI Component</title>
  <link rel="stylesheet" href="style.css" />
</head>
<body>
  <div class="course-card">
    <div class="card-header">
      <span class="badge">Lập trình Web</span>
      <h2>Khoá học UI/UX Toàn diện</h2>
    </div>
    <div class="card-body">
      <p>Học cách thiết kế giao diện tinh tế, hiện đại và thực tế. 🎨</p>
      <div class="progress-wrapper">
        <div class="progress-info">
          <span>Tiến độ</span>
          <span id="percent">65%</span>
        </div>
        <div class="progress-bar">
          <div class="progress-fill" id="fill"></div>
        </div>
      </div>
    </div>
    <button class="action-btn" onclick="completeModule()">Hoàn thành bài học</button>
  </div>
  <script src="script.js"><\/script>
</body>
</html>`
  },
  {
    name: 'style.css',
    lang: 'css',
    icon: '🎨',
    content: `@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;800&display=swap');

* { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: 'Outfit', sans-serif;
  background-color: #f8fafc;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #0f172a;
}

.course-card {
  background: #ffffff;
  padding: 32px;
  border-radius: 20px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.08);
  max-width: 400px;
  width: 90%;
  border: 1px solid #e2e8f0;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.course-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.12);
}

.badge {
  display: inline-block;
  background: #eff6ff;
  color: #3b82f6;
  padding: 6px 12px;
  border-radius: 100px;
  font-size: 0.8rem;
  font-weight: 600;
  margin-bottom: 16px;
  letter-spacing: 0.5px;
}

h2 {
  font-size: 1.8rem;
  font-weight: 800;
  margin-bottom: 12px;
  line-height: 1.2;
}

p {
  color: #64748b;
  font-size: 1rem;
  margin-bottom: 24px;
}

.progress-wrapper { margin-bottom: 32px; }

.progress-info {
  display: flex;
  justify-content: space-between;
  font-size: 0.9rem;
  font-weight: 600;
  color: #475569;
  margin-bottom: 8px;
}

.progress-bar {
  height: 8px;
  background: #f1f5f9;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  width: 65%;
  background: #3b82f6;
  border-radius: 4px;
  transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1), background 0.3s;
}

.action-btn {
  width: 100%;
  background: #0f172a;
  color: white;
  border: none;
  padding: 14px;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s, transform 0.1s;
}

.action-btn:hover { background: #334155; }
.action-btn:active { transform: scale(0.98); }`
  },
  {
    name: 'script.js',
    lang: 'javascript',
    icon: '⚡',
    content: `let currentProgress = 65;

function completeModule() {
  const fill = document.getElementById('fill');
  const percentText = document.getElementById('percent');
  const btn = document.querySelector('.action-btn');
  
  if (currentProgress < 100) {
    currentProgress = 100;
    fill.style.width = currentProgress + '%';
    
    // Animate percentage text
    let counter = 65;
    const interval = setInterval(() => {
      counter += 1;
      percentText.textContent = counter + '%';
      if (counter >= 100) {
        clearInterval(interval);
        fill.style.background = '#10b981'; // Success green
        percentText.style.color = '#10b981';
        btn.textContent = 'Khóa học hoàn tất 🎉';
        btn.style.background = '#10b981';
      }
    }, 15);
  }
}`
  }
])

const activeFile = ref(files.value[0])
const previewSrc = ref('')
const isRunning = ref(false)
const editorContainer = ref(null)
let monacoEditor = null
let monaco = null

// ── Editor setup ──────────────────────────────────────────────────
onMounted(async () => {
  loader.config({ paths: { vs: 'https://cdn.jsdelivr.net/npm/monaco-editor@0.45.0/min/vs' } })
  monaco = await loader.init()

  monacoEditor = monaco.editor.create(editorContainer.value, {
    value: activeFile.value.content,
    language: activeFile.value.lang,
    theme: 'vs-dark',
    fontSize: 14,
    fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
    fontLigatures: true,
    minimap: { enabled: false },
    scrollBeyondLastLine: false,
    lineNumbers: 'on',
    renderLineHighlight: 'all',
    smoothScrolling: true,
    cursorSmoothCaretAnimation: 'on',
    automaticLayout: true,
    tabSize: 2,
    wordWrap: 'on',
    padding: { top: 16, bottom: 16 },
  })

  // Sync editor changes back to file content
  monacoEditor.onDidChangeModelContent(() => {
    activeFile.value.content = monacoEditor.getValue()
  })

  // Auto-run on mount
  runCode()
  window.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  monacoEditor?.dispose()
  window.removeEventListener('keydown', handleKeydown)
})

function handleKeydown(e) {
  if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
    e.preventDefault()
    runCode()
  }
  if (e.key === 'Escape') emit('close')
}

// ── Switch file ───────────────────────────────────────────────────
function switchFile(file) {
  activeFile.value.content = monacoEditor.getValue()
  activeFile.value = file

  const model = monaco.editor.createModel(file.content, file.lang)
  monacoEditor.setModel(model)
  monacoEditor.focus()
}

// ── Run code ──────────────────────────────────────────────────────
function runCode() {
  isRunning.value = true
  activeFile.value.content = monacoEditor?.getValue() ?? activeFile.value.content

  const html  = files.value.find(f => f.name === 'index.html')?.content ?? ''
  const css   = files.value.find(f => f.name === 'style.css')?.content ?? ''
  const js    = files.value.find(f => f.name === 'script.js')?.content ?? ''

  const combined = html
    .replace('href="style.css"', ``)
    .replace('src="script.js"', ``)
    .replace('</head>', `<style>${css}</style></head>`)
    .replace('</body>', `<script>${js}<\/script></body>`)

  previewSrc.value = combined
  setTimeout(() => { isRunning.value = false }, 600)
}

// ── Splitter drag ─────────────────────────────────────────────────
const explorerWidth = ref(200)
const editorWidth   = ref(null) // flex: 1
const isDraggingL   = ref(false)
const isDraggingR   = ref(false)
const previewWidth  = ref(380)

function startDragLeft(e) {
  isDraggingL.value = true
  const startX = e.clientX
  const startW = explorerWidth.value

  const onMove = (ev) => {
    explorerWidth.value = Math.max(140, Math.min(360, startW + ev.clientX - startX))
  }
  const onUp = () => {
    isDraggingL.value = false
    window.removeEventListener('mousemove', onMove)
    window.removeEventListener('mouseup', onUp)
  }
  window.addEventListener('mousemove', onMove)
  window.addEventListener('mouseup', onUp)
}

function startDragRight(e) {
  isDraggingR.value = true
  const startX = e.clientX
  const startW = previewWidth.value

  const onMove = (ev) => {
    previewWidth.value = Math.max(240, Math.min(700, startW - (ev.clientX - startX)))
  }
  const onUp = () => {
    isDraggingR.value = false
    window.removeEventListener('mousemove', onMove)
    window.removeEventListener('mouseup', onUp)
  }
  window.addEventListener('mousemove', onMove)
  window.addEventListener('mouseup', onUp)
}
</script>

<template>
  <div class="ide-overlay">
    <!-- ── TOP BAR ── -->
    <div class="ide-topbar">
      <div class="ide-topbar-left">
        <span class="ide-logo">⚡ EduPress IDE</span>
        <span class="ide-badge">In-Browser Sandbox</span>
      </div>
      <div class="ide-topbar-center">
        <button
          class="run-btn"
          :class="{ running: isRunning }"
          @click="runCode"
          title="Ctrl + Enter"
        >
          <span>{{ isRunning ? '⟳' : '▶' }}</span>
          {{ isRunning ? 'Running...' : 'Run' }}
        </button>
      </div>
      <div class="ide-topbar-right">
        <span class="kbd-hint">Ctrl+Enter để chạy</span>
        <button class="ide-close" @click="emit('close')" title="Đóng (Esc)">✕</button>
      </div>
    </div>

    <!-- ── MAIN PANES ── -->
    <div class="ide-body" :class="{ 'no-select': isDraggingL || isDraggingR }">

      <!-- FILE EXPLORER -->
      <aside class="file-explorer" :style="{ width: explorerWidth + 'px' }">
        <div class="explorer-header">
          <span>📁 FILES</span>
        </div>
        <ul class="file-list">
          <li
            v-for="file in files"
            :key="file.name"
            :class="['file-item', { active: activeFile.name === file.name }]"
            @click="switchFile(file)"
          >
            <span class="file-icon">{{ file.icon }}</span>
            <span class="file-name">{{ file.name }}</span>
          </li>
        </ul>
        <div class="explorer-footer">
          <span>Issue <strong>#8</strong></span>
        </div>
      </aside>

      <!-- SPLITTER LEFT -->
      <div class="splitter" @mousedown.prevent="startDragLeft" :class="{ active: isDraggingL }">
        <div class="splitter-handle"></div>
      </div>

      <!-- EDITOR -->
      <div class="editor-pane">
        <div class="editor-tabs">
          <button
            v-for="file in files"
            :key="file.name"
            :class="['tab', { active: activeFile.name === file.name }]"
            @click="switchFile(file)"
          >
            {{ file.icon }} {{ file.name }}
          </button>
        </div>
        <div ref="editorContainer" class="editor-container"></div>
      </div>

      <!-- SPLITTER RIGHT -->
      <div class="splitter" @mousedown.prevent="startDragRight" :class="{ active: isDraggingR }">
        <div class="splitter-handle"></div>
      </div>

      <!-- PREVIEW -->
      <div class="preview-pane" :style="{ width: previewWidth + 'px' }">
        <div class="preview-header">
          <span class="preview-dot red"></span>
          <span class="preview-dot yellow"></span>
          <span class="preview-dot green"></span>
          <span class="preview-title">Preview</span>
          <button class="preview-refresh" @click="runCode" title="Refresh">⟳</button>
        </div>
        <iframe
          class="preview-frame"
          sandbox="allow-scripts"
          :srcdoc="previewSrc"
        ></iframe>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.ide-overlay {
  position: fixed;
  inset: 0;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  background: #0d1117;
  font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
  animation: ideSlideIn 0.3s ease;

  @keyframes ideSlideIn {
    from { opacity: 0; transform: translateY(20px); }
    to   { opacity: 1; transform: translateY(0); }
  }
}

// ── Top Bar ────────────────────────────────────────────────────────
.ide-topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  height: 48px;
  background: #161b22;
  border-bottom: 1px solid #30363d;
  flex-shrink: 0;
  gap: 16px;
}

.ide-topbar-left, .ide-topbar-right, .ide-topbar-center {
  display: flex;
  align-items: center;
  gap: 12px;
}

.ide-logo {
  font-size: 0.95rem;
  font-weight: 700;
  color: #e6edf3;
  letter-spacing: -0.02em;
}

.ide-badge {
  font-size: 0.65rem;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 999px;
  background: rgba(99,102,241,0.2);
  border: 1px solid rgba(99,102,241,0.4);
  color: #a5b4fc;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.run-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  background: linear-gradient(135deg, #22c55e, #16a34a);
  color: white;
  border: none;
  padding: 8px 24px;
  border-radius: 8px;
  font-weight: 700;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 0 20px rgba(34,197,94,0.3);

  span { font-size: 1rem; }

  &:hover { transform: translateY(-1px); box-shadow: 0 4px 20px rgba(34,197,94,0.5); }

  &.running {
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    box-shadow: 0 0 20px rgba(99,102,241,0.4);
    span { animation: spin 0.6s linear infinite; }
  }

  @keyframes spin { to { transform: rotate(360deg); } }
}

.kbd-hint {
  font-size: 0.72rem;
  color: #6e7681;
  font-family: 'Segoe UI', sans-serif;
}

.ide-close {
  width: 32px; height: 32px;
  background: rgba(255,255,255,0.05);
  border: 1px solid #30363d;
  border-radius: 6px;
  color: #8b949e;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex; align-items: center; justify-content: center;

  &:hover { background: rgba(220,38,38,0.2); border-color: rgba(220,38,38,0.4); color: #fca5a5; }
}

// ── Body ───────────────────────────────────────────────────────────
.ide-body {
  display: flex;
  flex: 1;
  overflow: hidden;

  &.no-select { user-select: none; }
}

// ── File Explorer ──────────────────────────────────────────────────
.file-explorer {
  display: flex;
  flex-direction: column;
  background: #161b22;
  border-right: 1px solid #30363d;
  flex-shrink: 0;
  overflow: hidden;
}

.explorer-header {
  padding: 12px 16px;
  font-size: 0.7rem;
  font-weight: 700;
  color: #8b949e;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  border-bottom: 1px solid #21262d;
}

.file-list {
  list-style: none;
  flex: 1;
  overflow-y: auto;
  padding: 8px 0;
}

.file-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 16px;
  cursor: pointer;
  transition: all 0.15s ease;
  border-left: 2px solid transparent;
  font-size: 0.85rem;
  color: #8b949e;

  &:hover { background: rgba(255,255,255,0.04); color: #e6edf3; }

  &.active {
    background: rgba(99,102,241,0.1);
    border-left-color: #6366f1;
    color: #e6edf3;
  }

  .file-icon { font-size: 1rem; }
  .file-name  { font-size: 0.85rem; }
}

.explorer-footer {
  padding: 12px 16px;
  font-size: 0.72rem;
  color: #484f58;
  border-top: 1px solid #21262d;
  font-family: 'Segoe UI', sans-serif;
}

// ── Splitter ───────────────────────────────────────────────────────
.splitter {
  width: 6px;
  background: #21262d;
  cursor: col-resize;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.15s;
  position: relative;

  &:hover, &.active { background: #6366f1; }

  .splitter-handle {
    width: 2px;
    height: 40px;
    background: rgba(255,255,255,0.15);
    border-radius: 999px;
  }
}

// ── Editor Pane ────────────────────────────────────────────────────
.editor-pane {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-width: 200px;
}

.editor-tabs {
  display: flex;
  background: #161b22;
  border-bottom: 1px solid #30363d;
  flex-shrink: 0;
  overflow-x: auto;

  &::-webkit-scrollbar { height: 2px; }
  &::-webkit-scrollbar-thumb { background: #30363d; }
}

.tab {
  padding: 10px 20px;
  background: transparent;
  border: none;
  border-right: 1px solid #21262d;
  border-bottom: 2px solid transparent;
  color: #6e7681;
  font-size: 0.8rem;
  font-family: 'JetBrains Mono', monospace;
  cursor: pointer;
  transition: all 0.15s ease;
  white-space: nowrap;
  flex-shrink: 0;

  &:hover { color: #e6edf3; background: rgba(255,255,255,0.03); }

  &.active {
    color: #e6edf3;
    border-bottom-color: #6366f1;
    background: #0d1117;
  }
}

.editor-container {
  flex: 1;
  overflow: hidden;
}

// ── Preview Pane ───────────────────────────────────────────────────
.preview-pane {
  display: flex;
  flex-direction: column;
  background: #ffffff;
  border-left: 1px solid #30363d;
  flex-shrink: 0;
  min-width: 240px;
}

.preview-header {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 16px;
  background: #f5f5f5;
  border-bottom: 1px solid #e0e0e0;
  flex-shrink: 0;
}

.preview-dot {
  width: 12px; height: 12px;
  border-radius: 50%;

  &.red    { background: #ff5f57; }
  &.yellow { background: #febc2e; }
  &.green  { background: #28c840; }
}

.preview-title {
  flex: 1;
  font-size: 0.75rem;
  color: #666;
  font-family: 'Segoe UI', sans-serif;
  margin-left: 8px;
}

.preview-refresh {
  background: transparent;
  border: none;
  color: #999;
  font-size: 1rem;
  cursor: pointer;
  padding: 2px 6px;
  border-radius: 4px;
  transition: all 0.15s;

  &:hover { background: #e0e0e0; color: #333; }
}

.preview-frame {
  flex: 1;
  border: none;
  width: 100%;
}
</style>
