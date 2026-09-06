import { test, expect } from '@playwright/test';

test.describe('Nemesis: Retaliation — Viewport Diagnostics E2E', () => {
  test('toggles debug panel and outputs valid copyable diagnostics JSON', async ({ page }) => {
    await page.goto('./');

    const toggleBtn = page.locator('#btn-toggle-debug');
    await expect(toggleBtn).toBeVisible();
    await expect(toggleBtn).toHaveText('🔍 VIEWPORT');

    // Click to open debug panel
    await toggleBtn.click();
    await expect(toggleBtn).toHaveText('✕ CLOSE DEBUG');

    const debugPanel = page.locator('#nemesis-debug-box');
    await expect(debugPanel).toBeVisible();

    const textarea = page.locator('#nemesis-debug-textarea');
    await expect(textarea).toBeVisible();

    const rawJson = await textarea.inputValue();
    const data = JSON.parse(rawJson);

    // Verify diagnostic fields
    expect(data.window.innerWidth).toBeGreaterThan(0);
    expect(data.window.innerHeight).toBeGreaterThan(0);
    expect(data.canvas.width).toBeGreaterThan(0);
    expect(data.canvas.height).toBeGreaterThan(0);
    expect(data.camera).toHaveProperty('x');
    expect(data.camera).toHaveProperty('y');
    expect(data.camera).toHaveProperty('zoom');
    expect(data.userAgent).toBeTruthy();

    // Verify copy button
    const copyBtn = page.locator('#btn-copy-debug');
    await expect(copyBtn).toBeVisible();
    await copyBtn.click();
    await expect(copyBtn).toHaveText('✓ COPIED TO CLIPBOARD!');

    // Click to close
    await toggleBtn.click();
    await expect(debugPanel).not.toBeVisible();
  });
});
