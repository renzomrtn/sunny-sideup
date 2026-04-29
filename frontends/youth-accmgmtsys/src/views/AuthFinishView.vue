<template>
  <div class="auth-finish">
    <p v-if="error" class="error">Login error: {{ error }}</p>
    <p v-else>Loading your profile…</p>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { authApi } from '@/composables/api'

const router = useRouter()
const auth   = useAuthStore()
const error  = ref(null)

onMounted(async () => {
  const params  = new URLSearchParams(window.location.search)
  const token   = params.get('token')
  const idToken = params.get('id_token')

  if (!token) {
    error.value = 'No token received from authentication provider.'
    return
  }

  if (idToken) localStorage.setItem('id_token', idToken)
  auth.setToken(token)

  // 1. Load the user profile — validates the token against the backend
  try {
    await auth.fetchMe()
  } catch {
    error.value = 'Could not load your profile. Contact your administrator.'
    auth.clearToken()
    return
  }

  // 2. Record the LOGIN event — fire-and-forget, never block navigation
  //    Even if this fails, the user is still logged in
  try {
    await authApi.loginEvent()
  } catch (e) {
    // Non-fatal: log to console but do not surface to user
    console.warn('[AuthFinish] login-event recording failed:', e?.response?.data ?? e)
  }

  router.replace('/accounts')
})
</script>

<style scoped>
.auth-finish {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100vh;
  font-family: sans-serif;
  color: #555;
}
.error { color: #c0392b; }
</style>
