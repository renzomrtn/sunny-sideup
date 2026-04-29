<template>
  <div class="view">
    <div class="page-header">
      <h1 class="page-title">My Profile</h1>
      <p class="page-desc">Your account details and active role assignments.</p>
    </div>

    <div v-if="auth.loading" class="loading-state">
      <div class="spinner"></div>
    </div>

    <div v-else-if="auth.user" class="profile-layout">
      <div class="info-card">
        <div class="info-card__header">
          <div class="profile-avatar">{{ initials }}</div>
          <div>
            <h2 class="profile-name">{{ auth.fullName }}</h2>
            <p class="profile-email">{{ auth.user.contact_email || 'No email on record' }}</p>
          </div>
          <span class="badge ml-auto" :class="auth.user.account_status === 'Active' ? 'badge--active' : 'badge--inactive'">
            {{ auth.user.account_status }}
          </span>
        </div>
      </div>

      <div v-if="auth.primaryRole" class="info-card">
        <h3 class="section-title">Primary Role</h3>
        <div class="role-display">
          <div class="role-display__item">
            <span class="role-label">Tenant</span>
            <span class="role-value">{{ auth.primaryRole.tenant_name }}</span>
          </div>
          <div class="role-display__item">
            <span class="role-label">Position</span>
            <span class="role-value">{{ auth.primaryRole.position_name }}</span>
          </div>
          <div class="role-display__item">
            <span class="role-label">Status</span>
            <span class="badge" :class="auth.primaryRole.role_status === 'Active' ? 'badge--active' : 'badge--inactive'">
              {{ auth.primaryRole.role_status }}
            </span>
          </div>
        </div>
      </div>

      <div class="info-card">
        <h3 class="section-title">Authentication</h3>
        <p class="auth-note">
          Your password, MFA settings, and active sessions are managed through your
          <strong>Authentik identity portal</strong>. Contact your administrator to update credentials.
        </p>
      </div>
    </div>
  </div>
</template>

<script>
import { useProfileView } from './scripts/useProfileView'

export default {
  name: 'ProfileView',
  setup() {
    return useProfileView()
  },
}
</script>

<style scoped>
.view { padding: 32px; display: flex; flex-direction: column; gap: 20px; max-width: 640px; margin: 0 auto; width: 100%; }
.page-title { font-family: var(--font-display); font-size: 26px; margin-bottom: 4px; }
.page-desc  { font-size: 13px; color: var(--c-text-muted); }
.loading-state { display: flex; justify-content: center; padding: 48px; }

.info-card {
  background: var(--c-bg-card);
  border: 1px solid var(--c-border);
  border-radius: var(--radius-lg);
  padding: 20px 24px;
  box-shadow: var(--shadow-sm);
}
.info-card__header { display: flex; align-items: center; gap: 16px; }
.profile-avatar {
  width: 56px; height: 56px;
  background: var(--c-primary-pale); color: var(--c-primary);
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-family: var(--font-display); font-size: 20px;
  flex-shrink: 0;
}
.profile-name  { font-family: var(--font-display); font-size: 20px; }
.profile-email { font-size: 13px; color: var(--c-text-muted); }
.ml-auto { margin-left: auto; }

.section-title { font-size: 13px; font-weight: 700; letter-spacing: 0.04em; text-transform: uppercase; color: var(--c-text-muted); margin-bottom: 14px; }
.role-display { display: flex; flex-direction: column; gap: 10px; }
.role-display__item { display: flex; align-items: center; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid var(--c-border-light); }
.role-display__item:last-child { border-bottom: none; }
.role-label { font-size: 12px; color: var(--c-text-muted); }
.role-value { font-size: 13px; font-weight: 600; }
.auth-note { font-size: 13px; line-height: 1.6; color: var(--c-text-muted); }
.auth-note strong { color: var(--c-text); }
.spinner { width: 24px; height: 24px; border: 2px solid var(--c-border); border-top-color: var(--c-primary); border-radius: 50%; animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
</style>
