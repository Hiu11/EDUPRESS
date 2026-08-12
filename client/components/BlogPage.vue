<script setup>
const { posts, asset } = defineProps({
  posts: { type: Array, required: true },
  asset: { type: Function, required: true },
})
const emit = defineEmits(['home'])
</script>

<template>
      <section class="content-section page-section">
        <button class="text-btn" style="display: block; margin-bottom: 32px; padding-left: 0;" type="button" @click="emit('home')">Về trang chủ</button>
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
</template>
