import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { accountsApi, rolesApi, tenantsApi } from '@/composables/api'

const ADMIN_ACCOUNT_ID = 1

const BLOCKED_ASSIGN_ROLE_POSITIONS = new Set([
  'Account Management Administrator', 'SK Councilor', 'SK Secretary',
  'SK Treasurer', 'Chief of Staff', 'Administrative Aide',
])

const CAPACITY = { 'SKF Member': 19, 'SK Councilor': 7 }
function getCapacity(name) { return CAPACITY[name] ?? 1 }

export function useAccountDetailView(props) {
  const route     = useRoute()
  const accountId = props.id || route.params.id

  const account         = ref(null)
  const loadingAccount  = ref(true)
  const loginHistory    = ref([])
  const historyLoading  = ref(false)
  const tenants         = ref([])
  const positions       = ref([])
  const roleCapacity    = ref({})

  const activeTab = ref('roles')
  const tabs      = [{ key: 'roles', label: 'Roles' }, { key: 'history', label: 'Login History' }]

  const showEditModal = ref(false)
  const showRoleModal = ref(false)
  const saving        = ref(false)
  const assigning     = ref(false)
  const roleError     = ref('')
  const editForm      = ref({})
  const roleForm      = ref({ tenant_id: '', position_id: '', is_primary_tenant: false })

  // ── Confirmation modal ────────────────────────────────────────────────────
  const confirmModal = ref({ show: false, title: '', message: '', action: null, danger: true })

  function showConfirm({ title, message, action, danger = true }) {
    confirmModal.value = { show: true, title, message, action, danger }
  }

  async function onConfirm() {
    if (confirmModal.value.action) await confirmModal.value.action()
    confirmModal.value.show = false
  }

  function onCancelConfirm() { confirmModal.value.show = false }

  // ── Admin guard ───────────────────────────────────────────────────────────
  const isAdminAccount = computed(() => parseInt(accountId) === ADMIN_ACCOUNT_ID)

  // ── Role computed ─────────────────────────────────────────────────────────
  const hasBlockedAssignRolePosition = computed(() =>
    account.value?.tenant_roles?.some(r => BLOCKED_ASSIGN_ROLE_POSITIONS.has(r.position_name)) ?? false
  )

  const isChairpersonAccount = computed(() =>
    account.value?.tenant_roles?.some(r => r.position_name === 'SK Chairperson') ?? false
  )

  const selectedTenantId = computed(() => {
    if (isChairpersonAccount.value)
      return tenants.value.find(t => t.is_federation)?.tenant_id ?? null
    return roleForm.value.tenant_id ? parseInt(roleForm.value.tenant_id, 10) : null
  })

  const selectedTenantIsFederation = computed(() => {
    if (!selectedTenantId.value) return null
    return tenants.value.find(t => t.tenant_id === selectedTenantId.value)?.is_federation ?? null
  })

  const canShowAssignRole = computed(() => {
    if (!account.value || isAdminAccount.value) return false
    if (hasBlockedAssignRolePosition.value) return false
    const roles = account.value.tenant_roles ?? []
    if (isChairpersonAccount.value && roles.length >= 2) return false
    return true
  })

  const availableTenants = computed(() => {
    const existing = new Set((account.value?.tenant_roles ?? []).map(r => r.tenant_id))
    return tenants.value.filter(t => !existing.has(t.tenant_id))
  })

  const filteredPositions = computed(() => {
    const isFed = selectedTenantIsFederation.value
    if (isFed === null && !isChairpersonAccount.value) return []
    return positions.value
      .filter(p => {
        const n = p.position_name
        if (n === 'Account Management Administrator') return false
        if (isFed) return n.startsWith('SKF ') || n === 'Chief of Staff' || n === 'Administrative Aide'
        return n.startsWith('SK ')
      })
      .map(p => ({
        ...p,
        capacityReached: (roleCapacity.value[p.position_name] ?? 0) >= getCapacity(p.position_name),
      }))
  })

  const canSubmitRole = computed(() => {
    if (!roleForm.value.position_id) return false
    const p = filteredPositions.value.find(x => x.position_id === parseInt(roleForm.value.position_id, 10))
    return p ? !p.capacityReached : false
  })

  // ── Data fetching ─────────────────────────────────────────────────────────
  async function fetchAccount() {
    loadingAccount.value = true
    try {
      const res  = await accountsApi.get(accountId)
      account.value = res.data
      editForm.value = {
        first_name: account.value.first_name, middle_name: account.value.middle_name,
        last_name: account.value.last_name, contact_email: account.value.contact_email,
        contact_number: account.value.contact_number,
      }
    } finally { loadingAccount.value = false }
  }

  async function fetchHistory() {
    historyLoading.value = true
    try { const res = await accountsApi.loginHistory(accountId); loginHistory.value = res.data }
    finally { historyLoading.value = false }
  }

  async function fetchRoleCapacity() {
    if (!selectedTenantId.value) { roleCapacity.value = {}; return }
    try { roleCapacity.value = (await rolesApi.capacity(selectedTenantId.value)).data }
    catch { roleCapacity.value = {} }
  }

  // ── Actions ───────────────────────────────────────────────────────────────
  function openRoleModal() {
    roleForm.value = { tenant_id: '', position_id: '', is_primary_tenant: false }
    roleError.value = ''
    if (isChairpersonAccount.value) {
      const fed = tenants.value.find(t => t.is_federation)
      if (fed) roleForm.value.tenant_id = fed.tenant_id
    }
    showRoleModal.value = true
    fetchRoleCapacity()
  }

  function onTenantChange() { roleForm.value.position_id = '' }

  function requestEditSave() {
    showConfirm({
      title: 'Save Changes', danger: false,
      message: `Are you sure you want to update the profile of ${account.value?.full_name}?`,
      action: saveEdit,
    })
  }

  async function saveEdit() {
    saving.value = true
    try { await accountsApi.update(accountId, editForm.value); showEditModal.value = false; await fetchAccount() }
    finally { saving.value = false }
  }

  function requestToggleStatus() {
    if (isAdminAccount.value) return
    const isActive = account.value.account_status === 'Active'
    showConfirm({
      title:   isActive ? 'Deactivate Account' : 'Activate Account',
      danger:  isActive,
      message: isActive
        ? `Are you sure you want to deactivate ${account.value?.full_name}? All their roles will also be deactivated.`
        : `Are you sure you want to activate ${account.value?.full_name}?`,
      action: toggleStatus,
    })
  }

  async function toggleStatus() {
    if (account.value.account_status === 'Active') await accountsApi.deactivate(accountId)
    else await accountsApi.activate(accountId)
    await fetchAccount()
  }

  async function assignRole() {
    const tenantId = selectedTenantId.value
    if (!tenantId || !roleForm.value.position_id) { roleError.value = 'Tenant and position are required.'; return }
    assigning.value = true; roleError.value = ''
    try {
      await rolesApi.assign({
        account_id: parseInt(accountId, 10), tenant_id: tenantId,
        position_id: parseInt(roleForm.value.position_id, 10),
        is_primary_tenant: roleForm.value.is_primary_tenant,
      })
      showRoleModal.value = false
      roleForm.value = { tenant_id: '', position_id: '', is_primary_tenant: false }
      await fetchAccount(); await fetchRoleCapacity()
    } catch (e) { roleError.value = e.response?.data?.detail || 'Failed to assign role.' }
    finally { assigning.value = false }
  }

  function requestRemoveRole(roleId, tenantName) {
    showConfirm({
      title: 'Remove Role', danger: true,
      message: `Are you sure you want to remove the role assignment for ${tenantName}?`,
      action: async () => { await rolesApi.remove(roleId); await fetchAccount(); await fetchRoleCapacity() },
    })
  }

  // ── Helpers ───────────────────────────────────────────────────────────────
  function getInitials(name) {
    if (!name) return '?'
    const parts = name.split(' ').filter(Boolean)
    return parts.length >= 2 ? (parts[0][0] + parts[parts.length - 1][0]).toUpperCase() : name.slice(0, 2).toUpperCase()
  }

  function formatDate(v) {
    return v ? new Date(v).toLocaleDateString('en-PH', { year: 'numeric', month: 'short', day: 'numeric' }) : '--'
  }

  function formatDateTime(v) {
    return v ? new Date(v).toLocaleString('en-PH', { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }) : '--'
  }

  watch(activeTab, tab => { if (tab === 'history' && loginHistory.value.length === 0) fetchHistory() })
  watch(selectedTenantId, () => { if (showRoleModal.value) fetchRoleCapacity() })

  onMounted(async () => {
    await fetchAccount()
    const [tr, pr] = await Promise.all([tenantsApi.list(), tenantsApi.positions()])
    tenants.value = tr.data; positions.value = pr.data
  })

  return {
    account, loadingAccount, loginHistory, historyLoading,
    tenants, positions, roleCapacity, activeTab, tabs,
    showEditModal, showRoleModal, saving, assigning, roleError, editForm, roleForm,
    confirmModal, isAdminAccount,
    isChairpersonAccount, canShowAssignRole, selectedTenantIsFederation,
    availableTenants, filteredPositions, canSubmitRole,
    openRoleModal, onTenantChange,
    requestEditSave, requestToggleStatus,
    assignRole, requestRemoveRole,
    onConfirm, onCancelConfirm,
    getInitials, formatDate, formatDateTime,
  }
}
