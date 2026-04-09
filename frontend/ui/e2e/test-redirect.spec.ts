import { test, expect } from '@playwright/test'
import { MOCK_LINK_ID, MOCK_LINK_OUT, MOCK_TARGET_URL } from './fixtures'

test.describe('Test redirect tab', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
    await page.getByRole('button', { name: 'Test redirect' }).click()
  })

  test('has Link ID input and Test button', async ({ page }) => {
    await expect(page.getByPlaceholder('id-to-test')).toBeVisible()
    await expect(page.getByRole('button', { name: 'Test', exact: true })).toBeVisible()
  })

  test('active link shows redirect code, target URL and active status', async ({ page }) => {
    await page.route(`**/api/links/${MOCK_LINK_ID}`, route =>
      route.fulfill({ json: MOCK_LINK_OUT })
    )
    await page.getByPlaceholder('id-to-test').fill(MOCK_LINK_ID)
    await page.getByRole('button', { name: 'Test', exact: true }).click()
    const result = page.locator('.result-row')
    await expect(result).toBeVisible()
    await expect(result).toContainText('301')
    await expect(result).toContainText(MOCK_TARGET_URL)
    await expect(result).toContainText('true')
  })

  // FR: deleted links return 410 Gone — the UI should reflect inactive status
  test('deleted (inactive) link shows active as false', async ({ page }) => {
    await page.route(`**/api/links/${MOCK_LINK_ID}`, route =>
      route.fulfill({ json: { ...MOCK_LINK_OUT, active: false, target_url: '' } })
    )
    await page.getByPlaceholder('id-to-test').fill(MOCK_LINK_ID)
    await page.getByRole('button', { name: 'Test', exact: true }).click()
    await expect(page.locator('.result-row')).toContainText('false')
  })

  // FR: non-existent IDs return 404
  test('unknown link ID shows error', async ({ page }) => {
    await page.route('**/api/links/unknown', route =>
      route.fulfill({ status: 404, body: 'Not found' })
    )
    await page.getByPlaceholder('id-to-test').fill('unknown')
    await page.getByRole('button', { name: 'Test', exact: true }).click()
    const result = page.locator('.result-row')
    await expect(result).toBeVisible()
    await expect(result).toContainText('error')
  })
})
