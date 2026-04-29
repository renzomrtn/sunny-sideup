import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  // ── Login page ───────────────────────────────────────────────────────────
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/LoginView.vue'),
    meta: { public: true },
  },

  // ── Auth callback — Authentik redirects here after login ─────────────────
  {
    path: '/auth/callback',
    name: 'AuthCallback',
    component: () => import('@/views/AuthCallbackView.vue'),
    meta: { public: true },
  },

  // ── Auth finish — backend redirects here with ?token= ────────────────────
  {
    path: '/auth/finish',
    name: 'AuthFinish',
    component: () => import('@/views/AuthFinishView.vue'),
    meta: { public: true },
  },
  {
    path: '/invalid-role',
    name: 'InvalidRole',
    component: () => import('@/views/InvalidRoleView.vue'),
  },

  // ── Protected shell ───────────────────────────────────────────────────────
  {
    path: '/',
    component: () => import('@/components/AppShell.vue'),
    children: [
      {
        path: '',
        redirect: '/accounts',
      },
      {
        path: 'accounts',
        name: 'Accounts',
        component: () => import('@/views/AccountsView.vue'),
      },
      {
        path: 'accounts/:id',
        name: 'AccountDetail',
        component: () => import('@/views/AccountDetailView.vue'),
        props: true,
      },
    ],
  },

  {
    path: '/:pathMatch(.*)*',
    redirect: '/',
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// ── Auth guard ─────────────────────────────────────────────────────────────
router.beforeEach(async (to) => {
  const auth = useAuthStore()

  // Public routes bypass the guard entirely
  if (to.meta.public) return true

  // If we have a token but no user profile yet, fetch it
  if (auth.isAuthenticated && !auth.user) {
    await auth.fetchMe()
  }

  // Not authenticated → go to our login page (not directly to Authentik)
  if (!auth.isAuthenticated) {
    return { name: 'Login' }
  }

  if (to.name !== 'InvalidRole' && !auth.canAccessAccountManagement) {
    return { name: 'InvalidRole' }
  }

  if (to.name === 'InvalidRole' && auth.canAccessAccountManagement) {
    return { name: 'Accounts' }
  }

  return true
})

export default router
