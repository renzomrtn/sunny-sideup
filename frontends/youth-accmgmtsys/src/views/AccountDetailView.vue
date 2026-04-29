<template>
  <div class="view" v-if="account">
    <div class="page-header">
      <button class="btn-back" @click="$router.push('/accounts')">
        <svg viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M9.707 14.707a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 1.414L7.414 9H15a1 1 0 110 2H7.414l2.293 2.293a1 1 0 010 1.414z" clip-rule="evenodd"/></svg>
        Back to Accounts
      </button>
    </div>

    <div class="detail-layout">
      <div class="profile-column">
        <div class="profile-card">
          <div class="profile-avatar">{{ getInitials(account.full_name) }}</div>
          <h2 class="profile-name">{{ account.full_name || 'Unnamed Account' }}</h2>
          <span v-if="isAdminAccount" class="admin-protected-badge">System Administrator — Protected</span>
          <p class="profile-email">{{ account.contact_email || '—' }}</p>
          <span class="badge mt-8" :class="account.account_status === 'Active' ? 'badge--active' : 'badge--inactive'">
            {{ account.account_status }}
          </span>

          <div class="profile-meta">
            <div class="meta-row">
              <span class="meta-label">Contact</span>
              <span>{{ account.contact_number || '—' }}</span>
            </div>
            <div class="meta-row">
              <span class="meta-label">Provider</span>
              <span>{{ account.identity_provider }}</span>
            </div>
            <div class="meta-row">
              <span class="meta-label">Auth ID</span>
              <span class="meta-code">{{ account.auth_external_id?.slice(0, 8) }}...</span>
            </div>
            <div class="meta-row">
              <span class="meta-label">Synced</span>
              <span>{{ formatDate(account.synced_at) }}</span>
            </div>
          </div>

          <div class="profile-actions">
            <button class="btn-edit-full" @click="showEditModal = true" :disabled="isAdminAccount" :title="isAdminAccount ? 'System Administrator cannot be edited' : ''">Edit Profile</button>
            <button
              class="btn-toggle-status"
              :class="account.account_status === 'Active' ? 'btn-deactivate' : 'btn-activate'"
              :disabled="isAdminAccount"
              :title="isAdminAccount ? 'System Administrator cannot be deactivated' : ''"
              @click="requestToggleStatus"
            >
              {{ account.account_status === 'Active' ? 'Deactivate' : 'Activate' }}
            </button>
          </div>
        </div>
      </div>

      <div class="tabs-column">
        <div class="tabs-header">
          <button
            v-for="tab in tabs"
            :key="tab.key"
            class="tab-btn"
            :class="{ 'tab-btn--active': activeTab === tab.key }"
            @click="activeTab = tab.key"
          >
            {{ tab.label }}
          </button>
        </div>

        <div v-if="activeTab === 'roles'" class="tab-content">
          <div class="tab-content-header">
            <h3>Role Assignments</h3>
            <button
              v-if="canShowAssignRole"
              class="btn-primary btn-sm"
              @click="openRoleModal"
            >
              + Assign Role
            </button>
          </div>

          <div v-if="account.tenant_roles.length === 0" class="empty-state">
            <svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="1.5">
              <circle cx="24" cy="24" r="20"/>
              <path d="M24 14v10M24 34v.01"/>
            </svg>
            <p>No roles assigned yet.</p>
          </div>

          <div v-else class="role-list">
            <div v-for="role in account.tenant_roles" :key="role.role_id" class="role-card">
              <div class="role-card__left">
                <div class="role-badge" :class="role.is_primary_tenant ? 'role-badge--primary' : 'role-badge--secondary'">
                  {{ role.is_primary_tenant ? 'Primary' : 'Secondary' }}
                </div>
                <div class="role-info">
                  <span class="role-tenant">{{ role.tenant_name }}</span>
                  <span class="role-position">{{ role.position_name }}</span>
                </div>
              </div>
              <div class="role-card__right">
                <span class="badge" :class="role.role_status === 'Active' ? 'badge--active' : 'badge--inactive'">
                  {{ role.role_status }}
                </span>
                <button class="btn-icon-sm" title="Remove role" @click="requestRemoveRole(role.role_id, role.tenant_name)" :disabled="isAdminAccount">
                  <svg viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd"/></svg>
                </button>
              </div>
            </div>
          </div>
        </div>

        <div v-if="activeTab === 'history'" class="tab-content">
          <div class="tab-content-header">
            <h3>Login History</h3>
            <span class="count-badge">{{ loginHistory.length }} events</span>
          </div>

          <div v-if="historyLoading" class="tab-loading">
            <div class="spinner"></div> Loading...
          </div>

          <div v-else-if="loginHistory.length === 0" class="empty-state">
            <p>No login events recorded.</p>
          </div>

          <div v-else class="history-list">
            <div v-for="event in loginHistory" :key="event.event_id" class="history-row">
              <div class="history-icon" :class="event.event_type === 'LOGIN' ? 'history-icon--login' : 'history-icon--logout'">
                <svg v-if="event.event_type === 'LOGIN'" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M3 3a1 1 0 011 1v12a1 1 0 01-2 0V4a1 1 0 011-1zm10.293 4.293a1 1 0 011.414 0l3 3a1 1 0 010 1.414l-3 3a1 1 0 01-1.414-1.414L14.586 11H8a1 1 0 010-2h6.586l-1.293-1.293a1 1 0 010-1.414z" clip-rule="evenodd"/>
                </svg>
                <svg v-else viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M17 3a1 1 0 01-1 1v12a1 1 0 010-2v-1.586l-1.293 1.293a1 1 0 01-1.414-1.414l3-3a1 1 0 010-1.414l-3-3a1 1 0 011.414-1.414L15 6.586V5a1 1 0 011-1zm-6.707 3.293a1 1 0 010 1.414L8.586 9H15a1 1 0 010 2H8.586l1.707 1.707a1 1 0 01-1.414 1.414l-3-3a1 1 0 010-1.414l3-3a1 1 0 011.414 0z" clip-rule="evenodd"/>
                </svg>
              </div>
              <div class="history-info">
                <span class="history-type">{{ event.event_type }}</span>
                <span class="history-meta">Tenant ID {{ event.tenant_id || '—' }}</span>
              </div>
              <span class="history-time">{{ formatDateTime(event.occurred_at) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <Teleport to="body">
      <Transition name="fade">
        <div v-if="showEditModal" class="modal-backdrop" @click.self="showEditModal = false">
          <div class="modal">
            <div class="modal-header">
              <h2>Edit Profile</h2>
              <button class="btn-icon" @click="showEditModal = false">
                <svg viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"/></svg>
              </button>
            </div>
            <div class="modal-body">
              <div class="form-grid">
                <div class="form-field">
                  <label>First Name</label>
                  <input v-model="editForm.first_name" />
                </div>
                <div class="form-field">
                  <label>Middle Name</label>
                  <input v-model="editForm.middle_name" />
                </div>
                <div class="form-field">
                  <label>Last Name</label>
                  <input v-model="editForm.last_name" />
                </div>
                <div class="form-field">
                  <label>Contact Email</label>
                  <input v-model="editForm.contact_email" type="email" />
                </div>
                <div class="form-field">
                  <label>Contact Number</label>
                  <input v-model="editForm.contact_number" />
                </div>
              </div>
            </div>
            <div class="modal-footer">
              <button class="btn-ghost" @click="showEditModal = false">Cancel</button>
              <button class="btn-primary" @click="requestEditSave" :disabled="saving">
                {{ saving ? 'Saving...' : 'Save Changes' }}
              </button>
            </div>
          </div>
        </div>
      </Transition>

      <Transition name="fade">
        <div v-if="showRoleModal" class="modal-backdrop" @click.self="showRoleModal = false">
          <div class="modal">
            <div class="modal-header">
              <h2>Assign Role</h2>
              <button class="btn-icon" @click="showRoleModal = false">
                <svg viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"/></svg>
              </button>
            </div>
            <div class="modal-body">
              <div class="form-stack">
                <div class="form-field" v-if="isChairpersonAccount">
                  <label>Tenant *</label>
                  <div class="locked-field">
                    <svg viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clip-rule="evenodd"/></svg>
                    SK Federation
                  </div>
                  <p class="field-hint">SK Chairperson's second tenant is always SK Federation.</p>
                </div>

                <div class="form-field" v-else>
                  <label>Tenant *</label>
                  <select v-model="roleForm.tenant_id" @change="onTenantChange">
                    <option value="">Select tenant...</option>
                    <option v-for="tenant in availableTenants" :key="tenant.tenant_id" :value="tenant.tenant_id">{{ tenant.tenant_name }}</option>
                  </select>
                </div>

                <div class="form-field">
                  <label>Position *</label>
                  <select v-model="roleForm.position_id" :disabled="!roleForm.tenant_id && !isChairpersonAccount">
                    <option value="">Select position...</option>
                    <option
                      v-for="position in filteredPositions"
                      :key="position.position_id"
                      :value="position.position_id"
                      :disabled="position.capacityReached"
                    >
                      {{ position.position_name }}{{ position.capacityReached ? ' - Full' : '' }}
                    </option>
                  </select>
                  <p v-if="selectedTenantIsFederation !== null && roleForm.tenant_id" class="field-hint">
                    <span v-if="selectedTenantIsFederation">
                      Showing SKF positions + Chief of Staff, Administrative Aide
                    </span>
                    <span v-else>
                      Showing SK barangay positions
                    </span>
                  </p>
                </div>

                <div class="form-field form-field--checkbox">
                  <label class="checkbox-label">
                    <input type="checkbox" v-model="roleForm.is_primary_tenant" />
                    Set as primary tenant
                  </label>
                </div>
              </div>

              <p v-if="roleError" class="form-error">{{ roleError }}</p>
            </div>
            <div class="modal-footer">
              <button class="btn-ghost" @click="showRoleModal = false">Cancel</button>
              <button
                v-if="canSubmitRole"
                class="btn-primary"
                @click="assignRole"
                :disabled="assigning"
              >
                {{ assigning ? 'Assigning...' : 'Assign Role' }}
              </button>
            </div>
          </div>
        </div>
      </Transition>
      <!-- ── Confirmation Modal ──────────────────────────────────── -->
      <Transition name="fade">
        <div v-if="confirmModal.show" class="modal-backdrop modal-backdrop--top" @click.self="onCancelConfirm">
          <div class="modal modal--confirm">
            <div class="modal-header">
              <h2>{{ confirmModal.title }}</h2>
            </div>
            <div class="modal-body">
              <p class="confirm-message">{{ confirmModal.message }}</p>
            </div>
            <div class="modal-footer">
              <button class="btn-ghost" @click="onCancelConfirm">Cancel</button>
              <button :class="confirmModal.danger ? 'btn-danger-sm' : 'btn-primary'" @click="onConfirm">Confirm</button>
            </div>
          </div>
        </div>
      </Transition>

    </Teleport>
  </div>

  <div v-else-if="loadingAccount" class="view-loading">
    <div class="spinner"></div>
  </div>
</template>

<script>
import { useAccountDetailView } from './scripts/useAccountDetailView'

export default {
  name: 'AccountDetailView',
  props: {
    id: {
      type: String,
      default: '',
    },
  },
  setup(props) {
    return useAccountDetailView(props)
  },
}
</script>

<style scoped>
.view { padding: 32px; display: flex; flex-direction: column; gap: 20px; max-width: 1100px; margin: 0 auto; width: 100%; }
.view-loading { display: flex; align-items: center; justify-content: center; height: 50vh; }

.btn-back {
  display: inline-flex; align-items: center; gap: 6px;
  font-size: 13px; color: var(--c-text-muted);
  background: none; border: none; cursor: pointer;
  padding: 0; transition: color 0.12s;
}
.btn-back:hover { color: var(--c-primary); }
.btn-back svg { width: 16px; height: 16px; }

.detail-layout { display: grid; grid-template-columns: 240px 1fr; gap: 20px; align-items: start; }

.profile-card {
  background: #fff;
  border: 1px solid var(--c-border);
  border-radius: var(--radius-lg);
  padding: 24px;
  display: flex; flex-direction: column; align-items: center;
  text-align: center; gap: 8px;
  box-shadow: var(--shadow-sm);
}
.profile-avatar {
  width: 64px; height: 64px;
  background: var(--c-primary-pale);
  color: var(--c-primary);
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-family: var(--font-display); font-size: 22px;
  margin-bottom: 8px;
}
.profile-name  { font-family: var(--font-display); font-size: 18px; line-height: 1.2; }
.profile-email { font-size: 12px; color: var(--c-text-muted); word-break: break-all; }
.mt-8          { margin-top: 4px; }

.profile-meta  { width: 100%; margin-top: 12px; display: flex; flex-direction: column; gap: 0; border-top: 1px solid var(--c-border-light); padding-top: 12px; }
.meta-row { display: flex; justify-content: space-between; align-items: center; padding: 6px 0; font-size: 12px; border-bottom: 1px solid var(--c-border-light); }
.meta-row:last-child { border-bottom: none; }
.meta-label { color: var(--c-text-muted); }
.meta-code  { font-family: monospace; font-size: 11px; color: var(--c-text-muted); }

.profile-actions { width: 100%; display: flex; flex-direction: column; gap: 8px; margin-top: 8px; }
.admin-protected-badge {
  display: inline-block; margin-bottom: 8px; padding: 4px 10px;
  border-radius: 20px; background: #FFF3CD; color: #856404;
  font-size: 11px; font-weight: 600;
}
.modal--confirm { max-width: 420px; }
.confirm-message { font-size: 14px; line-height: 1.6; color: var(--c-text); }
.btn-danger-sm {
  padding: 9px 16px; background: var(--c-danger); color: white;
  border: none; border-radius: var(--radius-md);
  font-size: 13px; font-weight: 600; cursor: pointer;
}
.btn-danger-sm:hover { background: #c0392b; }
.btn-edit-full {
  width: 100%; padding: 9px;
  background: var(--c-primary-pale); color: var(--c-primary);
  border: 1px solid rgba(26,82,118,0.15); border-radius: var(--radius-md);
  font-size: 13px; font-weight: 600; cursor: pointer; transition: all 0.15s;
}
.btn-edit-full:hover { background: var(--c-primary); color: white; }
.btn-toggle-status {
  width: 100%; padding: 9px;
  border: 1px solid; border-radius: var(--radius-md);
  font-size: 13px; font-weight: 600; cursor: pointer; transition: all 0.15s;
}
.btn-deactivate { background: var(--c-danger-bg); color: var(--c-danger); border-color: rgba(192,57,43,0.2); }
.btn-deactivate:hover { background: var(--c-danger); color: white; }
.btn-activate   { background: var(--c-success-bg); color: var(--c-success); border-color: rgba(30,132,73,0.2); }
.btn-activate:hover { background: var(--c-success); color: white; }

.tabs-column { display: flex; flex-direction: column; gap: 0; }
.tabs-header {
  display: flex; gap: 0;
  border-bottom: 2px solid var(--c-border-light);
  background: #fff;
  border-radius: var(--radius-lg) var(--radius-lg) 0 0;
  padding: 0 4px;
  border: 1px solid var(--c-border);
  border-bottom: none;
}
.tab-btn {
  padding: 12px 20px;
  font-size: 13px; font-weight: 500;
  color: var(--c-text-muted);
  background: none; border: none;
  border-bottom: 2px solid transparent;
  cursor: pointer; transition: all 0.15s;
}
.tab-btn:hover { color: var(--c-text); }
.tab-btn--active { color: var(--c-primary); border-bottom-color: var(--c-primary); font-weight: 600; }

.tab-content {
  background: #fff;
  border: 1px solid var(--c-border);
  border-top: none;
  border-radius: 0 0 var(--radius-lg) var(--radius-lg);
  min-height: 300px;
  box-shadow: var(--shadow-sm);
}
.tab-content-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid var(--c-border-light);
}
.tab-content-header h3 { font-size: 14px; font-weight: 600; }
.btn-sm { padding: 6px 12px !important; font-size: 12px !important; }

.empty-state {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  padding: 48px; gap: 12px; color: var(--c-text-light); font-size: 13px;
}
.empty-state svg { width: 40px; height: 40px; opacity: 0.4; }

.role-list { display: flex; flex-direction: column; padding: 16px 20px; gap: 8px; }
.role-card {
  display: flex; align-items: center; justify-content: space-between;
  padding: 12px 16px;
  border: 1px solid var(--c-border-light);
  border-radius: var(--radius-md);
  background: var(--c-bg);
  transition: border-color 0.12s;
}
.role-card:hover { border-color: var(--c-border); }
.role-card__left { display: flex; align-items: center; gap: 12px; }
.role-badge {
  font-size: 10px; font-weight: 700; letter-spacing: 0.06em;
  text-transform: uppercase;
  padding: 3px 8px; border-radius: 20px;
}
.role-badge--primary  { background: var(--c-primary-pale); color: var(--c-primary); }
.role-badge--secondary { background: #EEF0F3; color: var(--c-text-muted); }
.role-info { display: flex; flex-direction: column; }
.role-tenant   { font-size: 13px; font-weight: 600; color: var(--c-text); }
.role-position { font-size: 12px; color: var(--c-text-muted); }
.role-card__right { display: flex; align-items: center; gap: 8px; }

.btn-icon-sm {
  width: 26px; height: 26px;
  display: flex; align-items: center; justify-content: center;
  background: none; border: 1px solid transparent;
  border-radius: var(--radius-sm); cursor: pointer;
  color: var(--c-text-light); transition: all 0.12s;
}
.btn-icon-sm svg { width: 13px; height: 13px; }
.btn-icon-sm:hover { color: var(--c-danger); border-color: var(--c-danger); background: var(--c-danger-bg); }

.tab-loading { display: flex; align-items: center; gap: 10px; padding: 24px 20px; color: var(--c-text-muted); font-size: 13px; }
.history-list { display: flex; flex-direction: column; }
.history-row {
  display: flex; align-items: center; gap: 12px;
  padding: 10px 20px;
  border-bottom: 1px solid var(--c-border-light);
}
.history-row:last-child { border-bottom: none; }
.history-icon {
  width: 28px; height: 28px;
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.history-icon svg { width: 14px; height: 14px; }
.history-icon--login  { background: var(--c-success-bg); color: var(--c-success); }
.history-icon--logout { background: var(--c-danger-bg);  color: var(--c-danger); }
.history-info { flex: 1; display: flex; flex-direction: column; }
.history-type { font-size: 12px; font-weight: 600; }
.history-meta { font-size: 11px; color: var(--c-text-muted); }
.history-time { font-size: 11px; color: var(--c-text-light); white-space: nowrap; }
.count-badge { font-size: 11px; background: var(--c-border-light); color: var(--c-text-muted); padding: 2px 8px; border-radius: 20px; }

.modal-backdrop--top { z-index: 1100 !important; }
.modal-backdrop {
  position: fixed; inset: 0; background: rgba(26,35,50,0.4);
  backdrop-filter: blur(4px);
  display: flex; align-items: center; justify-content: center; z-index: 1000; padding: 16px;
}
.modal { background: #fff; border-radius: var(--radius-xl); box-shadow: var(--shadow-lg); width: 100%; max-width: 480px; overflow-y: auto; }
.modal-header { display: flex; align-items: center; justify-content: space-between; padding: 20px 24px 16px; border-bottom: 1px solid var(--c-border-light); }
.modal-header h2 { font-family: var(--font-display); font-size: 20px; }
.modal-body  { padding: 20px 24px; }
.modal-footer { display: flex; justify-content: flex-end; gap: 10px; padding: 16px 24px; border-top: 1px solid var(--c-border-light); }

.form-stack { display: flex; flex-direction: column; gap: 16px; }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
.form-field { display: flex; flex-direction: column; gap: 5px; }
.form-field label { font-size: 11px; font-weight: 600; color: var(--c-text-muted); letter-spacing: 0.04em; text-transform: uppercase; }
.form-field input, .form-field select {
  padding: 9px 12px; border: 1px solid var(--c-border); border-radius: var(--radius-md);
  font-size: 13px; color: var(--c-text); background: var(--c-bg); outline: none; transition: border 0.15s;
}
.form-field input:focus, .form-field select:focus { border-color: var(--c-primary); }
.form-field select:disabled { opacity: 0.5; cursor: not-allowed; }
.checkbox-label { display: flex; align-items: center; gap: 8px; font-size: 13px; cursor: pointer; }
.checkbox-label input { width: auto; }
.form-error { margin-top: 12px; font-size: 12px; color: var(--c-danger); }
.field-hint { font-size: 11px; color: var(--c-text-light); margin-top: 2px; }

.locked-field {
  display: flex; align-items: center; gap: 8px;
  padding: 9px 12px;
  border: 1px solid var(--c-border);
  border-radius: var(--radius-md);
  background: var(--c-border-light);
  font-size: 13px; color: var(--c-text-muted);
  cursor: not-allowed;
}
.locked-field svg { width: 14px; height: 14px; flex-shrink: 0; color: var(--c-text-light); }

.btn-primary {
  display: flex; align-items: center; gap: 6px;
  padding: 9px 16px; background: var(--c-primary); color: white;
  border: none; border-radius: var(--radius-md); font-size: 13px; font-weight: 600;
  cursor: pointer; transition: background 0.15s;
}
.btn-primary:hover:not(:disabled) { background: var(--c-primary-light); }
.btn-primary:disabled { opacity: 0.65; cursor: not-allowed; }
.btn-ghost {
  padding: 9px 16px; background: transparent; color: var(--c-text-muted);
  border: 1px solid var(--c-border); border-radius: var(--radius-md);
  font-size: 13px; font-weight: 500; cursor: pointer; transition: all 0.15s;
}
.btn-ghost:hover { border-color: var(--c-text-muted); color: var(--c-text); }
.btn-icon {
  width: 30px; height: 30px;
  display: flex; align-items: center; justify-content: center;
  background: transparent; border: 1px solid var(--c-border); border-radius: var(--radius-sm);
  cursor: pointer; color: var(--c-text-muted); transition: all 0.12s;
}
.btn-icon svg { width: 14px; height: 14px; }
.btn-icon:hover { border-color: var(--c-primary); color: var(--c-primary); }
.spinner { width: 20px; height: 20px; border: 2px solid var(--c-border); border-top-color: var(--c-primary); border-radius: 50%; animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
</style>
