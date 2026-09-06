import { test, expect } from '@playwright/test';

test.describe('Nemesis: Retaliation — Canvas & Viewport E2E', () => {
  test('canvas mounts, resizes with window, and accepts pan/zoom inputs', async ({ page }) => {
    await page.goto('./');

    const canvas = page.locator('#tactical-canvas');
    await expect(canvas).toBeVisible();

    // Verify initial canvas size
    const initialSize = await canvas.evaluate((el: HTMLCanvasElement) => ({
      width: el.width,
      height: el.height,
    }));
    expect(initialSize.width).toBeGreaterThan(0);
    expect(initialSize.height).toBeGreaterThan(0);

    // Resize viewport and verify canvas dimensions update
    await page.setViewportSize({ width: 1024, height: 768 });
    await page.waitForTimeout(200);

    const resizedSize = await canvas.evaluate((el: HTMLCanvasElement) => ({
      width: el.width,
      height: el.height,
    }));
    expect(resizedSize.width).toBe(1024);
    expect(resizedSize.height).toBe(768);

    // Pan canvas with mouse drag
    const box = await canvas.boundingBox();
    expect(box).not.toBeNull();
    const startX = box!.x + box!.width / 2;
    const startY = box!.y + box!.height / 2;

    await page.mouse.move(startX, startY);
    await page.mouse.down();
    await page.mouse.move(startX + 100, startY + 50);
    await page.mouse.up();

    // Mouse wheel zoom
    await page.mouse.wheel(0, -120);

    // Verify application state remains healthy
    const appState = await page.evaluate(() => {
      const win = window as any;
      return win.app ? { round: win.app.state.round, phase: win.app.state.phase } : null;
    });

    expect(appState).not.toBeNull();
    expect(appState?.round).toBe(1);
    expect(appState?.phase).toBe('player');
  });
});
