<script setup>
import { ref, onMounted, onUnmounted, computed, watch } from 'vue'
import loader from '@monaco-editor/loader'

const emit = defineEmits(['close'])

// ── File Explorer ─────────────────────────────────────────────────
const files = ref([
  {
    name: 'index.html',
    lang: 'html',
    icon: 'HTML',
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
      <p>Học cách thiết kế giao diện tinh tế, hiện đại và thực tế.</p>
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
    icon: 'CSS',
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
    icon: 'JS',
    content: `let currentProgress = 65;

function completeModule() {
  var fill = document.getElementById('fill');
  var percentText = document.getElementById('percent');
  const btn = document.querySelector('.action-btn');
  
  if (currentProgress == 100) {
    return;
  }
  
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
        btn.textContent = 'Khóa học hoàn tất';
        btn.style.background = '#10b981';
      }
    }, 15);
  }
}`
  }
])

const aiState = ref('idle')
const aiStatusText = ref('Trợ lý kiểm tra mã sẵn sàng')
const showAIPanel = ref(false)
const aiLogs = ref([])

function addAILog(message, type = 'info') {
  aiLogs.value.push({ time: new Date().toLocaleTimeString('vi-VN', {hour12: false}), message, type })
}

let scanId = 0
async function scanCodeSmells(model) {
  scanId++
  const currentScanId = scanId
  const code = model.getValue()
  const markers = []
  
  aiState.value = 'scanning'
  aiStatusText.value = 'Đang phân tích AST...'
  showAIPanel.value = true
  if (aiLogs.value.length > 50) aiLogs.value = [] // clear if too long
  
  addAILog('--- Khởi tạo phiên phân tích mới ---', 'system')
  addAILog('Khởi tạo bộ kiểm tra mã trong trình duyệt.', 'system')
  await new Promise(r => setTimeout(r, 400))
  if (scanId !== currentScanId) return
  
  addAILog('Đang đọc cấu trúc mã nguồn.', 'info')
  await new Promise(r => setTimeout(r, 500))
  if (scanId !== currentScanId) return
  
  addAILog('Bắt đầu phân tích JavaScript.', 'info')
  await new Promise(r => setTimeout(r, 600))
  if (scanId !== currentScanId) return
  
  addAILog('Kiểm tra các lỗi thường gặp.', 'info')
  await new Promise(r => setTimeout(r, 700))
  if (scanId !== currentScanId) return

  const lines = code.split('\n')
  lines.forEach((line, i) => {
    // Detect 'var'
    const varMatch = line.match(/\bvar\b/)
    if (varMatch) {
      markers.push({
        severity: monaco.MarkerSeverity.Error,
        startLineNumber: i + 1,
        startColumn: varMatch.index + 1,
        endLineNumber: i + 1,
        endColumn: varMatch.index + 4,
        message: "Nên thay `var` bằng `const` hoặc `let` để tránh lỗi scope và hoisting.",
        source: 'Code Review'
      })
    }
    
    // Detect '=='
    const eqMatch = line.match(/ == /)
    if (eqMatch) {
      markers.push({
        severity: monaco.MarkerSeverity.Warning,
        startLineNumber: i + 1,
        startColumn: eqMatch.index + 2,
        endLineNumber: i + 1,
        endColumn: eqMatch.index + 4,
        message: "Nên dùng `===` để tránh ép kiểu ngầm khi so sánh.",
        source: 'Code Review'
      })
    }
  })
  
  if (markers.length > 0) {
    addAILog(`Phát hiện ${markers.length} điểm cần xem lại.`, 'warning')
    aiState.value = 'found-smell'
    aiStatusText.value = `Phát hiện ${markers.length} điểm cần sửa`
  } else {
    addAILog('Không phát hiện vấn đề nổi bật.', 'success')
    aiState.value = 'idle'
    aiStatusText.value = 'Mã nguồn ổn định'
    setTimeout(() => { 
      if (scanId === currentScanId) showAIPanel.value = false 
    }, 4000)
  }
  
  monaco.editor.setModelMarkers(model, 'ai-mentor', markers)
}

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
    lightbulb: { enabled: true } // Enable Quick Fix lightbulb
  })

  // Register quick-fix command
  if (!window.aiCommandRegistered) {
    monaco.editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter, () => runCode())
    // Register QuickFix provider for JS
    monaco.languages.registerCodeActionProvider('javascript', {
      provideCodeActions: (model, range, context) => {
        const actions = context.markers
          .filter(m => m.source === 'Code Review')
          .map(marker => {
            let fixText = "const"
            if (marker.message.includes('==' )) fixText = "==="
            
            return {
              title: "Áp dụng gợi ý sửa",
              diagnostics: [marker],
              kind: "quickfix",
              edit: {
                edits: [{
                  resource: model.uri,
                  textEdit: { range: marker, text: fixText },
                  versionId: undefined
                }]
              },
              isPreferred: true
            }
          })
        return { actions, dispose: () => {} }
      }
    })
    window.aiCommandRegistered = true
  }

  // Sync editor changes back to file content and trigger review
  let aiTimeout = null
  monacoEditor.onDidChangeModelContent(() => {
    activeFile.value.content = monacoEditor.getValue()
    
    if (activeFile.value.lang === 'javascript') {
      aiState.value = 'scanning'
      aiStatusText.value = 'Đang kiểm tra mã...'
      clearTimeout(aiTimeout)
      aiTimeout = setTimeout(() => scanCodeSmells(monacoEditor.getModel()), 1200)
    }
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
        <span class="ide-logo">EduPress Practice</span>
        <span class="ide-badge">Sandbox</span>
      </div>
      <div class="ide-topbar-center">
        <div class="ai-status-pill" :class="aiState">
          <span class="ai-text">{{ aiStatusText }}</span>
          <div class="ai-laser" v-if="aiState === 'scanning'"></div>
        </div>
        
        <button
          class="run-btn"
          :class="{ running: isRunning }"
          @click="runCode"
          title="Ctrl + Enter"
        >
          {{ isRunning ? 'Running...' : 'Run' }}
        </button>
      </div>
      <div class="ide-topbar-right">
        <span class="kbd-hint">Ctrl+Enter để chạy</span>
        <button class="ide-close" @click="emit('close')" title="Đóng (Esc)">Đóng</button>
      </div>
    </div>

    <!-- ── MAIN PANES ── -->
    <div class="ide-body" :class="{ 'no-select': isDraggingL || isDraggingR }">

      <!-- FILE EXPLORER -->
      <aside class="file-explorer" :style="{ width: explorerWidth + 'px' }">
        <div class="explorer-header">
          <span>FILES</span>
        </div>
        <ul class="file-list">
          <li
            v-for="file in files"
            :key="file.name"
            :class="['file-item', { active: activeFile.name === file.name }]"
            @click="switchFile(file)"
          >
          <span class="file-icon">{{ file.lang.toUpperCase() }}</span>
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
            {{ file.name }}
          </button>
        </div>
        <div ref="editorContainer" class="editor-container"></div>
        
        <!-- REVIEW LOG PANEL -->
        <transition name="slide-up">
          <div v-if="showAIPanel" class="ai-terminal-panel">
            <div class="ai-terminal-header">
              <span class="title">Nhật ký kiểm tra mã</span>
              <button class="close-btn" @click="showAIPanel = false" title="Đóng terminal">Đóng</button>
            </div>
            <div class="ai-terminal-body" ref="terminalBody">
              <div v-for="(log, idx) in aiLogs" :key="idx" :class="['ai-log-line', log.type]">
                <span class="log-time">[{{ log.time }}]</span>
                <span class="log-msg">{{ log.message }}</span>
              </div>
            </div>
          </div>
        </transition>
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
          <button class="preview-refresh" @click="runCode" title="Refresh">Refresh</button>
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

@media (max-width: 768px) {
  .ide-topbar {
    flex-wrap: nowrap; // Don't wrap, keep it 1 line
    padding: 0 12px;
    gap: 8px;
  }
  .ide-badge, .kbd-hint, .ai-status-pill {
    display: none !important; // Hide non-essentials on mobile
  }
  .run-btn {
    padding: 6px 12px;
    font-size: 0.8rem;
  }
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
  padding: 3px 8px;
  border-radius: 6px;
  background: rgba(255,255,255,0.05);
  border: 1px solid #30363d;
  color: #8b949e;
  text-transform: none;
  letter-spacing: 0;
}

.run-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #238636;
  color: white;
  border: none;
  padding: 8px 24px;
  border-radius: 8px;
  font-weight: 700;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: none;

  span { font-size: 1rem; }

  &:hover { background: #2ea043; }

  &.running {
    background: #30363d;
    box-shadow: none;
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

  @media (max-width: 768px) {
    flex-direction: column;
  }
}

// ── File Explorer ──────────────────────────────────────────────────
.file-explorer {
  display: flex;
  flex-direction: column;
  background: #161b22;
  border-right: 1px solid #30363d;
  flex-shrink: 0;
  overflow: hidden;

  @media (max-width: 768px) {
    width: 100% !important;
    border-right: none;
    border-bottom: 1px solid #30363d;
  }
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

  @media (max-width: 768px) {
    display: flex;
    flex-direction: row;
    overflow-x: auto;
    overflow-y: hidden;
    padding: 0;
  }
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
    background: rgba(255,255,255,0.06);
    border-left-color: #8b949e;
    color: #e6edf3;
  }

  .file-icon { min-width: 32px; font-size: 0.65rem; color: #6e7681; }
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

  @media (max-width: 768px) {
    width: 100%;
    height: 6px;
    cursor: row-resize;
    .splitter-handle {
      width: 40px;
      height: 2px;
    }
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
    border-bottom-color: #8b949e;
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

  @media (max-width: 768px) {
    width: 100% !important;
    border-left: none;
    border-top: 1px solid #30363d;
    min-height: 200px;
    flex: 1;
  }
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
  border: 1px solid #d0d7de;
  color: #57606a;
  font-size: 0.72rem;
  cursor: pointer;
  padding: 2px 6px;
  border-radius: 4px;
  transition: all 0.15s;

  &:hover { background: #eaeef2; color: #24292f; }
}

.preview-frame {
  flex: 1;
  border: none;
  width: 100%;
}
// ── Code Review Status UI ──────────────────────────────────────────
.ai-status-pill {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 6px 16px;
  border-radius: 8px;
  font-size: 0.8rem;
  font-weight: 600;
  color: #8b949e;
  margin-right: 16px;
  position: relative;
  overflow: hidden;
  transition: all 0.3s ease;
  min-width: 220px;
  justify-content: center;

  &.scanning {
    color: #60a5fa;
    border-color: rgba(96, 165, 250, 0.3);
    background: rgba(96, 165, 250, 0.05);
  }

  &.found-smell {
    color: #fb7185;
    border-color: rgba(251, 113, 133, 0.4);
    background: rgba(251, 113, 133, 0.1);
  }

  &.idle {
    color: #10b981;
    border-color: rgba(16, 185, 129, 0.3);
  }

  .ai-laser {
    position: absolute;
    top: 0; left: -100%;
    width: 36%;
    height: 100%;
    background: rgba(96, 165, 250, 0.22);
    animation: laserScan 1.4s infinite linear;
  }
}

@keyframes laserScan {
  0% { left: -100%; }
  100% { left: 200%; }
}

// ── Review Log Panel ───────────────────────────────────────────────
.ai-terminal-panel {
  height: 180px;
  background: #0d1117;
  border-top: 1px solid #30363d;
  display: flex;
  flex-direction: column;
  z-index: 10;
}

.ai-terminal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 6px 12px;
  background: #161b22;
  border-bottom: 1px solid #21262d;
  
  .title {
    font-size: 0.75rem;
    font-weight: 700;
    color: #6366f1;
    font-family: 'Segoe UI', sans-serif;
  }
  
  .close-btn {
    background: transparent;
    border: none;
    color: #8b949e;
    cursor: pointer;
    font-size: 0.9rem;
    &:hover { color: #fff; }
  }
}

.ai-terminal-body {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  font-size: 0.8rem;
  line-height: 1.5;
  display: flex;
  flex-direction: column;
  gap: 4px;

  &::-webkit-scrollbar { width: 6px; }
  &::-webkit-scrollbar-thumb { background: #30363d; border-radius: 4px; }
}

.ai-log-line {
  display: flex;
  gap: 8px;
  opacity: 0;
  animation: fadeInLog 0.3s forwards;
  
  .log-time { color: #484f58; flex-shrink: 0; }
  
  &.system .log-msg { color: #8b949e; }
  &.info .log-msg { color: #58a6ff; }
  &.warning .log-msg { color: #e3b341; }
  &.success .log-msg { color: #3fb950; }
}

@keyframes fadeInLog {
  to { opacity: 1; }
}

.slide-up-enter-active, .slide-up-leave-active { transition: all 0.3s ease; }
.slide-up-enter-from, .slide-up-leave-to { transform: translateY(100%); opacity: 0; }
</style>
