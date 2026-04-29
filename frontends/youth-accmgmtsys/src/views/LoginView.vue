<template>
  <div class="login-page">
    <div class="login-container">
      
      <header class="brand">
        <div class="brand__logo">
          <img :src="youthLogo" alt="Youth Logo" class="logo-img" />
        </div>
        <div class="brand__text">
          <h1 class="brand__title">YOUTH</h1>
          <p class="brand__sub">Youth Officials' Unified Transparency Hub <br> Account Management System</p>
        </div>
      </header>

      <main class="login-card">
        <div class="login-card__header">
          <h2 class="login-card__title">Sign in to your account</h2>
          <p class="login-card__sub">Use your authorized credentials to continue.</p>
        </div>

        <div class="login-card__warning">
          <svg viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/>
          </svg>
          <span>Authorized Personnel Only. Unauthorized access is prohibited.</span>
        </div>

        <button class="btn-login" @click="handleLogin" :disabled="loading">
          <span v-if="loading" class="btn-login__spinner"></span>
          <span>{{ loading ? 'Redirecting…' : 'Log in with Authentik' }}</span>
        </button>
      </main>

    </div>

    <footer class="login-footer">
      <span>© {{ year }} YOUTH Account Management System</span>
    </footer>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import youthLogo from '@/assets/youth-ims-logo.svg';

const auth    = useAuthStore()
const loading = ref(false)
const year    = new Date().getFullYear()

function handleLogin() {
  loading.value = true
  auth.redirectToLogin()
}
</script>

<style scoped>
/* ── Page Layout (Unified) ── */
.login-page {
  height: 100vh; /* Changed from min-height to height to match */
  width: 100%;
  background: linear-gradient(160deg, #e67e22 0%, #a04000 100%);
  display: flex;
  flex-direction: column; /* Match Main System flex flow */
  justify-content: center;
  align-items: center;
  padding: 40px 20px;
  box-sizing: border-box;
}

/* ── Center Content Wrapper ── */
.login-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  max-width: 440px;
  gap: 40px;
  flex: 1; /* This pushes the footer down */
}

/* ── Branding (Changed to Row Layout) ── */
.brand {
  display: flex;
  flex-direction: row; /* Match Main System */
  align-items: center;
  justify-content: center;
  text-align: left;
  gap: 16px;
}

.brand__logo {
  width: 80px; /* Matched size from Main System */
}

.logo-img {
  width: 100%;
  filter: drop-shadow(0 4px 12px rgba(0, 0, 0, 0.3));
}

.brand__text {
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.brand__title {
  font-size: 52px;
  font-weight: 900;
  color: #ffffff;
  line-height: 1;
  margin: 0;
}

.brand__sub {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.9);
  margin-top: 4px;
}

/* ── Login Card (Kept your specific styling) ── */
.login-card {
  width: 100%;
  background: #ffffff;
  border-radius: var(--radius-xl, 16px);
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.25);
  padding: 40px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.login-card__header {
  text-align: center;
}

.login-card__title {
  font-size: 20px;
  font-weight: 700;
  color: #2c3e50;
  margin-bottom: 8px;
}

.login-card__sub {
  font-size: 13px;
  color: #7f8c8d;
}

.login-card__warning {
  display: flex;
  gap: 10px;
  background: #fff7ed;
  border: 1px solid #fed7aa;
  border-left: 4px solid #f39c12;
  border-radius: var(--radius-md, 8px);
  padding: 12px;
  font-size: 12px;
  color: #9a3412;
  line-height: 1.4;
}

.login-card__warning svg {
  width: 16px;
  height: 16px;
  flex-shrink: 0;
}

/* ── Button (Kept your Blue brand color) ── */
.btn-login {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 14px;
  background: #1a5276;
  color: #ffffff;
  border: none;
  border-radius: var(--radius-md, 8px);
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 4px 6px rgba(26, 82, 118, 0.2);
}

.btn-login:hover {
  background: #154360;
  transform: translateY(-1px);
}

.btn-login:disabled {
  background: #bdc3c7;
  cursor: not-allowed;
}

.btn-login__spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: #ffffff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

/* ── Footer (Fixed bottom) ── */
.login-footer {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.6);
  letter-spacing: 0.5px;
  text-align: center;
  margin-top: auto;
}

/* ── Mobile Responsiveness ── */
@media (max-width: 480px) {
  .brand__title {
    font-size: 40px;
  }
  .brand__logo {
    width: 70px;
  }
  .login-card {
    padding: 28px 24px;
  }
}
</style>