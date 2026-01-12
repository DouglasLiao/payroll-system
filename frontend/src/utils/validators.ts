/**
 * Validation utilities for Brazilian documents and form inputs
 */

/**
 * Validates Brazilian CPF (Cadastro de Pessoas Físicas)
 * @param cpf - CPF string with or without formatting
 * @returns true if valid, false otherwise
 */
export const validateCPF = (cpf: string): boolean => {
  // Remove non-numeric characters
  const cleaned = cpf.replace(/\D/g, '')

  // Check length
  if (cleaned.length !== 11) return false

  // Check for invalid sequences (111.111.111-11, etc)
  if (/^(\d)\1{10}$/.test(cleaned)) return false

  // Validate check digits
  let sum = 0
  let remainder: number

  // First check digit
  for (let i = 1; i <= 9; i++) {
    sum += parseInt(cleaned.substring(i - 1, i)) * (11 - i)
  }
  remainder = (sum * 10) % 11
  if (remainder === 10 || remainder === 11) remainder = 0
  if (remainder !== parseInt(cleaned.substring(9, 10))) return false

  // Second check digit
  sum = 0
  for (let i = 1; i <= 10; i++) {
    sum += parseInt(cleaned.substring(i - 1, i)) * (12 - i)
  }
  remainder = (sum * 10) % 11
  if (remainder === 10 || remainder === 11) remainder = 0
  if (remainder !== parseInt(cleaned.substring(10, 11))) return false

  return true
}

/**
 * Validates Brazilian CNPJ (Cadastro Nacional da Pessoa Jurídica)
 * @param cnpj - CNPJ string with or without formatting
 * @returns true if valid, false otherwise
 */
export const validateCNPJ = (cnpj: string): boolean => {
  // Remove non-numeric characters
  const cleaned = cnpj.replace(/\D/g, '')

  // Check length
  if (cleaned.length !== 14) return false

  // Check for invalid sequences
  if (/^(\d)\1{13}$/.test(cleaned)) return false

  // Validate check digits
  let length = cleaned.length - 2
  let numbers = cleaned.substring(0, length)
  const digits = cleaned.substring(length)
  let sum = 0
  let pos = length - 7

  // First check digit
  for (let i = length; i >= 1; i--) {
    sum += parseInt(numbers.charAt(length - i)) * pos--
    if (pos < 2) pos = 9
  }
  let result = sum % 11 < 2 ? 0 : 11 - (sum % 11)
  if (result !== parseInt(digits.charAt(0))) return false

  // Second check digit
  length = length + 1
  numbers = cleaned.substring(0, length)
  sum = 0
  pos = length - 7
  for (let i = length; i >= 1; i--) {
    sum += parseInt(numbers.charAt(length - i)) * pos--
    if (pos < 2) pos = 9
  }
  result = sum % 11 < 2 ? 0 : 11 - (sum % 11)
  if (result !== parseInt(digits.charAt(1))) return false

  return true
}

/**
 * Validates if string contains only letters and spaces
 * @param value - String to validate
 * @returns true if valid, false otherwise
 */
export const onlyLetters = (value: string): boolean => {
  if (!value) return true // Allow empty
  return /^[a-zA-ZÀ-ÿ\s]+$/.test(value)
}

/**
 * Validates if string contains only numbers
 * @param value - String to validate
 * @returns true if valid, false otherwise
 */
export const onlyNumbers = (value: string): boolean => {
  if (!value) return true // Allow empty
  return /^\d+$/.test(value)
}

/**
 * Validates email format
 * @param email - Email string to validate
 * @returns true if valid, false otherwise
 */
export const validateEmail = (email: string): boolean => {
  if (!email) return true // Allow empty
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)
}

/**
 * Formats CPF string with mask (000.000.000-00)
 * @param cpf - CPF string
 * @returns Formatted CPF
 */
export const formatCPF = (cpf: string): string => {
  const cleaned = cpf.replace(/\D/g, '')
  return cleaned
    .replace(/(\d{3})(\d)/, '$1.$2')
    .replace(/(\d{3})(\d)/, '$1.$2')
    .replace(/(\d{3})(\d{1,2})$/, '$1-$2')
}

/**
 * Formats CNPJ string with mask (00.000.000/0000-00)
 * @param cnpj - CNPJ string
 * @returns Formatted CNPJ
 */
export const formatCNPJ = (cnpj: string): string => {
  const cleaned = cnpj.replace(/\D/g, '')
  return cleaned
    .replace(/(\d{2})(\d)/, '$1.$2')
    .replace(/(\d{3})(\d)/, '$1.$2')
    .replace(/(\d{3})(\d)/, '$1/$2')
    .replace(/(\d{4})(\d{1,2})$/, '$1-$2')
}

/**
 * Validates if a value is a positive number
 * @param value - Value to validate
 * @returns true if valid positive number, false otherwise
 */
export const isPositiveNumber = (value: string | number): boolean => {
  const num =
    typeof value === 'string'
      ? parseFloat(value.replace(/[^\d,.-]/g, '').replace(',', '.'))
      : value
  return !isNaN(num) && num > 0
}

/**
 * Validates if a value is a non-negative number (>= 0)
 * @param value - Value to validate
 * @returns true if valid non-negative number, false otherwise
 */
export const isNonNegativeNumber = (value: string | number): boolean => {
  const num =
    typeof value === 'string'
      ? parseFloat(value.replace(/[^\d,.-]/g, '').replace(',', '.'))
      : value
  return !isNaN(num) && num >= 0
}
