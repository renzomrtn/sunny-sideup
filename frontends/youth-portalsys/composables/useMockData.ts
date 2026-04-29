import type { Expenditure, ExpenditureParticular, VerificationFlagging } from '~/types/expenditure'

// ── Mock data for local development without a running backend ─────────────────

export const useMockData = () => {
  const vendors = [
    { vendor_id: 1, tenant_id: 1, vendor_name: 'Naga Fresh Catering', category: 'Catering & Food Services' as const, address: 'Brgy. Tinago, Naga City', created_at: '2025-01-01' },
    { vendor_id: 2, tenant_id: 1, vendor_name: 'City Sports Depot',   category: 'Sports & Recreation'    as const, address: 'Brgy. Concepcion Pequeña', created_at: '2025-01-01' },
    { vendor_id: 3, tenant_id: 1, vendor_name: 'EduSupplies Co.',     category: 'Office & School Supplies' as const, address: 'Brgy. Pacol', created_at: '2025-01-01' },
    { vendor_id: 4, tenant_id: 1, vendor_name: 'LogiMove Transport',  category: 'Transportation & Logistics' as const, address: 'Brgy. Mabolo', created_at: '2025-01-01' },
  ]

  const particulars: ExpenditureParticular[] = [
    {
      particular_id: 1, expenditure_id: 1,
      vendor_id: 1, vendor: vendors[0],
      particular_name: 'Catering for 80 pax — Day 1',
      amount_claimed: 24000.00,
      date_of_expense: '2025-09-11',
      file_ref_id: 101,
    },
    {
      particular_id: 2, expenditure_id: 1,
      vendor_id: 1, vendor: vendors[0],
      particular_name: 'Catering for 80 pax — Day 2',
      amount_claimed: 24000.00,
      date_of_expense: '2025-09-12',
      file_ref_id: 102,
    },
    {
      particular_id: 3, expenditure_id: 1,
      vendor_id: 3, vendor: vendors[2],
      particular_name: 'Training materials & workbooks',
      amount_claimed: 12500.00,
      date_of_expense: '2025-09-10',
      file_ref_id: 103,
    },
    {
      particular_id: 4, expenditure_id: 2,
      vendor_id: 2, vendor: vendors[1],
      particular_name: 'Sports equipment — basketballs (12 pcs)',
      amount_claimed: 18000.00,
      date_of_expense: '2025-09-08',
      file_ref_id: 104,
    },
    {
      particular_id: 5, expenditure_id: 2,
      vendor_id: 4, vendor: vendors[3],
      particular_name: 'Transport — team van rental (3 days)',
      amount_claimed: 9000.00,
      date_of_expense: '2025-09-09',
      file_ref_id: 105,
    },
    {
      particular_id: 6, expenditure_id: 3,
      vendor_id: 1, vendor: vendors[0],
      particular_name: 'Snacks & refreshments',
      amount_claimed: 8500.00,
      date_of_expense: '2025-09-13',
      file_ref_id: 106,
    },
  ]

  const expenditures: Expenditure[] = [
    {
      expenditure_id: 1,
      tenant_id: 1,
      line_item_id: 10,
      line_item_snapshot: { line_item_id: 10, program_name: 'Leadership Training Camp', budget_allocation: 80000, fiscal_year: 2025 },
      submitted_by_role_id: 5,
      submitted_by_snapshot: { role_id: 5, full_name: 'Maria Santos', position: 'SK Treasurer', barangay: 'SK Federation' },
      status: 'Unverified',
      total_amount_spent: 60500.00,
      particulars: particulars.filter(p => p.expenditure_id === 1),
    },
    {
      expenditure_id: 2,
      tenant_id: 1,
      line_item_id: 11,
      line_item_snapshot: { line_item_id: 11, program_name: 'Inter-Barangay Sports League', budget_allocation: 45000, fiscal_year: 2025 },
      submitted_by_role_id: 6,
      submitted_by_snapshot: { role_id: 6, full_name: 'Jose Reyes', position: 'SK Secretary', barangay: 'Brgy. Concepcion Pequeña' },
      status: 'Flagged',
      total_amount_spent: 27000.00,
      particulars: particulars.filter(p => p.expenditure_id === 2),
    },
    {
      expenditure_id: 3,
      tenant_id: 1,
      line_item_id: 12,
      line_item_snapshot: { line_item_id: 12, program_name: 'HIV/AIDS Awareness Seminar', budget_allocation: 30000, fiscal_year: 2025 },
      submitted_by_role_id: 7,
      submitted_by_snapshot: { role_id: 7, full_name: 'Ana Villanueva', position: 'SK Chairperson', barangay: 'Brgy. Tinago' },
      status: 'Verified',
      total_amount_spent: 8500.00,
      particulars: particulars.filter(p => p.expenditure_id === 3),
    },
    {
      expenditure_id: 4,
      tenant_id: 1,
      line_item_id: 13,
      line_item_snapshot: { line_item_id: 13, program_name: 'Anti-Illegal Drugs Seminar', budget_allocation: 25000, fiscal_year: 2025 },
      submitted_by_role_id: 8,
      submitted_by_snapshot: { role_id: 8, full_name: 'Carlo Magno', position: 'SK Treasurer', barangay: 'Brgy. Pacol' },
      status: 'Unverified',
      total_amount_spent: 14200.00,
      particulars: [],
    },
    {
      expenditure_id: 5,
      tenant_id: 1,
      line_item_id: 14,
      line_item_snapshot: { line_item_id: 14, program_name: 'Livelihood Skills Workshop', budget_allocation: 60000, fiscal_year: 2025 },
      submitted_by_role_id: 9,
      submitted_by_snapshot: { role_id: 9, full_name: 'Liza Cruz', position: 'SK Chairperson', barangay: 'Brgy. Mabolo' },
      status: 'Verified',
      total_amount_spent: 55800.00,
      particulars: [],
    },
  ]

  const verifications: VerificationFlagging[] = [
    {
      verification_id: 1,
      particular_id: 4,
      verifier_role_id: 1,
      verifier_snapshot: { role_id: 1, full_name: 'Admin Verifier', position: 'SK Auditor' },
      flag_particular: false,
      flag_amount: true,
      flag_date: false,
      flag_attachment: true,
      flag_vendor: false,
      remarks: 'Receipt amount does not match the claimed amount. OR is missing from the attachment.',
      created_at: '2025-09-15T09:30:00Z',
    },
  ]

  return { expenditures, particulars, vendors, verifications }
}
