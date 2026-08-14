<script setup>
const { contactForm } = defineProps({
  contactForm: { type: Object, required: true },
})
const emit = defineEmits(['home', 'submit'])
</script>

<template>
      <section class="content-section page-section contact-layout" data-testid="contact-page">
        <div class="contact-copy">
          <button class="text-btn" style="display: block; margin-bottom: 32px; padding-left: 0;" type="button" @click="emit('home')">Về trang chủ</button>
          <p class="eyebrow">Contact</p>
          <h1>Liên hệ với EduPress</h1>
          <p>Đội ngũ EduPress hỗ trợ tư vấn khóa học, hợp tác giảng dạy và triển khai lớp học online.</p>
          <div class="contact-list"><span>support@edupress.vn</span><span>0900 123 456</span><span>MindX Technology School</span></div>
        </div>
        <form class="form-card" data-testid="contact-form" @submit.prevent="emit('submit')">
          <input v-model="contactForm.name" data-testid="contact-name" placeholder="Họ tên" />
          <input v-model="contactForm.email" data-testid="contact-email" type="email" placeholder="Email" />
          <textarea v-model="contactForm.message" data-testid="contact-message" placeholder="Nội dung cần tư vấn"></textarea>
          <button class="primary-btn" data-testid="contact-submit" type="submit">Gửi phản hồi</button>
        </form>
      </section>
</template>
