import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/composables/api'

// ── Authentik OIDC config (injected via Vite env vars) ────────────────────
const AUTHENTIK_URL    = import.meta.env.VITE_AUTHENTIK_URL
const AUTHENTIK_SLUG   = import.meta.env.VITE_AUTHENTIK_SLUG
const AUTHENTIK_CLIENT = import.meta.env.VITE_AUTHENTIK_CLIENT_ID
const REDIRECT_URI     = `${window.location.origin}/auth/callback`

// Where Authentik sends the user after logging out
const POST_LOGOUT_URI  = `${window.location.origin}/login`

export const useAuthStore = defineStore('auth', () => {
  const token   = ref(localStorage.getItem('access_token') || null)
  const user    = ref(null)
  const loading = ref(false)

  const isAuthenticated = computed(() => !!token.value)
  const fullName        = computed(() => user.value?.full_name || '')
  const primaryRole     = computed(() => user.value?.primary_role || null)
  const tenantName      = computed(() => primaryRole.value?.tenant_name || '')
  const positionName    = computed(() => primaryRole.value?.position_name || '')
  const canAccessAccountManagement = computed(() =>
    user.value?.can_access_account_management === true ||
    positionName.value === 'Account Management Administrator'
  )

  function setToken(t) {
    token.value = t
    localStorage.setItem('access_token', t)
  }

  function clearToken() {
    token.value = null
    user.value  = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('id_token')
  }

  /**
   * Redirects the browser to Authentik's authorization endpoint.
   * Authentik will redirect back to /auth/callback?code=... after login.
   */
  function redirectToLogin() {
    const params = new URLSearchParams({
      response_type: 'code',
      client_id:     AUTHENTIK_CLIENT,
      redirect_uri:  REDIRECT_URI,
      scope:         'openid profile email',
    })
    window.location.href =
      `${AUTHENTIK_URL}/application/o/authorize/?${params.toString()}`
  }

  async function fetchMe() {
    if (!token.value) return
    loading.value = true
    try {
      const res = await authApi.me()
      user.value = res.data
    } catch {
      clearToken()
    } finally {
      loading.value = false
    }
  }

  async function logout() {
  const idToken = localStorage.getItem('id_token') // we'll store this at login
  try {
    await authApi.logout()
  } finally {
    clearToken()
    const params = new URLSearchParams({
      post_logout_redirect_uri: POST_LOGOUT_URI,
      ...(idToken && { id_token_hint: idToken }),
    })
    window.location.href =
      `${AUTHENTIK_URL}/application/o/${AUTHENTIK_SLUG}/end-session/?${params.toString()}`
  }
}

  return {
    token, user, loading,
    isAuthenticated, fullName, primaryRole, tenantName, positionName, canAccessAccountManagement,
    setToken, clearToken, fetchMe, logout, redirectToLogin,
  }
})
