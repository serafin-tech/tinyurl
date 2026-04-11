import { test, expect } from '@playwright/test'

test.describe('Tab navigation', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/mgnt/')
  })

  test('shows Create tab active by default', async ({ page }) => {
    await expect(page.locator('.tabs').getByRole('button', { name: 'Create' })).toHaveClass(/active/)
    await expect(page.getByRole('heading', { name: 'Create short link' })).toBeVisible()
  })

  test('switching to Edit tab shows edit form and hides create form', async ({ page }) => {
    await page.getByRole('button', { name: 'Edit' }).click()
    await expect(page.getByRole('heading', { name: 'Edit link' })).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Create short link' })).not.toBeVisible()
  })

  test('switching to Delete tab shows delete form', async ({ page }) => {
    await page.getByRole('button', { name: 'Delete' }).click()
    await expect(page.getByRole('heading', { name: 'Delete link' })).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Create short link' })).not.toBeVisible()
  })

  test('switching to Test redirect tab shows test form', async ({ page }) => {
    await page.getByRole('button', { name: 'Test redirect' }).click()
    await expect(page.getByRole('heading', { name: 'Test redirect' })).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Create short link' })).not.toBeVisible()
  })

  test('only one tab panel is visible at a time', async ({ page }) => {
    const headings = ['Create short link', 'Edit link', 'Delete link', 'Test redirect']
    for (const tab of ['Edit', 'Delete', 'Test redirect', 'Create']) {
      await page.getByRole('button', { name: tab }).click()
      let visibleCount = 0
      for (const h of headings) {
        const el = page.getByRole('heading', { name: h })
        if (await el.isVisible()) visibleCount++
      }
      expect(visibleCount).toBe(1)
    }
  })
})
