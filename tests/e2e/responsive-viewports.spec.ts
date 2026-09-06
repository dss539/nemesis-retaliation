import { test, expect } from '@playwright/test';

const VIEWPORTS = [
  { name: 'Mobile Phone Portrait (Pixel / iPhone)', width: 390, height: 844 },
  { name: 'Mobile Compact (SE / Small Android)', width: 360, height: 740 },
  { name: 'Tablet Portrait (Lenovo Tab / iPad)', width: 800, height: 1180 },
  { name: 'Tablet Landscape (Lenovo Tab / iPad)', width: 1180, height: 800 },
  { name: 'Desktop Full HD', width: 1920, height: 1080 },
];

test.describe('Nemesis: Retaliation — Multi-Viewport Responsive E2E', () => {
  for (const vp of VIEWPORTS) {
    test(`renders cleanly and without overflow at ${vp.name} (${vp.width}x${vp.height})`, async ({ page }) => {
      await page.setViewportSize({ width: vp.width, height: vp.height });
      await page.goto('./');

      const canvas = page.locator('#tactical-canvas');
      await expect(canvas).toBeVisible();

      const overlay = page.locator('#nemesis-ui-overlay');
      await expect(overlay).toBeVisible();

      // Verify header elements
      await expect(page.locator('.nemesis-brand')).toHaveText('NEMESIS: RETALIATION');
      await expect(overlay).toContainText('Round: 1 / 15');
      await expect(overlay).toContainText('Phase: player');
      await expect(overlay).toContainText('Room Code:');

      // Verify pass button visibility and clickability
      const passBtn = page.locator('#btn-pass');
      await expect(passBtn).toBeVisible();

      // Verify pass button bounding box is inside the viewport
      const passBox = await passBtn.boundingBox();
      expect(passBox).not.toBeNull();
      if (passBox) {
        expect(passBox.x).toBeGreaterThanOrEqual(0);
        expect(passBox.x + passBox.width).toBeLessThanOrEqual(vp.width + 2); // allow subpixel tolerance
        expect(passBox.y + passBox.height).toBeLessThanOrEqual(vp.height + 2);
      }

      // Verify cards drawer has playable/visible cards
      const cards = page.locator('.nemesis-card');
      const count = await cards.count();
      expect(count).toBeGreaterThanOrEqual(1);

      // Verify body has no accidental horizontal scroll overflow
      const hasHorizontalScroll = await page.evaluate(() => {
        return document.documentElement.scrollWidth > document.documentElement.clientWidth;
      });
      expect(hasHorizontalScroll).toBe(false);

      // Verify clicking Pass Turn works cleanly at this viewport
      await passBtn.click();
      await expect(overlay).toContainText('Active: Player 2');
    });
  }
});
