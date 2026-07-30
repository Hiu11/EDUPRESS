<script setup>
import { computed, onMounted, ref } from 'vue'
import confetti from 'canvas-confetti'
import '~/assets/css/tailwind.css'
import LearningUniverse from './components/LearningUniverse.vue'
import CinematicPlayer from './components/CinematicPlayer.vue'
import InBrowserIDE from './components/InBrowserIDE.vue'
import TrophyRoom from './components/TrophyRoom.vue'
import AICompanion from './components/AICompanion.vue'
import SwipeableFlashcards from './components/SwipeableFlashcards.vue'
import CourseCreatorStudio from './components/CourseCreatorStudio.vue'
import WhiteboardPro from './components/WhiteboardPro.vue'

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

const defaultQuizQuestions = [
  { q: 'HTML dùng để làm gì trong lập trình web?', a: 'Cấu trúc nội dung trang web', options: ['Thiết kế giao diện màu sắc', 'Cấu trúc nội dung trang web', 'Xử lý logic phía server', 'Quản lý database'], explanation: 'HTML phụ trách cấu trúc và ngữ nghĩa nội dung. CSS phụ trách giao diện, JS xử lý tương tác, server-side languages xử lý logic backend.', difficulty: 'easy', topic_tag: 'HTML Basics' },
  { q: 'CSS Flexbox và CSS Grid khác nhau ở điểm nào chính?', a: 'Flexbox là 1 chiều, Grid là 2 chiều', options: ['Flexbox nhanh hơn Grid', 'Flexbox là 1 chiều, Grid là 2 chiều', 'Grid chỉ dùng được trên Desktop', 'Chúng hoàn toàn giống nhau'], explanation: 'Flexbox được thiết kế để bố cục 1 chiều (hàng hoặc cột). Grid xử lý 2 chiều đồng thời (cả hàng và cột). Dùng kết hợp cả hai là best practice.', difficulty: 'medium', topic_tag: 'CSS Layout' },
  { q: 'Trong JavaScript, sự khác biệt giữa == và === là gì?', a: '=== kiểm tra cả giá trị và kiểu dữ liệu', options: ['=== chạy nhanh hơn ==', '=== kiểm tra cả giá trị và kiểu dữ liệu', '== luôn trả về true', 'Chúng không có sự khác biệt'], explanation: '== thực hiện type coercion (ép kiểu) trước so sánh nên "1" == 1 là true. === so sánh strict không coerce nên "1" === 1 là false. Luôn dùng === trong thực tế.', difficulty: 'easy', topic_tag: 'JavaScript Core' },
  { q: 'REST API sử dụng HTTP method nào để cập nhật toàn bộ một resource?', a: 'PUT', options: ['GET', 'POST', 'PUT', 'DELETE'], explanation: 'PUT thay thế toàn bộ resource. PATCH chỉ cập nhật một phần. POST tạo resource mới. GET chỉ đọc. Đây là convention của RESTful API design.', difficulty: 'medium', topic_tag: 'REST API' },
  { q: 'Event bubbling trong JavaScript hoạt động như thế nào?', a: 'Sự kiện lan truyền từ phần tử con lên phần tử cha', options: ['Sự kiện lan truyền từ phần tử cha xuống con', 'Sự kiện chỉ xảy ra ở phần tử được click', 'Sự kiện lan truyền từ phần tử con lên phần tử cha', 'Sự kiện xảy ra ngẫu nhiên'], explanation: 'Event Bubbling: khi click vào button con, sự kiện "nổi" lên qua div cha, rồi body, rồi document. Dùng event.stopPropagation() để dừng. Event Capturing là chiều ngược lại.', difficulty: 'hard', topic_tag: 'JavaScript DOM' },
]
const quizQuestions = ref([...defaultQuizQuestions])

const testimonials = [
  { name: 'Minh Anh', role: 'Sinh viên CNTT', quote: 'EduPress giúp mình nhìn rõ tiến trình học và biết bài nào cần ôn lại trước khi làm project.' },
  { name: 'Gia Huy', role: 'Frontend learner', quote: 'Khóa web có bài tập sát thực tế, phần quiz sau mỗi module làm mình nhớ kiến thức lâu hơn.' },
  { name: 'Thanh Trúc', role: 'Giảng viên', quote: 'Dashboard quản lý khóa học rõ ràng, nội dung dễ cập nhật và phù hợp cho lớp hybrid.' },
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
const loginForm = ref({ email: '' })
const registerForm = ref({ name: '', email: '' })
const profileForm = ref({ name: '', phone: '', school: '', bio: '' })
const contactForm = ref({ name: '', email: '', message: '' })
const notice = ref('')
const showPlayer = ref(false)
const showIDE = ref(false)
const showFlashcards = ref(false)
const showStudio = ref(false)
const showWhiteboard = ref(false)

const { data: users, saveData: saveUsersDB } = useLocalSync('users', [])
const { data: currentUserEmail, saveData: saveEmailDB } = useLocalSync('loggedInUser', '')
const { data: quizHistory, saveData: saveQuizHistoryDB } = useLocalSync('quizHistory', [])
const { data: courseInteractions, saveData: saveInteractionsDB } = useLocalSync('courseInteractions', {})

const courseRoadmaps = {
  ai: [
    { title: '🧮 Toán & Phân tích', links: [{ text: 'AI & Data Scientist Roadmap', url: 'https://roadmap.sh/ai-data-scientist' }, { text: 'Python for AI', url: 'https://www.w3schools.com/python/' }] },
    { title: '🤖 Machine Learning', links: [{ text: 'Prompt Engineering Roadmap', url: 'https://roadmap.sh/prompt-engineering' }, { text: 'TensorFlow Docs', url: 'https://www.tensorflow.org/' }] }
  ],
  web: [
    { title: '🎨 Frontend (Giao diện)', links: [{ text: 'Frontend Developer Roadmap', url: 'https://roadmap.sh/frontend' }, { text: 'W3Schools: HTML/CSS/JS', url: 'https://www.w3schools.com/html/' }, { text: 'Vue.js Official Docs', url: 'https://vuejs.org/guide/introduction.html' }] },
    { title: '⚙️ Backend (Xử lý Logic)', links: [{ text: 'Backend Developer Roadmap', url: 'https://roadmap.sh/backend' }, { text: 'Node.js API Reference', url: 'https://nodejs.org/en/docs/' }, { text: 'Express Framework', url: 'https://expressjs.com/' }] },
    { title: '🗄️ Database (Lưu trữ)', links: [{ text: 'PostgreSQL DBA Roadmap', url: 'https://roadmap.sh/postgresql-dba' }, { text: 'W3Schools: SQL Tutorial', url: 'https://www.w3schools.com/sql/' }, { text: 'MongoDB NoSQL Docs', url: 'https://www.mongodb.com/docs/' }] }
  ],
  security: [
    { title: '🛡️ Cyber Security', links: [{ text: 'Cyber Security Roadmap', url: 'https://roadmap.sh/cyber-security' }, { text: 'OWASP Top 10', url: 'https://owasp.org/www-project-top-ten/' }] }
  ]
}
const activeRoadmap = computed(() => courseRoadmaps[selectedCourseId.value] || courseRoadmaps.web)

const { isOnline, networkState } = useNetworkStatus()
const currentUser = computed(() => users.value.find((user) => user.email === currentUserEmail.value))
const selectedCourse = computed(() => courses.find((course) => course.id === selectedCourseId.value) || courses[0])
const enrolledIds = computed(() => currentUser.value?.registeredCourses || [])
const completedIds = computed(() => currentUser.value?.completedCourses || [])

const quizIndex = ref(0)
const quizScore = ref(0)
const selectedAnswer = ref('')
const quizFinished = ref(false)
const showPodcast = ref(false)
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
  saveUsersDB(nextUsers)
}

function setNotice(message) {
  notice.value = message
  window.setTimeout(() => {
    if (notice.value === message) notice.value = ''
  }, 2600)
}

const theme = ref('light')
if (import.meta.client) {
  const stored = localStorage.getItem('theme')
  if (stored) {
    theme.value = stored
  } else if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
    theme.value = 'dark'
  }
}

function cycleTheme() {
  const themes = ['light', 'dark', 'oled']
  const next = themes[(themes.indexOf(theme.value) + 1) % themes.length]
  theme.value = next
  localStorage.setItem('theme', next)
  if (next === 'light') {
    document.documentElement.removeAttribute('data-theme')
  } else {
    document.documentElement.setAttribute('data-theme', next)
  }
}

function executeNavigation(nextRoute, courseId) {
  route.value = nextRoute
  if (courseId) selectedCourseId.value = courseId
  window.location.hash = courseId ? `${nextRoute}/${courseId}` : nextRoute
  window.scrollTo({ top: 0, behavior: 'smooth' })
  
  if (nextRoute === 'course-detail' && courseId) {
    loadCourseComments(courseId)
    connectSSE(courseId)
  } else {
    if (sseConnection.value) {
      sseConnection.value.close()
      sseConnection.value = null
    }
  }
}

// ── Realtime Comments Logic ──────────────────────────────────────────
const courseComments = ref([])
const commentInput = ref("")
const sseConnection = ref(null)

async function loadCourseComments(courseId) {
  try {
    const res = await fetch(`http://localhost:8001/api/comments/${courseId}`)
    const data = await res.json()
    courseComments.value = data
  } catch (e) {
    console.error("Failed to load comments", e)
  }
}

async function submitComment() {
  if (!commentInput.value.trim() || !selectedCourseId.value) return
  const content = commentInput.value.trim()
  commentInput.value = ""
  try {
    await fetch("http://localhost:8001/api/comments", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        post_id: selectedCourseId.value,
        user_id: currentUser.value?.name || currentUser.value?.email || "Guest",
        content: content
      })
    })
  } catch (e) {
    console.error("Failed to submit comment", e)
  }
}

function connectSSE(courseId) {
  if (sseConnection.value) sseConnection.value.close()
  sseConnection.value = new EventSource("http://localhost:8001/api/stream")
  sseConnection.value.onmessage = (event) => {
    try {
      const parsed = JSON.parse(event.data)
      if (parsed.event === "CommentCreated" && parsed.data.post_id === courseId) {
        // SSE trigger: Add directly to top
        courseComments.value.unshift(parsed.data)
      }
    } catch (e) {
      console.error("SSE parse error", e)
    }
  }
}

function navigate(nextRoute, courseId) {
  if (document.startViewTransition) {
    document.startViewTransition(() => {
      executeNavigation(nextRoute, courseId)
    })
  } else {
    executeNavigation(nextRoute, courseId)
  }
}

function syncProfileForm() {
  profileForm.value = {
    name: currentUser.value?.name || '',
    phone: currentUser.value?.phone || '',
    school: currentUser.value?.school || '',
    bio: currentUser.value?.bio || '',
  }
}

function isValidEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)
}

async function register() {
  const payload = {
    name: registerForm.value.name.trim(),
    email: registerForm.value.email.trim().toLowerCase(),
  }
  if (!payload.name || !payload.email) return setNotice('Vui lòng nhập đủ thông tin.')
  if (!isValidEmail(payload.email)) return setNotice('Email không hợp lệ.')
  if (users.value.some((user) => user.email === payload.email)) return setNotice('Email này đã được đăng ký.')
  
  try {
    const publicKeyCredentialCreationOptions = {
        challenge: Uint8Array.from('edu-challenge-' + Date.now(), c => c.charCodeAt(0)),
        rp: { name: "EduPress", id: window.location.hostname },
        user: {
            id: Uint8Array.from(payload.email, c => c.charCodeAt(0)),
            name: payload.email,
            displayName: payload.name,
        },
        pubKeyCredParams: [{alg: -7, type: "public-key"}, {alg: -257, type: "public-key"}],
        authenticatorSelection: {
            authenticatorAttachment: "platform",
            residentKey: "required",
            userVerification: "required"
        },
        timeout: 60000,
        attestation: "none"
    };
    
    const credential = await navigator.credentials.create({ publicKey: publicKeyCredentialCreationOptions });
    const passkeyId = credential.id;
    
    saveUsers([...users.value, { ...payload, passkeyId: passkeyId, role: 'student', registeredCourses: [], completedCourses: [] }])
    saveEmailDB(payload.email)
    registerForm.value = { name: '', email: '' }
    loginForm.value = { email: '' }
    syncProfileForm()
    navigate('profile')
    setNotice('Đăng ký bằng sinh trắc học thành công 🛡️')
  } catch (err) {
    console.error(err)
    setNotice('Lỗi đăng ký Passkey hoặc bạn đã hủy.')
  }
}

async function login() {
  try {
    const publicKeyCredentialRequestOptions = {
        challenge: Uint8Array.from('edu-challenge-' + Date.now(), c => c.charCodeAt(0)),
        timeout: 60000,
        rpId: window.location.hostname,
        userVerification: "required"
    };

    const assertion = await navigator.credentials.get({ publicKey: publicKeyCredentialRequestOptions });
    const passkeyId = assertion.id;
    
    const found = users.value.find((user) => user.passkeyId === passkeyId)
    if (!found) return setNotice('Không tìm thấy tài khoản cho Passkey này.')
    
    saveEmailDB(found.email)
    loginForm.value = { email: '' }
    registerForm.value = { name: '', email: '' }
    syncProfileForm()
    navigate('profile')
    setNotice('Đăng nhập sinh trắc học thành công 🛡️')
  } catch (err) {
    console.error(err)
    setNotice('Lỗi đăng nhập Passkey hoặc thiết bị không hỗ trợ.')
  }
}

function loginMagicLink() {
  const email = loginForm.value.email.trim().toLowerCase()
  if (!email || !isValidEmail(email)) return setNotice('Nhập email hợp lệ để gửi Magic Link.')
  if (!users.value.some((user) => user.email === email)) return setNotice('Email này chưa được đăng ký.')
  
  // Simulate clicking magic link
  setTimeout(() => {
    saveEmailDB(email)
    loginForm.value = { email: '' }
    syncProfileForm()
    navigate('profile')
    setNotice('Đã xác thực qua Magic Link 📧')
  }, 1000)
  setNotice('Đã gửi Magic Link đến email của bạn!')
}

function logout() {
  saveEmailDB('')
  profileForm.value = { name: '', phone: '', school: '', bio: '' }
  loginForm.value = { email: '' }
  registerForm.value = { name: '', email: '' }
  navigate('home')
  setNotice('Đã đăng xuất.')
}

function updateProfile() {
  if (!currentUser.value) return navigate('auth')
  saveUsers(users.value.map((user) => (user.email === currentUserEmail.value ? { ...user, ...profileForm.value } : user)))
  setNotice('Đã cập nhật hồ sơ.')
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

const isEnrolled = computed(() => {
  if (!currentUser.value || !selectedCourse.value) return false
  return (currentUser.value.registeredCourses || []).includes(selectedCourse.value.id)
})

const isCompleted = computed(() => {
  if (!currentUser.value || !selectedCourse.value) return false
  return (currentUser.value.completedCourses || []).includes(selectedCourse.value.id)
})

// ── Quiz State (V3) ─────────────────────────────────────────────
const quizAnswered = ref(false)
const quizAnswers = ref([])
const quizStreak = ref(0)
const quizMaxStreak = ref(0)
const quizAIReasoning = ref('')
const quizWeakTopic = ref('')
const quizTimeLeft = ref(30)
const quizTimerActive = ref(false)
let quizTimerInterval = null

function startTimer() {
  clearInterval(quizTimerInterval)
  quizTimeLeft.value = 30
  quizTimerActive.value = true
  quizTimerInterval = setInterval(() => {
    if (quizAnswered.value || quizFinished.value) { clearInterval(quizTimerInterval); return }
    if (quizTimeLeft.value <= 0) {
      clearInterval(quizTimerInterval)
      quizTimerActive.value = false
      if (!quizAnswered.value) { selectedAnswer.value = '__timeout__'; answerQuiz() }
    } else {
      quizTimeLeft.value -= 1
    }
  }, 1000)
}

function stopTimer() {
  clearInterval(quizTimerInterval)
  quizTimerActive.value = false
}

function playSound(type) {
  if (!import.meta.client) return
  try {
    const ctx = new (window.AudioContext || window.webkitAudioContext)()
    const osc = ctx.createOscillator()
    const gainNode = ctx.createGain()
    osc.connect(gainNode)
    gainNode.connect(ctx.destination)
    if (type === 'correct') {
      osc.type = 'sine'
      osc.frequency.setValueAtTime(500, ctx.currentTime)
      osc.frequency.exponentialRampToValueAtTime(1000, ctx.currentTime + 0.1)
      gainNode.gain.setValueAtTime(0.1, ctx.currentTime)
      gainNode.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.1)
      osc.start()
      osc.stop(ctx.currentTime + 0.1)
    } else {
      osc.type = 'sawtooth'
      osc.frequency.setValueAtTime(300, ctx.currentTime)
      osc.frequency.exponentialRampToValueAtTime(150, ctx.currentTime + 0.2)
      gainNode.gain.setValueAtTime(0.1, ctx.currentTime)
      gainNode.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.2)
      osc.start()
      osc.stop(ctx.currentTime + 0.2)
    }
  } catch (e) {}
}

const isSyncing = ref(false)
const syncSuccess = ref(false)

async function syncQuizHistoryToDB(score, total, topic, maxStreak) {
  isSyncing.value = true
  try {
    const res = await fetch('http://localhost:8001/api/quiz/sync', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: currentUser.value?.id || 'guest',
        course_id: selectedCourseId.value || 'course_1',
        score,
        total,
        topic,
        max_streak: maxStreak
      })
    })
    const data = await res.json()
    if (data.success) {
      syncSuccess.value = true
      setTimeout(() => syncSuccess.value = false, 3000)
    }
  } catch(e) {
    console.error("Sync failed", e)
  } finally {
    isSyncing.value = false
  }
}

function answerQuiz() {
  if (!selectedAnswer.value) return setNotice('Chọn một đáp án trước đã.')
  stopTimer()
  const current = quizQuestions.value[quizIndex.value]
  const isRight = selectedAnswer.value !== '__timeout__' && selectedAnswer.value === current.a
  if (isRight) {
    playSound('correct')
    quizScore.value += 1
    quizStreak.value += 1
    if (quizStreak.value > quizMaxStreak.value) quizMaxStreak.value = quizStreak.value
  } else {
    playSound('wrong')
    quizStreak.value = 0
  }
  quizAnswers.value.push({
    question: current.q,
    chosen: selectedAnswer.value === '__timeout__' ? '(Hết giờ)' : selectedAnswer.value,
    correct: current.a,
    isRight,
    explanation: current.explanation || '',
    topic_tag: current.topic_tag || '',
    difficulty: current.difficulty || 'medium',
    timeSpent: 30 - quizTimeLeft.value
  })
  quizAnswered.value = true
}

function nextQuestion() {
  quizAnswered.value = false
  if (quizIndex.value === quizQuestions.value.length - 1) {
    quizFinished.value = true
    const score = quizScore.value
    const total = quizQuestions.value.length
    const topic = quizWeakTopic.value || quizQuestions.value[0]?.topic_tag || ''
    
    if (score === total && import.meta.client) {
      confetti({ particleCount: 150, spread: 70, origin: { y: 0.6 } })
    }

    localStorage.setItem('quizHistory', JSON.stringify([
      { score, total, topic, maxStreak: quizMaxStreak.value, date: new Date().toISOString() },
      ...quizHistory.value
    ]))

    syncQuizHistoryToDB(score, total, topic, quizMaxStreak.value)
  } else {
    quizIndex.value += 1
    selectedAnswer.value = ''
    startTimer()
  }
}

function retryWrongAnswers() {
  const wrongAnswers = quizAnswers.value.filter(a => !a.isRight)
  if (!wrongAnswers.length) return
  quizQuestions.value = wrongAnswers.map(w => {
    return {
      q: w.question,
      a: w.correct,
      options: quizQuestions.value.find(q => q.q === w.question)?.options || [],
      explanation: w.explanation,
      topic_tag: w.topic_tag,
      difficulty: w.difficulty
    }
  })
  quizIndex.value = 0
  quizScore.value = 0
  quizStreak.value = 0
  quizMaxStreak.value = 0
  selectedAnswer.value = ''
  quizFinished.value = false
  quizAnswered.value = false
  quizAnswers.value = []
  quizAIReasoning.value = "Chế độ ôn tập: Chỉ làm lại các câu bạn vừa chọn sai."
  stopTimer()
  startTimer()
}

function restartQuiz() {
  quizQuestions.value = [...defaultQuizQuestions]
  quizIndex.value = 0
  quizScore.value = 0
  quizStreak.value = 0
  quizMaxStreak.value = 0
  selectedAnswer.value = ''
  quizFinished.value = false
  quizAnswered.value = false
  quizAnswers.value = []
  quizAIReasoning.value = ''
  quizWeakTopic.value = ''
  stopTimer()
  startTimer()
}

const isGeneratingQuiz = ref(false)
async function generateAutoQuiz() {
  isGeneratingQuiz.value = true
  stopTimer()
  try {
    const res = await fetch('http://localhost:8001/api/quiz/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        history: quizHistory.value.map(h => ({ score: h.score, total: h.total, topic: h.topic || '', date: h.date })),
        course_title: selectedCourse.value?.title || 'Lập trình Web',
        course_category: selectedCourse.value?.category || 'Technology',
        batch_size: 5
      })
    })
    const json = await res.json()
    if (json.success && json.data?.length) {
      quizQuestions.value = json.data.map(d => ({
        q: d.question, a: d.correct_answer, options: d.options,
        explanation: d.explanation, topic_tag: d.topic_tag, difficulty: d.difficulty
      }))
      quizAIReasoning.value = json.analyzer_reasoning || ''
      quizWeakTopic.value = json.weak_topic || ''
      quizIndex.value = 0
      quizScore.value = 0
      quizStreak.value = 0
      quizMaxStreak.value = 0
      quizFinished.value = false
      quizAnswered.value = false
      quizAnswers.value = []
      selectedAnswer.value = ''
      startTimer()
      setNotice(`Đã tạo ${json.question_count} câu hỏi về "${json.weak_topic}" (${json.generated_in_seconds}s)`)
    } else {
      setNotice('Lỗi khi tạo quiz từ AI.')
    }
  } catch {
    setNotice('Không thể kết nối backend AI. Dùng bộ câu hỏi mẫu.')
  } finally {
    isGeneratingQuiz.value = false
  }
}

if (import.meta.client) {
  window.addEventListener('keydown', (e) => {
    if (route.value !== 'quiz' || quizFinished.value || quizAnswered.value) return
    const current = quizQuestions.value[quizIndex.value]
    if (!current) return
    const keyMap = { '1': 0, '2': 1, '3': 2, '4': 3 }
    if (keyMap[e.key] !== undefined && current.options[keyMap[e.key]]) {
      selectedAnswer.value = current.options[keyMap[e.key]]
    }
    if ((e.key === 'Enter') && selectedAnswer.value && !quizAnswered.value) {
      answerQuiz()
    }
  })
}

function trackInteraction(courseId, action) {
  const interactions = courseInteractions.value[courseId] || []
  if (!interactions.includes(action)) {
    courseInteractions.value[courseId] = [...interactions, action]
    saveInteractionsDB(courseInteractions.value)
  }
}

function openTool(tool) {
  if (tool === 'video') showPlayer.value = true
  if (tool === 'ide') showIDE.value = true
  if (tool === 'flashcards') showFlashcards.value = true
  if (tool === 'whiteboard') showWhiteboard.value = true
  if (tool === 'podcast') showPodcast.value = true
  
  if (selectedCourseId.value) {
    trackInteraction(selectedCourseId.value, tool)
  }
}

const showCompletionModal = ref(false)
const completionConditions = computed(() => {
  const id = selectedCourseId.value
  const interactions = courseInteractions.value[id] || []
  return [
    { id: 'video', name: 'Xem video bài giảng ít nhất 1 lần', met: interactions.includes('video') },
    { id: 'ide', name: 'Mở không gian Thực hành (IDE)', met: interactions.includes('ide') },
    { id: 'podcast', name: 'Nghe Podcast tổng ôn kiến thức', met: interactions.includes('podcast') }
  ]
})

function tryMarkCompleted() {
  if (completionConditions.value.every(c => c.met)) {
    markCompleted(selectedCourseId.value)
  } else {
    showCompletionModal.value = true
  }
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
  <div :class="['app-frame', { 'is-offline': networkState === 'offline' }]">
    <VitePwaManifest />
    
    <!-- Floating Sync Status Toast -->
    <Transition name="sync-toast">
      <div v-if="networkState !== 'online'" :class="['sync-toast-container', networkState]">
        <div class="sync-icon">
          <svg v-if="networkState === 'offline'" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 1l22 22M16.72 11.06A10.94 10.94 0 0 1 19 12.55M5 12.55a10.94 10.94 0 0 1 5.17-2.39M10.71 5.05A16 16 0 0 1 22.58 9M1.42 9a15.91 15.91 0 0 1 4.7-2.88M8.53 16.11a6 6 0 0 1 6.95 0M12 20h.01"/></svg>
          <svg v-else-if="networkState === 'syncing'" class="spin" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21.5 2v6h-6M2.5 22v-6h6M2 11.5a10 10 0 0 1 18.8-4.3M22 12.5a10 10 0 0 1-18.8 4.3"/></svg>
          <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 6L9 17l-5-5"/></svg>
        </div>
        <div class="sync-text">
          <strong v-if="networkState === 'offline'">Mất kết nối mạng</strong>
          <strong v-else-if="networkState === 'syncing'">Đang đồng bộ dữ liệu...</strong>
          <strong v-else>Đã đồng bộ 100%</strong>
          
          <span v-if="networkState === 'offline'">EduPress đang chạy chế độ Offline (0-Latency)</span>
          <span v-else-if="networkState === 'syncing'">Vui lòng không đóng trình duyệt</span>
          <span v-else>Dữ liệu đã an toàn trên đám mây</span>
        </div>
      </div>
    </Transition>

    <!-- Floating AI Study Companion -->
    <AICompanion />
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
        <button 
          class="flex items-center gap-2 px-4 py-1.5 rounded-full bg-[var(--bg-glass)] backdrop-blur-md border border-[var(--border-glass)] shadow-inner hover:scale-105 hover:shadow-[0_4px_15px_var(--border-glow)] transition-all duration-300 group" 
          type="button" 
          @click="cycleTheme" 
          :title="'Current Theme: ' + theme.toUpperCase()"
        >
          <span class="text-lg">{{ theme === 'light' ? '☀️' : theme === 'dark' ? '🌙' : '🌌' }}</span>
          <span class="text-xs font-bold uppercase tracking-widest opacity-80 group-hover:opacity-100 text-[var(--text-main)] group-hover:text-[var(--primary)] transition-colors">{{ theme }}</span>
        </button>
        <span :class="['api-pill', apiStatus]">{{ apiStatus === 'online' ? 'API live' : 'API offline' }}</span>
        <button v-if="currentUser && currentUser.role === 'instructor'" class="primary-btn" type="button" @click="showStudio = true" style="background: linear-gradient(135deg, #8b5cf6, #6366f1); border: none;">✍️ Soạn bài</button>
        <button class="ide-launch-btn" type="button" @click="showIDE = true">⚡ IDE</button>
        <button v-if="currentUser" class="ghost-btn" type="button" @click="navigate('profile')">{{ currentUser.name || currentUser.email }}</button>
        <button v-if="currentUser" class="ghost-btn" type="button" @click="logout">Thoát</button>
        <button v-else class="primary-btn" type="button" @click="navigate('auth')">Đăng nhập</button>
      </div>
    </header>

    <p v-if="notice" class="toast">{{ notice }}</p>

    <!-- Cinematic Player Overlay -->
    <CinematicPlayer v-if="showPlayer" :course="selectedCourse" @close="showPlayer = false" />

    <!-- In-Browser IDE Overlay -->
    <InBrowserIDE v-if="showIDE" :course="selectedCourse" @close="showIDE = false" />

    <!-- Swipeable Flashcards Overlay -->
    <SwipeableFlashcards v-if="showFlashcards" :course="selectedCourse" @close="showFlashcards = false" />

    <!-- Course Creator Studio Overlay -->
    <CourseCreatorStudio v-if="showStudio" @close="showStudio = false" />

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
              <img :src="courseImage(course)" :alt="course.title" :style="`view-transition-name: course-img-${course.id}`" />
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
            <img :src="courseImage(course)" :alt="course.title" :style="`view-transition-name: course-img-${course.id}`" />
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
          <img :src="courseImage(selectedCourse)" :alt="selectedCourse.title" :style="`view-transition-name: course-img-${selectedCourse.id}`" />
          <div>
            <button class="text-btn" style="display: block; margin-bottom: 32px; padding-left: 0;" type="button" @click="navigate('courses')">← Quay lại danh sách</button>
            <p class="eyebrow">{{ selectedCourse.category }} · {{ selectedCourse.level }}</p>
            <h1>{{ selectedCourse.title }}</h1>
            <p>{{ selectedCourse.description }}</p>
            <div class="detail-meta"><span>{{ selectedCourse.author }}</span><span>{{ selectedCourse.duration }}</span><span>{{ selectedCourse.rating }}/5</span><span>{{ selectedCourse.students }} học viên</span></div>
            <div class="card-actions action-grid">
              <!-- Primary action -->
              <button class="btn-hero" type="button" @click="openTool('video')">🎬 Xem bài học</button>
              
              <!-- Tools -->
              <div class="action-tools">
                <button class="btn-tool ide-tool" type="button" @click="openTool('ide')">⚡ Thực hành</button>
                <button class="btn-tool flashcard-tool" type="button" @click="openTool('flashcards')">📇 Ôn tập nhanh</button>
                <button class="btn-tool whiteboard-tool" type="button" @click="openTool('whiteboard')">🎨 Bảng vẽ nhóm</button>
                <button class="btn-tool podcast-tool" type="button" @click="openTool('podcast')">🎧 Nghe Podcast</button>
              </div>

              <!-- Secondary -->
              <div class="action-secondary">
                <button v-if="!isEnrolled" class="btn-outline" type="button" @click="enroll(selectedCourse.id)">Đăng ký học</button>
                <button v-else-if="!isCompleted" class="btn-outline" style="border-color: #10b981; color: #10b981;" type="button" @click="tryMarkCompleted">Đánh dấu hoàn thành</button>
                <button v-else class="btn-outline" style="border-color: #10b981; background: rgba(16, 185, 129, 0.1); color: #10b981; cursor: default;" type="button">🎉 Đã hoàn thành</button>
                
                <button class="btn-outline" type="button" @click="navigate('quiz')">Làm quiz</button>
              </div>
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
            <p class="eyebrow">Tài nguyên & Lộ trình</p>
            <h2>Học liệu Mở rộng</h2>
            <div class="roadmap-links">
              <div class="roadmap-group" v-for="group in activeRoadmap" :key="group.title">
                <h4>{{ group.title }}</h4>
                <ul>
                  <li v-for="link in group.links" :key="link.text">
                    <a :href="link.url" target="_blank">{{ link.text }}</a>
                  </li>
                </ul>
              </div>
            </div>
          </aside>
        </div>

        <!-- Live Comments Section (Realtime Event Sourcing) -->
        <div class="live-comments-section" style="margin-top: 48px;">
          <div class="section-heading">
            <p class="eyebrow">Real-time Discussion</p>
            <h2>Thảo luận trực tiếp</h2>
            <p>Hệ thống Backend Kafka CQRS: Gửi bình luận sẽ đẩy Event qua Kafka, người khác nhận được qua SSE ngay lập tức.</p>
          </div>
          
          <div class="comment-input-area" style="display:flex;gap:12px;margin-bottom:24px;">
            <input v-model="commentInput" @keyup.enter="submitComment" type="text" placeholder="Viết bình luận của bạn..." style="flex:1;padding:12px 16px;border-radius:var(--radius-sm);border:1px solid var(--border-glass);background:var(--bg-surface);color:var(--text-main);" />
            <button class="primary-btn" type="button" @click="submitComment">Gửi bình luận</button>
          </div>
          
          <div class="comments-list" style="display:flex;flex-direction:column;gap:16px;">
            <transition-group name="slide-up">
              <div v-for="(comment, index) in courseComments" :key="comment.id" class="comment-card" :style="{ padding:'16px', background:'var(--bg-surface)', border:'1px solid var(--border-glass)', borderRadius:'var(--radius-sm)', transition:'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)', animation: index === 0 ? 'pulse-border 2s ease-out' : 'none' }">
                <div style="display:flex; gap: 12px; align-items: flex-start;">
                  <div class="comment-avatar" style="width: 40px; height: 40px; border-radius: 50%; background: linear-gradient(135deg, var(--primary), #7c3aed); display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; flex-shrink: 0; box-shadow: 0 4px 10px rgba(124, 58, 237, 0.3);">
                    {{ comment.user_id.charAt(0).toUpperCase() }}
                  </div>
                  <div style="flex: 1;">
                    <div style="display:flex;justify-content:space-between;margin-bottom:4px;align-items:center;">
                      <div style="display:flex; align-items:center; gap: 8px;">
                        <strong style="color:var(--text-main); font-size: 1.05rem;">{{ comment.user_id }}</strong>
                        <span v-if="index === 0" style="background: rgba(16,185,129,0.15); color: #10b981; padding: 2px 8px; border-radius: 999px; font-size: 0.7rem; font-weight: bold; border: 1px solid rgba(16,185,129,0.3);">Vừa xong</span>
                      </div>
                      <small style="color:var(--text-muted); font-size: 0.8rem;">{{ new Date(comment.created_at).toLocaleString() }}</small>
                    </div>
                    <p style="margin:0;color:var(--text-main);font-size:0.95rem;line-height:1.5;">{{ comment.content }}</p>
                  </div>
                </div>
              </div>
            </transition-group>
            <p v-if="courseComments.length === 0" style="color:var(--text-muted);text-align:center;">Chưa có bình luận nào. Hãy là người đầu tiên!</p>
          </div>
        </div>
      </section>

      <style scoped>
      @keyframes pulse-border {
        0% { box-shadow: 0 0 0 0 rgba(124, 58, 237, 0.4); border-color: var(--primary); }
        70% { box-shadow: 0 0 0 10px rgba(124, 58, 237, 0); border-color: var(--border-glass); }
        100% { box-shadow: 0 0 0 0 rgba(124, 58, 237, 0); }
      }
      .slide-up-enter-active { transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275); }
      .slide-up-leave-active { transition: all 0.3s ease; position: absolute; }
      .slide-up-enter-from, .slide-up-leave-to { opacity: 0; transform: translateY(20px) scale(0.95); }
      .slide-up-move { transition: transform 0.4s ease; }
      </style>

      <section v-if="route === 'quiz'" class="content-section page-section quiz-layout">
        <!-- Header -->
        <div class="quiz-intro">
          <button class="text-btn" style="display:block;margin-bottom:24px;padding-left:0;" type="button" @click="navigate('course-detail', selectedCourseId)">← Quay lại khóa học</button>
          <p class="eyebrow">AI-Powered Quiz</p>
          <h1>Kiểm tra kiến thức cá nhân hóa</h1>
          <p>AI phân tích lịch sử học của bạn để tạo câu hỏi nhắm đúng điểm yếu cần cải thiện.</p>

          <!-- AI Reasoning Banner -->
          <div v-if="quizAIReasoning" class="ai-reasoning-banner">
            <span class="ai-reasoning-icon">🤖</span>
            <p>{{ quizAIReasoning }}</p>
          </div>

          <div class="quiz-meta-bar">
            <span class="quiz-meta-pill">{{ quizQuestions.length }} câu hỏi</span>
            <span class="quiz-meta-pill">{{ quizHistory.length }} lượt đã làm</span>
            <span v-if="quizWeakTopic || quizQuestions[0]?.topic_tag" class="quiz-meta-pill topic-pill">🎯 {{ quizWeakTopic || quizQuestions[0]?.topic_tag }}</span>
            <span v-if="quizQuestions[0]?.difficulty" :class="['quiz-meta-pill', 'diff-pill', quizQuestions[0].difficulty]">
              {{ quizQuestions[0].difficulty === 'easy' ? '⚪ Cơ bản' : quizQuestions[0].difficulty === 'hard' ? '🔴 Nâng cao' : '🟡 Trung bình' }}
            </span>
            <button class="ai-gen-btn" type="button" @click="generateAutoQuiz" :disabled="isGeneratingQuiz">
              <span v-if="isGeneratingQuiz" class="gen-spinner"></span>
              <span>{{ isGeneratingQuiz ? 'Đang phân tích...' : '✨ Tạo bộ 5 câu AI' }}</span>
            </button>
          </div>
          <p class="quiz-keyboard-hint">💻 Tip: Bấm phím <kbd>1</kbd><kbd>2</kbd><kbd>3</kbd><kbd>4</kbd> để chọn, <kbd>Enter</kbd> để xác nhận</p>
        </div>

        <!-- Active Question -->
        <div v-if="!quizFinished" class="quiz-card-v2">
          <!-- Top bar: progress + timer + streak -->
          <div class="quiz-top-bar">
            <div class="quiz-progress-track" style="flex:1">
              <div class="quiz-progress-fill" :style="{ width: `${(quizIndex / quizQuestions.length) * 100}%` }"></div>
            </div>
            <!-- Timer -->
            <div :class="['quiz-timer', { 'danger': quizTimeLeft <= 10 && !quizAnswered }]">
              <svg width="36" height="36" viewBox="0 0 36 36">
                <circle cx="18" cy="18" r="15" fill="none" stroke="var(--border-glass)" stroke-width="3"/>
                <circle cx="18" cy="18" r="15" fill="none" stroke="currentColor" stroke-width="3"
                  stroke-dasharray="94.2" :stroke-dashoffset="94.2 * (1 - quizTimeLeft / 30)"
                  stroke-linecap="round" transform="rotate(-90 18 18)"
                  style="transition: stroke-dashoffset 1s linear;"/>
              </svg>
              <span class="timer-number">{{ quizTimeLeft }}</span>
            </div>
            <!-- Streak -->
            <div v-if="quizStreak >= 2" class="quiz-streak">
              <span>🔥 {{ quizStreak }}x</span>
            </div>
          </div>
          <div class="quiz-q-header">
            <small class="quiz-q-counter">Câu {{ quizIndex + 1 }} / {{ quizQuestions.length }}</small>
          </div>
          <h2 class="quiz-question-text">{{ quizQuestions[quizIndex].q }}</h2>

          <!-- Options -->
          <div class="quiz-options-grid">
            <button
              v-for="(option, idx) in quizQuestions[quizIndex].options"
              :key="option"
              class="quiz-option-btn"
              :class="{
                'selected': !quizAnswered && selectedAnswer === option,
                'correct': quizAnswered && option === quizQuestions[quizIndex].a,
                'wrong': quizAnswered && selectedAnswer === option && option !== quizQuestions[quizIndex].a,
                'dimmed': quizAnswered && option !== quizQuestions[quizIndex].a && selectedAnswer !== option
              }"
              :disabled="quizAnswered"
              @click="selectedAnswer = option"
            >
              <span class="option-letter">{{ ['A', 'B', 'C', 'D'][idx] }}</span>
              <span class="option-text">{{ option }}</span>
              <span v-if="quizAnswered && option === quizQuestions[quizIndex].a" class="option-icon">✓</span>
              <span v-else-if="quizAnswered && selectedAnswer === option && option !== quizQuestions[quizIndex].a" class="option-icon wrong-icon">✗</span>
            </button>
          </div>

          <!-- Explanation panel (after answering) -->
          <Transition name="slide-up">
            <div v-if="quizAnswered" :class="['quiz-explanation', quizAnswers[quizAnswers.length-1]?.isRight ? 'correct-explanation' : 'wrong-explanation']">
              <div class="explanation-header">
                <strong>{{ quizAnswers[quizAnswers.length-1]?.isRight ? '✓ Chính xác!' : '✗ Chưa đúng' }}</strong>
                <span v-if="!quizAnswers[quizAnswers.length-1]?.isRight" class="explanation-correct-label">Đáp án đúng: {{ quizQuestions[quizIndex].a }}</span>
              </div>
              <p v-if="quizQuestions[quizIndex].explanation" class="explanation-body">{{ quizQuestions[quizIndex].explanation }}</p>
              <button class="next-question-btn" @click="nextQuestion">
                {{ quizIndex === quizQuestions.length - 1 ? 'Xem kết quả' : 'Câu tiếp theo →' }}
              </button>
            </div>
          </Transition>

          <!-- Submit button (before answering) -->
          <button v-if="!quizAnswered" class="quiz-submit-btn" type="button" @click="answerQuiz" :disabled="!selectedAnswer">
            Xác nhận đáp án
          </button>
        </div>

        <!-- Result Screen -->
        <div v-else class="quiz-result-v2">
          <div class="result-circle" :class="{ 'perfect': quizScore === quizQuestions.length, 'pass': quizScore >= quizQuestions.length * 0.6 }">
            <span class="result-score">{{ quizScore }}/{{ quizQuestions.length }}</span>
            <span class="result-label">{{ quizScore === quizQuestions.length ? '🌟 Hoàn hảo!' : quizScore >= quizQuestions.length * 0.6 ? '🍊 Tốt lắm!' : '📚 Cần ôn thêm' }}</span>
          </div>

          <!-- Stats row -->
          <div class="result-stats-row">
            <div class="result-stat">
              <span class="stat-num">{{ Math.round((quizScore / quizQuestions.length) * 100) }}%</span>
              <span class="stat-label">Tỷ lệ đúng</span>
            </div>
            <div class="result-stat">
              <span class="stat-num">🔥 {{ quizMaxStreak }}</span>
              <span class="stat-label">Streak cao nhất</span>
            </div>
            <div class="result-stat">
              <span class="stat-num">{{ quizAnswers.filter(a => a.isRight).length }}</span>
              <span class="stat-label">Câu đúng</span>
            </div>
            <div class="result-stat">
              <span class="stat-num">{{ quizAnswers.filter(a => !a.isRight).length }}</span>
              <span class="stat-label">Cần xem lại</span>
            </div>
          </div>

          <div class="result-breakdown">
            <h3>Chi tiết từng câu</h3>
            <div class="breakdown-list">
              <div v-for="(ans, i) in quizAnswers" :key="i" :class="['breakdown-item', ans.isRight ? 'right' : 'wrong']">
                <span class="breakdown-icon">{{ ans.isRight ? '✓' : '✗' }}</span>
                <div class="breakdown-body">
                  <p class="breakdown-q">{{ ans.question }}</p>
                  <p v-if="!ans.isRight" class="breakdown-correct">Đáp án đúng: <strong>{{ ans.correct }}</strong></p>
                  <p v-if="ans.explanation" class="breakdown-exp">{{ ans.explanation }}</p>
                </div>
              </div>
            </div>
          </div>

          <div class="result-actions">
            <button class="primary-btn" type="button" @click="restartQuiz">Làm lại từ đầu</button>
            <button v-if="quizAnswers.filter(a => !a.isRight).length > 0" class="btn-outline" type="button" @click="retryWrongAnswers">Làm lại câu sai</button>
            <button class="ai-gen-btn" type="button" @click="generateAutoQuiz" :disabled="isGeneratingQuiz">
              {{ isGeneratingQuiz ? 'Đang tạo...' : 'Tạo câu hỏi AI mới' }}
            </button>
          </div>
          
          <p v-if="isSyncing" style="color:var(--text-muted);font-size:0.85rem;text-align:center;">Đang đồng bộ điểm lên Cloud...</p>
          <p v-if="syncSuccess" style="color:#10b981;font-size:0.85rem;text-align:center;">✓ Đã đồng bộ điểm lên PostgreSQL Cloud!</p>
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
          <p class="eyebrow">Account</p><h1>{{ authMode === 'login' ? 'Chào mừng quay lại' : 'Tạo tài khoản học tập' }}</h1><p>Đăng nhập bằng sinh trắc học để bảo mật tuyệt đối và loại bỏ hoàn toàn mật khẩu.</p>
        </div>
        <form v-if="authMode === 'login'" class="form-card" @submit.prevent="loginMagicLink">
          <input v-model="loginForm.email" type="email" placeholder="Email" />
          
          <div class="passkey-actions flex flex-col gap-3 mt-4 w-full">
            <button class="primary-btn relative overflow-hidden group w-full" type="button" @click="login">
              <span class="relative z-10 flex items-center justify-center gap-2">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="M9 12l2 2 4-4"/></svg>
                Tiếp tục bằng Passkey 🛡️
              </span>
              <div class="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-1000"></div>
            </button>
            <button class="secondary-btn w-full" type="submit">Gửi Magic Link 📧</button>
          </div>
          
          <button class="text-btn mt-4 w-full text-center" type="button" @click="authMode = 'register'">Chưa có tài khoản? Đăng ký ngay</button>
        </form>
        <form v-else class="form-card" @submit.prevent="register">
          <input v-model="registerForm.name" placeholder="Họ tên" />
          <input v-model="registerForm.email" type="email" placeholder="Email" />
          
          <div class="passkey-actions flex flex-col gap-3 mt-4 w-full">
            <button class="primary-btn relative overflow-hidden group w-full" type="submit">
              <span class="relative z-10 flex items-center justify-center gap-2">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="M9 12l2 2 4-4"/></svg>
                Tạo Passkey (FaceID / Vân tay) 🛡️
              </span>
              <div class="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-1000"></div>
            </button>
          </div>
          
          <button class="text-btn mt-4 w-full text-center" type="button" @click="authMode = 'login'">Đã có tài khoản? Đăng nhập bằng Passkey</button>
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
                <div class="stat-header"><span>Tiến độ hoàn thành</span><span>{{ completedIds.length > 0 ? '100%' : '0%' }}</span></div>
                <div class="animated-progress"><div class="animated-progress-fill" :style="`width: ${completedIds.length > 0 ? 100 : 0}%`"></div></div>
              </div>
              <div class="stat-box">
                <div class="stat-header"><span>Điểm tích lũy</span><span>{{ quizHistory.length > 0 ? '80%' : '0%' }}</span></div>
                <div class="animated-progress"><div class="animated-progress-fill" :style="`width: ${quizHistory.length > 0 ? 80 : 0}%`"></div></div>
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
                <span>Tiến độ: {{ completedIds.includes(enrolledIds[enrolledIds.length - 1]) ? '100%' : '15%' }}</span>
              </div>
              <div class="progress-bar"><div class="progress-fill" :style="`width: ${completedIds.includes(enrolledIds[enrolledIds.length - 1]) ? 100 : 15}%;`"></div></div>
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
          <div class="bento-item bento-security rich-panel">
            <p class="eyebrow">Bảo mật đa tầng</p>
            <h2>Passkey Auth 🛡️</h2>
            <div class="mt-4 p-4 rounded-xl border border-[var(--border-glass)] bg-[var(--bg-glass)]">
              <div class="flex items-center gap-3 mb-2">
                <div class="w-2 h-2 rounded-full bg-green-500 shadow-[0_0_8px_#22c55e]"></div>
                <strong class="text-sm">Bảo vệ bằng Sinh trắc học</strong>
              </div>
              <p class="text-xs text-muted">Tài khoản của bạn hiện đang được liên kết với một cặp khóa public/private mã hóa phần cứng. EduPress không lưu bất kỳ mật khẩu nào của bạn.</p>
            </div>
          </div>

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

          <!-- 6. Trophy Room (Span 4) -->
          <div class="bento-item bento-courses">
            <TrophyRoom
              :completed-courses="completedIds"
              :enrolled-courses="enrolledIds"
              :user-name="currentUser.name || currentUser.email"
              :courses="courses"
            />
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

    <!-- Whiteboard Sandbox -->
    <WhiteboardPro 
      v-if="showWhiteboard" 
      :current-user="currentUser || { name: currentUserEmail || 'Ẩn danh' }" 
      @close="showWhiteboard = false" 
    />

    <!-- Podcast Sandbox -->
    <PodcastPlayer
      v-if="showPodcast"
      :courseTitle="selectedCourse.title"
      @close="showPodcast = false"
    />
    
    <ConfettiExplosion v-if="showConfetti" />
    
    <!-- Completion Conditions Modal -->
    <div v-if="showCompletionModal" class="completion-modal-overlay">
      <div class="completion-modal-card">
        <button class="close-btn" @click="showCompletionModal = false">✕</button>
        <h2>Chưa đủ điều kiện hoàn thành 🎓</h2>
        <p>Để nhận chứng chỉ khóa học <strong>{{ selectedCourse.title }}</strong>, bạn cần hoàn thành các tiêu chí sau:</p>
        
        <ul class="condition-list">
          <li v-for="cond in completionConditions" :key="cond.id" :class="{ 'is-met': cond.met }">
            <span class="icon">{{ cond.met ? '✅' : '⏳' }}</span>
            <span class="text">{{ cond.name }}</span>
          </li>
        </ul>
        
        <button class="primary-btn mt-6 w-full" style="width: 100%; margin-top: 24px;" @click="showCompletionModal = false">Tiếp tục học</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.roadmap-links {
  display: flex;
  flex-direction: column;
  gap: 24px;
  margin-top: 16px;
}

.roadmap-group h4 {
  font-size: 1rem;
  font-weight: 700;
  margin-bottom: 12px;
  color: var(--primary);
  display: flex;
  align-items: center;
  gap: 8px;
}

.roadmap-group ul {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.roadmap-group li a {
  display: block;
  padding: 10px 16px;
  background: var(--bg-surface);
  border: 1px solid var(--border-glass);
  border-radius: var(--radius-sm);
  color: var(--text-main);
  text-decoration: none;
  font-size: 0.9rem;
  font-weight: 600;
  transition: all 0.3s ease;
}

.roadmap-group li a:hover {
  background: rgba(99, 102, 241, 0.1);
  border-color: var(--primary);
  color: var(--primary);
  transform: translateX(5px);
}
</style>
