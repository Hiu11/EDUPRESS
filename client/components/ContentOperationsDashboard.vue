<script setup>
import { computed, reactive, ref, watch } from 'vue'

const props = defineProps({
  courses: { type: Array, default: () => [] },
  posts: { type: Array, default: () => [] },
  quizQuestions: { type: Array, default: () => [] },
  comments: { type: Array, default: () => [] },
  users: { type: Array, default: () => [] },
  currentUser: { type: Object, default: null },
})

const emit = defineEmits(['close', 'updateCourses', 'updatePosts', 'updateQuizQuestions', 'updateComments', 'updateUsers', 'notice'])

const activeTab = ref('overview')
const selectedCourseId = ref('')
const selectedPostId = ref('')
const selectedQuizIndex = ref(-1)

const courseForm = reactive(blankCourse())
const postForm = reactive(blankPost())
const quizForm = reactive(blankQuiz())

const isAdmin = computed(() => props.currentUser?.role === 'admin')
const pendingComments = computed(() => props.comments.filter((comment) => (comment.moderation_status || 'visible') === 'needs_review').length)
const visibleComments = computed(() => props.comments.filter((comment) => (comment.moderation_status || 'visible') === 'visible').length)
const activeUsers = computed(() => props.users.filter((user) => user.is_active !== false).length)

watch(
  () => props.courses,
  (next) => {
    if (!selectedCourseId.value && next.length) selectCourse(next[0])
  },
  { immediate: true }
)

function blankCourse() {
  return {
    id: '',
    title: '',
    author: 'MindX',
    category: 'Web Development',
    description: '',
    level: 'Beginner',
    lessons: 8,
    duration: '4 tuần',
    rating: 4.8,
    students: 0,
    progress: 0,
    tag: 'Mới',
    access_type: 'free',
    price_cents: 0,
    currency: 'VND',
    manual_enrollment_enabled: true,
    image: 'course-web-bg.png',
    outcomesText: '',
    syllabusText: '',
    resourcesText: '',
  }
}

function blankPost() {
  return {
    id: '',
    title: '',
    slug: '',
    image: 'news1.jpg',
    category: 'EdTech',
    date: new Date().toLocaleDateString('vi-VN'),
    excerpt: '',
  }
}

function blankQuiz() {
  return {
    q: '',
    a: '',
    optionsText: '',
    explanation: '',
    difficulty: 'medium',
    topic_tag: 'Web Basics',
  }
}

function assign(target, source) {
  Object.keys(target).forEach((key) => {
    target[key] = source[key] ?? target[key]
  })
}

function slugify(value) {
  return value
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '')
    .slice(0, 80)
}

function lines(value) {
  return String(value || '')
    .split('\n')
    .map((item) => item.trim())
    .filter(Boolean)
}

function selectCourse(course) {
  selectedCourseId.value = course.id
  assign(courseForm, {
    ...course,
    outcomesText: (course.outcomes || []).join('\n'),
    syllabusText: (course.syllabus || []).join('\n'),
    resourcesText: (course.resources || []).join('\n'),
  })
}

function newCourse() {
  selectedCourseId.value = ''
  assign(courseForm, blankCourse())
}

function saveCourse() {
  if (!courseForm.title.trim()) return emit('notice', 'Nhập tên khóa học trước khi lưu.')
  const id = selectedCourseId.value || slugify(courseForm.title) || `course-${Date.now()}`
  const nextCourse = {
    id,
    title: courseForm.title.trim(),
    author: courseForm.author.trim(),
    category: courseForm.category.trim(),
    description: courseForm.description.trim(),
    level: courseForm.level,
    lessons: Number(courseForm.lessons || 0),
    duration: courseForm.duration,
    rating: Number(courseForm.rating || 0),
    students: Number(courseForm.students || 0),
    progress: Number(courseForm.progress || 0),
    tag: courseForm.tag,
    access_type: courseForm.access_type,
    price_cents: courseForm.access_type === 'paid' ? Number(courseForm.price_cents || 0) : 0,
    currency: courseForm.currency,
    manual_enrollment_enabled: courseForm.manual_enrollment_enabled,
    image: courseForm.image,
    outcomes: lines(courseForm.outcomesText),
    syllabus: lines(courseForm.syllabusText),
    resources: lines(courseForm.resourcesText),
  }
  const existing = props.courses.some((course) => course.id === id)
  const next = existing ? props.courses.map((course) => (course.id === id ? nextCourse : course)) : [nextCourse, ...props.courses]
  emit('updateCourses', next)
  selectedCourseId.value = id
  emit('notice', existing ? 'Đã cập nhật khóa học.' : 'Đã tạo khóa học mới.')
}

function selectPost(post) {
  selectedPostId.value = post.id
  assign(postForm, { ...post })
}

function newPost() {
  selectedPostId.value = ''
  assign(postForm, blankPost())
}

function savePost() {
  if (!postForm.title.trim()) return emit('notice', 'Nhập tiêu đề bài viết trước khi lưu.')
  const id = selectedPostId.value || Date.now()
  const nextPost = {
    id,
    slug: postForm.slug || slugify(postForm.title),
    title: postForm.title.trim(),
    image: postForm.image,
    category: postForm.category,
    date: postForm.date,
    excerpt: postForm.excerpt.trim(),
  }
  const existing = props.posts.some((post) => post.id === id)
  const next = existing ? props.posts.map((post) => (post.id === id ? nextPost : post)) : [nextPost, ...props.posts]
  emit('updatePosts', next)
  selectedPostId.value = id
  emit('notice', existing ? 'Đã cập nhật bài viết.' : 'Đã tạo bài viết mới.')
}

function selectQuiz(question, index) {
  selectedQuizIndex.value = index
  assign(quizForm, {
    ...question,
    optionsText: (question.options || []).join('\n'),
  })
}

function newQuiz() {
  selectedQuizIndex.value = -1
  assign(quizForm, blankQuiz())
}

function saveQuiz() {
  const options = lines(quizForm.optionsText)
  if (!quizForm.q.trim() || !quizForm.a.trim() || options.length < 2) {
    return emit('notice', 'Quiz cần có câu hỏi, đáp án đúng và ít nhất 2 lựa chọn.')
  }
  const nextQuestion = {
    q: quizForm.q.trim(),
    a: quizForm.a.trim(),
    options: options.includes(quizForm.a.trim()) ? options : [quizForm.a.trim(), ...options],
    explanation: quizForm.explanation.trim(),
    difficulty: quizForm.difficulty,
    topic_tag: quizForm.topic_tag.trim(),
  }
  const next = [...props.quizQuestions]
  if (selectedQuizIndex.value >= 0) {
    next[selectedQuizIndex.value] = nextQuestion
  } else {
    next.unshift(nextQuestion)
    selectedQuizIndex.value = 0
  }
  emit('updateQuizQuestions', next)
  emit('notice', 'Đã lưu câu hỏi quiz.')
}

function setCommentStatus(commentId, status) {
  emit(
    'updateComments',
    props.comments.map((comment) => (comment.id === commentId ? { ...comment, moderation_status: status } : comment))
  )
  emit('notice', status === 'hidden' ? 'Đã ẩn bình luận.' : 'Đã cập nhật trạng thái bình luận.')
}

function updateUser(userEmail, updates) {
  emit(
    'updateUsers',
    props.users.map((user) => (user.email === userEmail ? { ...user, ...updates } : user))
  )
  emit('notice', 'Đã cập nhật người dùng.')
}
</script>

<template>
  <div class="ops-shell">
    <header class="ops-header">
      <div>
        <p>Content operations</p>
        <h2>Bảng điều phối nội dung</h2>
      </div>
      <div class="ops-header-actions">
        <span>{{ currentUser?.role || 'operator' }}</span>
        <button type="button" @click="emit('close')">Đóng</button>
      </div>
    </header>

    <nav class="ops-tabs" aria-label="Content operations">
      <button :class="{ active: activeTab === 'overview' }" type="button" @click="activeTab = 'overview'">Tổng quan</button>
      <button :class="{ active: activeTab === 'courses' }" type="button" @click="activeTab = 'courses'">Khóa học</button>
      <button :class="{ active: activeTab === 'posts' }" type="button" @click="activeTab = 'posts'">Tin tức</button>
      <button :class="{ active: activeTab === 'quiz' }" type="button" @click="activeTab = 'quiz'">Quiz</button>
      <button :class="{ active: activeTab === 'comments' }" type="button" @click="activeTab = 'comments'">Bình luận</button>
      <button v-if="isAdmin" :class="{ active: activeTab === 'users' }" type="button" @click="activeTab = 'users'">Người dùng</button>
    </nav>

    <main class="ops-body">
      <section v-if="activeTab === 'overview'" class="ops-overview">
        <article><span>Khóa học</span><strong>{{ courses.length }}</strong></article>
        <article><span>Bài viết</span><strong>{{ posts.length }}</strong></article>
        <article><span>Câu quiz</span><strong>{{ quizQuestions.length }}</strong></article>
        <article><span>Chờ duyệt</span><strong>{{ pendingComments }}</strong></article>
        <article><span>Bình luận hiển thị</span><strong>{{ visibleComments }}</strong></article>
        <article><span>Người dùng hoạt động</span><strong>{{ activeUsers }}</strong></article>
        <article><span>Quyền hiện tại</span><strong>{{ isAdmin ? 'Admin' : 'Instructor' }}</strong></article>
      </section>

      <section v-else-if="activeTab === 'courses'" class="ops-grid">
        <aside class="ops-list">
          <button type="button" class="new-row" @click="newCourse">Tạo khóa học</button>
          <button v-for="course in courses" :key="course.id" type="button" :class="{ active: selectedCourseId === course.id }" @click="selectCourse(course)">
            <strong>{{ course.title }}</strong>
            <span>{{ course.category }} · {{ course.level }}</span>
          </button>
        </aside>
        <form class="ops-form" @submit.prevent="saveCourse">
          <label>Tên khóa học<input v-model="courseForm.title" /></label>
          <div class="form-row">
            <label>Giảng viên<input v-model="courseForm.author" /></label>
            <label>Lĩnh vực<input v-model="courseForm.category" /></label>
          </div>
          <label>Mô tả<textarea v-model="courseForm.description" rows="3"></textarea></label>
          <div class="form-row">
            <label>Cấp độ<select v-model="courseForm.level"><option>Beginner</option><option>Intermediate</option><option>Advanced</option></select></label>
            <label>Số bài học<input v-model.number="courseForm.lessons" type="number" min="0" /></label>
            <label>Thời lượng<input v-model="courseForm.duration" /></label>
          </div>
          <div class="form-row">
            <label>Truy cập<select v-model="courseForm.access_type"><option value="free">Miễn phí</option><option value="paid">Trả phí</option></select></label>
            <label>Giá theo VND nhỏ nhất<input v-model.number="courseForm.price_cents" type="number" min="0" /></label>
            <label>Ảnh nền<input v-model="courseForm.image" /></label>
          </div>
          <label>Kết quả đầu ra<textarea v-model="courseForm.outcomesText" rows="4"></textarea></label>
          <label>Giáo trình<textarea v-model="courseForm.syllabusText" rows="4"></textarea></label>
          <label>Tài nguyên<textarea v-model="courseForm.resourcesText" rows="3"></textarea></label>
          <button class="save-btn" type="submit">Lưu khóa học</button>
        </form>
      </section>

      <section v-else-if="activeTab === 'posts'" class="ops-grid">
        <aside class="ops-list">
          <button type="button" class="new-row" @click="newPost">Tạo bài viết</button>
          <button v-for="post in posts" :key="post.id" type="button" :class="{ active: selectedPostId === post.id }" @click="selectPost(post)">
            <strong>{{ post.title }}</strong>
            <span>{{ post.category }} · {{ post.date }}</span>
          </button>
        </aside>
        <form class="ops-form" @submit.prevent="savePost">
          <label>Tiêu đề<input v-model="postForm.title" /></label>
          <div class="form-row">
            <label>Slug<input v-model="postForm.slug" /></label>
            <label>Chuyên mục<input v-model="postForm.category" /></label>
          </div>
          <div class="form-row">
            <label>Ngày đăng<input v-model="postForm.date" /></label>
            <label>Ảnh<input v-model="postForm.image" /></label>
          </div>
          <label>Tóm tắt<textarea v-model="postForm.excerpt" rows="5"></textarea></label>
          <button class="save-btn" type="submit">Lưu bài viết</button>
        </form>
      </section>

      <section v-else-if="activeTab === 'quiz'" class="ops-grid">
        <aside class="ops-list">
          <button type="button" class="new-row" @click="newQuiz">Tạo câu quiz</button>
          <button v-for="(question, index) in quizQuestions" :key="`${question.q}-${index}`" type="button" :class="{ active: selectedQuizIndex === index }" @click="selectQuiz(question, index)">
            <strong>{{ question.q }}</strong>
            <span>{{ question.topic_tag }} · {{ question.difficulty }}</span>
          </button>
        </aside>
        <form class="ops-form" @submit.prevent="saveQuiz">
          <label>Câu hỏi<textarea v-model="quizForm.q" rows="3"></textarea></label>
          <label>Đáp án đúng<input v-model="quizForm.a" /></label>
          <label>Các lựa chọn<textarea v-model="quizForm.optionsText" rows="5"></textarea></label>
          <div class="form-row">
            <label>Độ khó<select v-model="quizForm.difficulty"><option>easy</option><option>medium</option><option>hard</option></select></label>
            <label>Chủ đề<input v-model="quizForm.topic_tag" /></label>
          </div>
          <label>Giải thích<textarea v-model="quizForm.explanation" rows="4"></textarea></label>
          <button class="save-btn" type="submit">Lưu quiz</button>
        </form>
      </section>

      <section v-else-if="activeTab === 'comments'" class="comment-panel">
        <article v-for="comment in comments" :key="comment.id" class="comment-row">
          <div>
            <strong>{{ comment.user_name || comment.user_id || 'Người học' }}</strong>
            <p>{{ comment.content }}</p>
            <span>{{ comment.moderation_status || 'visible' }}</span>
          </div>
          <div class="comment-actions">
            <button type="button" @click="setCommentStatus(comment.id, 'visible')">Hiển thị</button>
            <button type="button" @click="setCommentStatus(comment.id, 'needs_review')">Cần xem lại</button>
            <button type="button" @click="setCommentStatus(comment.id, 'hidden')">Ẩn</button>
          </div>
        </article>
        <p v-if="!comments.length" class="empty-state">Chưa có bình luận trong khóa học đang mở.</p>
      </section>

      <section v-else class="user-panel">
        <article v-for="user in users" :key="user.email" class="user-row">
          <div>
            <strong>{{ user.name || user.email }}</strong>
            <span>{{ user.email }}</span>
          </div>
          <select :value="user.role || 'student'" @change="updateUser(user.email, { role: $event.target.value })">
            <option value="student">student</option>
            <option value="instructor">instructor</option>
            <option value="admin">admin</option>
          </select>
          <button type="button" @click="updateUser(user.email, { is_active: user.is_active === false })">
            {{ user.is_active === false ? 'Mở tài khoản' : 'Khóa tài khoản' }}
          </button>
        </article>
        <p v-if="!users.length" class="empty-state">Chưa có người dùng để hiển thị.</p>
      </section>
    </main>
  </div>
</template>

<style scoped>
.ops-shell {
  position: fixed;
  inset: 0;
  z-index: 10000;
  background: #f8fafc;
  color: #0f172a;
  display: flex;
  flex-direction: column;
}

.ops-header {
  min-height: 84px;
  padding: 18px 28px;
  background: #ffffff;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
}

.ops-header p {
  margin: 0 0 4px;
  color: #64748b;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  font-size: 0.75rem;
}

.ops-header h2 {
  margin: 0;
  font-size: 1.4rem;
}

.ops-header-actions,
.ops-tabs,
.form-row,
.comment-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.ops-header-actions span {
  border: 1px solid #cbd5e1;
  border-radius: 999px;
  padding: 8px 12px;
  font-weight: 700;
  color: #475569;
}

button {
  border: 1px solid #cbd5e1;
  background: #ffffff;
  color: #0f172a;
  border-radius: 8px;
  padding: 10px 14px;
  font-weight: 700;
  cursor: pointer;
}

button:hover,
button.active {
  border-color: #dc2626;
  color: #dc2626;
}

.ops-tabs {
  padding: 14px 28px;
  background: #ffffff;
  border-bottom: 1px solid #e2e8f0;
}

.ops-body {
  flex: 1;
  overflow: auto;
  padding: 28px;
}

.ops-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 16px;
}

.ops-overview article,
.ops-form,
.ops-list,
.comment-row,
.user-row {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
}

.ops-overview article {
  padding: 24px;
}

.ops-overview span {
  color: #64748b;
  font-weight: 700;
}

.ops-overview strong {
  display: block;
  margin-top: 12px;
  font-size: 2rem;
}

.ops-grid {
  display: grid;
  grid-template-columns: minmax(260px, 360px) 1fr;
  gap: 20px;
}

.ops-list {
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: calc(100vh - 190px);
  overflow: auto;
}

.ops-list button {
  text-align: left;
}

.ops-list strong,
.ops-list span {
  display: block;
}

.ops-list span {
  margin-top: 4px;
  color: #64748b;
  font-size: 0.85rem;
}

.new-row {
  justify-content: center;
  text-align: center;
}

.ops-form {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.ops-form label {
  display: flex;
  flex-direction: column;
  gap: 6px;
  color: #475569;
  font-weight: 700;
}

.form-row > label {
  flex: 1;
  min-width: 180px;
}

input,
textarea,
select {
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  padding: 10px 12px;
  font: inherit;
  color: #0f172a;
}

textarea {
  resize: vertical;
}

.save-btn {
  align-self: flex-start;
  background: #dc2626;
  border-color: #dc2626;
  color: #ffffff;
}

.comment-panel,
.user-panel {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.comment-row,
.user-row {
  padding: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
}

.comment-row p {
  margin: 8px 0;
  color: #334155;
}

.comment-row span,
.user-row span,
.empty-state {
  color: #64748b;
}

@media (max-width: 860px) {
  .ops-grid {
    grid-template-columns: 1fr;
  }

  .comment-row,
  .user-row {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>
