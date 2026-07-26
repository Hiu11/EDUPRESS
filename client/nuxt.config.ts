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

  compatibilityDate: '2026-07-26'
})
