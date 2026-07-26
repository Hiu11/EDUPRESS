// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  ssr: true, // Enables Server-Side Rendering for FCP < 1s
  devtools: { enabled: false },
  
  // Register SCSS assets
  css: [
    '~/assets/styles/_variables.scss',
    '~/assets/styles/_base.scss',
    '~/assets/styles/_buttons.scss',
    '~/assets/styles/_layout.scss',
    '~/assets/styles/_cards.scss',
    '~/assets/styles/_pages.scss',
    '~/assets/styles/_cinema.scss',
    '~/assets/styles/_animations.scss',
    '~/assets/styles/_responsive.scss'
  ],

  // Optional: Auto import components is true by default
  components: true,

  // Vue compiler options
  vue: {
    compilerOptions: {
      // Define custom elements if any
    }
  },

  app: {
    head: {
      link: [
        { rel: 'preconnect', href: 'https://fonts.googleapis.com' },
        { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: '' },
        { rel: 'stylesheet', href: 'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap' }
      ]
    }
  },

  compatibilityDate: '2026-07-26'
})
