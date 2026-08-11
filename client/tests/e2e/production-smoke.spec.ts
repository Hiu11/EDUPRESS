import { expect, test } from '@playwright/test';

const apiBase = process.env.SMOKE_API_BASE;

async function openApp(page) {
  await page.goto('/');
  await page.waitForLoadState('networkidle');
  await expect(page.getByLabel('Primary')).toBeVisible();
}

async function navigateByPrimaryNav(page, index, expectedHash) {
  await page.locator('.nav-links button').nth(index).click();
  await page.waitForFunction((hash) => window.location.hash === hash, expectedHash);
}

test.describe('production smoke checks', () => {
  test('frontend renders the primary learning shell', async ({ page }) => {
    await openApp(page);

    const primaryNav = page.getByLabel('Primary');

    await expect(page.locator('body')).toContainText('EduPress');
    await expect(primaryNav.getByRole('button', { name: /Trang chủ/i })).toBeVisible();
    await expect(primaryNav.getByRole('button', { name: /^Khóa học$/i })).toBeVisible();
    await expect(primaryNav.getByRole('button', { name: /^Quiz$/i })).toBeVisible();
    await expect(page.getByRole('button', { name: /Khám phá khóa học/i })).toBeVisible();
  });

  test('course catalog loads without a blank screen', async ({ page }) => {
    await openApp(page);
    await navigateByPrimaryNav(page, 1, '#courses');

    await expect.poll(async () => page.locator('.course-row-card').count()).toBeGreaterThan(0);
    await expect(page.getByPlaceholder(/Tìm AI, Web, OOP/i)).toBeVisible();
  });

  test('built-in quiz can answer the first question', async ({ page }) => {
    await openApp(page);
    await navigateByPrimaryNav(page, 4, '#quiz');

    await expect(page.locator('.quiz-option-btn').first()).toBeVisible();
    await page.locator('.quiz-option-btn').first().click();
    await page.locator('.quiz-submit-btn').click();
    await expect(page.locator('.quiz-explanation')).toBeVisible();
  });

  test('course detail exposes the comments path', async ({ page }) => {
    await openApp(page);
    await navigateByPrimaryNav(page, 1, '#courses');

    await page.locator('.course-row-card .primary-btn').first().click();

    await expect(page.locator('.live-comments-section')).toBeVisible();
    await expect(page.locator('.comment-input-area input')).toBeVisible();
    await expect(page.locator('.comment-input-area button')).toBeVisible();
  });

  test('api health endpoint responds when configured', async ({ request }) => {
    test.skip(!apiBase, 'Set SMOKE_API_BASE to check the deployed API.');

    const health = await request.get(`${apiBase}/health`);
    expect(health.ok()).toBeTruthy();
    await expect(health).toBeOK();
    expect(await health.json()).toMatchObject({ ok: true, service: 'edupress-api' });
  });

  test('deployment health reports subsystem status when configured', async ({ request }) => {
    test.skip(!apiBase, 'Set SMOKE_API_BASE to check the deployed API.');

    const deployment = await request.get(`${apiBase}/health/deployment`);
    const payload = await deployment.json();

    expect(payload.service).toBe('edupress-api');
    expect(payload.checks).toHaveProperty('postgres');
    expect(payload.checks).toHaveProperty('mongo');
    expect(payload.checks).toHaveProperty('redis');
    expect(payload.checks).toHaveProperty('ai_engine');
  });
});
