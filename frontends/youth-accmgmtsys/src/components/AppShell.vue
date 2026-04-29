<template>
  <div class="shell">
    <!-- ── Top Header ── -->
    <header class="topbar">
      <div class="topbar-brand">
        <div class="brand-icon">
           <img :src="youthLogo" alt="Logo" class="topbar-logo" />
        </div>
        <div class="brand-text">
          <span class="brand-title">YOUTH Account Management System</span>
        </div>
      </div>

      <div class="topbar-user">
        <div class="user-info">
          <span class="user-name">{{ auth.fullName || 'Loading…' }}</span>
          <span class="user-role">{{ auth.positionName || auth.tenantName || 'Administrator' }}</span>
        </div>
        <div class="user-avatar">{{ initials }}</div>
        <button class="btn-logout" @click="auth.logout" title="Sign out">
          <span>Sign out</span>
        </button>
      </div>
    </header>

    <!-- ── Main Content ── -->
    <main class="main-content">
      <RouterView v-slot="{ Component }">
        <Transition name="fade" mode="out-in">
          <component :is="Component" />
        </Transition>
      </RouterView>
    </main>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { RouterLink, RouterView } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import youthLogo from '@/assets/youth-ims-logo.svg';

const auth = useAuthStore()

const initials = computed(() => {
  const name = auth.fullName
  if (!name) return '?'
  const parts = name.split(' ').filter(Boolean)
  return parts.length >= 2
    ? (parts[0][0] + parts[parts.length - 1][0]).toUpperCase()
    : name.slice(0, 2).toUpperCase()
})
</script>

<style scoped>
.shell {
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
  background: var(--c-bg);
}

/* ── Top Header ── */
.topbar {
  height: var(--topbar-height);
  background: #ffffff;
  border-bottom: 1px solid var(--c-border);
  display: flex;
  align-items: center;
  padding: 0 28px;
  gap: 0;
  flex-shrink: 0;
  box-shadow: 0 1px 4px rgba(26,35,50,0.06);
  z-index: 100;
}

.topbar-brand {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-right: 36px;
}

.brand-icon {
  height: 32px; /* Increased slightly for better visibility */
  display: flex;
  align-items: center;
  flex-shrink: 0;
}

.brand-text {
  display: flex;
  align-items: center;
  gap: 8px;
}
.brand-title {
  font-size: 15px;
  font-weight: 700;
  color: var(--c-primary);
  letter-spacing: 0.01em;
}
.brand-divider {
  color: var(--c-border);
  font-size: 16px;
}
.brand-sub {
  font-size: 13px;
  color: var(--c-text-muted);
  font-weight: 400;
}

/* ── Nav ── */
.topbar-nav {
  display: flex;
  align-items: center;
  gap: 2px;
  flex: 1;
}

.topbar-logo {
  height: 100%;
  width: auto; /* This allows the logo to maintain its aspect ratio */
  display: block;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 7px;
  padding: 7px 14px;
  border-radius: var(--radius-md);
  color: var(--c-text-muted);
  font-size: 13px;
  font-weight: 500;
  transition: background 0.15s, color 0.15s;
}
.nav-item svg { width: 15px; height: 15px; flex-shrink: 0; }
.nav-item:hover {
  background: var(--c-bg);
  color: var(--c-text);
}
.nav-item--active {
  background: var(--c-primary-pale);
  color: var(--c-primary) !important;
  font-weight: 600;
}

/* ── User Section ── */
.topbar-user {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-left: auto;
  padding-left: 20px;
  border-left: 1px solid var(--c-border);
}

.user-info {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}
.user-name {
  font-size: 13px;
  font-weight: 600;
  color: var(--c-text);
  white-space: nowrap;
}
.user-role {
  font-size: 11px;
  color: var(--c-text-muted);
  white-space: nowrap;
}

.user-avatar {
  width: 34px;
  height: 34px;
  background: var(--c-primary);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
  color: white;
  flex-shrink: 0;
}

.btn-logout {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 7px 12px;
  background: transparent;
  border: 1px solid var(--c-border);
  border-radius: var(--radius-md);
  color: var(--c-text-muted);
  font-size: 12px;
  font-weight: 500;
  transition: all 0.15s;
  cursor: pointer;
  white-space: nowrap;
}
.btn-logout svg { width: 14px; height: 14px; }
.btn-logout:hover {
  color: var(--c-danger);
  border-color: var(--c-danger);
  background: var(--c-danger-bg);
}

/* ── Main Content ── */
.main-content {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  background: var(--c-bg);
}
</style>
