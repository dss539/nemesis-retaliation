#!/usr/bin/env python3
import asyncio
from playwright.async_api import async_playwright
from pathlib import Path

async def main():
    screenshot_path = "/home/smithers/nemesis-retaliation/docs/qa/map-fixes-verification.png"
    Path(screenshot_path).parent.mkdir(parents=True, exist_ok=True)
    
    console_errors = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1400, "height": 900})
        
        # Capture console errors
        page.on("console", lambda msg: console_errors.append(f"[{msg.type}] {msg.text}") if msg.type in ("error", "warning") else None)
        page.on("pageerror", lambda err: console_errors.append(f"[pageerror] {str(err)}"))
        
        await page.goto("file:///home/smithers/nemesis-retaliation/index.html")
        await page.wait_for_load_state("networkidle")
        
        # Click "Host Game"
        await page.click("#btn-host")
        await page.wait_for_timeout(500)
        
        # Enter name
        await page.fill("#host-name", "TestHost")
        await page.wait_for_timeout(200)
        
        # Click "Create Game"
        await page.click("text=Create Game")
        await page.wait_for_timeout(3000)
        
        # The Start button is disabled because not all players have joined.
        # Force-start: mark all placeholder players as connected, then call startGame()
        await page.evaluate("""
            () => {
                // Mark all players as connected so startGame() passes its check
                if (window.nemesisEngine && window.nemesisEngine.state) {
                    window.nemesisEngine.state.players.forEach(p => { p.connected = true; p.hasJoined = true; });
                }
                // Call startGame directly
                if (typeof startGame === 'function') startGame();
            }
        """)
        await page.wait_for_timeout(3000)
        
        # Take screenshot
        await page.screenshot(path=screenshot_path, full_page=False)
        print(f"Screenshot saved to {screenshot_path}")
        
        # Print console errors
        if console_errors:
            print(f"\nConsole errors/warnings ({len(console_errors)}):")
            for err in console_errors:
                print(f"  {err}")
        else:
            print("\nNo console errors or warnings detected.")
        
        # Also capture the page title and current URL for verification
        print(f"\nPage title: {await page.title()}")
        print(f"Page URL: {page.url}")
        
        # Check if canvas has content
        canvas = page.locator("#game-canvas")
        if await canvas.count() > 0:
            box = await canvas.bounding_box()
            print(f"Canvas found: {box}")
        else:
            print("Canvas NOT found!")
        
        # Check game screen is active
        game_screen_active = await page.evaluate("document.getElementById('game-screen')?.classList.contains('active')")
        print(f"Game screen active: {game_screen_active}")
        
        # Check engine state
        state_info = await page.evaluate("""
            () => {
                if (!window.nemesisEngine || !window.nemesisEngine.state) return null;
                const s = window.nemesisEngine.state;
                return {
                    phase: s.phase,
                    round: s.round,
                    landingZonePos: s.rooms.landingZone?.position,
                    hibernatoriumPos: s.rooms.hibernatorium?.position,
                    hibernatoriumDiscovered: s.rooms.hibernatorium?.discovered,
                    mapGridKeys: Object.keys(s.mapGrid),
                    missionTaskName: s.missionTask?.name,
                    objectiveChoiceTrack: s.objectiveChoiceTrack
                };
            }
        """)
        print(f"\nEngine state: {state_info}")
        
        await browser.close()

asyncio.run(main())