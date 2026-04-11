import { test, expect } from '@playwright/test'
import { MOCK_CREATE_RESPONSE, MOCK_TARGET_URL, MOCK_LINK_ID, MOCK_SHORT_URL, MOCK_EDIT_TOKEN } from './fixtures'

test.describe('Create link tab', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/mgnt/')
  })

  test('has required Target URL field', async ({ page }) => {
    await expect(page.getByPlaceholder('https://example.com')).toBeVisible()
  })

  test('has optional Custom alias field', async ({ page }) => {
    await expect(page.getByPlaceholder('my-alias')).toBeVisible()
  })

  // FR: allowed redirect codes are 301, 302, 307, 308; default is 301
  test('redirect code selector has correct options with 301 as default', async ({ page }) => {
    const select = page.locator('select')
    await expect(select).toHaveValue('301')
    for (const code of ['301', '302', '307', '308']) {
      await expect(select.locator(`option[value="${code}"]`)).toHaveCount(1)
    }
  })

  test('successful create displays short URL and edit token', async ({ page }) => {
    await page.route('**/api/links', route =>
      route.fulfill({ json: MOCK_CREATE_RESPONSE })
    )
    await page.getByPlaceholder('https://example.com').fill(MOCK_TARGET_URL)
    await page.locator('.tab-panel').getByRole('button', { name: 'Create' }).click()
    const pre = page.locator('pre')
    await expect(pre).toBeVisible()
    await expect(pre).toContainText(MOCK_SHORT_URL)
    await expect(pre).toContainText(MOCK_EDIT_TOKEN)
    await expect(pre).toContainText(MOCK_LINK_ID)
  })

  test('API error is shown to the user', async ({ page }) => {
    await page.route('**/api/links', route =>
      route.fulfill({ status: 400, body: 'Invalid URL' })
    )
    await page.getByPlaceholder('https://example.com').fill('not-a-url')
    await page.locator('.tab-panel').getByRole('button', { name: 'Create' }).click()
    await expect(page.locator('.error')).toBeVisible()
    await expect(page.locator('.error')).toContainText('Error')
  })

  test('alias conflict (409) is shown as an error', async ({ page }) => {
    await page.route('**/api/links', route =>
      route.fulfill({ status: 409, body: 'Conflict: link-id already taken' })
    )
    await page.getByPlaceholder('https://example.com').fill(MOCK_TARGET_URL)
    await page.getByPlaceholder('my-alias').fill('taken-alias')
    await page.locator('.tab-panel').getByRole('button', { name: 'Create' }).click()
    await expect(page.locator('.error')).toContainText('Error')
  })
})
