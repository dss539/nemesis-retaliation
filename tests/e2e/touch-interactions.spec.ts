import { test, expect } from '@playwright/test';

test.describe('Nemesis: Retaliation — Multi-Touch Gestures E2E', () => {
  test('smoothly handles pinch-zoom and transition to single-finger pan without jumping', async ({ page }) => {
    await page.goto('./');

    const canvas = page.locator('#tactical-canvas');
    await expect(canvas).toBeVisible();

    // Verify initial camera coordinates
    const initialCam = await page.evaluate(() => {
      const app = (window as any).app;
      return {
        x: app.renderer.camera.transform.x,
        y: app.renderer.camera.transform.y,
        zoom: app.renderer.camera.transform.zoom,
      };
    });

    // Simulate 2-finger pinch
    await page.evaluate(() => {
      const canvasEl = document.getElementById('tactical-canvas')!;
      
      const createTouch = (id: number, x: number, y: number) => {
        return new Touch({
          identifier: id,
          target: canvasEl,
          clientX: x,
          clientY: y,
          pageX: x,
          pageY: y,
          screenX: x,
          screenY: y,
        });
      };

      // 1. Touch start with 2 fingers
      const t1Start = createTouch(1, 400, 300);
      const t2Start = createTouch(2, 500, 300);
      canvasEl.dispatchEvent(new TouchEvent('touchstart', {
        touches: [t1Start, t2Start],
        targetTouches: [t1Start, t2Start],
        changedTouches: [t1Start, t2Start],
      }));

      // 2. Pinch spread (zoom in)
      const t1Move = createTouch(1, 350, 300);
      const t2Move = createTouch(2, 550, 300);
      canvasEl.dispatchEvent(new TouchEvent('touchmove', {
        touches: [t1Move, t2Move],
        targetTouches: [t1Move, t2Move],
        changedTouches: [t1Move, t2Move],
      }));

      // 3. Lift finger 2 (touchend with 1 remaining touch)
      canvasEl.dispatchEvent(new TouchEvent('touchend', {
        touches: [t1Move],
        targetTouches: [t1Move],
        changedTouches: [t2Move],
      }));

      // 4. Move finger 1 slightly (5px to the right)
      const t1SlightMove = createTouch(1, 355, 300);
      canvasEl.dispatchEvent(new TouchEvent('touchmove', {
        touches: [t1SlightMove],
        targetTouches: [t1SlightMove],
        changedTouches: [t1SlightMove],
      }));
    });

    const postTouchCam = await page.evaluate(() => {
      const app = (window as any).app;
      return {
        x: app.renderer.camera.transform.x,
        y: app.renderer.camera.transform.y,
        zoom: app.renderer.camera.transform.zoom,
      };
    });

    // Zoom should have increased from pinch
    expect(postTouchCam.zoom).toBeGreaterThan(initialCam.zoom);

    // Delta X between touch 1 slight move (5px) should be exactly 5px, not a jump of 100+ px!
    const deltaXAfterPinch = await page.evaluate(() => {
      const canvasEl = document.getElementById('tactical-canvas')!;
      const camBefore = (window as any).app.renderer.camera.transform.x;
      
      const touchMove = new Touch({
        identifier: 1,
        target: canvasEl,
        clientX: 365,
        clientY: 300,
        pageX: 365,
        pageY: 300,
      });

      canvasEl.dispatchEvent(new TouchEvent('touchmove', {
        touches: [touchMove],
        targetTouches: [touchMove],
        changedTouches: [touchMove],
      }));

      const camAfter = (window as any).app.renderer.camera.transform.x;
      return Math.abs(camAfter - camBefore);
    });

    // Moving 10px should pan exactly 10px without any jumping
    expect(deltaXAfterPinch).toBeCloseTo(10, 1);
  });
});
