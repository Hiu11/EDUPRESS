<script setup>
import { computed, onMounted, ref } from 'vue'
import LearningUniverse from './components/LearningUniverse.vue'
import CinematicPlayer from './components/CinematicPlayer.vue'

const ASSET_BASE = '/legacy-assets/'
const GENERATED_BASE = '/generated-assets/'

const navItems = [
  { id: 'home', label: 'Trang chủ' },
  { id: 'courses', label: 'Khóa học' },
  { id: 'blog', label: 'Tin tức' },
  { id: 'contact', label: 'Liên hệ' },
]

const categories = [
  { name: 'Artificial Intelligence', count: 8, tone: 'teal', copy: 'Machine learning, prompt design, data workflow' },
  { name: 'Software Engineering', count: 12, tone: 'amber', copy: 'OOP, clean code, testing, teamwork' },
  { name: 'Web Development', count: 15, tone: 'blue', copy: 'Frontend, backend, API, deployment' },
  { name: 'UX/UI Design', count: 6, tone: 'rose', copy: 'Layout, visual systems, product thinking' },
]

const courses = [
  {
    id: 'ai',
    title: 'Trí tuệ nhân tạo ứng dụng',
    author: 'TS. Đặng Ngọc Hoàng Thành',
    category: 'AI',
    image: 'course-ai-bg.png',
    level: 'Intermediate',
    lessons: 18,
    duration: '8 tuần',
    rating: 4.8,
    students: 482,
    progress: 72,
    tag: 'Bán chạy',
    description: 'Nền tảng AI, machine learning, xử lý dữ liệu và cách đưa mô hình vào sản phẩm học tập thực tế.',
    outcomes: ['Hiểu quy trình xây mô hình AI', 'Biết chuẩn bị dữ liệu và đánh giá kết quả', 'Tạo một prototype AI assistant cho lớp học'],
    syllabus: ['Tổng quan AI và ứng dụng giáo dục', 'Machine learning căn bản', 'Xử lý dữ liệu học viên', 'Prompt workflow và đánh giá mô hình', 'Triển khai demo AI assistant'],
    resources: ['Bộ dataset mẫu', 'Notebook thực hành', 'Rubric đánh giá project'],
  },
  {
    id: 'oop',
    title: 'Lập trình hướng đối tượng',
    author: 'TS. Nguyễn Mạnh Tuấn',
    category: 'Software Engineering',
    image: 'course-oop-bg.png',
    level: 'Beginner',
    lessons: 14,
    duration: '6 tuần',
    rating: 4.7,
    students: 356,
    progress: 46,
    tag: 'Căn bản',
    description: 'Nắm vững class, object, kế thừa, đa hình và cách tổ chức phần mềm theo hướng module rõ ràng.',
    outcomes: ['Thiết kế class và object đúng trách nhiệm', 'Refactor code procedural sang OOP', 'Xây mini project quản lý khóa học'],
    syllabus: ['Class, object và constructor', 'Encapsulation và validation', 'Inheritance và composition', 'Polymorphism', 'Project cuối khóa'],
    resources: ['Source code starter', 'Bài tập UML', 'Checklist clean code'],
  },
  {
    id: 'web',
    title: 'Phát triển ứng dụng web',
    author: 'ThS. Hồ Thị Thanh Tuyến',
    category: 'Web Development',
    image: 'course-web-bg.png',
    level: 'Advanced',
    lessons: 22,
    duration: '10 tuần',
    rating: 4.9,
    students: 628,
    progress: 88,
    tag: 'Project-based',
    description: 'Xây dựng web app hiện đại từ giao diện, API, database đến deployment với quy trình làm việc giống dự án thật.',
    outcomes: ['Xây SPA bằng component', 'Thiết kế REST API', 'Kết nối database và deploy sản phẩm'],
    syllabus: ['HTML/CSS nâng cao', 'Vue component architecture', 'FastAPI REST endpoint', 'PostgreSQL data modeling', 'Deploy và review sản phẩm'],
    resources: ['UI kit', 'API checklist', 'Deployment guide'],
  },
  {
    id: 'ui',
    title: 'Thiết kế giao diện học tập',
    author: 'ThS. Nguyễn Thị Bích Ngọc',
    category: 'Design',
    image: 'course-ui-bg.png',
    level: 'Beginner',
    lessons: 12,
    duration: '5 tuần',
    rating: 4.6,
    students: 241,
    progress: 34,
    tag: 'Workshop',
    description: 'Học nguyên tắc layout, màu sắc, typography và thiết kế trải nghiệm học tập trực tuyến dễ dùng.',
    outcomes: ['Thiết kế wireframe LMS', 'Xây visual system', 'Review accessibility cơ bản'],
    syllabus: ['Design principles', 'Wireframe và user flow', 'Responsive UI', 'Design system', 'Prototype review'],
    resources: ['Figma template', 'Color token guide', 'Accessibility checklist'],
  },
  {
    id: 'cloud',
    title: 'Kiến trúc Cloud & DevOps',
    author: 'ThS. Phan Hữu Vinh',
    category: 'Software Engineering',
    image: 'course-cloud-bg.png',
    level: 'Advanced',
    lessons: 16,
    duration: '8 tuần',
    rating: 4.9,
    students: 312,
    progress: 20,
    tag: 'Mới',
    description: 'Triển khai hệ thống mượt mà với Docker, CI/CD, AWS và tối ưu hóa tài nguyên server.',
    outcomes: ['Viết Dockerfile và docker-compose', 'Cấu hình GitHub Actions CI/CD', 'Quản lý tài nguyên AWS cơ bản'],
    syllabus: ['Docker cơ bản', 'Container orchestration', 'CI/CD Pipelines', 'AWS EC2 & S3', 'System Monitoring'],
    resources: ['AWS Free Tier Guide', 'Docker cheatsheet', 'Workflow templates'],
  },
  {
    id: 'mobile',
    title: 'Lập trình Mobile Đa nền tảng',
    author: 'TS. Trần Công Nam',
    category: 'Mobile Dev',
    image: 'course-mobile-bg.png',
    level: 'Intermediate',
    lessons: 20,
    duration: '9 tuần',
    rating: 4.8,
    students: 540,
    progress: 60,
    tag: 'Xu hướng',
    description: 'Tạo ứng dụng chạy cả trên iOS và Android với Flutter và Dart từ con số 0.',
    outcomes: ['Thiết kế giao diện bằng Widget', 'Quản lý state phức tạp', 'Kết nối Firebase realtime'],
    syllabus: ['Dart basics', 'Flutter layout', 'State management (Provider/Bloc)', 'Firebase integration', 'App Store deployment'],
    resources: ['Flutter UI kit', 'Dart cheatsheet', 'Asset pack'],
  },
  {
    id: 'data',
    title: 'Phân tích dữ liệu với Python',
    author: 'TS. Lê Đức Hùng',
    category: 'Data Science',
    image: 'course-data-bg.png',
    level: 'Beginner',
    lessons: 15,
    duration: '7 tuần',
    rating: 4.7,
    students: 420,
    progress: 10,
    tag: 'Được săn đón',
    description: 'Trích xuất insight từ dữ liệu lớn bằng Pandas, Numpy và vẽ biểu đồ trực quan.',
    outcomes: ['Làm sạch dữ liệu thô', 'Sử dụng Pandas thành thạo', 'Vẽ dashboard với Plotly'],
    syllabus: ['Python for Data', 'Pandas & Numpy', 'Data Cleaning', 'Data Visualization', 'Capstone Project'],
    resources: ['Kaggle Datasets', 'Jupyter notebooks', 'Cheat sheets'],
  },
  {
    id: 'security',
    title: 'Bảo mật ứng dụng Web',
    author: 'ThS. Nguyễn Văn Toàn',
    category: 'Cyber Security',
    image: 'course-sec-bg.png',
    level: 'Advanced',
    lessons: 14,
    duration: '6 tuần',
    rating: 4.9,
    students: 198,
    progress: 5,
    tag: 'Đặc thù',
    description: 'Tấn công và phòng thủ các lỗi phổ biến (XSS, SQLi, CSRF) để bảo vệ hệ thống.',
    outcomes: ['Tìm và khai thác lỗ hổng web', 'Vá lỗi bảo mật', 'Triển khai xác thực an toàn'],
    syllabus: ['OWASP Top 10', 'Injection attacks', 'XSS & CSRF', 'Authentication flaws', 'Penetration testing cơ bản'],
    resources: ['Vulnerable VM', 'Báo cáo mẫu', 'Security checklist'],
  }
]

const posts = [
  {
    id: 1,
    title: 'Xu hướng học trực tuyến năm 2026',
    image: 'news1.jpg',
    category: 'EdTech',
    date: '12/06/2026',
    excerpt: 'Cá nhân hóa lộ trình, quiz tương tác và nội dung ngắn đang thay đổi cách người học tiếp cận tri thức.',
  },
  {
    id: 2,
    title: 'AI hỗ trợ giảng viên tạo khóa học',
    image: 'news2.jpg',
    category: 'AI',
    date: '18/06/2026',
    excerpt: 'Công cụ AI giúp tạo đề cương, gợi ý bài tập và theo dõi mức độ hoàn thành của học viên.',
  },
  {
    id: 3,
    title: 'Cách học hiệu quả với LMS',
    image: 'news4.jpg',
    category: 'Learning',
    date: '24/06/2026',
    excerpt: 'Một hệ thống LMS tốt cần có tiến trình rõ ràng, phản hồi nhanh và dữ liệu học tập dễ theo dõi.',
  },
  {
    id: 4,
    title: 'Thiết kế quiz để học viên nhớ lâu hơn',
    image: 'news6.png',
    category: 'Quiz',
    date: '27/06/2026',
    excerpt: 'Quiz ngắn, phản hồi tức thì và câu hỏi theo ngữ cảnh giúp tăng khả năng ghi nhớ sau mỗi buổi học.',
  },
]

const testimonials = [
  { name: 'Minh Anh', role: 'Sinh viên CNTT', quote: 'EduPress giúp mình nhìn rõ tiến trình học và biết bài nào cần ôn lại trước khi làm project.' },
  { name: 'Gia Huy', role: 'Frontend learner', quote: 'Khóa web có bài tập sát thực tế, phần quiz sau mỗi module làm mình nhớ kiến thức lâu hơn.' },
  { name: 'Thanh Trúc', role: 'Giảng viên', quote: 'Dashboard quản lý khóa học rõ ràng, nội dung dễ cập nhật và phù hợp cho lớp hybrid.' },
]

const quizQuestions = [
  { q: 'HTML dùng để làm gì?', a: 'Cấu trúc nội dung trang web', options: ['Thiết kế database', 'Cấu trúc nội dung trang web', 'Biên dịch Python'] },
  { q: 'CSS phụ trách phần nào?', a: 'Giao diện và bố cục', options: ['Giao diện và bố cục', 'Xác thực người dùng', 'Lưu trữ server'] },
  { q: 'FastAPI thường dùng để xây gì?', a: 'Backend API', options: ['Backend API', 'Ảnh minh họa', 'File CSS'] },
  { q: 'PostgreSQL là gì?', a: 'Hệ quản trị cơ sở dữ liệu', options: ['Framework frontend', 'Hệ quản trị cơ sở dữ liệu', 'Công cụ vẽ icon'] },
]

const learningSteps = [
  'Chọn khóa học theo mục tiêu nghề nghiệp',
  'Học từng module với tài liệu và bài thực hành',
  'Làm quiz để kiểm tra mức độ hiểu bài',
  'Theo dõi tiến trình và hoàn thành chứng nhận',
]

const route = ref('home')
const selectedCourseId = ref('ai')
const search = ref('')
const apiStatus = ref('checking')
const authMode = ref('login')
const loginForm = ref({ email: '', password: '' })
const registerForm = ref({ name: '', email: '', password: '' })
const profileForm = ref({ name: '', phone: '', school: '', bio: '' })
const passwordForm = ref({ current: '', next: '', confirm: '' })
const contactForm = ref({ name: '', email: '', message: '' })
const currentUserEmail = ref(localStorage.getItem('loggedInUser') || '')
const quizIndex = ref(0)
const quizScore = ref(0)
const selectedAnswer = ref('')
const quizFinished = ref(false)
const notice = ref('')
const showPlayer = ref(false)

const users = computed(() => JSON.parse(localStorage.getItem('users') || '[]'))
const currentUser = computed(() => users.value.find((user) => user.email === currentUserEmail.value))
const selectedCourse = computed(() => courses.find((course) => course.id === selectedCourseId.value) || courses[0])
const enrolledIds = computed(() => currentUser.value?.registeredCourses || [])
const completedIds = computed(() => currentUser.value?.completedCourses || [])
const quizHistory = computed(() => JSON.parse(localStorage.getItem('quizHistory') || '[]'))
const featuredCourse = computed(() => courses[2])
const filteredCourses = computed(() => {
  const keyword = search.value.trim().toLowerCase()
  if (!keyword) return courses
  return courses.filter((course) => [course.title, course.author, course.category, course.level, course.description].join(' ').toLowerCase().includes(keyword))
})

function asset(name) {
  return `${ASSET_BASE}${name}`
}

function generatedAsset(name) {
  return `${GENERATED_BASE}${name}`
}

function courseImage(course) {
  return generatedAsset(course.image)
}

function saveUsers(nextUsers) {
  localStorage.setItem('users', JSON.stringify(nextUsers))
}

function setNotice(message) {
  notice.value = message
  window.setTimeout(() => {
    if (notice.value === message) notice.value = ''
  }, 2600)
}

function navigate(nextRoute, courseId) {
  route.value = nextRoute
  if (courseId) selectedCourseId.value = courseId
  window.location.hash = courseId ? `${nextRoute}/${courseId}` : nextRoute
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function syncProfileForm() {
  profileForm.value = {
    name: currentUser.value?.name || '',
    phone: currentUser.value?.phone || '',
    school: currentUser.value?.school || '',
    bio: currentUser.value?.bio || '',
  }
}

function register() {
  const payload = { ...registerForm.value }
  if (!payload.name || !payload.email || payload.password.length < 6) return setNotice('Vui lòng nhập đủ thông tin và mật khẩu ít nhất 6 ký tự.')
  if (users.value.some((user) => user.email === payload.email)) return setNotice('Email này đã được đăng ký.')
  saveUsers([...users.value, { ...payload, registeredCourses: [], completedCourses: [] }])
  localStorage.setItem('loggedInUser', payload.email)
  currentUserEmail.value = payload.email
  registerForm.value = { name: '', email: '', password: '' }
  syncProfileForm()
  navigate('profile')
  setNotice('Tạo tài khoản thành công.')
}

function login() {
  const found = users.value.find((user) => user.email === loginForm.value.email && user.password === loginForm.value.password)
  if (!found) return setNotice('Email hoặc mật khẩu chưa đúng.')
  localStorage.setItem('loggedInUser', found.email)
  currentUserEmail.value = found.email
  loginForm.value = { email: '', password: '' }
  syncProfileForm()
  navigate('profile')
  setNotice('Đăng nhập thành công.')
}

function logout() {
  localStorage.removeItem('loggedInUser')
  currentUserEmail.value = ''
  navigate('home')
  setNotice('Đã đăng xuất.')
}

function resetPassword() {
  const email = loginForm.value.email.trim()
  if (!email) return setNotice('Nhập email để đặt lại mật khẩu demo.')
  saveUsers(users.value.map((user) => (user.email === email ? { ...user, password: '123456' } : user)))
  setNotice('Mật khẩu demo đã đổi thành 123456.')
}

function updateProfile() {
  if (!currentUser.value) return navigate('auth')
  saveUsers(users.value.map((user) => (user.email === currentUserEmail.value ? { ...user, ...profileForm.value } : user)))
  setNotice('Đã cập nhật hồ sơ.')
}

function changePassword() {
  if (!currentUser.value) return navigate('auth')
  if (passwordForm.value.current !== currentUser.value.password) return setNotice('Mật khẩu hiện tại chưa đúng.')
  if (passwordForm.value.next.length < 6 || passwordForm.value.next !== passwordForm.value.confirm) return setNotice('Mật khẩu mới chưa hợp lệ.')
  saveUsers(users.value.map((user) => (user.email === currentUserEmail.value ? { ...user, password: passwordForm.value.next } : user)))
  passwordForm.value = { current: '', next: '', confirm: '' }
  setNotice('Đã đổi mật khẩu.')
}

function enroll(courseId) {
  if (!currentUser.value) {
    setNotice('Bạn cần đăng nhập để đăng ký khóa học.')
    return navigate('auth')
  }
  saveUsers(users.value.map((user) => {
    if (user.email !== currentUserEmail.value) return user
    return { ...user, registeredCourses: [...new Set([...(user.registeredCourses || []), courseId])] }
  }))
  setNotice('Đã đăng ký khóa học.')
}

function markCompleted(courseId) {
  if (!currentUser.value) return navigate('auth')
  saveUsers(users.value.map((user) => {
    if (user.email !== currentUserEmail.value) return user
    return {
      ...user,
      registeredCourses: [...new Set([...(user.registeredCourses || []), courseId])],
      completedCourses: [...new Set([...(user.completedCourses || []), courseId])],
    }
  }))
  setNotice('Đã đánh dấu hoàn thành.')
}

function answerQuiz() {
  if (!selectedAnswer.value) return setNotice('Chọn một đáp án trước đã.')
  const nextScore = selectedAnswer.value === quizQuestions[quizIndex.value].a ? quizScore.value + 1 : quizScore.value
  quizScore.value = nextScore
  if (quizIndex.value === quizQuestions.length - 1) {
    quizFinished.value = true
    localStorage.setItem('quizHistory', JSON.stringify([{ score: nextScore, total: quizQuestions.length, date: new Date().toISOString() }, ...quizHistory.value]))
    return
  }
  quizIndex.value += 1
  selectedAnswer.value = ''
}

function restartQuiz() {
  quizIndex.value = 0
  quizScore.value = 0
  selectedAnswer.value = ''
  quizFinished.value = false
}

function sendContact() {
  if (!contactForm.value.name || !contactForm.value.email || !contactForm.value.message) return setNotice('Vui lòng nhập đủ thông tin liên hệ.')
  contactForm.value = { name: '', email: '', message: '' }
  setNotice('EduPress đã nhận phản hồi của bạn.')
}

function handleHashChange() {
  const hash = window.location.hash.replace('#', '')
  if (hash) {
    const [nextRoute, courseId] = hash.split('/')
    route.value = nextRoute
    if (courseId) selectedCourseId.value = courseId
  } else {
    route.value = 'home'
  }
}

onMounted(async () => {
  handleHashChange()
  window.addEventListener('hashchange', handleHashChange)
  
  syncProfileForm()
  try {
    const response = await fetch('http://localhost:8001/health')
    apiStatus.value = response.ok ? 'online' : 'offline'
  } catch {
    apiStatus.value = 'offline'
  }
})
</script>

<template>
  <div class="app-frame">
    <header class="site-header">
      <button class="brand" type="button" @click="navigate('home')">
        <img :src="generatedAsset('edupress-logo.svg')" alt="EduPress" />
        <span class="logo-text">EduPress</span>
      </button>

      <nav class="nav-links" aria-label="Primary">
        <button v-for="item in navItems" :key="item.id" :class="{ active: route === item.id }" type="button" @click="navigate(item.id)">{{ item.label }}</button>
        <button type="button" :class="{ active: route === 'quiz' }" @click="navigate('quiz')">Quiz</button>
      </nav>

      <div class="header-actions">
        <span :class="['api-pill', apiStatus]">{{ apiStatus === 'online' ? 'API live' : 'API offline' }}</span>
        <button v-if="currentUser" class="ghost-btn" type="button" @click="navigate('profile')">{{ currentUser.name || currentUser.email }}</button>
        <button v-if="currentUser" class="ghost-btn" type="button" @click="logout">Thoát</button>
        <button v-else class="primary-btn" type="button" @click="navigate('auth')">Đăng nhập</button>
      </div>
    </header>

    <p v-if="notice" class="toast">{{ notice }}</p>

    <!-- Cinematic Player Overlay -->
    <CinematicPlayer v-if="showPlayer" :course="selectedCourse" @close="showPlayer = false" />

    <main>
      <template v-if="route === 'home'">
        <section class="hero-section">
          <div class="hero-copy">
            <p class="eyebrow">Online learning platform</p>
            <h1>Học công nghệ theo lộ trình rõ ràng, có quiz và tiến trình thật.</h1>
            <p>EduPress kết hợp khóa học, bài kiểm tra, hồ sơ học tập và nội dung tin tức để tạo một trải nghiệm LMS đầy đủ hơn bản HTML cũ.</p>
            <div class="hero-actions">
              <button class="primary-btn" type="button" @click="navigate('courses')">Khám phá khóa học</button>
              <button class="secondary-btn" type="button" @click="navigate('course-detail', featuredCourse.id)">Xem khóa nổi bật</button>
            </div>
            <div class="hero-proof">
              <span>4.8/5 đánh giá</span>
              <span>1,284 học viên</span>
              <span>36 khóa học</span>
            </div>
          </div>

          <div class="hero-media">
            <img class="hero-image" :src="generatedAsset('edupress-hero.png')" alt="Học trực tuyến" />
            <article class="floating-card course-progress-card">
              <strong>{{ featuredCourse.title }}</strong>
              <span>{{ featuredCourse.progress }}% hoàn thành</span>
              <div class="progress-track"><i :style="{ width: `${featuredCourse.progress}%` }"></i></div>
            </article>
            <article class="floating-card quiz-badge">
              <strong>Quiz</strong>
              <span>Phản hồi tức thì</span>
            </article>
          </div>
        </section>

        <section class="metric-grid">
          <article><span>Học viên đang học</span><strong>1,284</strong></article>
          <article><span>Khóa học xuất bản</span><strong>36</strong></article>
          <article><span>Lượt quiz đã lưu</span><strong>{{ quizHistory.length }}</strong></article>
        </section>

        <section class="content-section section-band">
          <div class="section-heading split-heading">
            <div>
              <p class="eyebrow">Danh mục</p>
              <h2>Chọn lĩnh vực phù hợp với mục tiêu của bạn</h2>
            </div>
            <button class="secondary-btn" type="button" @click="navigate('courses')">Xem tất cả</button>
          </div>
          <div class="category-grid">
            <article v-for="category in categories" :key="category.name" :class="['category-card', category.tone]">
              <span>{{ category.count }} khóa</span>
              <h3>{{ category.name }}</h3>
              <p>{{ category.copy }}</p>
            </article>
          </div>
        </section>

        <section class="content-section section-band">
          <div class="section-heading">
            <p class="eyebrow">Khóa học nổi bật</p>
            <h2>Nội dung có hình ảnh, tiến trình và thông tin chi tiết</h2>
          </div>
          <div class="course-grid">
            <article v-for="course in courses.slice(0, 3)" :key="course.id" class="course-card featured-card">
              <img :src="courseImage(course)" :alt="course.title" />
              <div class="course-body">
                <div class="card-topline"><span>{{ course.tag }}</span><small>{{ course.rating }}/5</small></div>
                <h3>{{ course.title }}</h3>
                <p>{{ course.description }}</p>
                <div class="course-meta-row"><span>{{ course.lessons }} bài</span><span>{{ course.duration }}</span><span>{{ course.students }} học viên</span></div>
                <button class="text-btn" type="button" @click="navigate('course-detail', course.id)">Xem chi tiết</button>
              </div>
            </article>
          </div>
        </section>

        <section class="content-section learning-path">
          <div>
            <p class="eyebrow">Learning path</p>
            <h2>Một quy trình học rõ ràng từ đăng ký đến hoàn thành</h2>
            <p>Phần này thay cho các trang profile, quiz và course detail rời rạc của bản cũ, gom thành trải nghiệm LMS mạch lạc hơn.</p>
          </div>
          <ol>
            <li v-for="(step, index) in learningSteps" :key="step"><span>{{ index + 1 }}</span>{{ step }}</li>
          </ol>
        </section>

        <section class="content-section section-band testimonial-section">
          <article v-for="item in testimonials" :key="item.name" class="testimonial-card">
            <p>“{{ item.quote }}”</p>
            <strong>{{ item.name }}</strong>
            <span>{{ item.role }}</span>
          </article>
        </section>
      </template>

      <section v-if="route === 'courses'" class="content-section page-section">
        <div class="page-hero compact-hero">
          <div>
            <p class="eyebrow">Course catalog</p>
            <h1>Danh sách khóa học</h1>
            <p>Tìm khóa học theo lĩnh vực, cấp độ hoặc giảng viên. Mỗi khóa có lộ trình, tài nguyên và quiz liên quan.</p>
          </div>
          <input v-model="search" type="search" placeholder="Tìm AI, Web, OOP..." />
        </div>
        
        <LearningUniverse :courses="filteredCourses" @selectCourse="navigate('course-detail', $event)" />

        <div class="course-list">
          <article v-for="course in filteredCourses" :key="course.id" class="course-row-card">
            <img :src="courseImage(course)" :alt="course.title" />
            <div class="course-row-content">
              <div class="card-topline"><span>{{ course.category }}</span><small>{{ course.level }}</small></div>
              <h2>{{ course.title }}</h2>
              <p>{{ course.description }}</p>
              <div class="course-meta-row"><span>{{ course.author }}</span><span>{{ course.lessons }} bài học</span><span>{{ course.students }} học viên</span></div>
              <div class="card-actions">
                <button class="primary-btn" type="button" @click="navigate('course-detail', course.id)">Xem chi tiết</button>
                <button class="secondary-btn" type="button" @click="enroll(course.id)">Đăng ký</button>
              </div>
            </div>
          </article>
        </div>
      </section>

      <section v-if="route === 'course-detail'" class="content-section page-section detail-page">
        <div class="detail-hero">
          <img :src="courseImage(selectedCourse)" :alt="selectedCourse.title" />
          <div>
            <button class="text-btn" style="display: block; margin-bottom: 32px; padding-left: 0;" type="button" @click="navigate('courses')">← Quay lại danh sách</button>
            <p class="eyebrow">{{ selectedCourse.category }} · {{ selectedCourse.level }}</p>
            <h1>{{ selectedCourse.title }}</h1>
            <p>{{ selectedCourse.description }}</p>
            <div class="detail-meta"><span>{{ selectedCourse.author }}</span><span>{{ selectedCourse.duration }}</span><span>{{ selectedCourse.rating }}/5</span><span>{{ selectedCourse.students }} học viên</span></div>
            <div class="card-actions">
              <button class="primary-btn cinema-launch-btn" type="button" @click="showPlayer = true">🎬 Xem bài học</button>
              <button class="secondary-btn" type="button" @click="enroll(selectedCourse.id)">Đăng ký học</button>
              <button class="secondary-btn" type="button" @click="markCompleted(selectedCourse.id)">Hoàn thành</button>
              <button class="secondary-btn" type="button" @click="navigate('quiz')">Làm quiz</button>
            </div>
          </div>
        </div>

        <div class="detail-content-grid">
          <section class="panel rich-panel">
            <p class="eyebrow">Bạn sẽ đạt được</p>
            <h2>Kết quả đầu ra</h2>
            <ul class="check-list"><li v-for="item in selectedCourse.outcomes" :key="item">{{ item }}</li></ul>
          </section>
          <section class="panel rich-panel">
            <p class="eyebrow">Curriculum</p>
            <h2>Nội dung khóa học</h2>
            <ol class="module-list"><li v-for="item in selectedCourse.syllabus" :key="item">{{ item }}</li></ol>
          </section>
          <aside class="panel rich-panel resource-panel">
            <p class="eyebrow">Tài nguyên</p>
            <h2>Học liệu đi kèm</h2>
            <ul class="resource-list"><li v-for="item in selectedCourse.resources" :key="item">{{ item }}</li></ul>
          </aside>
        </div>
      </section>

      <section v-if="route === 'quiz'" class="content-section page-section quiz-layout">
        <div class="quiz-intro">
          <button class="text-btn" style="display: block; margin-bottom: 32px; padding-left: 0;" type="button" @click="navigate('course-detail', selectedCourseId)">← Quay lại khóa học</button>
          <p class="eyebrow">Interactive quiz</p>
          <h1>Kiểm tra kiến thức sau mỗi module</h1>
          <p>Quiz được thiết kế ngắn, rõ, có lưu lịch sử để học viên tự theo dõi tiến bộ.</p>
          <div class="quiz-stats"><span>{{ quizQuestions.length }} câu hỏi</span><span>{{ quizHistory.length }} lượt đã lưu</span></div>
        </div>
        <div v-if="!quizFinished" class="quiz-card">
          <div class="progress-line"><span :style="{ width: `${((quizIndex + 1) / quizQuestions.length) * 100}%` }"></span></div>
          <small>Câu {{ quizIndex + 1 }}/{{ quizQuestions.length }}</small>
          <h2>{{ quizQuestions[quizIndex].q }}</h2>
          <label v-for="option in quizQuestions[quizIndex].options" :key="option" class="option-row"><input v-model="selectedAnswer" type="radio" :value="option" /><span>{{ option }}</span></label>
          <button class="primary-btn" type="button" @click="answerQuiz">{{ quizIndex === quizQuestions.length - 1 ? 'Hoàn thành' : 'Câu tiếp theo' }}</button>
        </div>
        <div v-else class="quiz-card result-card">
          <h2>Kết quả: {{ quizScore }}/{{ quizQuestions.length }}</h2>
          <p>Lịch sử quiz đã được lưu trong trình duyệt.</p>
          <button class="primary-btn" type="button" @click="restartQuiz">Làm lại</button>
        </div>
      </section>

      <section v-if="route === 'blog'" class="content-section page-section">
        <button class="text-btn" style="display: block; margin-bottom: 32px; padding-left: 0;" type="button" @click="navigate('home')">← Về trang chủ</button>
        <div class="blog-hero">
          <img :src="asset('blog-banner.jpg')" alt="EduPress blog" />
          <div><p class="eyebrow">EduPress Blog</p><h1>Tin tức giáo dục và công nghệ</h1><p>Nhiều hình ảnh hơn bản trước, giữ lại chất tin tức của EduPress cũ nhưng trình bày gọn và hiện đại hơn.</p></div>
        </div>
        <div class="post-grid">
          <article v-for="post in posts" :key="post.id" class="post-card">
            <img :src="asset(post.image)" :alt="post.title" />
            <div><span>{{ post.category }} · {{ post.date }}</span><h3>{{ post.title }}</h3><p>{{ post.excerpt }}</p></div>
          </article>
        </div>
      </section>

      <section v-if="route === 'contact'" class="content-section page-section contact-layout">
        <div class="contact-copy">
          <button class="text-btn" style="display: block; margin-bottom: 32px; padding-left: 0;" type="button" @click="navigate('home')">← Về trang chủ</button>
          <p class="eyebrow">Contact</p>
          <h1>Liên hệ với EduPress</h1>
          <p>Đội ngũ EduPress hỗ trợ tư vấn khóa học, hợp tác giảng dạy và triển khai lớp học online.</p>
          <div class="contact-list"><span>support@edupress.vn</span><span>0900 123 456</span><span>MindX Technology School</span></div>
        </div>
        <form class="form-card" @submit.prevent="sendContact">
          <input v-model="contactForm.name" placeholder="Họ tên" />
          <input v-model="contactForm.email" type="email" placeholder="Email" />
          <textarea v-model="contactForm.message" placeholder="Nội dung cần tư vấn"></textarea>
          <button class="primary-btn" type="submit">Gửi phản hồi</button>
        </form>
      </section>

      <section v-if="route === 'auth'" class="content-section page-section auth-layout">
        <div class="auth-art">
          <button class="text-btn" style="display: block; margin-bottom: 32px; padding-left: 0;" type="button" @click="navigate('home')">← Về trang chủ</button>
          <p class="eyebrow">Account</p><h1>{{ authMode === 'login' ? 'Chào mừng quay lại' : 'Tạo tài khoản học tập' }}</h1><p>Đăng nhập để lưu khóa học, lịch sử quiz và tiến trình hoàn thành.</p>
        </div>
        <form v-if="authMode === 'login'" class="form-card" @submit.prevent="login">
          <input v-model="loginForm.email" type="email" placeholder="Email" />
          <input v-model="loginForm.password" type="password" placeholder="Mật khẩu" />
          <button class="primary-btn" type="submit">Đăng nhập</button>
          <button class="text-btn" type="button" @click="resetPassword">Quên mật khẩu demo</button>
          <button class="text-btn" type="button" @click="authMode = 'register'">Chưa có tài khoản? Đăng ký</button>
        </form>
        <form v-else class="form-card" @submit.prevent="register">
          <input v-model="registerForm.name" placeholder="Họ tên" />
          <input v-model="registerForm.email" type="email" placeholder="Email" />
          <input v-model="registerForm.password" type="password" placeholder="Mật khẩu" />
          <button class="primary-btn" type="submit">Tạo tài khoản</button>
          <button class="text-btn" type="button" @click="authMode = 'login'">Đã có tài khoản? Đăng nhập</button>
        </form>
      </section>

      <section v-if="route === 'profile'" class="content-section page-section profile-page">
        <button class="text-btn" style="display: block; margin-bottom: 32px; padding-left: 0; align-self: flex-start; text-align: left; margin-right: auto;" type="button" @click="navigate('home')">← Về trang chủ</button>

        <div v-if="!currentUser" class="profile-summary">
          <p class="eyebrow">Learner profile</p>
          <h1>Bạn chưa đăng nhập</h1>
          <p>Đăng nhập để xem Dashboard học tập và quản lý lộ trình của bạn.</p>
          <button class="primary-btn" type="button" @click="navigate('auth')">Đăng nhập ngay</button>
        </div>

        <div v-else class="bento-dashboard">
          <!-- 1. Welcome & Stats (Span 2) -->
          <div class="bento-item bento-welcome rich-panel">
            <p class="eyebrow">Dashboard</p>
            <h2>Chào {{ currentUser.name }},</h2>
            <p class="text-muted">Tiếp tục hành trình học tập của bạn cùng EduPress hôm nay nhé!</p>
            <div class="bento-stats-row">
              <div class="stat-box">
                <div class="stat-header"><span>Khóa đang học</span><span>{{ enrolledIds.length > 0 ? '65%' : '0%' }}</span></div>
                <div class="animated-progress"><div class="animated-progress-fill" :style="`width: ${enrolledIds.length > 0 ? 65 : 0}%`"></div></div>
              </div>
              <div class="stat-box">
                <div class="stat-header"><span>Tiến độ hoàn thành</span><span>{{ completedIds.length > 0 ? '100%' : '20%' }}</span></div>
                <div class="animated-progress"><div class="animated-progress-fill" :style="`width: ${completedIds.length > 0 ? 100 : 20}%`"></div></div>
              </div>
              <div class="stat-box">
                <div class="stat-header"><span>Điểm tích lũy</span><span>45%</span></div>
                <div class="animated-progress"><div class="animated-progress-fill" style="width: 45%"></div></div>
              </div>
            </div>
          </div>

          <!-- 2. Continue Learning (Span 2) -->
          <div class="bento-item bento-continue rich-panel">
            <p class="eyebrow">Tiến trình</p>
            <h2>Đang học gần đây</h2>
            <div v-if="enrolledIds.length > 0" class="current-course-widget">
              <div class="widget-info">
                <strong>{{ courses.find(c => c.id === enrolledIds[enrolledIds.length - 1])?.title || 'Khóa học' }}</strong>
                <span>Tiến độ: 45%</span>
              </div>
              <div class="progress-bar"><div class="progress-fill" style="width: 45%;"></div></div>
              <button class="primary-btn small-btn" type="button" @click="navigate('course-detail', enrolledIds[enrolledIds.length - 1])">Tiếp tục học</button>
            </div>
            <div v-else class="empty-state">
              <p>Bạn chưa đăng ký khóa học nào.</p>
              <button class="secondary-btn" type="button" @click="navigate('courses')">Khám phá lộ trình</button>
            </div>
          </div>

          <!-- 3. Profile Info (Span 2) -->
          <form class="bento-item bento-profile form-card" @submit.prevent="updateProfile">
            <p class="eyebrow">Cài đặt</p>
            <h2>Hồ sơ cá nhân</h2>
            <input v-model="profileForm.name" placeholder="Họ tên" />
            <input v-model="profileForm.phone" placeholder="Số điện thoại" />
            <input v-model="profileForm.school" placeholder="Trường / đơn vị công tác" />
            <textarea v-model="profileForm.bio" placeholder="Mục tiêu học tập của bạn..."></textarea>
            <button class="primary-btn" type="submit">Lưu thay đổi</button>
          </form>

          <!-- 4. Security (Span 2) -->
          <form class="bento-item bento-security form-card" @submit.prevent="changePassword">
            <p class="eyebrow">Bảo mật</p>
            <h2>Đổi mật khẩu</h2>
            <input v-model="passwordForm.current" type="password" placeholder="Mật khẩu hiện tại" />
            <input v-model="passwordForm.next" type="password" placeholder="Mật khẩu mới" />
            <input v-model="passwordForm.confirm" type="password" placeholder="Nhập lại mật khẩu mới" />
            <button class="secondary-btn" type="submit">Cập nhật mật khẩu</button>
          </form>

          <!-- 5. All Enrolled Courses (Span 4) -->
          <div class="bento-item bento-courses rich-panel">
            <p class="eyebrow">Thư viện của bạn</p>
            <h2>Khóa học đã đăng ký</h2>
            <div class="bento-course-grid" v-if="enrolledIds.length > 0">
              <article v-for="course in courses.filter(c => enrolledIds.includes(c.id))" :key="course.id" class="mini-course-card">
                <img :src="courseImage(course)" :alt="course.title" />
                <div class="mini-course-info">
                  <strong>{{ course.title }}</strong>
                  <span :class="['status-badge', completedIds.includes(course.id) ? 'done' : 'learning']">
                    {{ completedIds.includes(course.id) ? '✓ Hoàn thành' : '▶ Đang học' }}
                  </span>
                </div>
              </article>
            </div>
            <p v-else class="text-muted">Chưa có dữ liệu.</p>
          </div>
        </div>
      </section>
    </main>

    <footer class="site-footer">
      <div class="footer-inner">
        <div class="footer-brand">
          <img :src="generatedAsset('edupress-logo.svg')" alt="EduPress" />
          <div>
            <strong class="logo-text">EduPress</strong>
            <p>Nền tảng học trực tuyến với khóa học, quiz, tiến trình và tài nguyên học tập.</p>
          </div>
        </div>
        <div class="footer-columns">
          <div>
            <h3>Nền tảng</h3>
            <button type="button" @click="navigate('courses')">Khóa học</button>
            <button type="button" @click="navigate('quiz')">Quiz</button>
            <button type="button" @click="navigate('profile')">Hồ sơ</button>
          </div>
          <div>
            <h3>Nội dung</h3>
            <button type="button" @click="navigate('blog')">Tin tức</button>
            <button type="button" @click="navigate('contact')">Liên hệ</button>
            <button type="button" @click="navigate('course-detail', featuredCourse.id)">Khóa nổi bật</button>
          </div>
          <div>
            <h3>Liên hệ</h3>
            <span>support@edupress.vn</span>
            <span>0900 123 456</span>
            <span>MindX Technology School</span>
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>
