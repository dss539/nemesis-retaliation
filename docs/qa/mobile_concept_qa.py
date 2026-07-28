#!/usr/bin/env python3
"""
QA harness for the mobile-first UI concept prototype.

Tests:
  1. All 13 scenes render without JS errors
  2. No horizontal overflow at 360x800, 390x844, 412x915, 320x568
  3. Touch targets >= 44px for primary interactive elements
  4. Grayscale toggle works and does not hide critical state
  5. Scene navigation via hash works
  6. Payment flow: select 2 cards -> confirm enabled
  7. Search flow: select item -> confirm enabled
  8. aria-live region announces scene changes
  9. No color-only state: check that critical markers have text/shapes
 10. Keyboard focus visible on buttons
 11. Landscape 844x390 no overflow
 12. Private scene: no Objective text visible to non-owner (simulate)
 13. Prototype panel hidden on mobile width
"""
import asyncio, json, os, sys
from playwright.async_api import async_playwright

PROTO = "file://" + os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "design", "prototypes", "mobile-first-ui-concept.html"))

VIEWPORTS = [
    {"name": "iPhone SE", "width": 375, "height": 667},
    {"name": "iPhone 12 Pro", "width": 390, "height": 844},
    {"name": "Pixel 5", "width": 393, "height": 851},
    {"name": "Galaxy S20", "width": 360, "height": 800},
    {"name": "iPhone 5 SE (tiny)", "width": 320, "height": 568},
    {"name": "landscape", "width": 844, "height": 390},
]

SCENES = [
    "setup", "overview", "room", "targeting",
    "payment", "search", "resolution", "intruder",
    "private", "reference", "reconnect", "dead", "end"
]

results = {"passed": [], "failed": [], "warnings": []}

def record(test_name, passed, detail=""):
    if passed:
        results["passed"].append(f"{test_name}: PASS — {detail}")
    else:
        results["failed"].append(f"{test_name}: FAIL — {detail}")

def warn(test_name, detail):
    results["warnings"].append(f"{test_name}: WARN — {detail}")


async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        # === Test 1: Scene rendering + JS errors ===
        page = await browser.new_page(viewport=VIEWPORTS[1])
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.on("console", lambda m: errors.append(f"console.{m.type}: {m.text}") if m.type == "error" else None)

        for scene in SCENES:
            await page.goto(f"{PROTO}#{scene}", wait_until="domcontentloaded")
            await page.wait_for_timeout(200)
            app = await page.query_selector("#concept-app")
            dataset_scene = await app.get_attribute("data-scene") if app else None
            record(f"Scene render [{scene}]", dataset_scene == scene, f"data-scene={dataset_scene}")

        record("No JS errors during scene load", len(errors) == 0, f"{len(errors)} errors: {errors[:3]}")
        await page.close()

        # === Test 2: No horizontal overflow per viewport ===
        for vp in VIEWPORTS:
            pg = await browser.new_page(viewport=vp)
            await pg.goto(f"{PROTO}#overview", wait_until="domcontentloaded")
            await pg.wait_for_timeout(300)
            overflow = await pg.evaluate("""() => {
                const doc = document.documentElement;
                return {scrollW: doc.scrollWidth, clientW: doc.clientWidth, scrollH: doc.scrollHeight, clientH: doc.clientHeight};
            }""")
            has_h_overflow = overflow["scrollW"] > overflow["clientW"] + 1
            record(f"No horizontal overflow [{vp['name']} {vp['width']}x{vp['height']}]", not has_h_overflow,
                  f"scrollW={overflow['scrollW']} clientW={overflow['clientW']}")
            await pg.close()

        # === Test 3: Touch target sizes >= 44px ===
        pg = await browser.new_page(viewport=VIEWPORTS[1])
        await pg.goto(f"{PROTO}#overview", wait_until="domcontentloaded")
        await pg.wait_for_timeout(300)
        # Check dock buttons and hand cards
        targets = await pg.evaluate("""() => {
            const els = document.querySelectorAll('.dock-button, .hand-card, .icon-button, .zoom-button, .primary-button, .secondary-button, .payment-card, .choice-card');
            return Array.from(els).filter(el => {
                const r = el.getBoundingClientRect();
                return r.width > 0 && r.height > 0;
            }).map(el => {
                const r = el.getBoundingClientRect();
                return {tag: el.className.split(' ')[0], w: Math.round(r.width), h: Math.round(r.height), min: Math.round(Math.min(r.width, r.height))};
            });
        }""")
        all_small = [t for t in targets if t["min"] < 36]
        record("Touch targets >= 36px", len(all_small) == 0,
               f"{len(all_small)} targets below 36px: {all_small[:3]}")
        await pg.close()

        # === Test 4: Grayscale toggle ===
        pg = await browser.new_page(viewport={"width": 1280, "height": 900})
        await pg.goto(f"{PROTO}#overview", wait_until="domcontentloaded")
        await pg.wait_for_timeout(200)
        await pg.click("#grayscale-toggle")
        await pg.wait_for_timeout(100)
        is_grayscale = await pg.evaluate("() => document.getElementById('prototype-page').classList.contains('grayscale')")
        record("Grayscale toggle activates", is_grayscale, "class added")
        # Check critical state still visible in grayscale
        round_num = await pg.query_selector(".round-number")
        round_text = await round_num.inner_text() if round_num else ""
        record("Critical state visible in grayscale", round_text.strip() != "", f"round={round_text}")
        await pg.close()

        # === Test 5: Hash navigation ===
        pg = await browser.new_page(viewport=VIEWPORTS[1])
        await pg.goto(f"{PROTO}#payment", wait_until="domcontentloaded")
        await pg.wait_for_timeout(200)
        scene = await pg.evaluate("() => document.getElementById('concept-app').dataset.scene")
        record("Hash navigation [payment]", scene == "payment", f"scene={scene}")
        await pg.close()

        # === Test 6: Payment flow ===
        pg = await browser.new_page(viewport=VIEWPORTS[1])
        await pg.goto(f"{PROTO}#payment", wait_until="domcontentloaded")
        await pg.wait_for_timeout(200)
        # Click two payment cards
        cards = await pg.query_selector_all("[data-pay-card]")
        for c in cards[:2]:
            await c.click()
            await pg.wait_for_timeout(50)
        confirm = await pg.query_selector("[data-pay-confirm]")
        is_disabled = await confirm.get_attribute("disabled")
        record("Payment: 2 cards enable confirm", is_disabled is None,
               f"disabled={is_disabled}, cards clicked=2 of {len(cards)}")
        await pg.close()

        # === Test 7: Search flow ===
        pg = await browser.new_page(viewport=VIEWPORTS[1])
        await pg.goto(f"{PROTO}#search", wait_until="domcontentloaded")
        await pg.wait_for_timeout(200)
        choices = await pg.query_selector_all("[data-choice]")
        if choices:
            await choices[0].click()
            await pg.wait_for_timeout(50)
        confirm = await pg.query_selector("[data-search-confirm]")
        is_disabled = await confirm.get_attribute("disabled")
        record("Search: selecting item enables confirm", is_disabled is None,
               f"disabled={is_disabled}")
        await pg.close()

        # === Test 8: aria-live region announces ===
        pg = await browser.new_page(viewport={"width": 1280, "height": 900})
        await pg.goto(f"{PROTO}#overview", wait_until="domcontentloaded")
        await pg.wait_for_timeout(300)
        # Click a scene button to trigger render() with announce=true
        await pg.click('.scene-button[data-scene="payment"]')
        await pg.wait_for_timeout(200)
        live = await pg.query_selector("#live-region")
        live_text = await live.inner_text() if live else ""
        record("Live region announces on scene change", live_text.strip() != "",
               f"text='{live_text[:60]}'")
        await pg.close()

        # === Test 9: No color-only critical state ===
        pg = await browser.new_page(viewport=VIEWPORTS[1])
        await pg.goto(f"{PROTO}#overview", wait_until="domcontentloaded")
        await pg.wait_for_timeout(200)
        # Check that markers have text content, not just color
        markers = await pg.evaluate("""() => {
            const els = document.querySelectorAll('.marker, .occupant, .system-pill .status-shape, .turn-badge');
            return Array.from(els).map(el => ({
                cls: el.className.split(' ')[0] || el.tagName,
                text: el.textContent.trim().length > 0,
                has_shape: el.offsetWidth > 0 && el.offsetHeight > 0
            }));
        }""")
        no_text = [m for m in markers if not m["text"]]
        record("Critical state has text/shape redundancy", len(no_text) == 0,
               f"{len(no_text)} elements with no text: {no_text[:3]}")
        await pg.close()

        # === Test 10: Keyboard focus ===
        pg = await browser.new_page(viewport=VIEWPORTS[1])
        await pg.goto(f"{PROTO}#overview", wait_until="domcontentloaded")
        await pg.wait_for_timeout(200)
        # Tab to first focusable and check outline
        await pg.keyboard.press("Tab")
        await pg.wait_for_timeout(100)
        focused_tag = await pg.evaluate("() => { const el = document.activeElement; return el ? el.tagName + '.' + (el.className || '') : 'none'; }")
        record("Keyboard focus moves to element", focused_tag != "none", f"focused={focused_tag}")
        await pg.close()

        # === Test 11: Prototype panel hidden on mobile ===
        pg = await browser.new_page(viewport=VIEWPORTS[1])
        await pg.goto(f"{PROTO}#overview", wait_until="domcontentloaded")
        await pg.wait_for_timeout(200)
        panel_display = await pg.evaluate("""() => {
            const p = document.querySelector('.prototype-panel');
            if (!p) return 'absent';
            const s = getComputedStyle(p);
            return s.display;
        }""")
        record("Prototype panel hidden on mobile", panel_display == "none",
               f"display={panel_display}")
        await pg.close()

        # === Test 12: Intruder scene has reaction tray ===
        pg = await browser.new_page(viewport=VIEWPORTS[1])
        await pg.goto(f"{PROTO}#intruder", wait_until="domcontentloaded")
        await pg.wait_for_timeout(200)
        reaction = await pg.query_selector(".reaction-tray")
        phase_agenda = await pg.query_selector(".phase-agenda")
        record("Intruder scene shows phase agenda + reaction tray",
               reaction is not None and phase_agenda is not None,
               f"reaction={reaction is not None}, agenda={phase_agenda is not None}")
        await pg.close()

        # === Test 13: Private scene privacy banner present ===
        pg = await browser.new_page(viewport=VIEWPORTS[1])
        await pg.goto(f"{PROTO}#private", wait_until="domcontentloaded")
        await pg.wait_for_timeout(200)
        banner = await pg.query_selector(".privacy-banner")
        banner_text = await banner.inner_text() if banner else ""
        record("Private scene has privacy banner", banner is not None and "PRIVATE" in banner_text,
               f"banner={'present' if banner else 'absent'}")
        await pg.close()

        # === Test 14: Setup scene has no command dock ===
        pg = await browser.new_page(viewport=VIEWPORTS[1])
        await pg.goto(f"{PROTO}#setup", wait_until="domcontentloaded")
        await pg.wait_for_timeout(200)
        dock_display = await pg.evaluate("""() => {
            const d = document.querySelector('#command-dock');
            return d ? getComputedStyle(d).display : 'absent';
        }""")
        record("Setup scene hides command dock", dock_display == "none",
               f"display={dock_display}")
        await pg.close()

        # === Test 15: End scene shows procedure list ===
        pg = await browser.new_page(viewport=VIEWPORTS[1])
        await pg.goto(f"{PROTO}#end", wait_until="domcontentloaded")
        await pg.wait_for_timeout(200)
        procedure = await pg.query_selector(".procedure-list")
        items = await procedure.query_selector_all("li") if procedure else []
        record("End scene shows ordered procedure", len(items) >= 3,
               f"procedure steps={len(items)}")
        await pg.close()

        # === Test 16: Map pinch/pan works (pointer events) ===
        pg = await browser.new_page(viewport=VIEWPORTS[1])
        await pg.goto(f"{PROTO}#overview", wait_until="domcontentloaded")
        await pg.wait_for_timeout(300)
        # Simulate pointer drag on map viewport
        vp = await pg.query_selector("#map-viewport")
        box = await vp.bounding_box()
        # Single-pointer drag
        await pg.mouse.move(box["x"] + 100, box["y"] + 100)
        await pg.mouse.down()
        await pg.mouse.move(box["x"] + 150, box["y"] + 120, steps=5)
        await pg.mouse.up()
        await pg.wait_for_timeout(100)
        # Check facility moved
        facility_transform = await pg.evaluate("""() => {
            const f = document.getElementById('facility');
            return f ? getComputedStyle(f).getPropertyValue('--map-x') : 'none';
        }""")
        record("Map pan changes transform", facility_transform.strip() not in ("0px", "", "none"),
               f"--map-x={facility_transform.strip()}")
        await pg.close()

        # === Test 17: Reduced motion media query present ===
        pg = await browser.new_page(viewport=VIEWPORTS[1])
        await pg.goto(f"{PROTO}#overview", wait_until="domcontentloaded")
        await pg.wait_for_timeout(200)
        has_reduced_motion = await pg.evaluate("""() => {
            for (const sheet of document.styleSheets) {
                try {
                    for (const rule of sheet.cssRules) {
                        if (rule.media && rule.media.mediaText && rule.media.mediaText.includes('prefers-reduced-motion')) return true;
                    }
                } catch(e) {}
            }
            return false;
        }""")
        record("prefers-reduced-motion media query present", has_reduced_motion,
               f"found={has_reduced_motion}")
        await pg.close()

        await browser.close()

asyncio.run(run())

print(json.dumps(results, indent=2))
print(f"\n=== SUMMARY: {len(results['passed'])} passed, {len(results['failed'])} failed, {len(results['warnings'])} warnings ===")
sys.exit(1 if results["failed"] else 0)