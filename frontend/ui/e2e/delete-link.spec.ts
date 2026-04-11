import { test, expect } from '@playwright/test'
import { MOCK_LINK_ID, MOCK_EDIT_TOKEN } from './fixtures'

test.describe('Delete link tab', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/api/')
    await page.getByRole('button', { name: 'Delete' }).click()
  })

  test('has Link ID and Edit token fields', async ({ page }) => {
    await expect(page.getByPlaceholder('existing-id')).toBeVisible()
    await expect(page.getByPlaceholder('paste edit token')).toBeVisible()
  })

  // FR: delete button should be visually distinct (danger) to prevent accidental deletion
  test('Delete button has danger styling', async ({ page }) => {
    await expect(page.getByRole('button', { name: 'Delete' }).last()).toHaveClass(/danger/)
  })

  test('successful delete shows confirmation', async ({ page }) => {
    await page.route(`**/api/links/${MOCK_LINK_ID}`, route => {
      if (route.request().method() === 'DELETE')
        route.fulfill({ json: { status: 'deleted', link_id: MOCK_LINK_ID } })
    })
    await page.getByPlaceholder('existing-id').fill(MOCK_LINK_ID)
    await page.getByPlaceholder('paste edit token').fill(MOCK_EDIT_TOKEN)
    await page.getByRole('button', { name: 'Delete' }).last().click()
    const pre = page.locator('pre')
    await expect(pre).toBeVisible()
    await expect(pre).toContainText('deleted')
  })

  test('invalid edit token (401) is shown as an error', async ({ page }) => {
    await page.route(`**/api/links/${MOCK_LINK_ID}`, route => {
      if (route.request().method() === 'DELETE')
        route.fulfill({ status: 401, body: 'Invalid edit token' })
    })
    await page.getByPlaceholder('existing-id').fill(MOCK_LINK_ID)
    await page.getByPlaceholder('paste edit token').fill('wrongtoken')
    await page.getByRole('button', { name: 'Delete' }).last().click()
    await expect(page.locator('.error')).toContainText('Error')
  })

  test('deleting non-existent link (404) is shown as an error', async ({ page }) => {
    await page.route('**/api/links/ghost', route => {
      if (route.request().method() === 'DELETE')
        route.fulfill({ status: 404, body: 'Not found' })
    })
    await page.getByPlaceholder('existing-id').fill('ghost')
    await page.getByPlaceholder('paste edit token').fill(MOCK_EDIT_TOKEN)
    await page.getByRole('button', { name: 'Delete' }).last().click()
    await expect(page.locator('.error')).toContainText('Error')
  })
})
