<template>
  <main class="invalid-role">
    <section class="invalid-role__panel">
      <p class="invalid-role__eyebrow">Invalid User</p>
      <h1>Unauthorized Access! Keep Out.</h1>
      <p class="invalid-role__copy">
        This system is restricted to Administrators Only.
      </p>
      <button class="invalid-role__button" @click="auth.logout">Sign out</button>
    </section>
  </main>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
</script>

<style scoped>
.invalid-role {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  background:
    linear-gradient(135deg, rgba(176, 38, 38, 0.08), transparent 34%),
    var(--c-bg);
}

.invalid-role__panel {
  width: 100%;
  max-width: 520px;
  padding: 32px;
  border: 1px solid #F1B5B5;
  border-radius: var(--radius-lg);
  background: #FFFFFF;
  box-shadow: var(--shadow-lg);
  text-align: center;
}

.invalid-role__eyebrow {
  margin-bottom: 10px;
  color: var(--c-danger);
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.invalid-role h1 {
  margin: 0;
  color: var(--c-text);
  font-family: var(--font-display);
  font-size: 28px;
  line-height: 1.15;
}

.invalid-role__copy {
  margin: 14px 0 24px;
  color: var(--c-text-muted);
  font-size: 14px;
  line-height: 1.6;
}

.invalid-role__button {
  padding: 10px 18px;
  border: 1px solid var(--c-danger);
  border-radius: var(--radius-md);
  background: var(--c-danger);
  color: #FFFFFF;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
}
</style>
