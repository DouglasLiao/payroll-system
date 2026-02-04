import type { Provider } from '../../../types'

interface PayrollFormInputs {
  provider_id: number
  reference_month: string
  hired_date?: string | null
  overtime_hours_50?: number
  holiday_hours?: number
  night_hours?: number
  late_minutes?: number
  absence_hours?: number
  absence_days?: number
  manual_discounts?: number
  notes?: string
}

interface CalendarInfo {
  workDays: number
  restDays: number
}

export const usePayrollCalculations = (
  selectedProvider: Provider | null,
  watchedValues: PayrollFormInputs,
  calendarInfo: CalendarInfo
) => {
  const hourlyRate = selectedProvider
    ? Number(selectedProvider.monthly_value) / selectedProvider.monthly_hours
    : 0

  const overtimeValue = hourlyRate * 1.5
  const holidayValue = hourlyRate * 2
  const nightValue = hourlyRate * 1.2

  const totalOvertime = (watchedValues.overtime_hours_50 || 0) * overtimeValue
  const totalHoliday = (watchedValues.holiday_hours || 0) * holidayValue
  const totalNight = (watchedValues.night_hours || 0) * nightValue

  const dsrValue =
    ((totalOvertime + totalHoliday) / calendarInfo.workDays) *
    calendarInfo.restDays

  const lateDiscount = ((watchedValues.late_minutes || 0) / 60) * hourlyRate
  const absenceDiscount = (watchedValues.absence_hours || 0) * hourlyRate

  const workDaysForVT =
    calendarInfo.workDays - (watchedValues.absence_days || 0)
  const calculatedVT = selectedProvider?.vt_enabled
    ? selectedProvider.vt_trips_per_day *
      parseFloat(selectedProvider.vt_fare) *
      Math.max(0, workDaysForVT)
    : 0

  const totalAdditionals = totalOvertime + totalHoliday + totalNight + dsrValue
  const totalDiscounts =
    lateDiscount +
    absenceDiscount +
    calculatedVT +
    (watchedValues.manual_discounts || 0)

  const advanceValue = selectedProvider
    ? Number(selectedProvider.monthly_value) *
      (Number(selectedProvider.advance_percentage) / 100)
    : 0

  const finalValue = selectedProvider
    ? Number(selectedProvider.monthly_value) -
      advanceValue +
      totalAdditionals -
      totalDiscounts
    : 0

  return {
    hourlyRate,
    overtimeValue,
    holidayValue,
    nightValue,
    totalOvertime,
    totalHoliday,
    totalNight,
    dsrValue,
    lateDiscount,
    absenceDiscount,
    workDaysForVT,
    calculatedVT,
    totalAdditionals,
    totalDiscounts,
    advanceValue,
    finalValue,
  }
}
