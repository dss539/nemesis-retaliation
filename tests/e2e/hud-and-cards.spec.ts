import { test, expect } from '@playwright/test';

test.describe('Nemesis: Retaliation — Player HUD and Cards E2E', () => {
  test('displays active player info, character stats, and hand action cards', async ({ page }) => {
    await page.goto('./');

    const overlay = page.locator('#nemesis-ui-overlay');
    await expect(overlay).toBeVisible();

    // Verify Active Player indicator and stats
    await expect(overlay).toContainText('Active: Player 1');
    await expect(overlay).toContainText('Actions Remaining: 2');
    await expect(overlay).toContainText(/HP:\s*\d+\/\d+/);
    await expect(overlay).toContainText(/O2:\s*\d+/);
    await expect(overlay).toContainText('🛡️ Safe');

    // Verify Pass Turn button
    const passButton = page.locator('#btn-pass');
    await expect(passButton).toBeVisible();
    await expect(passButton).toHaveText('PASS TURN');

    // Verify Action Cards in hand
    // Hand cards are rendered inside the bottom drawer
    const cardElements = overlay.locator('.nemesis-card');
    await expect(cardElements).toHaveCount(5);

    // Each card should show a combat status badge
    for (let i = 0; i < 5; i++) {
      const card = cardElements.nth(i);
      const text = await card.innerText();
      expect(text.length).toBeGreaterThan(0);
      const hasCombatBadge =
        text.includes('Playable in Combat') || text.includes('Out-of-Combat Only');
      expect(hasCombatBadge).toBe(true);
    }
  });
});
