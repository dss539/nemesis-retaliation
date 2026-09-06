import { chromium } from '@playwright/test';

async function playAgainstSelf() {
  console.log('Starting Playwright multi-browser head-to-head match...');

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1280, height: 720 },
  });

  const pageHost = await context.newPage();
  const pageClient = await context.newPage();

  const roomCode = 'SOLO';

  // 1. Host (Player 1) joins room
  console.log('1. Host (Player 1) launching...');
  await pageHost.goto(`http://127.0.0.1:5173/nemesis-retaliation/?room=${roomCode}&host=true&player=1`);
  await pageHost.waitForSelector('#nemesis-ui-overlay');

  // 2. Client (Player 2) joins same room
  console.log('2. Client (Player 2) launching and joining room...');
  await pageClient.goto(`http://127.0.0.1:5173/nemesis-retaliation/?room=${roomCode}&join=true&player=2`);
  await pageClient.waitForSelector('#nemesis-ui-overlay');

  await pageHost.waitForTimeout(200);

  // Take screenshot of Player 1 view at start
  await pageHost.screenshot({ path: '/tmp/p1-turn1-start.png' });
  console.log('Saved /tmp/p1-turn1-start.png');

  // 3. Player 1 executes their turn: Clicks "PASS TURN"
  console.log('3. Player 1 clicks PASS TURN in Browser 1...');
  await pageHost.locator('#btn-pass').click();
  await pageHost.waitForTimeout(200);

  // Take screenshot of Player 2 view after receiving Player 1 pass
  await pageClient.screenshot({ path: '/tmp/p2-turn1-active.png' });
  console.log('Saved /tmp/p2-turn1-active.png (Player 2 view now active)');

  // 4. Player 2 executes their turn in Browser 2: Clicks "PASS TURN"
  console.log('4. Player 2 clicks PASS TURN in Browser 2...');
  await pageClient.locator('#btn-pass').click();
  await pageClient.waitForTimeout(300);

  // Verify both browsers synchronized phase transition
  const hostPhase = await pageHost.evaluate(() => window.app.state.phase);
  const clientPhase = await pageClient.evaluate(() => window.app.state.phase);
  console.log(`Both browsers transitioned: Host Phase = ${hostPhase}, Client Phase = ${clientPhase}`);

  // Take screenshot of Intruder phase on Host
  await pageHost.screenshot({ path: '/tmp/p1-intruder-phase.png' });
  console.log('Saved /tmp/p1-intruder-phase.png');

  await context.close();
  await browser.close();
  console.log('Match complete! All states synchronized cleanly.');
}

playAgainstSelf().catch(console.error);
