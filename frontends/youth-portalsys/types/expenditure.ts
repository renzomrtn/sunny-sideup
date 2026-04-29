// ── Enums ─────────────────────────────────────────────────────────────────────

export type ExpenditureStatus = 'Unverified' | 'Verified' | 'Flagged'

export type VendorCategory =
  | 'Catering & Food Services'
  | 'Sports & Recreation'
  | 'Office & School Supplies'
  | 'Utilities & Communication'
  | 'Hardware & Construction'
  | 'Professional Services'
  | 'Transportation & Logistics'
  | 'General Merchandise'
  | 'Not Applicable'

// ── Snapshots ─────────────────────────────────────────────────────────────────

export interface LineItemSnapshot {
  line_item_id: number
  program_name: string
  budget_allocation: number
  fiscal_year: number
}

export interface UserSnapshot {
  role_id: number
  full_name: string
  position: string
  barangay?: string
}

// ── Core entities ──────────────────────────────────────────────────────────────

export interface Vendor {
  vendor_id: number
  tenant_id: number
  vendor_name: string
  category: VendorCategory
  address?: string
  created_at: string
}

export interface ExpenditureParticular {
  particular_id: number
  expenditure_id: number
  vendor_id?: number
  vendor?: Vendor
  particular_name: string
  amount_claimed: number
  date_of_expense: string
  file_ref_id?: number
  // Resolved relations
  verifications?: VerificationFlagging[]
}

export interface Expenditure {
  expenditure_id: number
  tenant_id: number
  line_item_id: number
  line_item_snapshot: LineItemSnapshot
  submitted_by_role_id: number
  submitted_by_snapshot: UserSnapshot
  status: ExpenditureStatus
  total_amount_spent: number
  particulars?: ExpenditureParticular[]
}

export interface VerificationFlagging {
  verification_id: number
  particular_id: number
  verifier_role_id: number
  verifier_snapshot: UserSnapshot
  flag_particular: boolean
  flag_amount: boolean
  flag_date: boolean
  flag_attachment: boolean
  flag_vendor: boolean
  remarks?: string
  created_at: string
}

export interface Correction {
  correction_id: number
  particular_id: number
  verification_id: number
  corrected_by_role_id: number
  corrected_by_snapshot: UserSnapshot
  field_name: string
  old_value: string
  new_value: string
  explanation: string
  corrected_at: string
}

// ── API response wrappers ──────────────────────────────────────────────────────

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  per_page: number
}

export interface ApiError {
  detail: string
  code?: string
}

// ── UI helpers ────────────────────────────────────────────────────────────────

export interface StatusMeta {
  label: string
  cssClass: string
  dot: string
}

export const STATUS_META: Record<ExpenditureStatus, StatusMeta> = {
  Unverified: { label: 'Pending Review', cssClass: 'badge-pending',  dot: 'bg-pending'  },
  Verified:   { label: 'Verified',       cssClass: 'badge-verified', dot: 'bg-verified' },
  Flagged:    { label: 'Flagged',        cssClass: 'badge-flagged',  dot: 'bg-flagged'  },
}
