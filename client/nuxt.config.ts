import { defineNuxtConfig } from 'nuxt/config'
import tresTemplateCompilerOptions from '@tresjs/core/template-compiler-options'

const tresCompilerOptions = tresTemplateCompilerOptions.template.compilerOptions

// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  ssr: true, // Enables Server-Side Rendering for FCP < 1s
  devtools: { enabled: false },
  
  // Deploy to Global Edge CDN (Vercel Edge Network) for TTFB < 50ms
  nitro: {
    preset: 'vercel_edge'
  },

  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:8000',
      adminEmail: process.env.NUXT_PUBLIC_ADMIN_EMAIL || '',
    }
  },
  
  // Register SCSS assets and new Tailwind v4 entry
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
      ...tresCompilerOptions
    }
  },

  app: {
    head: {
      link: [
        { rel: 'preconnect', href: 'https://fonts.googleapis.com' },
        { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: '' },
        { rel: 'stylesheet', href: 'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap' }
      ],
      script: [
        {
          innerHTML: `
            (function() {
              try {
                var storedTheme = localStorage.getItem('theme');
                if (storedTheme === 'dark' || storedTheme === 'oled') {
                  document.documentElement.setAttribute('data-theme', storedTheme);
                } else if (storedTheme === 'light') {
                  document.documentElement.removeAttribute('data-theme');
                } else {
                  if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
                    document.documentElement.setAttribute('data-theme', 'dark');
                  }
                }
              } catch (e) {}
            })();
          `,
          type: 'text/javascript'
        }
      ]
    }
  },

  compatibilityDate: '2026-07-26',

  modules: [
    '@vite-pwa/nuxt'
  ],

  // @ts-ignore - Vite PWA types are injected automatically by Nuxt during build
  pwa: {
    registerType: 'autoUpdate',
    manifest: {
      name: 'EduPress',
      short_name: 'EduPress',
      theme_color: '#0f172a',
      description: 'Nền tảng học tập trực tuyến 0-Latency',
      icons: [
        {
          src: '/generated-assets/edupress-logo.svg',
          sizes: 'any',
          type: 'image/svg+xml'
        }
      ]
    },
    workbox: {
      navigateFallback: '/',
      maximumFileSizeToCacheInBytes: 8 * 1024 * 1024,
      globPatterns: ['**/*.{js,css,html,png,svg,ico}'],
    },
    client: {
      installPrompt: true,
      periodicSyncForUpdates: 3600
    },
    devOptions: {
      enabled: true,
      suppressWarnings: true,
      navigateFallbackAllowlist: [/^\/$/],
      type: 'module',
    },
  },
  vite: {
    plugins: []
  }
})
