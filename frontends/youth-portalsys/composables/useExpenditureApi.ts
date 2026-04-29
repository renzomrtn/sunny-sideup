import type {
  Expenditure,
  ExpenditureParticular,
  VerificationFlagging,
  Correction,
  PaginatedResponse,
  ExpenditureStatus,
} from '~/types/expenditure'

export const useExpenditureApi = () => {
  const config = useRuntimeConfig()
  const base = config.public.expenditureApiBase

  // ── Expenditures ────────────────────────────────────────────────────────────

  const listExpenditures = (params?: {
    status?: ExpenditureStatus
    page?: number
    per_page?: number
    search?: string
  }) =>
    $fetch<PaginatedResponse<Expenditure>>(`${base}/expenditures`, {
      params,
    })

  const getExpenditure = (id: number) =>
    $fetch<Expenditure>(`${base}/expenditures/${id}`)

  const updateExpenditureStatus = (
    id: number,
    status: ExpenditureStatus,
  ) =>
    $fetch<Expenditure>(`${base}/expenditures/${id}/status`, {
      method: 'PATCH',
      body: { status },
    })

  // ── Particulars ─────────────────────────────────────────────────────────────

  const getParticular = (id: number) =>
    $fetch<ExpenditureParticular>(`${base}/particulars/${id}`)

  // ── Verification & Flagging ──────────────────────────────────────────────────

  const createVerification = (
    payload: Omit<VerificationFlagging, 'verification_id' | 'created_at'>,
  ) =>
    $fetch<VerificationFlagging>(`${base}/verifications`, {
      method: 'POST',
      body: payload,
    })

  const listVerifications = (particularId: number) =>
    $fetch<VerificationFlagging[]>(
      `${base}/particulars/${particularId}/verifications`,
    )

  // ── Corrections ─────────────────────────────────────────────────────────────

  const createCorrection = (
    payload: Omit<Correction, 'correction_id' | 'corrected_at'>,
  ) =>
    $fetch<Correction>(`${base}/corrections`, {
      method: 'POST',
      body: payload,
    })

  const listCorrections = (particularId: number) =>
    $fetch<Correction[]>(`${base}/particulars/${particularId}/corrections`)

  return {
    listExpenditures,
    getExpenditure,
    updateExpenditureStatus,
    getParticular,
    createVerification,
    listVerifications,
    createCorrection,
    listCorrections,
  }
}
