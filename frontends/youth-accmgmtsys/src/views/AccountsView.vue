<template>
  <div class="view">
    <div class="page-header">
      <div class="page-header__left">
        <h1 class="page-title">Accounts</h1>
        <p class="page-desc">Manage SK official accounts and their role assignments.</p>
      </div>
      <div class="header-actions">
        <!-- Bulk deactivate — shown only when items are selected -->
        <Transition name="slide-fade">
          <button v-if="hasSelection" class="btn-danger" @click="requestBulkDeactivate">
            <svg viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M13.477 14.89A6 6 0 015.11 6.524L13.477 14.89zm1.414-1.414A6 6 0 006.524 5.11L14.89 13.476zM18 10a8 8 0 11-16 0 8 8 0 0116 0z" clip-rule="evenodd"/></svg>
            Deactivate ({{ selectedIds.size }})
          </button>
        </Transition>
        <button class="btn-ghost" @click="openImportModal">Import Accounts</button>
        <button class="btn-primary" @click="openCreateModal">
          <svg viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clip-rule="evenodd"/></svg>
          New Account
        </button>
      </div>
    </div>

    <div class="filters-bar">
      <div class="search-wrap">
        <svg viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clip-rule="evenodd"/>
        </svg>
        <input v-model="search" type="text" placeholder="Search by name or email..." @input="debouncedFetch" />
      </div>
      <select v-model="statusFilter" @change="fetchAccounts">
        <option value="">All Statuses</option>
        <option value="Active">Active</option>
        <option value="Inactive">Inactive</option>
      </select>
      <select v-model="tenantFilter" @change="fetchAccounts">
        <option value="">All Tenants</option>
        <option v-for="t in tenants" :key="t.tenant_id" :value="t.tenant_id">{{ t.tenant_name }}</option>
      </select>
      <select v-model="positionFilter" @change="fetchAccounts">
        <option value="">All Positions</option>
        <option v-for="p in positions" :key="p.position_id" :value="p.position_id">{{ p.position_name }}</option>
      </select>
    </div>

    <div class="table-card">
      <div v-if="loading" class="table-loading">
        <div class="spinner"></div>
        <span>Loading accounts...</span>
      </div>

      <table v-else class="data-table">
        <thead>
          <tr>
            <th class="th-check">
              <input
                type="checkbox"
                class="row-checkbox"
                :checked="allSelected"
                :indeterminate="hasSelection && !allSelected"
                @change="toggleSelectAll"
                title="Select all"
              />
            </th>
            <th>Name</th>
            <th>Email</th>
            <th>Tenant</th>
            <th>Position</th>
            <th>Status</th>
            <th>Synced</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="accounts.length === 0">
            <td colspan="8" class="table-empty">No accounts found.</td>
          </tr>
          <tr
            v-for="account in accounts"
            :key="account.account_id"
            class="table-row"
            :class="{ 'row--selected': selectedIds.has(account.account_id), 'row--admin': isAdmin(account) }"
            @click="$router.push(`/accounts/${account.account_id}`)"
          >
            <!-- Checkbox cell — stops row navigation -->
            <td class="td-check" @click.stop>
              <input
                v-if="!isAdmin(account)"
                type="checkbox"
                class="row-checkbox"
                :checked="selectedIds.has(account.account_id)"
                @change="toggleSelect(account.account_id)"
              />
              <!-- Admin gets a lock icon instead of checkbox -->
              <span v-else class="admin-lock" title="System Administrator — protected">
                <svg viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clip-rule="evenodd"/></svg>
              </span>
            </td>
            <td class="cell-name">
              <div class="account-avatar" :class="isAdmin(account) ? 'avatar--admin' : ''">
                {{ getInitials(account.full_name) }}
              </div>
              <div class="name-col">
                <span>{{ account.full_name || '—' }}</span>
                <span v-if="isAdmin(account)" class="admin-badge">Admin</span>
              </div>
            </td>
            <td class="cell-muted">{{ account.contact_email || '—' }}</td>
            <td class="cell-muted">{{ account.primary_tenant || '—' }}</td>
            <td class="cell-muted">{{ account.primary_position || '—' }}</td>
            <td>
              <span class="badge" :class="account.account_status === 'Active' ? 'badge--active' : 'badge--inactive'">
                {{ account.account_status }}
              </span>
            </td>
            <td class="cell-muted cell-date">{{ formatDate(account.synced_at) }}</td>
            <td class="cell-actions" @click.stop>
              <button class="btn-icon" @click="$router.push(`/accounts/${account.account_id}`)">
                <svg viewBox="0 0 20 20" fill="currentColor">
                  <path d="M10 12a2 2 0 100-4 2 2 0 000 4z"/>
                  <path fill-rule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clip-rule="evenodd"/>
                </svg>
              </button>
            </td>
          </tr>
        </tbody>
      </table>

      <div v-if="pagination && !loading" class="pagination">
        <span class="pagination-info">
          Showing {{ (pagination.page - 1) * pagination.page_size + 1 }}–{{ Math.min(pagination.page * pagination.page_size, pagination.total) }}
          of {{ pagination.total }}
        </span>
        <div class="pagination-controls">
          <button :disabled="pagination.page <= 1" @click="changePage(pagination.page - 1)">
            <svg viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clip-rule="evenodd"/></svg>
          </button>
          <span class="page-num">{{ pagination.page }} / {{ pagination.total_pages }}</span>
          <button :disabled="pagination.page >= pagination.total_pages" @click="changePage(pagination.page + 1)">
            <svg viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd"/></svg>
          </button>
        </div>
      </div>
    </div>

    <Teleport to="body">

      <!-- ── Confirmation Modal ──────────────────────────────────────────── -->
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
              <button
                :class="confirmModal.danger ? 'btn-danger' : 'btn-primary'"
                @click="onConfirm"
              >
                Confirm
              </button>
            </div>
          </div>
        </div>
      </Transition>

      <!-- ── Create Account Modal ───────────────────────────────────────── -->
      <Transition name="fade">
        <div v-if="showCreateModal" class="modal-backdrop" @click.self="showCreateModal = false">
          <div class="modal">
            <div class="modal-header">
              <h2>New Account</h2>
              <button class="btn-icon" @click="showCreateModal = false">
                <svg viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"/></svg>
              </button>
            </div>
            <div class="modal-body">
              <div class="form-grid">
                <div class="form-field">
                  <label>Authentik External ID *</label>
                  <input v-model="newAccount.auth_external_id" placeholder="UUID from Authentik" />
                </div>
                <div class="form-field">
                  <label>First Name</label>
                  <input v-model="newAccount.first_name" placeholder="First name" />
                </div>
                <div class="form-field">
                  <label>Middle Name</label>
                  <input v-model="newAccount.middle_name" placeholder="Middle name" />
                </div>
                <div class="form-field">
                  <label>Last Name</label>
                  <input v-model="newAccount.last_name" placeholder="Last name" />
                </div>
                <div class="form-field">
                  <label>Contact Email</label>
                  <input v-model="newAccount.contact_email" type="email" placeholder="email@example.com" />
                </div>
                <div class="form-field">
                  <label>Contact Number</label>
                  <input v-model="newAccount.contact_number" placeholder="+63 9XX XXX XXXX" />
                </div>
              </div>
              <p v-if="createError" class="form-error">{{ createError }}</p>
            </div>
            <div class="modal-footer">
              <button class="btn-ghost" @click="showCreateModal = false">Cancel</button>
              <button class="btn-primary" @click="requestCreateAccount" :disabled="creating">
                <span v-if="creating" class="btn-spinner-sm"></span>
                {{ creating ? 'Creating...' : 'Create Account' }}
              </button>
            </div>
          </div>
        </div>
      </Transition>

      <!-- ── Import Modal ───────────────────────────────────────────────── -->
      <Transition name="fade">
        <div v-if="showImportModal" class="modal-backdrop" @click.self="closeImportModal">
          <div class="modal">
            <div class="modal-header">
              <h2>Import Accounts</h2>
              <button class="btn-icon" @click="closeImportModal">
                <svg viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"/></svg>
              </button>
            </div>
            <div class="modal-body">

              <!-- ── Loading overlay ──────────────────────────────────── -->
              <div v-if="importStatus === 'loading'" class="import-loading">
                <div class="import-spinner"></div>
                <p class="import-loading__title">Importing accounts…</p>
                <p class="import-loading__sub">{{ importStatusMsg || 'This may take a moment for large files.' }}</p>
                <div v-if="importJob" class="import-progress">
                  <div class="import-progress__bar">
                    <span :style="{ width: `${importProgress}%` }"></span>
                  </div>
                  <p>{{ importJob.processed_rows }} / {{ importJob.total_rows }} rows</p>
                </div>
              </div>

              <!-- ── Success state ────────────────────────────────────── -->
              <div v-else-if="importStatus === 'success'" class="import-done import-done--success">
                <svg class="import-done__icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>
                <p class="import-done__msg">{{ importStatusMsg }}</p>
                <div class="import-summary">
                  <span>Created: {{ importResult.created }}</span>
                  <span>Updated: {{ importResult.updated }}</span>
                  <span>Roles Created: {{ importResult.roles_created }}</span>
                  <span>Roles Updated: {{ importResult.roles_updated }}</span>
                  <span v-if="importResult.skipped">Skipped: {{ importResult.skipped }}</span>
                </div>
                <div v-if="importResult.warnings?.length" class="import-section">
                  <h3>Warnings</h3>
                  <ul class="import-list import-list--warning">
                    <li v-for="w in importResult.warnings" :key="`w-${w.row}`">Row {{ w.row }}: {{ w.message }}</li>
                  </ul>
                </div>
                <div v-if="importResult.errors?.length" class="import-section">
                  <h3>Skipped Rows</h3>
                  <ul class="import-list import-list--error">
                    <li v-for="e in importResult.errors" :key="`e-${e.row}`">Row {{ e.row }}: {{ e.message }}</li>
                  </ul>
                </div>
              </div>

              <!-- ── Failed state ──────────────────────────────────────── -->
              <div v-else-if="importStatus === 'failed'" class="import-done import-done--failed">
                <svg class="import-done__icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>
                <p class="import-done__msg">{{ importStatusMsg }}</p>
              </div>

              <!-- ── Idle — file selection ─────────────────────────────── -->
              <template v-else>
                <div class="import-note">
                  Upload a <code>.csv</code> or <code>.xlsx</code> file. Leave <strong>Auth External ID blank</strong> to auto-create the user in Authentik — a username and temporary password will be set automatically. If an ID is provided, the existing Authentik account is used.
                </div>
                <div class="import-actions">
                  <button class="btn-ghost" @click="downloadImportTemplate">Download Template</button>
                </div>
                <div class="form-field">
                  <label>Spreadsheet File</label>
                  <input type="file" accept=".csv,.xlsx" @change="handleImportFileChange" />
                </div>
                <p class="field-hint">Supported columns: Auth External ID, First Name, Middle Name, Last Name, Contact Email, Contact Number, Account Status, Tenant Name, Position Name, Is Primary Tenant, Role Status.</p>
              </template>

            </div>
            <div class="modal-footer">
              <button class="btn-ghost" @click="closeImportModal">
                {{ importStatus === 'success' || importStatus === 'failed' ? 'Close' : 'Cancel' }}
              </button>
              <button
                v-if="importStatus === 'idle'"
                class="btn-primary"
                @click="requestImport"
                :disabled="importing || !importFile"
              >
                Start Import
              </button>
              <button
                v-if="importStatus === 'failed'"
                class="btn-primary"
                @click="importStatus = 'idle'"
              >
                Try Again
              </button>
            </div>
          </div>
        </div>
      </Transition>

    </Teleport>
  </div>
</template>

<script>
import { useAccountsView } from './scripts/useAccountsView'
export default {
  name: 'AccountsView',
  setup() { return useAccountsView() },
}
</script>

<style scoped>
.view { padding: 32px; display: flex; flex-direction: column; gap: 20px; max-width: 1200px; margin: 0 auto; width: 100%; }

.page-header { display: flex; align-items: flex-start; justify-content: space-between; gap: 16px; }
.header-actions { display: flex; align-items: center; gap: 10px; }
.page-title  { font-family: var(--font-display); font-size: 26px; color: var(--c-text); margin-bottom: 4px; }
.page-desc   { font-size: 13px; color: var(--c-text-muted); }

.filters-bar { display: flex; gap: 10px; flex-wrap: wrap; }
.search-wrap {
  flex: 1; min-width: 220px;
  display: flex; align-items: center; gap: 8px;
  background: #fff; border: 1px solid var(--c-border);
  border-radius: var(--radius-md); padding: 0 12px;
}
.search-wrap svg { width: 15px; height: 15px; color: var(--c-text-light); flex-shrink: 0; }
.search-wrap input { flex: 1; border: none; background: none; outline: none; padding: 10px 0; font-size: 13px; color: var(--c-text); }

.filters-bar select {
  padding: 9px 32px 9px 12px; border: 1px solid var(--c-border);
  border-radius: var(--radius-md); background: #fff;
  font-size: 13px; color: var(--c-text); appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 20 20'%3E%3Cpath fill='%23566573' d='M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z'/%3E%3C/svg%3E");
  background-repeat: no-repeat; background-position: right 8px center;
  background-size: 16px; cursor: pointer; outline: none;
}

/* ── Table ─────────────────────────────────────────────── */
.table-card { background: #fff; border: 1px solid var(--c-border); border-radius: var(--radius-lg); overflow: hidden; box-shadow: var(--shadow-sm); }
.table-loading { display: flex; align-items: center; justify-content: center; gap: 12px; padding: 48px; color: var(--c-text-muted); font-size: 13px; }
.spinner { width: 20px; height: 20px; border: 2px solid var(--c-border); border-top-color: var(--c-primary); border-radius: 50%; animation: spin 0.8s linear infinite; }

.data-table { width: 100%; border-collapse: collapse; }
.data-table thead tr { border-bottom: 1px solid var(--c-border-light); background: #FAFBFC; }
.data-table th { padding: 11px 16px; font-size: 11px; font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase; color: var(--c-text-muted); text-align: left; white-space: nowrap; }
.th-check { width: 40px; padding-left: 16px; }

.table-row { border-bottom: 1px solid var(--c-border-light); cursor: pointer; transition: background 0.12s; }
.table-row:last-child { border-bottom: none; }
.table-row:hover { background: var(--c-primary-pale); }
.row--selected { background: #EEF5FF !important; }
.row--admin { background: #FFFDF0; }
.row--admin:hover { background: #FFF8D6 !important; }

.data-table td { padding: 12px 16px; font-size: 13px; vertical-align: middle; }
.td-check { width: 40px; padding-left: 16px; }
.cell-name  { display: flex; align-items: center; gap: 10px; font-weight: 500; }
.cell-muted { color: var(--c-text-muted); }
.cell-date  { font-size: 12px; }
.table-empty { text-align: center; color: var(--c-text-light); padding: 48px !important; }
.cell-actions { text-align: right; }

/* ── Checkbox ─────────────────────────────────────────── */
.row-checkbox {
  width: 15px; height: 15px; cursor: pointer;
  accent-color: var(--c-primary);
}

.admin-lock { display: flex; align-items: center; color: var(--c-text-light); opacity: 0.5; }
.admin-lock svg { width: 14px; height: 14px; }

/* ── Avatar / name ────────────────────────────────────── */
.account-avatar {
  width: 28px; height: 28px; background: var(--c-primary-pale); color: var(--c-primary);
  border-radius: 50%; display: flex; align-items: center; justify-content: center;
  font-size: 10px; font-weight: 700; flex-shrink: 0;
}
.avatar--admin { background: #FFF3CD; color: #856404; }

.name-col { display: flex; flex-direction: column; gap: 2px; }
.admin-badge {
  font-size: 10px; font-weight: 700; letter-spacing: 0.05em;
  background: #FFF3CD; color: #856404;
  padding: 1px 6px; border-radius: 20px; width: fit-content;
}

/* ── Pagination ───────────────────────────────────────── */
.pagination { display: flex; align-items: center; justify-content: space-between; padding: 12px 16px; border-top: 1px solid var(--c-border-light); }
.pagination-info { font-size: 12px; color: var(--c-text-muted); }
.pagination-controls { display: flex; align-items: center; gap: 8px; }
.pagination-controls button { width: 28px; height: 28px; display: flex; align-items: center; justify-content: center; border: 1px solid var(--c-border); border-radius: var(--radius-sm); background: #fff; cursor: pointer; transition: all 0.12s; }
.pagination-controls button svg { width: 14px; height: 14px; }
.pagination-controls button:hover:not(:disabled) { border-color: var(--c-primary); color: var(--c-primary); }
.pagination-controls button:disabled { opacity: 0.4; cursor: not-allowed; }
.page-num { font-size: 12px; color: var(--c-text-muted); min-width: 50px; text-align: center; }

/* ── Buttons ──────────────────────────────────────────── */
.btn-primary {
  display: flex; align-items: center; gap: 6px; padding: 9px 16px;
  background: var(--c-primary); color: white; border: none;
  border-radius: var(--radius-md); font-size: 13px; font-weight: 600;
  cursor: pointer; transition: background 0.15s; white-space: nowrap;
}
.btn-primary svg { width: 15px; height: 15px; }
.btn-primary:hover:not(:disabled) { background: var(--c-primary-light); }
.btn-primary:disabled { opacity: 0.65; cursor: not-allowed; }

.btn-ghost {
  padding: 9px 16px; background: transparent; color: var(--c-text-muted);
  border: 1px solid var(--c-border); border-radius: var(--radius-md);
  font-size: 13px; font-weight: 500; cursor: pointer; transition: all 0.15s;
}
.btn-ghost:hover { border-color: var(--c-text-muted); color: var(--c-text); }

.btn-danger {
  display: flex; align-items: center; gap: 6px; padding: 9px 16px;
  background: var(--c-danger); color: white; border: none;
  border-radius: var(--radius-md); font-size: 13px; font-weight: 600;
  cursor: pointer; transition: background 0.15s; white-space: nowrap;
}
.btn-danger svg { width: 15px; height: 15px; }
.btn-danger:hover { background: #c0392b; }

.btn-icon { width: 30px; height: 30px; display: flex; align-items: center; justify-content: center; background: transparent; border: 1px solid var(--c-border); border-radius: var(--radius-sm); cursor: pointer; color: var(--c-text-muted); transition: all 0.12s; }
.btn-icon svg { width: 14px; height: 14px; }
.btn-icon:hover { border-color: var(--c-primary); color: var(--c-primary); background: var(--c-primary-pale); }

/* ── Modals ───────────────────────────────────────────── */
.modal-backdrop { position: fixed; inset: 0; background: rgba(26,35,50,0.4); backdrop-filter: blur(4px); display: flex; align-items: center; justify-content: center; z-index: 1000; padding: 16px; }
.modal-backdrop--top { z-index: 1100; }
.modal { background: #fff; border-radius: var(--radius-xl); box-shadow: var(--shadow-lg); width: 100%; max-width: 520px; max-height: 90vh; overflow-y: auto; }
.modal--confirm { max-width: 420px; }
.modal-header { display: flex; align-items: center; justify-content: space-between; padding: 20px 24px 16px; border-bottom: 1px solid var(--c-border-light); }
.modal-header h2 { font-family: var(--font-display); font-size: 20px; }
.modal-body  { padding: 20px 24px; }
.modal-footer { display: flex; justify-content: flex-end; gap: 10px; padding: 16px 24px; border-top: 1px solid var(--c-border-light); }

.confirm-message { font-size: 14px; line-height: 1.6; color: var(--c-text); }

.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
.form-field { display: flex; flex-direction: column; gap: 5px; }
.form-field:first-child { grid-column: 1 / -1; }
.form-field label { font-size: 11px; font-weight: 600; color: var(--c-text-muted); letter-spacing: 0.04em; text-transform: uppercase; }
.form-field input { padding: 9px 12px; border: 1px solid var(--c-border); border-radius: var(--radius-md); font-size: 13px; color: var(--c-text); background: var(--c-bg); outline: none; transition: border 0.15s; }
.form-field input:focus { border-color: var(--c-primary); }
.form-error { margin-top: 12px; font-size: 12px; color: var(--c-danger); }
.field-hint { margin-top: 8px; font-size: 11px; line-height: 1.5; color: var(--c-text-light); }

.import-note { margin-bottom: 14px; padding: 12px 14px; border: 1px solid #F5D08A; border-radius: var(--radius-md); background: #FFF7E5; font-size: 12px; line-height: 1.5; color: #7A5A18; }
.import-results { margin-top: 16px; display: flex; flex-direction: column; gap: 14px; }
.import-actions { display: flex; justify-content: flex-start; margin-bottom: 14px; }
.import-summary { display: flex; flex-wrap: wrap; gap: 8px; }
.import-summary span { padding: 6px 10px; border-radius: 999px; background: var(--c-primary-pale); color: var(--c-primary); font-size: 12px; font-weight: 600; }
.import-section h3 { margin-bottom: 8px; font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.04em; color: var(--c-text-muted); }
.import-list { max-height: 180px; overflow: auto; margin: 0; padding-left: 18px; font-size: 12px; line-height: 1.5; }
.import-list--warning { color: #8A5A00; }
.import-list--error { color: var(--c-danger); }

.btn-spinner-sm { width: 12px; height: 12px; border: 2px solid rgba(255,255,255,0.3); border-top-color: white; border-radius: 50%; animation: spin 0.7s linear infinite; }

/* ── Import loading / done states ─────────────────────── */
.import-loading {
  display: flex; flex-direction: column; align-items: center;
  justify-content: center; gap: 12px; padding: 40px 0; text-align: center;
}
.import-spinner {
  width: 44px; height: 44px;
  border: 4px solid var(--c-border);
  border-top-color: var(--c-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
.import-loading__title { font-size: 16px; font-weight: 600; color: var(--c-text); }
.import-loading__sub   { font-size: 13px; color: var(--c-text-muted); }
.import-progress { width: 100%; max-width: 320px; display: flex; flex-direction: column; gap: 6px; align-items: center; }
.import-progress__bar { width: 100%; height: 8px; border-radius: 999px; overflow: hidden; background: var(--c-border-light); }
.import-progress__bar span { display: block; height: 100%; background: var(--c-primary); transition: width 0.2s ease; }
.import-progress p { font-size: 12px; color: var(--c-text-muted); }

.import-done { display: flex; flex-direction: column; align-items: center; gap: 10px; padding: 24px 0 8px; text-align: center; }
.import-done__icon { width: 48px; height: 48px; }
.import-done--success .import-done__icon { color: var(--c-success); }
.import-done--failed  .import-done__icon { color: var(--c-danger); }
.import-done__msg { font-size: 14px; font-weight: 500; color: var(--c-text); }
.import-done--success .import-done__msg { color: #1a7a3c; }
.import-done--failed  .import-done__msg { color: var(--c-danger); }

/* ── Animations ───────────────────────────────────────── */
.slide-fade-enter-active { transition: all 0.2s ease; }
.slide-fade-leave-active { transition: all 0.15s ease; }
.slide-fade-enter-from, .slide-fade-leave-to { opacity: 0; transform: translateX(8px); }

.fade-enter-active, .fade-leave-active { transition: opacity 0.2s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

@keyframes spin { to { transform: rotate(360deg); } }
</style>
