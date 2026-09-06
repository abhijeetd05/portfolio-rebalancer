export function formatNumber(value: string | number, maximumFractionDigits = 2): string {
  const numericValue = Number(value)
  if (!Number.isFinite(numericValue)) return '—'
  return new Intl.NumberFormat('en-IN', {
    minimumFractionDigits: 0,
    maximumFractionDigits,
  }).format(numericValue)
}

export function formatMoney(value: string | number, currency: string, maximumFractionDigits = 2): string {
  const numericValue = Number(value)
  if (!Number.isFinite(numericValue)) return '—'
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency,
    minimumFractionDigits: 2,
    maximumFractionDigits,
  }).format(numericValue)
}

export function formatPercent(value: string | number): string {
  return `${formatNumber(value, 2)}%`
}
