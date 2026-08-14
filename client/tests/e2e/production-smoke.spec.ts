import { expect, test } from '@playwright/test';

const apiBase = process.env.SMOKE_API_BASE;

async function openApp(page) {
  await page.goto('/', { waitUntil: 'domcontentloaded' });
  await expect(page.getByTestId('home-page')).toBeVisible();
  await expect(page.locator('.app-frame')).toHaveAttribute('data-mounted', 'true', { timeout: 30000 });
}

async function gotoSection(page, section, targetTestId = `${section}-page`) {
  await page.getByTestId(`nav-${section}`).click();
  await expect(page.getByTestId(targetTestId)).toBeVisible();
}

test.describe('deterministic product smoke tests', () => {
  test('homepage renders the learning shell and primary navigation', async ({ page }) => {
    await openApp(page);

    await expect(page.getByTestId('brand-home')).toBeVisible();
    await expect(page.getByTestId('nav-home')).toBeVisible();
    await expect(page.getByTestId('nav-courses')).toBeVisible();
    await expect(page.getByTestId('nav-blog')).toBeVisible();
    await expect(page.getByTestId('nav-contact')).toBeVisible();
    await expect(page.getByTestId('nav-quiz')).toBeVisible();
    await expect(page.getByTestId('home-browse-courses')).toBeVisible();
    await expect(page.getByTestId('home-featured-course')).toBeVisible();
  });

  test('course catalog supports browsing and search', async ({ page }) => {
    await openApp(page);
    await gotoSection(page, 'courses');

    await expect(page.getByTestId('course-search')).toBeVisible();
    await expect.poll(async () => page.locator('[data-testid^="course-card-"]').count()).toBeGreaterThan(0);

    await page.getByTestId('course-search').fill('web');
    await expect.poll(async () => page.locator('[data-testid^="course-card-"]').count()).toBeGreaterThan(0);
  });

  test('course detail exposes the learning content and comments path', async ({ page }) => {
    await openApp(page);
    await gotoSection(page, 'courses');

    await page.locator('[data-testid^="course-detail-"]').first().click();

    await expect(page.getByTestId('course-detail-page')).toBeVisible();
    await expect(page.getByTestId('comments-section')).toBeVisible();
    await expect(page.getByTestId('comment-input')).toBeVisible();
    await expect(page.getByTestId('comment-submit')).toBeVisible();

    await page.getByTestId('comment-input').fill('Deterministic smoke comment draft');
    await expect(page.getByTestId('comment-input')).toHaveValue('Deterministic smoke comment draft');
  });

  test('built-in quiz can answer and explain the first question', async ({ page }) => {
    await openApp(page);
    await gotoSection(page, 'quiz');

    await expect(page.getByTestId('quiz-card')).toBeVisible();
    await page.getByTestId('quiz-option-0').click();
    await page.getByTestId('quiz-submit').click();

    await expect(page.locator('.quiz-explanation')).toBeVisible();
  });

  test('blog and contact form render and accept a local submission', async ({ page }) => {
    await openApp(page);
    await gotoSection(page, 'blog');

    await expect.poll(async () => page.locator('[data-testid^="blog-post-"]').count()).toBeGreaterThan(0);

    await gotoSection(page, 'contact');
    await page.getByTestId('contact-name').fill('QA User');
    await page.getByTestId('contact-email').fill('qa@example.com');
    await page.getByTestId('contact-message').fill('Smoke test message');
    await page.getByTestId('contact-submit').click();
    await expect(page.locator('.toast')).toBeVisible();
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
