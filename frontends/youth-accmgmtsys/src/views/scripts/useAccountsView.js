import { onMounted, ref, computed } from 'vue'
import { accountsApi, tenantsApi } from '@/composables/api'

// Seed admin is always account_id 1 — immutable
const ADMIN_ACCOUNT_ID = 1

export function useAccountsView() {
  const accounts    = ref([])
  const pagination  = ref(null)
  const tenants     = ref([])
  const positions   = ref([])
  const loading     = ref(false)
  const search      = ref('')
  const statusFilter   = ref('')
  const tenantFilter   = ref('')
  const positionFilter = ref('')
  const currentPage    = ref(1)

  // ── Create modal ──────────────────────────────────────────────────────────
  const showCreateModal = ref(false)
  const creating        = ref(false)
  const createError     = ref('')
  const newAccount      = ref({
    auth_external_id: '', first_name: '', middle_name: '',
    last_name: '', contact_email: '', contact_number: '',
  })

  // ── Import modal ──────────────────────────────────────────────────────────
  const showImportModal  = ref(false)
  const importing        = ref(false)
  // 'idle' | 'loading' | 'success' | 'failed'
  const importStatus     = ref('idle')
  const importStatusMsg  = ref('')
  const importError      = ref('')
  const importFile       = ref(null)
  const importResult     = ref(null)
  const importJob        = ref(null)
  let importPollTimer    = null
  const importProgress   = computed(() => {
    if (!importJob.value?.total_rows) return 0
    return Math.round((importJob.value.processed_rows / importJob.value.total_rows) * 100)
  })

  // ── Checkbox selection ────────────────────────────────────────────────────
  const selectedIds = ref(new Set())

  const hasSelection = computed(() => selectedIds.value.size > 0)

  const selectableAccounts = computed(() =>
    accounts.value.filter(a => a.account_id !== ADMIN_ACCOUNT_ID)
  )

  const allSelected = computed(() =>
    selectableAccounts.value.length > 0 &&
    selectableAccounts.value.every(a => selectedIds.value.has(a.account_id))
  )

  function toggleSelectAll() {
    if (allSelected.value) {
      selectableAccounts.value.forEach(a => selectedIds.value.delete(a.account_id))
    } else {
      selectableAccounts.value.forEach(a => selectedIds.value.add(a.account_id))
    }
    selectedIds.value = new Set(selectedIds.value)
  }

  function toggleSelect(accountId) {
    if (accountId === ADMIN_ACCOUNT_ID) return
    const s = new Set(selectedIds.value)
    if (s.has(accountId)) s.delete(accountId)
    else s.add(accountId)
    selectedIds.value = s
  }

  function clearSelection() {
    selectedIds.value = new Set()
  }

  // ── Confirmation modal ────────────────────────────────────────────────────
  const confirmModal = ref({
    show: false, title: '', message: '', action: null, danger: true,
  })

  function showConfirm({ title, message, action, danger = true }) {
    confirmModal.value = { show: true, title, message, action, danger }
  }

  async function onConfirm() {
    if (confirmModal.value.action) await confirmModal.value.action()
    confirmModal.value.show = false
  }

  function onCancelConfirm() {
    confirmModal.value.show = false
  }

  // ── Debounce ──────────────────────────────────────────────────────────────
  let debounceTimer = null
  function debouncedFetch() {
    clearTimeout(debounceTimer)
    debounceTimer = setTimeout(() => { currentPage.value = 1; fetchAccounts() }, 350)
  }

  // ── Data fetching ─────────────────────────────────────────────────────────
  async function fetchAccounts() {
    loading.value = true
    try {
      const params = { page: currentPage.value, page_size: 20 }
      if (search.value)        params.search      = search.value
      if (statusFilter.value)  params.status      = statusFilter.value
      if (tenantFilter.value)  params.tenant_id   = tenantFilter.value
      if (positionFilter.value) params.position_id = positionFilter.value
      const res = await accountsApi.list(params)
      accounts.value   = res.data.items
      pagination.value = { ...res.data }
    } finally {
      loading.value = false
    }
  }

  async function fetchTenants() {
    const [tr, pr] = await Promise.all([tenantsApi.list(), tenantsApi.positions()])
    tenants.value   = tr.data
    positions.value = pr.data
  }

  function changePage(page) {
    currentPage.value = page
    clearSelection()
    fetchAccounts()
  }

  // ── Create account ────────────────────────────────────────────────────────
  function openCreateModal() {
    newAccount.value = { auth_external_id: '', first_name: '', middle_name: '', last_name: '', contact_email: '', contact_number: '' }
    createError.value     = ''
    showCreateModal.value = true
  }

  function requestCreateAccount() {
    if (!newAccount.value.auth_external_id) { createError.value = 'Authentik External ID is required.'; return }
    const name = [newAccount.value.first_name, newAccount.value.last_name].filter(Boolean).join(' ') || 'this account'
    showConfirm({
      title: 'Create Account', danger: false,
      message: `Are you sure you want to create an account for ${name}?`,
      action: createAccount,
    })
  }

  async function createAccount() {
    creating.value = true; createError.value = ''
    try {
      await accountsApi.create(newAccount.value)
      showCreateModal.value = false
      await fetchAccounts()
    } catch (e) {
      createError.value = e.response?.data?.detail || 'Failed to create account.'
      showCreateModal.value = true
    } finally {
      creating.value = false
    }
  }

  // ── Import ────────────────────────────────────────────────────────────────
  function openImportModal() {
    showImportModal.value = true
    importError.value     = ''
    importFile.value      = null
    importResult.value    = null
    importJob.value       = null
    importStatus.value    = 'idle'
    importStatusMsg.value = ''
  }

  function closeImportModal() {
    showImportModal.value = false
    importError.value     = ''
    importFile.value      = null
    importResult.value    = null
    importJob.value       = null
    importStatus.value    = 'idle'
    importStatusMsg.value = 'Import queued...'
    clearImportPolling()
  }

  function handleImportFileChange(event) {
    const [file] = event.target.files || []; importFile.value = file || null
  }

  function requestImport() {
    if (!importFile.value) { importError.value = 'Please choose a spreadsheet file first.'; return }
    showConfirm({
      title: 'Import Accounts', danger: false,
      message: `Are you sure you want to import accounts from "${importFile.value.name}"? Existing accounts with matching IDs will be updated.`,
      action: submitImport,
    })
  }

  async function submitImport() {
    importing.value       = true
    importStatus.value    = 'loading'
    importStatusMsg.value = ''
    importError.value     = ''
    try {
      const fd = new FormData(); fd.append('file', importFile.value)
      const res = await accountsApi.import(fd)
      importJob.value       = res.data
      importStatusMsg.value = res.data.message || 'Import started...'
      pollImportJob(res.data.job_id)
    } catch (e) {
      importStatus.value    = 'failed'
      importStatusMsg.value = e.response?.data?.detail || 'Import failed. Please check your file and try again.'
      importError.value     = importStatusMsg.value
      importing.value       = false
    }
  }

  function clearImportPolling() {
    if (importPollTimer) {
      clearTimeout(importPollTimer)
      importPollTimer = null
    }
  }

  async function pollImportJob(jobId) {
    clearImportPolling()
    try {
      const res = await accountsApi.importStatus(jobId)
      importJob.value = res.data
      importStatusMsg.value = res.data.message || 'Import running...'

      if (res.data.status === 'succeeded') {
        importResult.value    = res.data.result
        importStatus.value    = 'success'
        importStatusMsg.value = `Import complete - ${res.data.result.created} created, ${res.data.result.updated} updated, ${res.data.result.skipped} skipped.`
        importing.value       = false
        await fetchAccounts()
        return
      }

      if (res.data.status === 'failed') {
        importStatus.value    = 'failed'
        importStatusMsg.value = res.data.error || 'Import failed. Please check your file and try again.'
        importError.value     = importStatusMsg.value
        importing.value       = false
        return
      }

      importPollTimer = setTimeout(() => pollImportJob(jobId), 1500)
    } catch (e) {
      importStatus.value    = 'failed'
      importStatusMsg.value = e.response?.data?.detail || 'Could not check import status.'
      importError.value     = importStatusMsg.value
      importing.value       = false
    }
  }

  async function downloadImportTemplate() {
    try {
      const res  = await accountsApi.importTemplate()
      const url  = URL.createObjectURL(res.data)
      const link = document.createElement('a')
      link.href = url; link.download = 'accounts-import-template.xlsx'
      document.body.appendChild(link); link.click()
      document.body.removeChild(link); URL.revokeObjectURL(url)
    } catch (e) {
      importError.value = e.response?.data?.detail || 'Failed to download the import template.'
    }
  }

  // ── Bulk deactivate ───────────────────────────────────────────────────────
  function requestBulkDeactivate() {
    const ids = [...selectedIds.value]; const count = ids.length
    showConfirm({
      title: 'Deactivate Accounts', danger: true,
      message: `Are you sure you want to deactivate ${count} selected account${count !== 1 ? 's' : ''}? All their roles will also be deactivated.`,
      action: async () => {
        await accountsApi.bulkDeactivate(ids)
        clearSelection()
        await fetchAccounts()
      },
    })
  }

  // ── Helpers ───────────────────────────────────────────────────────────────
  function getInitials(name) {
    if (!name) return '?'
    const parts = name.split(' ').filter(Boolean)
    return parts.length >= 2 ? (parts[0][0] + parts[parts.length - 1][0]).toUpperCase() : name.slice(0, 2).toUpperCase()
  }

  function formatDate(value) {
    if (!value) return '—'
    return new Date(value).toLocaleDateString('en-PH', { year: 'numeric', month: 'short', day: 'numeric' })
  }

  function isAdmin(account) { return account.account_id === ADMIN_ACCOUNT_ID }

  onMounted(() => { fetchAccounts(); fetchTenants() })

  return {
    accounts, pagination, tenants, positions, loading,
    search, statusFilter, tenantFilter, positionFilter, currentPage,
    showCreateModal, creating, createError, newAccount,
    showImportModal, importing, importStatus, importStatusMsg, importError, importFile, importResult, importJob, importProgress,
    selectedIds, hasSelection, allSelected,
    confirmModal, ADMIN_ACCOUNT_ID,
    debouncedFetch, fetchAccounts, changePage,
    openCreateModal, requestCreateAccount,
    toggleSelect, toggleSelectAll, clearSelection,
    openImportModal, closeImportModal, handleImportFileChange,
    requestImport, submitImport, downloadImportTemplate,
    requestBulkDeactivate,
    showConfirm, onConfirm, onCancelConfirm,
    getInitials, formatDate, isAdmin,
  }
}
