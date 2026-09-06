import { test, expect } from '@playwright/test';

test.describe('Nemesis: Retaliation — Multi-Browser Multiplayer P2P E2E', () => {
  test('two independent browser sessions connect, synchronize actions, and play against each other', async ({ browser }) => {
    // Launch two separate pages in the browser session (simulating two tabs/windows)
    const context = await browser.newContext({
      viewport: { width: 1280, height: 720 },
    });

    const page1 = await context.newPage();
    const page2 = await context.newPage();

    const testRoom = `TEST${Math.floor(Math.random() * 8999 + 1000)}`;

    // 2. Browser 1 opens as Host
    await page1.goto(`./?room=${testRoom}&host=true&player=1`);
    await expect(page1.locator('#nemesis-ui-overlay')).toBeVisible();
    await expect(page1.locator('#nemesis-ui-overlay')).toContainText(`Room Code: ${testRoom}`);
    await expect(page1.locator('#nemesis-ui-overlay')).toContainText('Active: Player 1');

    // 3. Browser 2 opens as Client joining the same room
    await page2.goto(`./?room=${testRoom}&join=true&player=2`);
    await expect(page2.locator('#nemesis-ui-overlay')).toBeVisible();
    await expect(page2.locator('#nemesis-ui-overlay')).toContainText(`Room Code: ${testRoom}`);
    await expect(page2.locator('#nemesis-ui-overlay')).toContainText('Active: Player 1');

    // 4. Player 1 takes an action in Browser 1: clicks "PASS TURN"
    const passBtn1 = page1.locator('#btn-pass');
    await expect(passBtn1).toBeVisible();
    await passBtn1.click();

    // Verify Player 1's browser updates to Player 2
    await expect(page1.locator('#nemesis-ui-overlay')).toContainText('Active: Player 2');

    // Verify Player 2's browser received the action broadcast over P2P transport and updated!
    await expect(page2.locator('#nemesis-ui-overlay')).toContainText('Active: Player 2');

    // 5. Now Player 2 takes an action in Browser 2: clicks "PASS TURN"
    const passBtn2 = page2.locator('#btn-pass');
    await expect(passBtn2).toBeVisible();
    await passBtn2.click();

    // Since both players passed, both browsers should transition to Intruder Phase!
    await expect(page2.locator('#nemesis-ui-overlay')).toContainText('Phase: intruder');
    await expect(page1.locator('#nemesis-ui-overlay')).toContainText('Phase: intruder');

    // Clean up
    await context.close();
  });
});
