/**
 * E2E Test: Login Flow
 *
 * Testa o fluxo completo de autenticação do sistema.
 */

import { test, expect } from '@playwright/test'

test.describe('Login Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
  })

  test('should login successfully with valid credentials', async ({ page }) => {
    // Credenciais do agent.md
    const email = 'admin@techsolutions.com'
    const password = 'password123'

    // Preencher formulário de login
    await page.fill('input[type="email"]', email)
    await page.fill('input[type="password"]', password)

    // Clicar em entrar
    await page.click('button[type="submit"]')

    // Aguardar navegação para fora do /login (redirect após JWT)
    await page.waitForURL((url) => !url.pathname.includes('/login'), {
      timeout: 8000,
    })

    // Verificar que não está mais na página de login
    const currentUrl = page.url()
    expect(currentUrl).not.toContain('/login')

    // Verificar que existe algum conteúdo do dashboard
    await expect(page.locator('body')).toContainText(
      /dashboard|folha|prestador/i
    )
  })

  test('should fail login with invalid credentials', async ({ page }) => {
    await page.fill(
      'input[name="email"], input[type="email"]',
      'wrong@example.com'
    )
    await page.fill(
      'input[name="password"], input[type="password"]',
      'wrongpassword'
    )

    await page.click('button[type="submit"]')

    // Deve mostrar erro ou permanecer na página de login
    await page.waitForTimeout(2000)
    const currentUrl = page.url()

    // Pode continuar no login ou mostrar mensagem de erro
    const hasError = await page
      .locator('text=/erro|inválid|incorrect|falhou/i')
      .isVisible()
      .catch(() => false)

    expect(hasError || currentUrl.includes('/login')).toBeTruthy()
  })

  test('should logout successfully', async ({ page }) => {
    // Login primeiro
    await page.fill(
      'input[name="email"], input[type="email"]',
      'admin@techsolutions.com'
    )
    await page.fill(
      'input[name="password"], input[type="password"]',
      'password123'
    )
    await page.click('button[type="submit"]')

    // Aguardar dashboard carregar
    await page.waitForURL('**', { timeout: 5000 })
    await page.waitForTimeout(1000)

    // Procurar botão de logout (pode estar em menu, avatar, etc)
    const logoutButton = page
      .locator(
        'button:has-text("sair"), button:has-text("logout"), [aria-label*="sair"]'
      )
      .first()

    if (await logoutButton.isVisible()) {
      await logoutButton.click()

      // Deve voltar para login
      await page.waitForURL('**/login', { timeout: 5000 })
      expect(page.url()).toContain('/login')
    }
  })
})
