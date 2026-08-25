<script setup>
import { TresCanvas } from '@tresjs/core'
import { OrbitControls, Stars, Html } from '@tresjs/cientos'
import { ref, onMounted, onUnmounted, watch } from 'vue'

const props = defineProps({
  courses: {
    type: Array,
    required: true
  }
})

const emit = defineEmits(['selectCourse'])

const { courseImage } = useAssetPaths()

// Cấu hình quỹ đạo tự động dựa trên số lượng khóa học
const orbits = ref([])

function generateOrbits() {
  const count = props.courses.length;
  const newOrbits = [];
  for (let i = 0; i < count; i++) {
    // Xếp tất cả thành một vòng quay trình tự (Carousel) kép zic-zắc
    const isEven = i % 2 === 0;
    newOrbits.push({
      distance: isEven ? 16 : 22, // 2 vòng trong ngoài xen kẽ
      speed: 0.15, // Tất cả chung 1 tốc độ để giữ vững đội hình
      yOffset: isEven ? 1.5 : -1.5, // Cao thấp đan xen
      angleOffset: i * ((Math.PI * 2) / count) // Xếp cách đều nhau 360 độ
    })
  }
  orbits.value = newOrbits;
}

watch(() => props.courses, generateOrbits, { immediate: true })

const courseRefs = ref([])
let animationId = null
const startTime = Date.now()

function animate() {
  const elapsed = (Date.now() - startTime) / 1000
  if (courseRefs.value && courseRefs.value.length) {
    courseRefs.value.forEach((group, index) => {
      if (group && orbits.value.length > 0) {
        const config = orbits.value[index]
        if (!config) return
        
        // Tính toán góc với khoảng cách đều nhau
        const angle = elapsed * config.speed + config.angleOffset
        
        group.position.x = Math.cos(angle) * config.distance
        group.position.z = Math.sin(angle) * config.distance
        
        // Thêm hiệu ứng bồng bềnh 
        group.position.y = config.yOffset + Math.sin(elapsed * 1.5 + index) * 0.5
      }
    })
  }
  animationId = requestAnimationFrame(animate)
}

onMounted(() => {
  animate()
})

onUnmounted(() => {
  if (animationId) cancelAnimationFrame(animationId)
})

function setCourseRef(el, index) {
  if (el) {
    courseRefs.value[index] = el
  }
}
</script>

<template>
  <div class="universe-container">
    <div class="universe-overlay">
      <h2>Không gian Khóa học 3D</h2>
      <p>Click vào thẻ khóa học đang xoay để xem chi tiết</p>
    </div>
    
    <TresCanvas clear-color="#050510">
      <!-- Cố định Camera, người dùng không thể di chuyển -->
      <TresPerspectiveCamera :position="[0, 15, 55]" :fov="45" :near="0.1" :far="1000" />
      <OrbitControls :enable-zoom="false" :enable-pan="false" :enable-rotate="false" />
      
      <Stars :radius="100" :depth="50" :count="5000" :factor="6" :saturation="0.8" :fade="true" />
      
      <TresAmbientLight :intensity="0.2" />
      <TresPointLight :position="[0, 0, 0]" :intensity="5" :distance="200" color="#ffedd5" />

      <!-- TRUNG TÂM: LOGO EDUPRESS GLOWING -->
      <Html :position="[0, 0, 0]" center transform :distanceFactor="14">
        <div class="center-logo">
          <img src="/generated-assets/edupress-logo.svg" alt="EduPress Logo" />
          <h2>EDUPRESS</h2>
        </div>
      </Html>

      <!-- Vòng quỹ đạo mờ dưới nền -->
      <TresGroup v-for="(course, index) in courses" :key="'ring-'+course.id">
        <TresMesh v-if="orbits[index]" :rotation="[Math.PI / 2, 0, 0]" :position="[0, orbits[index].yOffset, 0]">
          <TresRingGeometry :args="[orbits[index].distance - 0.05, orbits[index].distance + 0.05, 128]" />
          <TresMeshBasicMaterial color="#ffffff" transparent :opacity="0.08" side="DoubleSide" />
        </TresMesh>
      </TresGroup>

      <!-- CÁC THẺ KHÓA HỌC XOAY VÒNG -->
      <TresGroup 
        v-for="(course, index) in courses" 
        :key="course.id"
        :ref="(el) => setCourseRef(el, index)"
      >
        <Html center transform :distanceFactor="14">
          <div class="floating-course-card" @click="emit('selectCourse', course.id)">
            <div class="card-image-wrapper">
              <img :src="courseImage(course)" :alt="course.title" />
              <span class="badge">{{ course.category }}</span>
            </div>
            <div class="content">
              <h3>{{ course.title }}</h3>
              <p>{{ course.author }}</p>
              <div class="stats">
                <span>{{ course.rating }}/5</span>
                <span>{{ course.students }} học viên</span>
              </div>
            </div>
          </div>
        </Html>
      </TresGroup>

    </TresCanvas>
  </div>
</template>

<style lang="scss" scoped>
.universe-container {
  position: relative;
  width: 100%;
  height: 700px;
  border-radius: var(--radius-lg);
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 30px 60px rgba(0,0,0,0.6), inset 0 0 100px rgba(0,0,0,0.8);
  margin-bottom: 48px;
  background: #050510;
}

.universe-overlay {
  position: absolute;
  top: 32px;
  left: 32px;
  z-index: 10;
  color: white;
  pointer-events: none;
  background: rgba(0, 0, 0, 0.5);
  padding: 16px 24px;
  border-radius: 12px;
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.universe-overlay h2 {
  font-size: 2.2rem;
  margin-bottom: 8px;
  background: linear-gradient(135deg, #fff, #38bdf8);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  font-weight: 800;
  letter-spacing: -1px;
}

.universe-overlay p {
  color: #cbd5e1;
  font-size: 1.05rem;
  margin: 0;
}

/* Central Logo */
.center-logo {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(15, 23, 42, 0.6);
  width: 250px;
  height: 250px;
  border-radius: 50%;
  box-shadow: 0 0 60px rgba(56, 189, 248, 0.4), inset 0 0 30px rgba(255,255,255,0.1);
  backdrop-filter: blur(15px);
  border: 1px solid rgba(255,255,255,0.15);
  pointer-events: none;
}

.center-logo img {
  width: 100px;
  height: 100px;
  object-fit: contain;
  margin-bottom: 12px;
  filter: drop-shadow(0 0 15px rgba(255,255,255,0.5));
}

.center-logo h2 {
  color: white;
  margin: 0;
  font-size: 2.2rem;
  font-weight: 900;
  letter-spacing: 2px;
  text-shadow: 0 0 20px rgba(56, 189, 248, 0.8);
}

/* Floating Course Cards */
.floating-course-card {
  width: 280px;
  background: rgba(15, 23, 42, 0.75);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 16px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1), border-color 0.3s, box-shadow 0.3s;
  pointer-events: auto;
  box-shadow: 0 15px 35px rgba(0,0,0,0.5);
}

.floating-course-card:hover {
  transform: scale(1.08) translateY(-10px);
  border-color: rgba(56, 189, 248, 0.6);
  box-shadow: 0 20px 50px rgba(56, 189, 248, 0.3);
}

.card-image-wrapper {
  position: relative;
  width: 100%;
  height: 150px;
}

.card-image-wrapper img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-bottom: 1px solid rgba(255,255,255,0.1);
}

.card-image-wrapper .badge {
  position: absolute;
  top: 12px;
  right: 12px;
  background: rgba(0,0,0,0.7);
  backdrop-filter: blur(4px);
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 700;
  color: white;
  border: 1px solid rgba(255,255,255,0.2);
}

.floating-course-card .content {
  padding: 16px;
  color: white;
  text-align: left;
}

.floating-course-card h3 {
  font-size: 1.15rem;
  font-weight: 700;
  margin: 0 0 6px 0;
  line-height: 1.3;
}

.floating-course-card p {
  color: #94a3b8;
  font-size: 0.9rem;
  margin: 0 0 12px 0;
}

.floating-course-card .stats {
  display: flex;
  gap: 16px;
  font-size: 0.85rem;
  color: #cbd5e1;
  font-weight: 500;
}
</style>
