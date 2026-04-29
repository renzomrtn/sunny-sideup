<template>
  <div class="auth-callback">
    <p v-if="error" class="error">Login failed: {{ error }}</p>
    <p v-else>Signing you in…</p>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const error  = ref(null)

onMounted(() => {
  const params = new URLSearchParams(window.location.search)
  const code   = params.get('code')
  const err    = params.get('error')

  if (err) {
    error.value = err
    return
  }

  if (!code) {
    error.value = 'No authorization code received.'
    return
  }

  // Redirect to backend callback — it will exchange the code and redirect
  // back to /auth/finish?token=<access_token>
  const redirectUri = encodeURIComponent(`${window.location.origin}/auth/callback`)
  window.location.href = `/api/auth/callback?code=${code}&redirect_uri=${redirectUri}`
})
</script>

<style scoped>
.auth-callback {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100vh;
  font-family: sans-serif;
  color: #555;
}
.error { color: #c0392b; }
</style>
