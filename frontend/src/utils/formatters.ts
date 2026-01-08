/**
 * Utility functions for formatting data display
 */

/**
 * Format a number or string as Brazilian Real currency
 */
export const formatCurrency = (value: number | string): string => {
    const num = typeof value === 'string' ? parseFloat(value) : value

    if (isNaN(num)) return 'R$ 0,00'

    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL',
    }).format(num)
}

/**
 * Format a date string to Brazilian format (DD/MM/YYYY)
 */
export const formatDate = (dateString: string): string => {
    if (!dateString) return '-'

    try {
        return new Date(dateString).toLocaleDateString('pt-BR')
    } catch {
        return dateString
    }
}

/**
 * Format a date string to Brazilian format with time
 */
export const formatDateTime = (dateString: string): string => {
    if (!dateString) return '-'

    try {
        return new Date(dateString).toLocaleString('pt-BR')
    } catch {
        return dateString
    }
}

/**
 * Format a number as percentage
 */
export const formatPercentage = (value: number | string): string => {
    const num = typeof value === 'string' ? parseFloat(value) : value

    if (isNaN(num)) return '0%'

    return `${num.toFixed(2)}%`
}

/**
 * Format hours to display (e.g., 8.5 -> "8h30min" or "8.5h")
 */
export const formatHours = (hours: number | string, detailed = false): string => {
    const num = typeof hours === 'string' ? parseFloat(hours) : hours

    if (isNaN(num)) return '0h'

    if (!detailed) {
        return `${num}h`
    }

    const wholeHours = Math.floor(num)
    const minutes = Math.round((num - wholeHours) * 60)

    if (minutes === 0) return `${wholeHours}h`

    return `${wholeHours}h${minutes}min`
}
