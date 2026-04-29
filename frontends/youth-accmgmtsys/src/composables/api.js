import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 120000,
  headers: { 'Content-Type': 'application/json' },
})

// ── Request interceptor — attach JWT ─────────────────────────────────────
api.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// ── Response interceptor — handle 401 globally ───────────────────────────
api.interceptors.response.use(
  res => res,
  err => {
    if (err.response?.status === 401) {
      localStorage.removeItem('access_token')
      window.location.href = '/'
    }
    return Promise.reject(err)
  }
)

// ── Auth ──────────────────────────────────────────────────────────────────
export const authApi = {
  loginEvent: () => api.post('/auth/login-event'),
  me:     () => api.get('/auth/me'),
  logout: () => api.post('/auth/logout'),
}

// ── Accounts ──────────────────────────────────────────────────────────────
export const accountsApi = {
  list:         (params)         => api.get('/accounts', { params }),
  get:          (id)             => api.get(`/accounts/${id}`),
  create:       (data)           => api.post('/accounts', data),
  import:       (formData)       => api.post('/accounts/import', formData, { headers: { 'Content-Type': 'multipart/form-data' }, timeout: 300000 }),
  importStatus: (jobId)          => api.get(`/accounts/import/${jobId}`),
  importTemplate: ()             => api.get('/accounts/template/import', { responseType: 'blob' }),
  update:       (id, data)       => api.patch(`/accounts/${id}`, data),
  activate:     (id)             => api.patch(`/accounts/${id}/activate`),
  deactivate:   (id)             => api.patch(`/accounts/${id}/deactivate`),
  bulkDeactivate: (ids)           => api.post('/accounts/bulk-deactivate', { account_ids: ids }),
  loginHistory: (id, limit = 50) => api.get(`/accounts/${id}/login-history`, { params: { limit } }),
}

// ── Tenants ───────────────────────────────────────────────────────────────
export const tenantsApi = {
  list:      ()           => api.get('/tenants'),
  get:       (id)         => api.get(`/tenants/${id}`),
  create:    (data)       => api.post('/tenants', data),
  update:    (id, data)   => api.patch(`/tenants/${id}`, data),
  positions: ()           => api.get('/tenants/positions/all'),
}

// ── Roles ─────────────────────────────────────────────────────────────────
export const rolesApi = {
  assign:   (data)     => api.post('/roles', data),
  get:      (id)       => api.get(`/roles/${id}`),
  update:   (id, data) => api.patch(`/roles/${id}`, data),
  remove:   (id)       => api.delete(`/roles/${id}`),
  capacity: (tenantId) => api.get('/roles/capacity', { params: { tenant_id: tenantId } }),
}

export default api
