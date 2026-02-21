import { test, expect } from '@playwright/test'

test.describe('Math Templates Manager E2E', () => {
  test.beforeEach(async ({ page }) => {
    // Assuming login is handled by global setup or needs to be done here
    // For this test, we navigate to the templates page directly,
    // assuming auth state is preserved or we login
    await page.goto('/login')
    await page.fill('input[name="email"]', 'super@admin.com') // change if needed
    await page.fill('input[name="password"]', 'admin123') // change if needed
    await page.click('button[type="submit"]')

    // Wait for navigation to dashboard/companies
    await page.waitForURL('**/companies')

    // Go to templates manager
    await page.goto('/templates')
  })

  test('should display default template with badge and disabled actions', async ({
    page,
  }) => {
    // Check if "Padrão" badge exists
    const defaultTemplateBadge = page.locator('span:has-text("Padrão")')
    await expect(defaultTemplateBadge).toBeVisible()

    // The row containing the badge should have disabled action buttons
    const defaultRow = page.locator('tr').filter({ has: defaultTemplateBadge })

    // Verify view button is enabled
    const viewBtn = defaultRow.locator('button[title="Visualizar"]')
    await expect(viewBtn).toBeVisible()
    await expect(viewBtn).toBeEnabled()

    // Verify delete button is disabled
    const deleteBtn = defaultRow.locator(
      'button[title="Template padrão não pode ser excluído"]'
    )
    await expect(deleteBtn).toBeVisible()
    await expect(deleteBtn).toBeDisabled()
  })
})
