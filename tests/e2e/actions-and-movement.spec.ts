import { test, expect } from '@playwright/test';

test.describe('Nemesis: Retaliation — Interactive Actions & Movement E2E', () => {
  test('allows selecting adjacent rooms, moving, exploring, and progressing phases', async ({ page }) => {
    await page.goto('./');

    const overlay = page.locator('#nemesis-ui-overlay');
    await expect(overlay).toBeVisible();

    // Verify initial location is Landing Zone
    await expect(overlay).toContainText('Target:');
    await expect(overlay).toContainText('YOU ARE HERE');

    // 1. Click on adjacent room slot_1_2 at its real physical canvas screen coordinates
    const targetPos = await page.evaluate(() => {
      const app = (window as any).app;
      const slotDef = app.renderer.getSlotCenter(1, 2); // slot_1_2 at (x=1, y=2)
      return app.renderer.camera.worldToScreen(slotDef.cx, slotDef.cy);
    });

    // Real user mouse click at (x, y) on the canvas
    await page.mouse.click(targetPos.x, targetPos.y);

    // Action Dock should now show Target: slot_1_2 and MOVE button
    const moveBtn = page.locator('#btn-act-move');
    await expect(moveBtn).toBeVisible();
    await expect(moveBtn).toContainText('MOVE (1 Card)');

    // 2. Click MOVE to move into slot_1_2
    await moveBtn.click();

    // Verify actions remaining decreased from 2 to 1
    await expect(overlay).toContainText('Actions Remaining: 1');

    // Verify the character's room in state is now slot_1_2
    const currentRoom = await page.evaluate(() => {
      const app = (window as any).app;
      const activeP = app.state.players[app.state.activePlayerIndex];
      return app.state.characters[activeP.characterId].currentRoomId;
    });
    expect(currentRoom).toBe('slot_1_2');

    // 3. Pass turn for Player 1
    await page.locator('#btn-pass').click();
    await expect(overlay).toContainText('Active: Player 2');

    // 4. Pass turn for Player 2
    await page.locator('#btn-pass').click();

    // Phase transitions to Intruder Phase
    await expect(overlay).toContainText('INTRUDER PHASE READY');
    const resolveIntruderBtn = page.locator('#btn-resolve-intruder');
    await expect(resolveIntruderBtn).toBeVisible();

    // 5. Click RESOLVE INTRUDER PHASE
    await resolveIntruderBtn.click();

    // Transitions to Event Phase
    await expect(overlay).toContainText('EVENT PHASE READY');
    const resolveEventBtn = page.locator('#btn-resolve-event');
    await expect(resolveEventBtn).toBeVisible();

    // 6. Click RESOLVE EVENT PHASE
    await resolveEventBtn.click();

    // Transitions to Cleanup Phase
    await expect(overlay).toContainText('CLEANUP PHASE READY');
    const resolveCleanupBtn = page.locator('#btn-resolve-cleanup');
    await expect(resolveCleanupBtn).toBeVisible();

    // 7. Click START ROUND 2
    await resolveCleanupBtn.click();

    // Round should now be 2, Phase should be player!
    await expect(overlay).toContainText('Round: 2 / 15');
    await expect(overlay).toContainText('Phase: player');
  });
});
