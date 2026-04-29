export const useFormatters = () => {
  const currency = (amount: number) =>
    new Intl.NumberFormat('en-PH', {
      style: 'currency',
      currency: 'PHP',
      minimumFractionDigits: 2,
    }).format(amount)

  const date = (iso: string) =>
    new Intl.DateTimeFormat('en-PH', {
      year: 'numeric', month: 'short', day: 'numeric',
    }).format(new Date(iso))

  const datetime = (iso: string) =>
    new Intl.DateTimeFormat('en-PH', {
      year: 'numeric', month: 'short', day: 'numeric',
      hour: '2-digit', minute: '2-digit',
    }).format(new Date(iso))

  const relativeTime = (iso: string) => {
    const diff = Date.now() - new Date(iso).getTime()
    const mins = Math.floor(diff / 60000)
    if (mins < 60) return `${mins}m ago`
    const hrs = Math.floor(mins / 60)
    if (hrs < 24) return `${hrs}h ago`
    return date(iso)
  }

  const budgetPercent = (spent: number, budget: number) =>
    budget > 0 ? Math.min(100, Math.round((spent / budget) * 100)) : 0

  return { currency, date, datetime, relativeTime, budgetPercent }
}
