/**
 * Composable that fetches real published data from the CMS portal endpoint.
 * No auth required — this is the public transparency portal.
 */

export interface PublishedExpenditure {
  publication_id: number
  tenant_id: number
  ref_expenditure_id: number | null
  ref_line_item_id: number | null
  content_snapshot: {
    title?: string
    summary?: string
    program_name?: string
    budget_allocation?: number
    fiscal_year?: number
    total_amount_spent?: number
    status?: string
    submitted_by?: string
    barangay?: string
    particulars?: Array<{
      particular_name: string
      amount_claimed: number
      date_of_expense: string
      vendor_name?: string
    }>
    [key: string]: unknown
  }
  status: string
  published_at: string | null
  published_by_snapshot?: Record<string, unknown> | null
}

export const usePortalApi = () => {
  const config = useRuntimeConfig()
  const base: string = (config.public as Record<string, string>).cmsApiBase || ''

  const fetchPublished = (): Promise<PublishedExpenditure[]> =>
    $fetch<PublishedExpenditure[]>(`${base}/api/cms/portal/published`)

  return { fetchPublished }
}
