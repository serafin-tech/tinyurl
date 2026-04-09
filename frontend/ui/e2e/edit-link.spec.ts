import { test, expect } from '@playwright/test'
import { MOCK_LINK_OUT, MOCK_LINK_ID, MOCK_EDIT_TOKEN, MOCK_TARGET_URL } from './fixtures'

test.describe('Edit link tab', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
    await page.getByRole('button', { name: 'Edit' }).click()
  })

  test('has Link ID and Edit token fields', async ({ page }) => {
    await expect(page.getByPlaceholder('existing-id')).toBeVisible()
    await expect(page.getByPlaceholder('paste edit token')).toBeVisible()
  })

  test('has new target URL and redirect code fields', async ({ page }) => {
    await expect(page.getByPlaceholder('https://example.com/new')).toBeVisible()
    const select = page.locator('select')
    await expect(select).toBeVisible()
    // "(no change)" option must be present so partial updates are possible
    await expect(select.locator('option[value=""]')).toHaveCount(1)
    for (const code of ['301', '302', '307', '308']) {
      await expect(select.locator(`option[value="${code}"]`)).toHaveCount(1)
    }
  })

  test('has Change alias field', async ({ page }) => {
    await expect(page.getByPlaceholder('new-alias')).toBeVisible()
  })

  test('successful update displays result', async ({ page }) => {
    await page.route(`**/api/links/${MOCK_LINK_ID}`, route => {
      if (route.request().method() === 'PATCH')
        route.fulfill({ json: { ...MOCK_LINK_OUT, target_url: 'https://updated.example.com' } })
    })
    await page.getByPlaceholder('existing-id').fill(MOCK_LINK_ID)
    await page.getByPlaceholder('paste edit token').fill(MOCK_EDIT_TOKEN)
    await page.getByPlaceholder('https://example.com/new').fill('https://updated.example.com')
    await page.getByRole('button', { name: 'Update' }).click()
    const pre = page.locator('pre')
    await expect(pre).toBeVisible()
    await expect(pre).toContainText('updated.example.com')
  })

  test('invalid edit token (401) is shown as an error', async ({ page }) => {
    await page.route(`**/api/links/${MOCK_LINK_ID}`, route => {
      if (route.request().method() === 'PATCH')
        route.fulfill({ status: 401, body: 'Invalid edit token' })
    })
    await page.getByPlaceholder('existing-id').fill(MOCK_LINK_ID)
    await page.getByPlaceholder('paste edit token').fill('wrongtoken')
    await page.getByPlaceholder('https://example.com/new').fill(MOCK_TARGET_URL)
    await page.getByRole('button', { name: 'Update' }).click()
    await expect(page.locator('.error')).toContainText('Error')
  })

  test('alias conflict (409) on rename is shown as an error', async ({ page }) => {
    await page.route(`**/api/links/${MOCK_LINK_ID}`, route => {
      if (route.request().method() === 'PATCH')
        route.fulfill({ status: 409, body: 'Conflict: link-id already taken' })
    })
    await page.getByPlaceholder('existing-id').fill(MOCK_LINK_ID)
    await page.getByPlaceholder('paste edit token').fill(MOCK_EDIT_TOKEN)
    await page.getByPlaceholder('new-alias').fill('taken')
    await page.getByRole('button', { name: 'Update' }).click()
    await expect(page.locator('.error')).toContainText('Error')
  })
})
