// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  devtools: { enabled: true },

  modules: [
    '@nuxtjs/tailwindcss',
    '@vueuse/nuxt',
    '@nuxt/icon',
    '@nuxtjs/google-fonts',
  ],

  googleFonts: {
    families: {
      'Source Sans 3': [300, 400, 500, 600, 700, 800],
      'DM Mono': [400, 500],
    },
    display: 'swap',
  },

  tailwindcss: {
    cssPath: '~/assets/css/main.css',
    configPath: '~/tailwind.config.ts',
  },

  app: {
    head: {
      title: 'Youth Transparency Portal — Expense Verification',
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        {
          name: 'description',
          content:
            'Sangguniang Kabataan Federation of Naga City — Expense Verification Portal',
        },
      ],
    },
  },

  runtimeConfig: {
    public: {
      expenditureApiBase:
        process.env.EXPENDITURE_API_BASE || 'http://localhost:8001',
      cmsApiBase:
        process.env.CMS_API_BASE || '',
    },
  },

  nitro: {
    devProxy: {
      '/api/cms': {
        target: process.env.CMS_API_BASE || 'http://localhost:9002',
        changeOrigin: true,
      },
      '/api/expenditures': {
        target: process.env.EXPENDITURE_API_BASE || 'http://localhost:9001',
        changeOrigin: true,
      },
    },
  },

  compatibilityDate: '2024-11-01',
})
