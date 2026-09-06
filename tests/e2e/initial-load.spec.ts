import { test, expect } from '@playwright/test';

test.describe('Nemesis: Retaliation — Initial Load E2E', () => {
  test('loads game, verifies canvas, overlay, header, and clean console', async ({ page }) => {
    const consoleErrors: string[] = [];
    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });
    page.on('pageerror', (err) => {
      consoleErrors.push(err.message);
    });

    const response = await page.goto('./');
    expect(response?.status()).toBe(200);

    // Verify page title
    await expect(page).toHaveTitle('Nemesis: Retaliation — Digital Implementation');

    // Verify tactical canvas exists and has non-zero dimensions
    const canvas = page.locator('#tactical-canvas');
    await expect(canvas).toBeVisible();
    const box = await canvas.boundingBox();
    expect(box).not.toBeNull();
    expect(box!.width).toBeGreaterThan(0);
    expect(box!.height).toBeGreaterThan(0);

    // Verify UI overlay is mounted
    const overlay = page.locator('#nemesis-ui-overlay');
    await expect(overlay).toBeVisible();

    // Verify header components
    await expect(overlay).toContainText('NEMESIS: RETALIATION');
    await expect(overlay).toContainText('Round: 1 / 15');
    await expect(overlay).toContainText('Phase: player');
    await expect(overlay).toContainText(/Room Code:\s*[A-Z0-9]{4}/);

    // Verify Life Support indicators
    await expect(overlay).toContainText('Sec A: ON');
    await expect(overlay).toContainText('Sec B: ON');
    await expect(overlay).toContainText('Sec C: ON');

    // No uncaught errors during startup
    expect(consoleErrors).toEqual([]);
  });
});
