import { test, expect } from '@playwright/test';

test.describe('Nemesis: Retaliation — Turn Flow E2E', () => {
  test('handles pass action, rotates active player, and transitions phase', async ({ page }) => {
    await page.goto('./');

    const overlay = page.locator('#nemesis-ui-overlay');
    const passButton = page.locator('#btn-pass');

    // Round 1 begins with Player 1 active in player phase
    await expect(overlay).toContainText('Phase: player');
    await expect(overlay).toContainText('Active: Player 1');

    // Player 1 passes
    await passButton.click();

    // Turn should transition to Player 2
    await expect(overlay).toContainText('Active: Player 2');
    await expect(overlay).toContainText('Actions Remaining: 2');

    // Player 2 passes
    await passButton.click();

    // Both players have passed; phase should transition to intruder phase
    await expect(overlay).toContainText('Phase: intruder');
  });
});
