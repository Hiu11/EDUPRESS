<script setup>
const { posts, asset } = defineProps({
  posts: { type: Array, required: true },
  asset: { type: Function, required: true },
})
const emit = defineEmits(['home', 'select-post'])
</script>

<template>
      <section class="content-section page-section" data-testid="blog-page">
        <button class="text-btn" style="display: block; margin-bottom: 32px; padding-left: 0;" type="button" @click="emit('home')">Về trang chủ</button>
        <div class="blog-hero">
          <img :src="asset('blog-banner.jpg')" alt="EduPress blog" />
          <div><p class="eyebrow">EduPress Blog</p><h1>Tin tức giáo dục và công nghệ</h1><p>Nhiều hình ảnh hơn bản trước, giữ lại chất tin tức của EduPress cũ nhưng trình bày gọn và hiện đại hơn.</p></div>
        </div>
        <div class="post-grid">
          <article
            v-for="post in posts"
            :key="post.id"
            class="post-card"
            :data-testid="`blog-post-${post.id}`"
            style="cursor: pointer; transition: transform 0.2s, box-shadow 0.2s;"
            @click="emit('select-post', post)"
            @mouseenter="$event.currentTarget.style.transform='translateY(-4px)'; $event.currentTarget.style.boxShadow='0 12px 28px rgba(0,0,0,0.12)'"
            @mouseleave="$event.currentTarget.style.transform=''; $event.currentTarget.style.boxShadow=''"
          >
            <img :src="asset(post.image)" :alt="post.title" />
            <div>
              <span>{{ post.category }} · {{ post.date }}</span>
              <h3>{{ post.title }}</h3>
              <p>{{ post.excerpt }}</p>
              <span style="display:inline-block;margin-top:8px;font-size:0.8rem;font-weight:700;color:#dc2626;">Đọc tiếp →</span>
            </div>
          </article>
        </div>
      </section>
</template>
