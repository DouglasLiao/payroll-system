import Holidays from 'date-holidays'
import dayjs from 'dayjs'

/**
 * Calcula informações do calendário para um mês específico
 * @param referenceMonth - String no formato "MM/YYYY"
 * @returns Objeto com workDays, sundays, e holidays do mês
 */
export const getMonthCalendarInfo = (referenceMonth: string) => {
  const [month, year] = referenceMonth.split('/').map(Number)

  // Configurar biblioteca de feriados para Brasil
  const hd = new Holidays('BR')

  // Pegar primeiro e último dia do mês
  const startOfMonth = dayjs(`${year}-${month.toString().padStart(2, '0')}-01`)
  const endOfMonth = startOfMonth.endOf('month')
  const daysInMonth = endOfMonth.date()

  // Contadores
  let workDays = 0
  let sundays = 0
  let holidays = 0

  // Pegar feriados do mês
  const monthHolidays = hd.getHolidays(year)
  const holidayDates = new Set(
    monthHolidays
      .filter((h) => {
        const holidayDate = dayjs(h.date)
        return holidayDate.month() === month - 1 // dayjs usa 0-11
      })
      .map((h) => dayjs(h.date).format('YYYY-MM-DD'))
  )

  // Iterar pelos dias do mês
  for (let day = 1; day <= daysInMonth; day++) {
    const currentDay = startOfMonth.date(day)
    const dayOfWeek = currentDay.day() // 0 = domingo, 6 = sábado
    const dateStr = currentDay.format('YYYY-MM-DD')

    const isSunday = dayOfWeek === 0
    const isHoliday = holidayDates.has(dateStr)

    if (isSunday) {
      sundays++
    } else if (isHoliday) {
      holidays++
    } else if (dayOfWeek !== 6) {
      // Não é sábado, domingo ou feriado = dia útil
      workDays++
    }
  }

  // Domingos + Feriados (para DSR)
  const restDays = sundays + holidays

  return {
    workDays,
    sundays,
    holidays,
    restDays,
    totalDays: daysInMonth,
  }
}

/**
 * Exemplo de uso:
 * const info = getMonthCalendarInfo('01/2026')
 * console.log(info)
 * // { workDays: 23, sundays: 5, holidays: 2, restDays: 7, totalDays: 31 }
 */
