<script setup>
import { computed, defineAsyncComponent, onMounted, ref } from 'vue'
import { categories, courseRoadmaps, courses, defaultQuizQuestions, learningSteps, navItems, posts, testimonials } from './data/learningContent'

const clientOnlyComponent = (loader) => import.meta.client ? defineAsyncComponent(loader) : null

const AICompanion = clientOnlyComponent(() => import('./components/AICompanion.vue'))
const BlogPage = defineAsyncComponent(() => import('./components/BlogPage.vue'))
const CinematicPlayer = clientOnlyComponent(() => import('./components/CinematicPlayer.vue'))
const ContactPage = defineAsyncComponent(() => import('./components/ContactPage.vue'))
const ContentOperationsDashboard = clientOnlyComponent(() => import('./components/ContentOperationsDashboard.vue'))
const InBrowserIDE = clientOnlyComponent(() => import('./components/InBrowserIDE.vue'))
const LearningUniverse = clientOnlyComponent(() => import('./components/LearningUniverse.vue'))
const PodcastPlayer = clientOnlyComponent(() => import('./components/PodcastPlayer.vue'))
const SwipeableFlashcards = clientOnlyComponent(() => import('./components/SwipeableFlashcards.vue'))
const TrophyRoom = clientOnlyComponent(() => import('./components/TrophyRoom.vue'))
const WhiteboardPro = clientOnlyComponent(() => import('./components/WhiteboardPro.vue'))

const config = useRuntimeConfig()
const { asset, generatedAsset, courseImage } = useAssetPaths()

const contentCourses = ref([...courses])
const contentPosts = ref([...posts])
const backendQuizQuestions = ref([])
const quizQuestions = ref([...defaultQuizQuestions])

const search = ref('')
const apiStatus = ref('checking')
const authMode = ref('login')
const loginForm = ref({ email: '' })
const registerForm = ref({ name: '', email: '' })
const profileForm = ref({ name: '', phone: '', school: '', bio: '' })
const contactForm = ref({ name: '', email: '', message: '' })
const notice = ref('')
const isMounted = ref(false)
const showPlayer = ref(false)
const showIDE = ref(false)
const showFlashcards = ref(false)
const showOperationsDashboard = ref(false)
const showWhiteboard = ref(false)
const showAICompanion = ref(false)

const { data: users, saveData: saveUsersDB, removeData: removeUsersDB } = useLocalSync('users', [])
const { data: currentUserEmail, saveData: saveEmailDB, removeData: removeEmailDB } = useLocalSync('loggedInUser', '')
const { data: quizHistory, saveData: saveQuizHistoryDB, removeData: removeQuizHistoryDB } = useLocalSync('quizHistory', [])
const { data: courseInteractions, saveData: saveInteractionsDB, removeData: removeInteractionsDB } = useLocalSync('courseInteractions', {})
const { route, selectedCourseId, navigate, syncHashRoute } = useHashNavigation({
  onCourseDetail: (courseId) => {
    loadCourseComments(courseId)
    connectSSE(courseId)
  },
  onLeaveCourseDetail: () => {
    if (sseConnection.value) {
      sseConnection.value.close()
      sseConnection.value = null
    }
  },
})

const activeRoadmap = computed(() => courseRoadmaps[selectedCourseId.value] || courseRoadmaps.web)

const { isOnline, networkState } = useNetworkStatus()
const currentUser = computed(() => users.value.find((user) => user.email === currentUserEmail.value))
const selectedCourse = computed(() => contentCourses.value.find((course) => course.id === selectedCourseId.value) || contentCourses.value[0])
const enrolledIds = computed(() => currentUser.value?.registeredCourses || [])
const pendingEnrollmentIds = computed(() => currentUser.value?.pendingEnrollments || [])
const completedIds = computed(() => currentUser.value?.completedCourses || [])

const quizIndex = ref(0)
const quizScore = ref(0)
const selectedAnswer = ref('')
const quizFinished = ref(false)
const showPodcast = ref(false)
const featuredCourse = computed(() => contentCourses.value[2] || contentCourses.value[0])
const filteredCourses = computed(() => {
  const keyword = search.value.trim().toLowerCase()
  if (!keyword) return contentCourses.value
  return contentCourses.value.filter((course) => [course.title, course.author, course.category, course.level, course.description].join(' ').toLowerCase().includes(keyword))
})

function normalizeCourse(course, index) {
  const fallback = courses[index] || courses[0]
  return {
    id: course.slug || String(course.id),
    title: course.title || fallback.title,
    author: course.author || fallback.author,
    category: course.category || fallback.category,
    image: course.image || course.image_url || fallback.image,
    level: course.level || fallback.level,
    lessons: Number(course.lessons ?? fallback.lessons ?? 0),
    duration: course.duration || fallback.duration,
    rating: Number(course.rating ?? fallback.rating ?? 0),
    students: Number(course.students ?? fallback.students ?? 0),
    progress: Number(course.progress ?? fallback.progress ?? 0),
    tag: course.tag || fallback.tag,
    access_type: course.access_type || fallback.access_type || (Number(course.price_cents || 0) > 0 ? 'paid' : 'free'),
    price_cents: Number(course.price_cents ?? fallback.price_cents ?? 0),
    currency: course.currency || fallback.currency || 'VND',
    manual_enrollment_enabled: course.manual_enrollment_enabled ?? fallback.manual_enrollment_enabled ?? true,
    description: course.description || fallback.description,
    outcomes: Array.isArray(course.outcomes) && course.outcomes.length ? course.outcomes : fallback.outcomes,
    syllabus: Array.isArray(course.syllabus) && course.syllabus.length ? course.syllabus : fallback.syllabus,
    resources: Array.isArray(course.resources) && course.resources.length ? course.resources : fallback.resources,
  }
}

function normalizeQuizQuestion(question) {
  return {
    q: question.q || question.question || question.title,
    a: question.a || question.correct_answer,
    options: Array.isArray(question.options) ? question.options : [],
    explanation: question.explanation || '',
    difficulty: question.difficulty || 'medium',
    topic_tag: question.topic_tag || question.topic || '',
  }
}

async function fetchJson(path) {
  const response = await fetch(`${config.public.apiBase}${path}`)
  if (!response.ok) throw new Error(`Request failed: ${path}`)
  return response.json()
}

function captureFrontendError(error, context = {}) {
  if (!import.meta.client) return
  const payload = {
    message: error?.message || String(error),
    stack: error?.stack || '',
    route: window.location.hash || window.location.pathname,
    source: 'edupress-client',
    context,
  }
  fetch(`${config.public.apiBase}/api/monitoring/frontend-error`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  }).catch(() => {})
}

async function loadBackendContent() {
  const [courseData, postData, quizData] = await Promise.all([
    fetchJson('/api/courses'),
    fetchJson('/api/content/blog-posts'),
    fetchJson('/api/content/quiz-questions'),
  ])

  if (Array.isArray(courseData) && courseData.length) {
    contentCourses.value = courseData.map(normalizeCourse)
    if (!contentCourses.value.some((course) => course.id === selectedCourseId.value)) {
      selectedCourseId.value = contentCourses.value[0].id
    }
  }
  if (Array.isArray(postData) && postData.length) {
    contentPosts.value = postData
  }
  if (Array.isArray(quizData) && quizData.length) {
    backendQuizQuestions.value = quizData.map(normalizeQuizQuestion).filter((question) => question.q && question.a && question.options.length)
    if (backendQuizQuestions.value.length) quizQuestions.value = [...backendQuizQuestions.value]
  }
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
const themeLabel = computed(() => ({ light: 'Sáng', dark: 'Tối', oled: 'Đêm' }[theme.value] || 'Sáng'))
const apiStatusLabel = computed(() => {
  if (apiStatus.value === 'online') return 'Đã kết nối'
  if (apiStatus.value === 'checking') return 'Đang đồng bộ'
  return 'Dữ liệu mẫu'
})
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

// ── Realtime Comments Logic ──────────────────────────────────────────
const courseComments = ref([])
const commentInput = ref("")
const sseConnection = ref(null)

async function loadCourseComments(courseId) {
  try {
    const res = await fetch(`${config.public.apiBase}/api/comments/${courseId}`)
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
    await fetch(`${config.public.apiBase}/api/comments`, {
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
  sseConnection.value = new EventSource(`${config.public.apiBase}/api/stream`)
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
    
    saveUsers([...users.value, { ...payload, passkeyId: passkeyId, role: 'student', registeredCourses: [], pendingEnrollments: [], completedCourses: [] }])
    saveEmailDB(payload.email)
    registerForm.value = { name: '', email: '' }
    loginForm.value = { email: '' }
    syncProfileForm()
    navigate('profile')
    setNotice('Đăng ký bằng sinh trắc học thành công')
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
    setNotice('Đăng nhập sinh trắc học thành công')
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
    setNotice('Đã xác thực qua Magic Link')
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


function buildLearnerDataExport() {
  return {
    exported_at: new Date().toISOString(),
    source: 'EduPress browser profile',
    user: currentUser.value,
    quiz_history: quizHistory.value,
    course_interactions: courseInteractions.value,
    storage_locations: {
      browser: ['IndexedDB: users', 'IndexedDB: loggedInUser', 'IndexedDB: quizHistory', 'IndexedDB: courseInteractions'],
      backend: ['PostgreSQL: users, enrollments, quiz_history', 'MongoDB: comments_read_model'],
    },
    retention_policy: {
      local_browser_storage: 'Browser demo data stays until the learner clears local data or deletes this local profile.',
      backend_storage: 'Production account, enrollment, quiz, and comment data is retained while the account is active and removed on account deletion.',
      backups: 'Production backups need a documented rotation schedule and restricted operational access.',
    },
  }
}

function exportLearnerData() {
  if (!currentUser.value || !import.meta.client) return navigate('auth')
  const blob = new Blob([JSON.stringify(buildLearnerDataExport(), null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const anchor = document.createElement('a')
  anchor.href = url
  anchor.download = `edupress-data-${currentUser.value.email || 'learner'}.json`
  anchor.click()
  URL.revokeObjectURL(url)
  setNotice('Da tao file xuat du lieu cuc bo.')
}

async function clearLocalLearnerData() {
  if (!import.meta.client) return
  const confirmed = window.confirm('Xoa ho so, lich su quiz va tuong tac khoa hoc luu trong trinh duyet nay?')
  if (!confirmed) return
  await Promise.all([removeUsersDB(), removeEmailDB(), removeQuizHistoryDB(), removeInteractionsDB()])
  localStorage.removeItem('quizHistory')
  profileForm.value = { name: '', phone: '', school: '', bio: '' }
  navigate('home')
  setNotice('Da xoa du lieu cuc bo tren trinh duyet nay.')
}

function isPaidCourse(course) {
  return course?.access_type === 'paid' || Number(course?.price_cents || 0) > 0
}

function formatCoursePrice(course) {
  if (!isPaidCourse(course)) return 'Miễn phí'
  const amount = Number(course.price_cents || 0) / 100
  return new Intl.NumberFormat('vi-VN', {
    style: 'currency',
    currency: course.currency || 'VND',
    maximumFractionDigits: 0,
  }).format(amount)
}

function courseEnrollmentState(course) {
  if (!course) return 'unknown'
  if ((currentUser.value?.registeredCourses || []).includes(course.id)) return 'enrolled'
  if ((currentUser.value?.pendingEnrollments || []).includes(course.id)) return 'pending'
  return isPaidCourse(course) ? 'paid_required' : 'free'
}

function enrollmentButtonLabel(course) {
  const state = courseEnrollmentState(course)
  if (state === 'enrolled') return 'Đang học'
  if (state === 'pending') return 'Chờ duyệt'
  if (state === 'paid_required') return 'Yêu cầu ghi danh'
  return 'Đăng ký miễn phí'
}

function canAccessCourse(course) {
  const state = courseEnrollmentState(course)
  return state === 'free' || state === 'enrolled'
}

function blockPaidCourseAccess(course) {
  if (canAccessCourse(course)) return false
  if (!currentUser.value) {
    setNotice('Đăng nhập để yêu cầu ghi danh khóa học trả phí.')
    navigate('auth')
    return true
  }
  if (courseEnrollmentState(course) === 'pending') {
    setNotice('Yêu cầu ghi danh đang chờ duyệt thủ công.')
    return true
  }
  setNotice('Khóa trả phí cần được duyệt ghi danh trước khi học.')
  return true
}


function enroll(courseId) {
  if (!currentUser.value) {
    setNotice('Bạn cần đăng nhập để đăng ký khóa học.')
    return navigate('auth')
  }
  const course = contentCourses.value.find((item) => item.id === courseId)
  const state = courseEnrollmentState(course)
  if (state === 'enrolled') return setNotice('Bạn đang học khóa này.')
  if (state === 'pending') return setNotice('Yêu cầu ghi danh đang chờ duyệt.')
  saveUsers(users.value.map((user) => {
    if (user.email !== currentUserEmail.value) return user
    if (isPaidCourse(course)) {
      return { ...user, pendingEnrollments: [...new Set([...(user.pendingEnrollments || []), courseId])] }
    }
    return { ...user, registeredCourses: [...new Set([...(user.registeredCourses || []), courseId])] }
  }))
  setNotice(isPaidCourse(course) ? 'Đã gửi yêu cầu ghi danh. EduPress sẽ duyệt thủ công.' : 'Đã đăng ký khóa học.')
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

const isEnrollmentPending = computed(() => {
  if (!currentUser.value || !selectedCourse.value) return false
  return (currentUser.value.pendingEnrollments || []).includes(selectedCourse.value.id)
})

const isCompleted = computed(() => {
  if (!currentUser.value || !selectedCourse.value) return false
  return (currentUser.value.completedCourses || []).includes(selectedCourse.value.id)
})

const canManageContent = computed(() => ['instructor', 'admin'].includes(currentUser.value?.role))

function updateManagedCourses(nextCourses) {
  contentCourses.value = [...nextCourses]
}

function updateManagedPosts(nextPosts) {
  contentPosts.value = [...nextPosts]
}

function updateManagedQuizQuestions(nextQuestions) {
  backendQuizQuestions.value = [...nextQuestions]
  quizQuestions.value = [...nextQuestions]
}

function updateManagedComments(nextComments) {
  courseComments.value = [...nextComments]
}

function updateManagedUsers(nextUsers) {
  saveUsers([...nextUsers])
}

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
const syncError = ref('')
const pendingQuizSync = ref(null)

async function syncQuizHistoryToDB(score, total, topic, maxStreak) {
  pendingQuizSync.value = { score, total, topic, maxStreak }
  isSyncing.value = true
  syncError.value = ''
  syncSuccess.value = false
  try {
    const res = await fetch(`${config.public.apiBase}/api/quiz/sync`, {
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
    if (!res.ok || !data.success) {
      const message = data?.detail?.message || data?.message || 'Không thể đồng bộ điểm. Vui lòng thử lại.'
      throw new Error(message)
    }
    if (data.success) {
      pendingQuizSync.value = null
      syncSuccess.value = true
      setTimeout(() => syncSuccess.value = false, 3000)
    }
  } catch (e) {
    syncError.value = e?.message || 'Không thể đồng bộ điểm. Vui lòng thử lại.'
  } finally {
    isSyncing.value = false
  }
}

function retryQuizSync() {
  if (!pendingQuizSync.value || isSyncing.value) return
  const { score, total, topic, maxStreak } = pendingQuizSync.value
  syncQuizHistoryToDB(score, total, topic, maxStreak)
}

async function launchCelebration() {
  if (!import.meta.client) return
  const { default: confetti } = await import('canvas-confetti')
  confetti({ particleCount: 150, spread: 70, origin: { y: 0.6 } })
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
    
    if (score === total) launchCelebration()

    saveQuizHistoryDB([
      { score, total, topic, maxStreak: quizMaxStreak.value, date: new Date().toISOString() },
      ...quizHistory.value
    ])

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
  quizQuestions.value = backendQuizQuestions.value.length ? [...backendQuizQuestions.value] : [...defaultQuizQuestions]
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
    const res = await fetch(`${config.public.apiBase}/api/quiz/generate`, {
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
      setNotice('Lỗi khi tạo quiz.')
    }
  } catch {
    setNotice('Không thể kết nối backend. Dùng bộ câu hỏi mẫu.')
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
  if (blockPaidCourseAccess(selectedCourse.value)) return
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
  if (blockPaidCourseAccess(selectedCourse.value)) return
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

onMounted(async () => {
  window.addEventListener('error', (event) => {
    captureFrontendError(event.error || event.message, { type: 'window_error', filename: event.filename, line: event.lineno })
  })
  window.addEventListener('unhandledrejection', (event) => {
    captureFrontendError(event.reason || 'Unhandled promise rejection', { type: 'unhandled_rejection' })
  })

  isMounted.value = true
  syncHashRoute()
  
  syncProfileForm()
  try {
    const response = await fetch(`${config.public.apiBase}/health`)
    if (!response.ok) throw new Error('Health check failed')
    await loadBackendContent()
    apiStatus.value = 'online'
  } catch {
    apiStatus.value = 'offline'
  }
})
</script>

<template>
  <div :class="['app-frame', { 'is-offline': networkState === 'offline' }]" :data-mounted="isMounted">
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

    <button v-if="!showAICompanion" class="ai-companion-lite" type="button" @click="showAICompanion = true">Hỗ trợ</button>
    <AICompanion v-else initial-open />
    <header class="site-header">
      <button class="brand" type="button" data-testid="brand-home" @click="navigate('home')">
        <img :src="generatedAsset('edupress-logo.svg')" alt="EduPress" />
        <span class="logo-text">EduPress</span>
      </button>

      <nav class="nav-links" aria-label="Primary">
        <button v-for="item in navItems" :key="item.id" :class="{ active: route === item.id }" type="button" :data-testid="`nav-${item.id}`" @click="navigate(item.id)">{{ item.label }}</button>
        <button type="button" data-testid="nav-quiz" :class="{ active: route === 'quiz' }" @click="navigate('quiz')">Quiz</button>
      </nav>

      <div class="header-actions">
        <button
          class="theme-toggle"
          type="button"
          @click="cycleTheme"
          title="Đổi giao diện"
        >
          <span class="theme-dot" aria-hidden="true"></span>
          <span>{{ themeLabel }}</span>
        </button>
        <span :class="['status-pill', apiStatus]">Dữ liệu: {{ apiStatusLabel }}</span>
        <button v-if="canManageContent" class="primary-btn" type="button" @click="showOperationsDashboard = true">Quản trị nội dung</button>
        <button class="practice-btn" type="button" @click="showIDE = true">Thực hành</button>
        <button v-if="currentUser" class="user-chip" type="button" @click="navigate('profile')">{{ currentUser.name || currentUser.email }}</button>
        <button v-if="currentUser" class="logout-link" type="button" @click="logout">Đăng xuất</button>
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
    <ContentOperationsDashboard
      v-if="showOperationsDashboard"
      :courses="contentCourses"
      :posts="contentPosts"
      :quiz-questions="quizQuestions"
      :comments="courseComments"
      :users="users"
      :current-user="currentUser"
      @close="showOperationsDashboard = false"
      @update-courses="updateManagedCourses"
      @update-posts="updateManagedPosts"
      @update-quiz-questions="updateManagedQuizQuestions"
      @update-comments="updateManagedComments"
      @update-users="updateManagedUsers"
      @notice="setNotice"
    />

    <main>
      <template v-if="route === 'home'">
        <section class="hero-section" data-testid="home-page">
          <div class="hero-copy">
            <p class="eyebrow">Online learning platform</p>
            <h1>Học công nghệ theo lộ trình rõ ràng, có quiz và tiến trình thật.</h1>
            <p>EduPress kết hợp khóa học, bài kiểm tra, hồ sơ học tập và nội dung tin tức để tạo một trải nghiệm LMS đầy đủ hơn bản HTML cũ.</p>
            <div class="hero-actions">
              <button class="primary-btn" type="button" data-testid="home-browse-courses" @click="navigate('courses')">Khám phá khóa học</button>
              <button class="secondary-btn" type="button" data-testid="home-featured-course" @click="navigate('course-detail', featuredCourse.id)">Xem khóa nổi bật</button>
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
              <strong>Bài kiểm tra</strong>
              <span>Chấm điểm sau khi nộp</span>
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
            <article v-for="course in contentCourses.slice(0, 3)" :key="course.id" class="course-card featured-card">
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

      <section v-if="route === 'courses'" class="content-section page-section" data-testid="courses-page">
        <div class="page-hero compact-hero">
          <div>
            <p class="eyebrow">Course catalog</p>
            <h1>Danh sách khóa học</h1>
            <p>Tìm khóa học theo lĩnh vực, cấp độ hoặc giảng viên. Mỗi khóa có lộ trình, tài nguyên và quiz liên quan.</p>
          </div>
          <input v-model="search" type="search" data-testid="course-search" placeholder="Tìm AI, Web, OOP..." />
        </div>
        
        <LearningUniverse :courses="filteredCourses" @selectCourse="navigate('course-detail', $event)" />

        <div class="course-list">
          <article v-for="course in filteredCourses" :key="course.id" class="course-row-card" :data-testid="`course-card-${course.id}`">
            <img :src="courseImage(course)" :alt="course.title" :style="`view-transition-name: course-img-${course.id}`" />
            <div class="course-row-content">
              <div class="card-topline"><span>{{ course.category }}</span><small>{{ course.level }}</small></div>
              <h2>{{ course.title }}</h2>
              <p>{{ course.description }}</p>
              <div class="course-meta-row"><span>{{ course.author }}</span><span>{{ course.lessons }} bài học</span><span>{{ course.students }} học viên</span></div>
              <div class="course-access-row">
                <span :class="['access-badge', courseEnrollmentState(course)]">{{ enrollmentButtonLabel(course) }}</span>
                <strong>{{ formatCoursePrice(course) }}</strong>
              </div>
              <div class="card-actions">
                <button class="primary-btn" type="button" :data-testid="`course-detail-${course.id}`" @click="navigate('course-detail', course.id)">Xem chi tiết</button>
                <button class="secondary-btn" type="button" :data-testid="`course-enroll-${course.id}`" @click="enroll(course.id)">{{ enrollmentButtonLabel(course) }}</button>
              </div>
            </div>
          </article>
        </div>
      </section>

      <section v-if="route === 'course-detail'" class="content-section page-section detail-page" data-testid="course-detail-page">
        <div class="detail-hero">
          <img :src="courseImage(selectedCourse)" :alt="selectedCourse.title" :style="`view-transition-name: course-img-${selectedCourse.id}`" />
          <div>
            <button class="text-btn" style="display: block; margin-bottom: 32px; padding-left: 0;" type="button" @click="navigate('courses')">Quay lại danh sách</button>
            <p class="eyebrow">{{ selectedCourse.category }} · {{ selectedCourse.level }}</p>
            <h1>{{ selectedCourse.title }}</h1>
            <p>{{ selectedCourse.description }}</p>
            <div class="detail-meta"><span>{{ selectedCourse.author }}</span><span>{{ selectedCourse.duration }}</span><span>{{ selectedCourse.rating }}/5</span><span>{{ selectedCourse.students }} học viên</span><span>{{ formatCoursePrice(selectedCourse) }}</span></div>
            <div class="course-access-row detail-access">
              <span :class="['access-badge', courseEnrollmentState(selectedCourse)]">{{ enrollmentButtonLabel(selectedCourse) }}</span>
              <small v-if="isEnrollmentPending">Đội ngũ EduPress sẽ duyệt thủ công trước khi mở nội dung trả phí.</small>
              <small v-else-if="isPaidCourse(selectedCourse) && !isEnrolled">Khóa trả phí cần được ghi danh trước khi mở bài học, tài nguyên và công cụ học.</small>
            </div>
            <div class="card-actions action-grid">
              <!-- Primary action -->
              <button class="btn-hero" type="button" @click="openTool('video')">Xem bài học</button>
              
              <!-- Tools -->
              <div class="action-tools">
                <button class="btn-tool ide-tool" type="button" @click="openTool('ide')">Thực hành</button>
                <button class="btn-tool flashcard-tool" type="button" @click="openTool('flashcards')">Ôn tập nhanh</button>
                <button class="btn-tool whiteboard-tool" type="button" @click="openTool('whiteboard')">Bảng vẽ nhóm</button>
                <button class="btn-tool podcast-tool" type="button" @click="openTool('podcast')">Nghe Podcast</button>
              </div>

              <!-- Secondary -->
              <div class="action-secondary">
                <button v-if="!isEnrolled" class="btn-outline" type="button" @click="enroll(selectedCourse.id)">{{ enrollmentButtonLabel(selectedCourse) }}</button>
                <button v-else-if="!isCompleted" class="btn-outline" style="border-color: #10b981; color: #10b981;" type="button" @click="tryMarkCompleted">Đánh dấu hoàn thành</button>
                <button v-else class="btn-outline" style="border-color: #10b981; background: rgba(16, 185, 129, 0.1); color: #10b981; cursor: default;" type="button">Đã hoàn thành</button>
                
                <button class="btn-outline" type="button" @click="navigate('quiz')">Làm quiz</button>
              </div>
            </div>
          </div>
        </div>

        <div v-if="!canAccessCourse(selectedCourse)" class="access-gate panel rich-panel">
          <p class="eyebrow">Enrollment required</p>
          <h2>Nội dung trả phí đang được khóa</h2>
          <p v-if="isEnrollmentPending">Yêu cầu ghi danh của bạn đang chờ duyệt. Sau khi được duyệt, bài học, tài nguyên và công cụ học sẽ mở lại.</p>
          <p v-else>Gửi yêu cầu ghi danh để EduPress xác nhận thủ công trước khi mở toàn bộ nội dung khóa học.</p>
          <button class="primary-btn" type="button" @click="enroll(selectedCourse.id)">{{ enrollmentButtonLabel(selectedCourse) }}</button>
        </div>

        <div v-else class="detail-content-grid">
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
        <div class="live-comments-section" data-testid="comments-section" style="margin-top: 48px;">
          <div class="section-heading">
            <p class="eyebrow">Real-time Discussion</p>
            <h2>Thảo luận trực tiếp</h2>
            <p>Hệ thống Backend Kafka CQRS: Gửi bình luận sẽ đẩy Event qua Kafka, người khác nhận được qua SSE ngay lập tức.</p>
          </div>
          
          <div class="comment-input-area" style="display:flex;gap:12px;margin-bottom:24px;">
            <input v-model="commentInput" data-testid="comment-input" @keyup.enter="submitComment" type="text" placeholder="Viết bình luận của bạn..." style="flex:1;padding:12px 16px;border-radius:var(--radius-sm);border:1px solid var(--border-glass);background:var(--bg-surface);color:var(--text-main);" />
            <button class="primary-btn" type="button" data-testid="comment-submit" @click="submitComment">Gửi bình luận</button>
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

      <section v-if="route === 'quiz'" class="content-section page-section quiz-layout" data-testid="quiz-page">
        <!-- Header -->
        <div class="quiz-intro">
          <button class="text-btn" style="display:block;margin-bottom:24px;padding-left:0;" type="button" @click="navigate('course-detail', selectedCourseId)">Quay lại khóa học</button>
          <p class="eyebrow">Luyện tập nhanh</p>
          <h1>Kiểm tra kiến thức cá nhân hóa</h1>
          <p>Làm bài ngắn theo chủ đề, xem kết quả ngay và ôn lại phần còn yếu.</p>

          <!-- Study suggestion banner -->
          <div v-if="quizAIReasoning" class="ai-reasoning-banner">
            <span class="ai-reasoning-icon">Gợi ý</span>
            <p>{{ quizAIReasoning }}</p>
          </div>

          <div class="quiz-meta-bar">
            <span class="quiz-meta-pill">{{ quizQuestions.length }} câu hỏi</span>
            <span class="quiz-meta-pill">{{ quizHistory.length }} lượt đã làm</span>
            <span v-if="quizWeakTopic || quizQuestions[0]?.topic_tag" class="quiz-meta-pill topic-pill">Chủ đề: {{ quizWeakTopic || quizQuestions[0]?.topic_tag }}</span>
            <span v-if="quizQuestions[0]?.difficulty" :class="['quiz-meta-pill', 'diff-pill', quizQuestions[0].difficulty]">
              {{ quizQuestions[0].difficulty === 'easy' ? 'Cơ bản' : quizQuestions[0].difficulty === 'hard' ? 'Nâng cao' : 'Trung bình' }}
            </span>
            <button class="ai-gen-btn" type="button" @click="generateAutoQuiz" :disabled="isGeneratingQuiz">
              <span v-if="isGeneratingQuiz" class="gen-spinner"></span>
              <span>{{ isGeneratingQuiz ? 'Đang chuẩn bị...' : 'Tạo bộ câu hỏi' }}</span>
            </button>
          </div>
          <p class="quiz-keyboard-hint">Có thể chọn bằng phím <kbd>1</kbd><kbd>2</kbd><kbd>3</kbd><kbd>4</kbd> và nộp bằng <kbd>Enter</kbd>.</p>
        </div>

        <!-- Active Question -->
        <div v-if="!quizFinished" class="quiz-card-v2" data-testid="quiz-card">
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
              <span>{{ quizStreak }}x liên tiếp</span>
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
              :data-testid="`quiz-option-${idx}`"
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
              <span v-if="quizAnswered && option === quizQuestions[quizIndex].a" class="option-icon">Đúng</span>
              <span v-else-if="quizAnswered && selectedAnswer === option && option !== quizQuestions[quizIndex].a" class="option-icon wrong-icon">Sai</span>
            </button>
          </div>

          <!-- Explanation panel (after answering) -->
          <Transition name="slide-up">
            <div v-if="quizAnswered" :class="['quiz-explanation', quizAnswers[quizAnswers.length-1]?.isRight ? 'correct-explanation' : 'wrong-explanation']">
              <div class="explanation-header">
                <strong>{{ quizAnswers[quizAnswers.length-1]?.isRight ? 'Chính xác' : 'Chưa đúng' }}</strong>
                <span v-if="!quizAnswers[quizAnswers.length-1]?.isRight" class="explanation-correct-label">Đáp án đúng: {{ quizQuestions[quizIndex].a }}</span>
              </div>
              <p v-if="quizQuestions[quizIndex].explanation" class="explanation-body">{{ quizQuestions[quizIndex].explanation }}</p>
              <button class="next-question-btn" @click="nextQuestion">
                {{ quizIndex === quizQuestions.length - 1 ? 'Xem kết quả' : 'Câu tiếp theo' }}
              </button>
            </div>
          </Transition>

          <!-- Submit button (before answering) -->
          <button v-if="!quizAnswered" class="quiz-submit-btn" type="button" data-testid="quiz-submit" @click="answerQuiz" :disabled="!selectedAnswer">
            Xác nhận đáp án
          </button>
        </div>

        <!-- Result Screen -->
        <div v-else class="quiz-result-v2" data-testid="quiz-result">
          <div class="result-circle" :class="{ 'perfect': quizScore === quizQuestions.length, 'pass': quizScore >= quizQuestions.length * 0.6 }">
            <span class="result-score">{{ quizScore }}/{{ quizQuestions.length }}</span>
            <span class="result-label">{{ quizScore === quizQuestions.length ? 'Hoàn hảo' : quizScore >= quizQuestions.length * 0.6 ? 'Tốt lắm' : 'Cần ôn thêm' }}</span>
          </div>

          <!-- Stats row -->
          <div class="result-stats-row">
            <div class="result-stat">
              <span class="stat-num">{{ Math.round((quizScore / quizQuestions.length) * 100) }}%</span>
              <span class="stat-label">Tỷ lệ đúng</span>
            </div>
            <div class="result-stat">
              <span class="stat-num">{{ quizMaxStreak }}</span>
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
                <span class="breakdown-icon">{{ ans.isRight ? 'Đúng' : 'Sai' }}</span>
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
              {{ isGeneratingQuiz ? 'Đang chuẩn bị...' : 'Tạo câu hỏi mới' }}
            </button>
          </div>
          
          <p v-if="isSyncing" style="color:var(--text-muted);font-size:0.85rem;text-align:center;">Đang đồng bộ điểm lên Cloud...</p>
          <p v-if="syncSuccess" style="color:#10b981;font-size:0.85rem;text-align:center;">Đã đồng bộ điểm lên PostgreSQL Cloud.</p>
          <div v-if="syncError" class="sync-error-panel">
            <p>{{ syncError }}</p>
            <button class="btn-outline" type="button" @click="retryQuizSync" :disabled="isSyncing">Thử đồng bộ lại</button>
          </div>
        </div>
      </section>

      <BlogPage v-if="route === 'blog'" :posts="contentPosts" :asset="asset" @home="navigate('home')" />

      <ContactPage v-if="route === 'contact'" :contact-form="contactForm" @home="navigate('home')" @submit="sendContact" />

      <section v-if="route === 'auth'" class="content-section page-section auth-layout">
        <div class="auth-art">
          <button class="text-btn" style="display: block; margin-bottom: 32px; padding-left: 0;" type="button" @click="navigate('home')">Về trang chủ</button>
          <p class="eyebrow">Account</p><h1>{{ authMode === 'login' ? 'Chào mừng quay lại' : 'Tạo tài khoản học tập' }}</h1><p>Đăng nhập bằng sinh trắc học để bảo mật tuyệt đối và loại bỏ hoàn toàn mật khẩu.</p>
        </div>
        <form v-if="authMode === 'login'" class="form-card" @submit.prevent="loginMagicLink">
          <input v-model="loginForm.email" type="email" placeholder="Email" />
          
          <div class="passkey-actions flex flex-col gap-3 mt-4 w-full">
            <button class="primary-btn relative overflow-hidden group w-full" type="button" @click="login">
              <span class="relative z-10 flex items-center justify-center gap-2">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="M9 12l2 2 4-4"/></svg>
                Tiếp tục bằng Passkey
              </span>
              <div class="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-1000"></div>
            </button>
            <button class="secondary-btn w-full" type="submit">Gửi Magic Link</button>
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
                Tạo Passkey (FaceID / Vân tay)
              </span>
              <div class="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-1000"></div>
            </button>
          </div>
          
          <button class="text-btn mt-4 w-full text-center" type="button" @click="authMode = 'login'">Đã có tài khoản? Đăng nhập bằng Passkey</button>
        </form>
      </section>

      <section v-if="route === 'privacy'" class="content-section page-section legal-page">
        <button class="text-btn legal-back" type="button" @click="navigate('home')">Ve trang chu</button>
        <div class="legal-hero">
          <p class="eyebrow">Privacy policy</p>
          <h1>Chinh sach quyen rieng tu</h1>
          <p>EduPress tach ro du lieu luu tren trinh duyet, du lieu backend va du lieu tu dich vu tich hop de nguoi hoc biet minh dang chia se gi.</p>
        </div>
        <div class="legal-grid">
          <article>
            <h2>Du lieu chung toi luu</h2>
            <p>Ho so nguoi dung, trang thai dang nhap demo, lich su quiz va tuong tac khoa hoc co the luu trong IndexedDB cua trinh duyet. Backend san xuat luu tai khoan, ghi danh va lich su quiz trong PostgreSQL; binh luan doc nhanh luu trong MongoDB.</p>
          </article>
          <article>
            <h2>Muc dich su dung</h2>
            <p>Du lieu duoc dung de duy tri dang nhap, hien thi tien trinh hoc, tao quiz phu hop, kiem tra quyen truy cap khoa hoc va dieu phoi binh luan.</p>
          </article>
          <article>
            <h2>Xuat va xoa du lieu</h2>
            <p>Nguoi hoc co the xuat du lieu cuc bo tu trang ho so. API backend cung cap duong dan xuat du lieu tai khoan va xoa tai khoan cho luong dang nhap san xuat.</p>
          </article>
          <article>
            <h2>Luu tru va sao luu</h2>
            <p>Du lieu tai khoan duoc giu khi tai khoan hoat dong. Ban sao luu san xuat can co lich quay vong, gioi han truy cap va khong dung cho muc dich ngoai van hanh.</p>
          </article>
        </div>
      </section>

      <section v-if="route === 'terms'" class="content-section page-section legal-page">
        <button class="text-btn legal-back" type="button" @click="navigate('home')">Ve trang chu</button>
        <div class="legal-hero">
          <p class="eyebrow">Terms</p>
          <h1>Dieu khoan su dung</h1>
          <p>Ban dieu khoan nay dat nen cho prototype EduPress: hoc tap cong bang, noi dung dung quyen va van hanh minh bach ve du lieu.</p>
        </div>
        <div class="legal-grid">
          <article>
            <h2>Tai khoan</h2>
            <p>Nguoi hoc chiu trach nhiem ve thong tin dang ky va viec bao ve phien dang nhap cua minh. Tai khoan co the bi khoa neu co hanh vi lam dung.</p>
          </article>
          <article>
            <h2>Noi dung khoa hoc</h2>
            <p>Noi dung duoc cung cap cho muc dich hoc tap. Viec sao chep, phan phoi lai hoac su dung ngoai pham vi duoc cho phep can co su dong y cua don vi so huu noi dung.</p>
          </article>
          <article>
            <h2>Binh luan va cong dong</h2>
            <p>Binh luan co the duoc kiem duyet. Noi dung gay hai, spam hoac vi pham quyen rieng tu co the bi an hoac xoa.</p>
          </article>
          <article>
            <h2>Dich vu tich hop</h2>
            <p>Cac tinh nang AI, phien am va thanh toan la tich hop tuy chon. Moi tich hop san xuat can duoc cau hinh bang khoa bao mat va chinh sach nha cung cap phu hop.</p>
          </article>
        </div>
      </section>

      <section v-if="route === 'profile'" class="content-section page-section profile-page">
        <button class="text-btn" style="display: block; margin-bottom: 32px; padding-left: 0; align-self: flex-start; text-align: left; margin-right: auto;" type="button" @click="navigate('home')">Về trang chủ</button>

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
                <strong>{{ contentCourses.find(c => c.id === enrolledIds[enrolledIds.length - 1])?.title || 'Khóa học' }}</strong>
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
            <h2>Passkey Auth</h2>
            <div class="mt-4 p-4 rounded-xl border border-[var(--border-glass)] bg-[var(--bg-glass)]">
              <div class="flex items-center gap-3 mb-2">
                <div class="w-2 h-2 rounded-full bg-green-500 shadow-[0_0_8px_#22c55e]"></div>
                <strong class="text-sm">Bảo vệ bằng Sinh trắc học</strong>
              </div>
              <p class="text-xs text-muted">Tài khoản của bạn hiện đang được liên kết với một cặp khóa public/private mã hóa phần cứng. EduPress không lưu bất kỳ mật khẩu nào của bạn.</p>
            </div>
          </div>

          <div class="bento-item bento-privacy rich-panel">
            <p class="eyebrow">Data controls</p>
            <h2>Du lieu ca nhan</h2>
            <p class="text-muted">Xuat ho so, lich su quiz va tuong tac khoa hoc dang luu tren trinh duyet nay. Khi can reset demo, ban co the xoa du lieu cuc bo.</p>
            <div class="privacy-actions">
              <button class="secondary-btn" type="button" @click="exportLearnerData">Xuat du lieu</button>
              <button class="danger-btn" type="button" @click="clearLocalLearnerData">Xoa du lieu cuc bo</button>
            </div>
            <button class="text-btn privacy-link" type="button" @click="navigate('privacy')">Xem chinh sach du lieu</button>
          </div>

          <!-- 5. All Enrolled Courses (Span 4) -->
          <div class="bento-item bento-courses rich-panel">
            <p class="eyebrow">Thư viện của bạn</p>
            <h2>Khóa học đã đăng ký</h2>
            <div class="bento-course-grid" v-if="enrolledIds.length > 0">
              <article v-for="course in contentCourses.filter(c => enrolledIds.includes(c.id))" :key="course.id" class="mini-course-card">
                <img :src="courseImage(course)" :alt="course.title" />
                <div class="mini-course-info">
                  <strong>{{ course.title }}</strong>
                  <span :class="['status-badge', completedIds.includes(course.id) ? 'done' : 'learning']">
                    {{ completedIds.includes(course.id) ? 'Hoàn thành' : 'Đang học' }}
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
              :courses="contentCourses"
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
          <div>
            <h3>Phap ly</h3>
            <button type="button" @click="navigate('privacy')">Chinh sach rieng tu</button>
            <button type="button" @click="navigate('terms')">Dieu khoan su dung</button>
            <button type="button" @click="navigate('profile')">Kiem soat du lieu</button>
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
    
    <!-- Completion Conditions Modal -->
    <div v-if="showCompletionModal" class="completion-modal-overlay">
      <div class="completion-modal-card">
        <button class="close-btn" @click="showCompletionModal = false">Đóng</button>
        <h2>Chưa đủ điều kiện hoàn thành</h2>
        <p>Để nhận chứng chỉ khóa học <strong>{{ selectedCourse.title }}</strong>, bạn cần hoàn thành các tiêu chí sau:</p>
        
        <ul class="condition-list">
          <li v-for="cond in completionConditions" :key="cond.id" :class="{ 'is-met': cond.met }">
            <span class="icon">{{ cond.met ? 'Xong' : 'Chưa' }}</span>
            <span class="text">{{ cond.name }}</span>
          </li>
        </ul>
        
        <button class="primary-btn mt-6 w-full" style="width: 100%; margin-top: 24px;" @click="showCompletionModal = false">Tiếp tục học</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.ai-companion-lite {
  position: fixed;
  right: 24px;
  bottom: 24px;
  z-index: 900;
  min-width: 92px;
  height: 44px;
  padding: 0 18px;
  border: 1px solid var(--border-glass);
  border-radius: var(--radius-sm);
  background: var(--bg-surface);
  color: var(--text-main);
  font-weight: 700;
  box-shadow: 0 12px 28px rgba(15, 23, 42, 0.12);
  cursor: pointer;
  transition: border-color 0.2s ease, background-color 0.2s ease, transform 0.2s ease;
}

.ai-companion-lite:hover {
  transform: translateY(-2px);
  border-color: var(--primary);
  background: var(--bg-base);
}

.legal-page {
  display: flex;
  flex-direction: column;
  gap: 28px;
}

.legal-back {
  align-self: flex-start;
}

.legal-hero {
  max-width: 780px;
}

.legal-hero h1 {
  margin: 10px 0 16px;
}

.legal-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 20px;
}

.legal-grid article,
.bento-privacy {
  border: 1px solid var(--border-glass);
}

.legal-grid article {
  background: var(--bg-surface);
  border-radius: var(--radius-md);
  padding: 28px;
  box-shadow: var(--shadow-glass);
}

.legal-grid h2 {
  font-size: 1.1rem;
  margin-bottom: 12px;
}

.legal-grid p,
.bento-privacy p {
  max-width: none;
}

.bento-privacy {
  grid-column: span 2;
}

.privacy-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 20px;
}

.privacy-link {
  align-self: flex-start;
  margin-top: 14px;
  padding-left: 0;
}

.danger-btn {
  border: 1px solid rgba(185, 28, 28, 0.28);
  border-radius: var(--radius-sm);
  background: rgba(185, 28, 28, 0.06);
  color: #b91c1c;
  min-height: 44px;
  padding: 0 18px;
  font-weight: 700;
  cursor: pointer;
  transition: border-color 0.2s ease, background-color 0.2s ease;
}

.danger-btn:hover {
  border-color: #b91c1c;
  background: rgba(185, 28, 28, 0.1);
}

@media (max-width: 768px) {
  .legal-grid {
    grid-template-columns: 1fr;
  }

  .bento-privacy {
    grid-column: span 1;
  }
}

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

@keyframes pulse-border {
  0% { box-shadow: 0 0 0 0 rgba(124, 58, 237, 0.4); border-color: var(--primary); }
  70% { box-shadow: 0 0 0 10px rgba(124, 58, 237, 0); border-color: var(--border-glass); }
  100% { box-shadow: 0 0 0 0 rgba(124, 58, 237, 0); }
}

.slide-up-enter-active { transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275); }
.slide-up-leave-active { transition: all 0.3s ease; position: absolute; }
.slide-up-enter-from,
.slide-up-leave-to { opacity: 0; transform: translateY(20px) scale(0.95); }
.slide-up-move { transition: transform 0.4s ease; }
</style>
