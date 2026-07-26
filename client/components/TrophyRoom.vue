<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { TresCanvas } from '@tresjs/core'
import { OrbitControls, Stars, Html } from '@tresjs/cientos'

const props = defineProps({
  completedCourses: { type: Array, default: () => [] },
  enrolledCourses:  { type: Array, default: () => [] },
  userName:         { type: String, default: 'Học viên' },
  courses:          { type: Array, default: () => [] },
})

// ── Badge definitions ──────────────────────────────────────────────
const badgeDefs = [
  { id: 'first-step',  icon: '🚀', label: 'First Step',    desc: 'Đăng ký khóa học đầu tiên',         color: '#6366f1', req: (e, c) => e.length >= 1 },
  { id: 'learner',     icon: '📚', label: 'Learner',       desc: 'Đăng ký 3 khóa học',                color: '#8b5cf6', req: (e, c) => e.length >= 3 },
  { id: 'achiever',    icon: '🏆', label: 'Achiever',      desc: 'Hoàn thành khóa học đầu tiên',       color: '#f59e0b', req: (e, c) => c.length >= 1 },
  { id: 'champion',    icon: '⭐', label: 'Champion',      desc: 'Hoàn thành 3 khóa học',             color: '#dc2626', req: (e, c) => c.length >= 3 },
  { id: 'explorer',    icon: '🌍', label: 'Explorer',      desc: 'Học đủ 4 lĩnh vực khác nhau',       color: '#10b981', req: (e, c) => new Set(e.map(id => props.courses.find(x => x.id === id)?.category)).size >= 4 },
  { id: 'master',      icon: '👑', label: 'Master',        desc: 'Hoàn thành tất cả khóa học',        color: '#ec4899', req: (e, c) => c.length >= props.courses.length && props.courses.length > 0 },
]

const badges = computed(() =>
  badgeDefs.map(b => ({
    ...b,
    unlocked: b.req(props.enrolledCourses, props.completedCourses)
  }))
)

const unlockedBadges  = computed(() => badges.value.filter(b => b.unlocked))
const lockedBadges    = computed(() => badges.value.filter(b => !b.unlocked))
const completedCourseObjects = computed(() =>
  props.completedCourses.map(id => props.courses.find(c => c.id === id)).filter(Boolean)
)

// ── Certificate holographic effect ────────────────────────────────
const certRef = ref(null)
const mouseX  = ref(0.5)
const mouseY  = ref(0.5)
const isHovering = ref(false)

function onCertMouseMove(e) {
  const rect = e.currentTarget.getBoundingClientRect()
  mouseX.value = (e.clientX - rect.left) / rect.width
  mouseY.value = (e.clientY - rect.top) / rect.height
}
function onCertEnter() { isHovering.value = true }
function onCertLeave() {
  isHovering.value = false
  mouseX.value = 0.5
  mouseY.value = 0.5
}

const certTransform = computed(() => {
  const rx = (mouseY.value - 0.5) * 24
  const ry = (mouseX.value - 0.5) * -24
  return `perspective(900px) rotateX(${rx}deg) rotateY(${ry}deg)`
})

const foilGradient = computed(() => {
  const x = mouseX.value * 100
  const y = mouseY.value * 100
  return `
    radial-gradient(circle at ${x}% ${y}%,
      rgba(255,255,255,0.35) 0%,
      transparent 50%
    ),
    linear-gradient(
      ${105 + mouseX.value * 60}deg,
      rgba(255,0,128,0.25) 0%,
      rgba(255,165,0,0.25) 15%,
      rgba(255,255,0,0.25) 30%,
      rgba(0,255,128,0.25) 45%,
      rgba(0,200,255,0.25) 60%,
      rgba(128,0,255,0.25) 75%,
      rgba(255,0,128,0.25) 100%
    )
  `
})

// ── Share certificate ─────────────────────────────────────────────
const selectedCert = ref(null)
const shareNotice  = ref('')

function openCert(course) { selectedCert.value = course }
function closeCert()      { selectedCert.value = null; shareNotice.value = '' }

function shareCert() {
  const url = `${window.location.origin}${window.location.pathname}#cert/${selectedCert.value.id}/${encodeURIComponent(props.userName)}`
  navigator.clipboard.writeText(url).then(() => {
    shareNotice.value = '✓ Đã copy link chứng chỉ!'
    setTimeout(() => { shareNotice.value = '' }, 2500)
  })
}

// ── 3D Badge scene ────────────────────────────────────────────────
const badgeRefs    = ref([])
const badgeStartTime = Date.now()
let   badgeRafId   = null

function animateBadges() {
  const t = (Date.now() - badgeStartTime) / 1000
  badgeRefs.value.forEach((mesh, i) => {
    if (!mesh) return
    mesh.rotation.y = t * 0.6 + i * 1.2
    mesh.position.y = Math.sin(t * 1.2 + i) * 0.15
  })
  badgeRafId = requestAnimationFrame(animateBadges)
}

onMounted(() => { badgeRafId = requestAnimationFrame(animateBadges) })
onUnmounted(() => { if (badgeRafId) cancelAnimationFrame(badgeRafId) })

// Badge layout in 3D
function badgePosition(i, total) {
  const cols  = Math.min(total, 3)
  const row   = Math.floor(i / cols)
  const col   = i % cols
  const xOff  = (cols - 1) / 2
  return [(col - xOff) * 3.5, -row * 3, 0]
}

const showScene = computed(() => unlockedBadges.value.length > 0)
</script>

<template>
  <div class="trophy-room">

    <!-- ── HEADER ── -->
    <div class="trophy-header">
      <div>
        <p class="eyebrow">🏆 Phòng trưng bày</p>
        <h2>Thành tích của {{ userName }}</h2>
        <p class="trophy-sub">{{ unlockedBadges.length }}/{{ badges.length }} huy hiệu · {{ completedCourseObjects.length }} chứng chỉ</p>
      </div>
      <div class="trophy-summary-pills">
        <span>{{ enrolledCourses.length }} khóa đang học</span>
        <span>{{ completedCourseObjects.length }} hoàn thành</span>
        <span>{{ unlockedBadges.length }} huy hiệu</span>
      </div>
    </div>

    <!-- ── 3D BADGE SHOWCASE ── -->
    <div class="badge-section">
      <div class="section-label">🎖️ Huy hiệu 3D</div>

      <!-- 3D scene for unlocked badges -->
      <div v-if="showScene" class="badge-scene-wrap">
        <TresCanvas clear-color="#080d1a" :alpha="false">
          <TresPerspectiveCamera :position="[0, 0, 10]" :fov="50" />
          <OrbitControls :enable-zoom="false" :enable-pan="false" />
          <Stars :radius="50" :depth="30" :count="2000" :factor="4" :fade="true" />
          <TresAmbientLight :intensity="0.4" />
          <TresPointLight :position="[5, 5, 5]"  :intensity="3" color="#a5b4fc" />
          <TresPointLight :position="[-5, -3, 3]" :intensity="2" color="#f9a8d4" />

          <TresMesh
            v-for="(badge, i) in unlockedBadges"
            :key="badge.id"
            :ref="el => badgeRefs[i] = el"
            :position="badgePosition(i, unlockedBadges.length)"
          >
            <TresCylinderGeometry :args="[1, 1, 0.18, 6]" />
            <TresMeshStandardMaterial
              :color="badge.color"
              :metalness="0.85"
              :roughness="0.12"
              :emissive="badge.color"
              :emissive-intensity="0.18"
            />

            <Html center :distance-factor="5">
              <div class="badge-html-label">{{ badge.icon }}</div>
            </Html>
          </TresMesh>
        </TresCanvas>

        <!-- Badge legend below scene -->
        <div class="badge-legend">
          <div v-for="badge in unlockedBadges" :key="badge.id" class="badge-legend-item">
            <span class="legend-dot" :style="{ background: badge.color }"></span>
            <span class="legend-name">{{ badge.label }}</span>
          </div>
        </div>
      </div>

      <!-- Empty state -->
      <div v-else class="badge-empty">
        <p>🔒 Đăng ký khóa học đầu tiên để mở khóa huy hiệu!</p>
      </div>

      <!-- Locked badges grid -->
      <div class="badge-grid">
        <div
          v-for="badge in badges"
          :key="badge.id"
          :class="['badge-card', { unlocked: badge.unlocked }]"
        >
          <div class="badge-icon" :style="badge.unlocked ? { background: badge.color + '22', borderColor: badge.color + '66' } : {}">
            <span>{{ badge.icon }}</span>
            <div v-if="!badge.unlocked" class="badge-lock">🔒</div>
          </div>
          <strong>{{ badge.label }}</strong>
          <p>{{ badge.desc }}</p>
          <span v-if="badge.unlocked" class="badge-status unlocked-tag">✓ Đã mở khóa</span>
          <span v-else class="badge-status locked-tag">Chưa đạt</span>
        </div>
      </div>
    </div>

    <!-- ── HOLOGRAPHIC CERTIFICATES ── -->
    <div class="cert-section">
      <div class="section-label">📜 Chứng chỉ hoàn thành</div>

      <div v-if="completedCourseObjects.length === 0" class="badge-empty">
        <p>📭 Hoàn thành khóa học để nhận chứng chỉ holographic!</p>
      </div>

      <div class="cert-grid">
        <div
          v-for="course in completedCourseObjects"
          :key="course.id"
          class="cert-card"
          @mousemove="onCertMouseMove"
          @mouseenter="onCertEnter"
          @mouseleave="onCertLeave"
          @click="openCert(course)"
          :style="{ transform: certTransform }"
        >
          <!-- Holographic foil overlay -->
          <div class="cert-foil" :style="{ background: foilGradient, opacity: isHovering ? 1 : 0 }"></div>
          <div class="cert-shine" :style="{ opacity: isHovering ? 0.6 : 0.15 }"></div>

          <!-- Content -->
          <div class="cert-body">
            <div class="cert-logo">🎓</div>
            <div class="cert-issuer">EduPress · Certificate of Completion</div>
            <h3 class="cert-course">{{ course.title }}</h3>
            <p class="cert-recipient">Cấp cho: <strong>{{ userName }}</strong></p>
            <div class="cert-meta">
              <span>{{ course.category }}</span>
              <span>{{ course.level }}</span>
              <span>{{ course.duration }}</span>
            </div>
            <div class="cert-seal">✦</div>
          </div>

          <div class="cert-hover-hint">Click để xem & chia sẻ</div>
        </div>
      </div>
    </div>

    <!-- ── CERTIFICATE MODAL ── -->
    <Transition name="cert-modal">
      <div v-if="selectedCert" class="cert-modal-overlay" @click.self="closeCert">
        <div class="cert-modal">
          <button class="cert-modal-close" @click="closeCert">✕</button>

          <div
            class="cert-full"
            @mousemove="onCertMouseMove"
            @mouseenter="onCertEnter"
            @mouseleave="onCertLeave"
            :style="{ transform: certTransform }"
          >
            <div class="cert-foil" :style="{ background: foilGradient, opacity: isHovering ? 1 : 0 }"></div>
            <div class="cert-shine" :style="{ opacity: isHovering ? 0.7 : 0.2 }"></div>
            <div class="cert-body cert-body--full">
              <div class="cert-logo-lg">🎓</div>
              <div class="cert-issuer">EduPress · Certificate of Completion</div>
              <h2 class="cert-course-lg">{{ selectedCert.title }}</h2>
              <p class="cert-recipient-lg">Cấp cho: <strong>{{ userName }}</strong></p>
              <div class="cert-divider"></div>
              <div class="cert-meta">
                <span>{{ selectedCert.category }}</span>
                <span>{{ selectedCert.level }}</span>
                <span>{{ selectedCert.duration }}</span>
                <span>{{ selectedCert.rating }}/5 ⭐</span>
              </div>
              <div class="cert-author">Giảng viên: {{ selectedCert.author }}</div>
              <div class="cert-seal-lg">✦ EDUPRESS ✦</div>
            </div>
          </div>

          <div class="cert-modal-actions">
            <button class="share-btn" @click="shareCert">
              🔗 Sao chép link chia sẻ
            </button>
            <p v-if="shareNotice" class="share-notice">{{ shareNotice }}</p>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<style lang="scss" scoped>
.trophy-room {
  display: flex;
  flex-direction: column;
  gap: 48px;
}

// ── Header ──────────────────────────────────────────────────────
.trophy-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 16px;

  h2 { font-size: 2rem; margin-bottom: 8px; }
}

.trophy-sub { color: var(--text-muted); font-size: 0.95rem; margin-top: 4px; }

.trophy-summary-pills {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  align-items: center;

  span {
    background: rgba(99,102,241,0.1);
    border: 1px solid rgba(99,102,241,0.3);
    color: #a5b4fc;
    border-radius: 999px;
    padding: 6px 16px;
    font-size: 0.85rem;
    font-weight: 600;
  }
}

// ── Section label ────────────────────────────────────────────────
.section-label {
  font-size: 0.8rem;
  font-weight: 800;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--text-muted);
  margin-bottom: 24px;
}

// ── Badge 3D scene ────────────────────────────────────────────────
.badge-scene-wrap {
  border-radius: 20px;
  overflow: hidden;
  border: 1px solid rgba(255,255,255,0.06);
  margin-bottom: 32px;
  background: #080d1a;
  height: 300px;
  position: relative;
}

.badge-legend {
  position: absolute;
  bottom: 16px;
  left: 0; right: 0;
  display: flex;
  justify-content: center;
  gap: 20px;
  flex-wrap: wrap;
  pointer-events: none;
}

.badge-legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.75rem;
  color: rgba(255,255,255,0.6);
}

.badge-html-label {
  font-size: 1.6rem;
  user-select: none;
  pointer-events: none;
  filter: drop-shadow(0 0 8px rgba(255,255,255,0.5));
}

.legend-dot {
  width: 10px; height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}

// ── Badge grid ────────────────────────────────────────────────────
.badge-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.badge-card {
  background: #f8fafc;
  border: 1px solid rgba(0,0,0,0.06);
  border-radius: 16px;
  padding: 24px 20px;
  text-align: center;
  transition: all 0.3s ease;
  opacity: 0.45;
  filter: grayscale(1);

  &.unlocked {
    opacity: 1;
    filter: none;
    background: #ffffff;
    box-shadow: 0 8px 24px rgba(0,0,0,0.06);

    &:hover { transform: translateY(-4px); box-shadow: 0 16px 40px rgba(99,102,241,0.15); }
  }
}

.badge-icon {
  width: 64px; height: 64px;
  border-radius: 16px;
  border: 2px solid rgba(0,0,0,0.06);
  margin: 0 auto 12px;
  display: flex; align-items: center; justify-content: center;
  font-size: 2rem;
  position: relative;
}

.badge-lock {
  position: absolute;
  bottom: -6px; right: -6px;
  font-size: 0.9rem;
}

.badge-card strong { display: block; font-size: 0.95rem; margin-bottom: 4px; }
.badge-card p { font-size: 0.8rem; color: var(--text-muted); line-height: 1.4; margin-bottom: 10px; }

.badge-status {
  font-size: 0.72rem;
  font-weight: 700;
  padding: 3px 10px;
  border-radius: 999px;
  letter-spacing: 0.04em;

  &.unlocked-tag { background: #ecfdf5; color: #10b981; }
  &.locked-tag   { background: #f1f5f9; color: #94a3b8; }
}

.badge-empty {
  background: #f8fafc;
  border: 1px dashed rgba(0,0,0,0.1);
  border-radius: 16px;
  padding: 40px;
  text-align: center;
  color: var(--text-muted);
  margin-bottom: 24px;
}

// ── Certificate cards ─────────────────────────────────────────────
.cert-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 24px;
}

.cert-card {
  position: relative;
  border-radius: 20px;
  overflow: hidden;
  cursor: pointer;
  transform-style: preserve-3d;
  transition: transform 0.1s ease;
  background: linear-gradient(135deg, #1e1b4b 0%, #312e81 50%, #1e1b4b 100%);
  border: 1px solid rgba(165,180,252,0.2);
  box-shadow: 0 20px 60px rgba(99,102,241,0.2);

  &:hover { box-shadow: 0 30px 80px rgba(99,102,241,0.35); }
}

.cert-foil {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 2;
  border-radius: inherit;
  mix-blend-mode: screen;
  transition: opacity 0.3s ease;
}

.cert-shine {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 1;
  border-radius: inherit;
  background: linear-gradient(135deg,
    rgba(255,255,255,0.08) 0%,
    transparent 50%,
    rgba(255,255,255,0.04) 100%
  );
  transition: opacity 0.3s ease;
}

.cert-body {
  position: relative;
  z-index: 3;
  padding: 32px;
  color: white;
  text-align: center;
}

.cert-logo { font-size: 2.5rem; margin-bottom: 12px; }
.cert-issuer {
  font-size: 0.7rem;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  color: rgba(165,180,252,0.7);
  margin-bottom: 16px;
}

.cert-course {
  font-size: 1.3rem;
  font-weight: 800;
  margin-bottom: 10px;
  line-height: 1.3;
  color: #fff;
}

.cert-recipient {
  font-size: 0.85rem;
  color: rgba(255,255,255,0.7);
  margin-bottom: 16px;
  strong { color: #a5b4fc; }
}

.cert-meta {
  display: flex;
  justify-content: center;
  gap: 8px;
  flex-wrap: wrap;

  span {
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 999px;
    padding: 4px 12px;
    font-size: 0.72rem;
    color: rgba(255,255,255,0.7);
  }
}

.cert-seal {
  margin-top: 20px;
  font-size: 1.5rem;
  color: rgba(253,224,71,0.6);
}

.cert-hover-hint {
  position: absolute;
  bottom: 0; left: 0; right: 0;
  background: linear-gradient(to top, rgba(0,0,0,0.6), transparent);
  color: rgba(255,255,255,0.6);
  font-size: 0.72rem;
  text-align: center;
  padding: 20px 16px 12px;
  z-index: 4;
  opacity: 0;
  transition: opacity 0.3s ease;

  .cert-card:hover & { opacity: 1; }
}

// ── Certificate modal ─────────────────────────────────────────────
.cert-modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 9999;
  background: rgba(0,0,0,0.8);
  backdrop-filter: blur(16px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
}

.cert-modal {
  position: relative;
  max-width: 600px;
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 24px;
}

.cert-modal-close {
  position: absolute;
  top: -12px; right: -12px;
  z-index: 10;
  width: 36px; height: 36px;
  background: rgba(255,255,255,0.1);
  border: 1px solid rgba(255,255,255,0.15);
  border-radius: 50%;
  color: white;
  cursor: pointer;
  font-size: 0.9rem;
  display: flex; align-items: center; justify-content: center;
  transition: all 0.2s;

  &:hover { background: rgba(220,38,38,0.5); }
}

.cert-full {
  width: 100%;
  border-radius: 24px;
  overflow: hidden;
  position: relative;
  transform-style: preserve-3d;
  transition: transform 0.08s ease;
  background: linear-gradient(135deg, #1e1b4b 0%, #312e81 50%, #1e1b4b 100%);
  border: 1px solid rgba(165,180,252,0.25);
  box-shadow: 0 40px 100px rgba(99,102,241,0.4);
}

.cert-body--full {
  padding: 48px 40px;
}

.cert-logo-lg { font-size: 4rem; margin-bottom: 16px; }
.cert-course-lg { font-size: 2rem; font-weight: 900; margin-bottom: 12px; color: #fff; }
.cert-recipient-lg { font-size: 1rem; color: rgba(255,255,255,0.7); margin-bottom: 24px; strong { color: #a5b4fc; } }
.cert-divider { height: 1px; background: rgba(165,180,252,0.2); margin: 20px 0; }
.cert-author { margin-top: 16px; font-size: 0.85rem; color: rgba(255,255,255,0.5); }
.cert-seal-lg {
  margin-top: 24px;
  font-size: 0.8rem;
  letter-spacing: 0.3em;
  color: rgba(253,224,71,0.6);
  font-weight: 800;
}

.cert-modal-actions {
  text-align: center;
}

.share-btn {
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: white;
  border: none;
  padding: 14px 32px;
  border-radius: 12px;
  font-weight: 700;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.25s ease;
  box-shadow: 0 0 30px rgba(99,102,241,0.4);

  &:hover { transform: translateY(-2px); box-shadow: 0 8px 30px rgba(99,102,241,0.6); }
}

.share-notice {
  margin-top: 12px;
  color: #4ade80;
  font-weight: 600;
  font-size: 0.9rem;
}

// ── Modal transition ──────────────────────────────────────────────
.cert-modal-enter-active, .cert-modal-leave-active { transition: all 0.3s ease; }
.cert-modal-enter-from, .cert-modal-leave-to { opacity: 0; transform: scale(0.95); }

// ── Responsive ────────────────────────────────────────────────────
@media (max-width: 768px) {
  .badge-grid { grid-template-columns: repeat(2, 1fr); }
  .trophy-header { flex-direction: column; }
}
</style>
