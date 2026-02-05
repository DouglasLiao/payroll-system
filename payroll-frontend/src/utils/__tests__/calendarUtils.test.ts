/**
 * Testes para calendarUtils
 *
 * Valida que a função getMonthCalendarInfo calcula corretamente
 * os dias úteis, domingos e feriados para diferentes meses.
 */

import { describe, it, expect } from 'vitest'
import { getMonthCalendarInfo } from '../calendarUtils'

describe('calendarUtils', () => {
  describe('getMonthCalendarInfo', () => {
    it('should calculate calendar info for January 2026', () => {
      const result = getMonthCalendarInfo('01/2026')

      expect(result.workDays).toBeGreaterThan(20)
      expect(result.restDays).toBeGreaterThan(4)
      expect(result.totalDays).toBe(31)
      expect(result.workDays + result.restDays).toBeLessThanOrEqual(31)
    })

    it('should calculate calendar info for February 2026 (non-leap year)', () => {
      const result = getMonthCalendarInfo('02/2026')

      expect(result.totalDays).toBe(28)
      expect(result.workDays).toBeGreaterThan(18)
      expect(result.workDays).toBeLessThan(25)
    })

    it('should include Brazilian holidays in calculation', () => {
      // Janeiro tem 1 feriado (Ano Novo - 01/01)
      const jan = getMonthCalendarInfo('01/2026')

      // Dezembro tem feriado de Natal (25/12)
      const dec = getMonthCalendarInfo('12/2025')

      expect(jan.holidays).toBeGreaterThanOrEqual(1)
      expect(dec.holidays).toBeGreaterThanOrEqual(1)
    })

    it('should calculate restDays correctly (sundays + holidays)', () => {
      const result = getMonthCalendarInfo('01/2026')

      // restDays deve ser a soma de domingos + feriados
      expect(result.restDays).toBe(result.sundays + result.holidays)
    })

    it('should handle different months with varying business days', () => {
      const jan = getMonthCalendarInfo('01/2026')
      const feb = getMonthCalendarInfo('02/2026')

      // Janeiro (31 dias) deve ter mais dias úteis que Fevereiro (28 dias)
      expect(jan.workDays).toBeGreaterThan(feb.workDays)
    })
  })
})
