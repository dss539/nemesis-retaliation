#!/usr/bin/env python3
"""Quick QA: verify hand bar + action panel overlays render correctly."""
import subprocess, json, os

result = subprocess.run([
    "node", "-e", """
const { chromium } = require('playwright');
(async () => {
    const browser = await chromium.launch({ headless: true });
    const page = await browser.newPage({ viewport: { width: 1400, height: 900 } });
    const errors = [];
    page.on('console', msg => { if (msg.type() === 'error') errors.push(msg.text); });
    page.on('pageerror', err => errors.push(String(err)));
    await page.goto('file:///home/smithers/nemesis-retaliation/index.html');
    await page.click('#btn-host');
    await page.fill('#host-name', 'Tester');
    await page.click('#host-name-panel .btn-primary');
    await page.waitForSelector('#host-panel', { timeout: 5000 });
    await page.click('#host-start-btn');
    await page.waitForSelector('#game-screen.active', { timeout: 5000 });
    await page.waitForSelector('#game-canvas', { timeout: 5000 });
    await page.waitForTimeout(2000);
    const handVisible = await page.isVisible('#hand-bar');
    const actionVisible = await page.isVisible('#action-panel');
    const handCount = await page.evaluate(() => document.getElementById('hand-bar')?.children.length || 0);
    const actionCount = await page.evaluate(() => document.getElementById('action-panel')?.children.length || 0);
    console.log(JSON.stringify({ handVisible, actionVisible, handCount, actionCount, errors }));
    await page.screenshot({ path: '/home/smithers/nemesis-retaliation/docs/qa/hand-action-verification.png' });
    await browser.close();
})();
"""
], capture_output=True, text=True, timeout=25, cwd="/home/smithers/.local/lib/python3.13/site-packages/playwright")

print("stdout:", result.stdout)
print("stderr:", result.stderr[:500] if result.stderr else "")