<script setup>
import { ref, onMounted, onUnmounted, reactive, computed, nextTick } from 'vue'
import * as Y from 'yjs'
import { WebrtcProvider } from 'y-webrtc'

const props = defineProps({
  currentUser: {
    type: Object,
    default: () => ({ name: 'Anonymous User', id: Math.random().toString(36).substring(7) })
  }
})

// ── Yjs Setup (Real-time CRDT) ──────────────────────────────────
let ydoc = null
let provider = null
let yShapes = null

const connected = ref(false)
const cursors = reactive({})
const shapes = reactive({})
const activeTool = ref('select') // select, sticky, shape, text
const toolColor = ref('#fef08a') // default sticky color
const colors = ['#fef08a', '#bbf7d0', '#bfdbfe', '#fbcfe8', '#e5e7eb']

// ── Infinite Canvas State ───────────────────────────────────────
const viewport = ref(null)
const canvasWrapper = ref(null)
const transform = reactive({ x: 0, y: 0, scale: 1 })
const isPanning = ref(false)
const panStart = { x: 0, y: 0, tx: 0, ty: 0 }
const selectedShapeId = ref(null)

// ── Utility: Screen to Canvas Coords ────────────────────────────
function getCanvasCoords(clientX, clientY) {
  if (!viewport.value) return { x: 0, y: 0 }
  const rect = viewport.value.getBoundingClientRect()
  const x = (clientX - rect.left - transform.x) / transform.scale
  const y = (clientY - rect.top - transform.y) / transform.scale
  return { x, y }
}

// ── Lifecycle ───────────────────────────────────────────────────
onMounted(() => {
  // 1. Initialize Y.Doc
  ydoc = new Y.Doc()
  
  // 2. Map for Shapes
  yShapes = ydoc.getMap('shapes')
  yShapes.observe((event) => {
    // Sync Yjs map changes to local Vue reactive state
    event.changes.keys.forEach((change, key) => {
      if (change.action === 'add' || change.action === 'update') {
        shapes[key] = yShapes.get(key)
      } else if (change.action === 'delete') {
        delete shapes[key]
      }
    })
  })

  // 3. Connect to WebRTC signaling server (Public for demo)
  // We use a custom room name to ensure privacy
  provider = new WebrtcProvider('edupress-whiteboard-room-v1', ydoc, {
    signaling: [
      'wss://signaling.yjs.dev',
      'wss://y-webrtc-signaling-eu.herokuapp.com'
    ]
  })

  provider.on('synced', (isSynced) => {
    connected.value = isSynced
  })

  // 4. Cursor & Presence Awareness
  const awareness = provider.awareness
  // Random color for cursor
  const userColor = '#' + Math.floor(Math.random()*16777215).toString(16).padStart(6, '0')
  
  awareness.setLocalStateField('user', {
    name: props.currentUser?.name || 'EduPress Learner',
    color: userColor,
    cursor: null
  })

  awareness.on('change', () => {
    const states = awareness.getStates()
    Object.keys(cursors).forEach(key => delete cursors[key])
    states.forEach((state, clientID) => {
      if (clientID !== awareness.clientID && state.user && state.user.cursor) {
        cursors[clientID] = state.user
      }
    })
  })

  // Listen to wheel for zoom & pan
  viewport.value.addEventListener('wheel', handleWheel, { passive: false })
})

onUnmounted(() => {
  viewport.value?.removeEventListener('wheel', handleWheel)
  if (provider) provider.destroy()
  if (ydoc) ydoc.destroy()
})

// ── Interactions ────────────────────────────────────────────────
function handlePointerDown(e) {
  // Middle click or Space+Click or Tool=Hand -> Pan
  if (e.button === 1 || e.shiftKey) {
    isPanning.value = true
    panStart.x = e.clientX
    panStart.y = e.clientY
    panStart.tx = transform.x
    panStart.ty = transform.y
    return
  }

  // Click on background
  if (e.target === canvasWrapper.value || e.target === viewport.value) {
    selectedShapeId.value = null

    if (activeTool.value === 'sticky') {
      const coords = getCanvasCoords(e.clientX, e.clientY)
      createShape('sticky', coords.x, coords.y)
      activeTool.value = 'select'
    } else if (activeTool.value === 'text') {
      const coords = getCanvasCoords(e.clientX, e.clientY)
      createShape('text', coords.x, coords.y)
      activeTool.value = 'select'
    }
  }
}

function handlePointerMove(e) {
  if (isPanning.value) {
    const dx = e.clientX - panStart.x
    const dy = e.clientY - panStart.y
    transform.x = panStart.tx + dx
    transform.y = panStart.ty + dy
  }

  // Broadcast cursor
  if (provider?.awareness) {
    const coords = getCanvasCoords(e.clientX, e.clientY)
    const localState = provider.awareness.getLocalState()
    provider.awareness.setLocalStateField('user', {
      ...localState.user,
      cursor: coords
    })
  }
}

function handlePointerUp() {
  isPanning.value = false
}

function handleWheel(e) {
  e.preventDefault()
  if (e.ctrlKey || e.metaKey) {
    // Zoom
    const zoomSensitivity = 0.001
    const delta = -e.deltaY * zoomSensitivity
    const newScale = Math.min(Math.max(0.1, transform.scale * (1 + delta)), 5)
    
    // Zoom towards cursor
    const rect = viewport.value.getBoundingClientRect()
    const x = e.clientX - rect.left
    const y = e.clientY - rect.top
    
    transform.x = x - (x - transform.x) * (newScale / transform.scale)
    transform.y = y - (y - transform.y) * (newScale / transform.scale)
    transform.scale = newScale
  } else {
    // Pan
    transform.x -= e.deltaX
    transform.y -= e.deltaY
  }
}

// ── Shape Operations ────────────────────────────────────────────
function createShape(type, x, y) {
  const id = 'shape_' + Math.random().toString(36).substr(2, 9)
  const shape = {
    id,
    type,
    x: x - 100, // offset to center
    y: y - 100,
    width: 200,
    height: 200,
    content: type === 'sticky' ? 'Ghi chú mới...' : 'Văn bản...',
    color: toolColor.value,
    zIndex: Date.now()
  }
  yShapes.set(id, shape)
  selectedShapeId.value = id
}

function updateShapeContent(id, newContent) {
  const shape = yShapes.get(id)
  if (shape) {
    shape.content = newContent
    yShapes.set(id, shape)
  }
}

function deleteShape(id) {
  yShapes.delete(id)
  if (selectedShapeId.value === id) selectedShapeId.value = null
}

// Shape Dragging
let draggingShape = null
let dragOffset = { x: 0, y: 0 }

function startDragShape(e, shape) {
  if (activeTool.value !== 'select') return
  e.stopPropagation()
  selectedShapeId.value = shape.id
  draggingShape = shape
  
  const coords = getCanvasCoords(e.clientX, e.clientY)
  dragOffset.x = coords.x - shape.x
  dragOffset.y = coords.y - shape.y
  
  // Bring to front
  const updatedShape = { ...shape, zIndex: Date.now() }
  yShapes.set(shape.id, updatedShape)
  
  document.addEventListener('pointermove', onDragShape)
  document.addEventListener('pointerup', stopDragShape)
}

function onDragShape(e) {
  if (!draggingShape) return
  const coords = getCanvasCoords(e.clientX, e.clientY)
  const updatedShape = {
    ...draggingShape,
    x: coords.x - dragOffset.x,
    y: coords.y - dragOffset.y
  }
  yShapes.set(draggingShape.id, updatedShape)
  draggingShape = updatedShape
}

function stopDragShape() {
  draggingShape = null
  document.removeEventListener('pointermove', onDragShape)
  document.removeEventListener('pointerup', stopDragShape)
}

</script>

<template>
  <div class="whiteboard-container">
    <!-- TOOLBAR -->
    <div class="wb-toolbar">
      <div class="tool-group">
        <button 
          :class="['tool-btn', { active: activeTool === 'select' }]" 
          @click="activeTool = 'select'"
          title="Chọn (V)"
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m3 3 7.07 16.97 2.51-7.39 7.39-2.51L3 3z"/><path d="m13 13 6 6"/></svg>
        </button>
        <button 
          :class="['tool-btn', { active: activeTool === 'sticky' }]" 
          @click="activeTool = 'sticky'"
          title="Sticky Note (S)"
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="18" x="3" y="3" rx="2"/><path d="M13 3v18"/><path d="M3 13h18"/></svg>
        </button>
        <button 
          :class="['tool-btn', { active: activeTool === 'text' }]" 
          @click="activeTool = 'text'"
          title="Văn bản (T)"
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 7V4h16v3"/><path d="M9 20h6"/><path d="M12 4v16"/></svg>
        </button>
      </div>

      <div class="divider"></div>

      <!-- Color Picker -->
      <div class="tool-group">
        <button 
          v-for="c in colors" :key="c"
          class="color-btn"
          :class="{ active: toolColor === c }"
          :style="{ background: c }"
          @click="toolColor = c"
        ></button>
      </div>

      <div class="wb-status">
        <span class="status-dot" :class="{ connected }"></span>
        {{ connected ? 'Connected (Live)' : 'Connecting...' }}
        <span class="users-count">({{ Object.keys(cursors).length + 1 }} online)</span>
      </div>
      
      <button class="close-wb-btn" @click="$emit('close')">Đóng bảng</button>
    </div>

    <!-- CANVAS VIEWPORT -->
    <div 
      ref="viewport" 
      class="wb-viewport" 
      :class="{ 'panning': isPanning, ['cursor-' + activeTool]: true }"
      @pointerdown="handlePointerDown"
      @pointermove="handlePointerMove"
      @pointerup="handlePointerUp"
      @pointerleave="handlePointerUp"
    >
      <!-- TRANSFORM WRAPPER -->
      <div 
        ref="canvasWrapper" 
        class="wb-canvas"
        :style="{ transform: `translate(${transform.x}px, ${transform.y}px) scale(${transform.scale})` }"
      >
        <!-- GRID BACKGROUND (Optional) -->
        <div class="wb-grid"></div>

        <!-- SHAPES -->
        <div 
          v-for="shape in shapes" 
          :key="shape.id"
          class="wb-shape"
          :class="[shape.type, { selected: selectedShapeId === shape.id }]"
          :style="{
            transform: `translate(${shape.x}px, ${shape.y}px)`,
            width: shape.type === 'text' ? 'auto' : shape.width + 'px',
            height: shape.type === 'text' ? 'auto' : shape.height + 'px',
            backgroundColor: shape.type === 'sticky' ? shape.color : 'transparent',
            zIndex: shape.zIndex
          }"
          @pointerdown="startDragShape($event, shape)"
        >
          <!-- Sticky Content -->
          <textarea 
            v-if="shape.type === 'sticky' || shape.type === 'text'"
            class="shape-textarea"
            :class="{ 'is-text-tool': shape.type === 'text' }"
            :value="shape.content"
            @input="updateShapeContent(shape.id, $event.target.value)"
            @pointerdown.stop
          ></textarea>

          <!-- Delete Button when selected -->
          <button 
            v-if="selectedShapeId === shape.id"
            class="delete-shape-btn"
            @click.stop="deleteShape(shape.id)"
          >
            ✕
          </button>
        </div>

        <!-- MULTIPLAYER CURSORS -->
        <div 
          v-for="(state, clientId) in cursors" 
          :key="clientId"
          class="wb-cursor"
          :style="{ 
            transform: `translate(${state.cursor.x}px, ${state.cursor.y}px)`,
            color: state.color 
          }"
        >
          <svg class="cursor-svg" viewBox="0 0 24 24" width="24" height="24">
            <path fill="currentColor" stroke="#fff" stroke-width="2" d="M3 3l7.07 16.97 2.51-7.39 7.39-2.51L3 3z"/>
          </svg>
          <div class="cursor-name" :style="{ backgroundColor: state.color }">
            {{ state.name }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.whiteboard-container {
  position: fixed;
  inset: 0;
  z-index: 9999;
  background: #f1f5f9;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  font-family: 'Inter', sans-serif;
}

/* ── Toolbar ──────────────────────────────────────────── */
.wb-toolbar {
  position: absolute;
  bottom: 32px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 100;
  background: #ffffff;
  padding: 12px 24px;
  border-radius: 999px;
  box-shadow: 0 10px 40px rgba(0,0,0,0.1);
  display: flex;
  align-items: center;
  gap: 16px;
  border: 1px solid #e2e8f0;
}

.tool-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.divider {
  width: 1px;
  height: 24px;
  background: #e2e8f0;
}

.tool-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: none;
  background: transparent;
  color: #475569;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
}

.tool-btn:hover {
  background: #f1f5f9;
  color: #0f172a;
}

.tool-btn.active {
  background: #ebf4ff;
  color: #3b82f6;
}

.color-btn {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  border: 2px solid transparent;
  cursor: pointer;
  transition: transform 0.2s;
}

.color-btn:hover {
  transform: scale(1.1);
}

.color-btn.active {
  border-color: #3b82f6;
  box-shadow: 0 0 0 2px #fff, 0 0 0 4px #3b82f6;
}

.wb-status {
  font-size: 0.85rem;
  font-weight: 600;
  color: #475569;
  display: flex;
  align-items: center;
  gap: 8px;
  margin-left: 16px;
}

.status-dot {
  width: 8px;
  height: 8px;
  background: #f87171;
  border-radius: 50%;
}
.status-dot.connected {
  background: #34d399;
  box-shadow: 0 0 10px #34d399;
}

.close-wb-btn {
  background: #ef4444;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 999px;
  font-weight: 600;
  cursor: pointer;
}

/* ── Viewport & Canvas ────────────────────────────────── */
.wb-viewport {
  flex: 1;
  width: 100%;
  height: 100%;
  overflow: hidden;
  position: relative;
  touch-action: none; /* Crucial for custom pan/zoom */
}

.wb-viewport.cursor-select { cursor: default; }
.wb-viewport.cursor-sticky { cursor: crosshair; }
.wb-viewport.cursor-text   { cursor: text; }
.wb-viewport.panning       { cursor: grab; }

.wb-canvas {
  position: absolute;
  top: 0;
  left: 0;
  width: 0;
  height: 0;
  transform-origin: 0 0;
  /* Will-change helps rendering performance during pan/zoom */
  will-change: transform; 
}

/* Grid background that moves with pan but doesn't scale perfectly to keep it looking infinite */
.wb-grid {
  position: absolute;
  top: -100000px;
  left: -100000px;
  width: 200000px;
  height: 200000px;
  background-size: 20px 20px;
  background-image: radial-gradient(circle, #cbd5e1 1px, transparent 1px);
  pointer-events: none;
  z-index: -1;
}

/* ── Shapes ───────────────────────────────────────────── */
.wb-shape {
  position: absolute;
  top: 0; left: 0;
  cursor: grab;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

.wb-shape:active { cursor: grabbing; }

.wb-shape.sticky {
  padding: 16px;
  border-radius: 2px;
  /* subtle inner shadow for paper effect */
  box-shadow: 2px 4px 10px rgba(0,0,0,0.1), inset 0 0 20px rgba(0,0,0,0.02);
}

.wb-shape.text {
  box-shadow: none;
  background: transparent !important;
}

.wb-shape.selected {
  outline: 2px solid #3b82f6;
  outline-offset: 4px;
}

.shape-textarea {
  width: 100%;
  height: 100%;
  background: transparent;
  border: none;
  resize: none;
  outline: none;
  font-family: 'Kalam', cursive, sans-serif;
  font-size: 1.2rem;
  color: #1e293b;
  line-height: 1.4;
}

.shape-textarea.is-text-tool {
  font-family: 'Inter', sans-serif;
  font-size: 1.5rem;
  font-weight: 700;
  min-width: 200px;
  min-height: 50px;
  padding: 8px;
}

.delete-shape-btn {
  position: absolute;
  top: -12px;
  right: -12px;
  width: 24px;
  height: 24px;
  background: #ef4444;
  color: white;
  border: none;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  cursor: pointer;
  z-index: 10;
}

/* ── Cursors ──────────────────────────────────────────── */
.wb-cursor {
  position: absolute;
  top: 0; left: 0;
  pointer-events: none;
  z-index: 99999;
  transition: transform 0.1s linear;
}

.cursor-svg {
  position: absolute;
  top: 0; left: 0;
  /* The SVG path points top-left, we want it exactly at 0,0 */
  transform: translate(-3px, -3px); 
}

.cursor-name {
  position: absolute;
  top: 16px; left: 16px;
  padding: 4px 8px;
  border-radius: 4px;
  color: white;
  font-size: 0.75rem;
  font-weight: 600;
  white-space: nowrap;
  box-shadow: 0 2px 5px rgba(0,0,0,0.2);
}

</style>
