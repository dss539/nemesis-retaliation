#!/usr/bin/env python3
"""Browser QA for the mobile-first concept prototype.

The harness exercises every scene at six touch viewport classes, then checks the
highest-risk interactions and the non-color information contract. It does not
claim rules-engine, real-device, or assistive-technology certification.
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import cast

from playwright.async_api import async_playwright
from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[2]
PROTO_PATH = ROOT / "docs" / "design" / "prototypes" / "mobile-first-ui-concept.html"
PROTO = PROTO_PATH.as_uri()
CAPTURE_DIR = ROOT / "docs" / "qa" / "mobile-concept-captures"
CAPTURE = os.environ.get("MOBILE_CONCEPT_SCREENSHOTS", "1") != "0"

VIEWPORTS = [
    {"name": "tiny-portrait", "width": 320, "height": 568},
    {"name": "compact-portrait", "width": 360, "height": 800},
    {"name": "standard-portrait", "width": 390, "height": 844},
    {"name": "large-portrait", "width": 412, "height": 915},
    {"name": "phone-landscape", "width": 844, "height": 390},
    {"name": "large-touch-landscape", "width": 1180, "height": 600},
]

SCENES = [
    "setup", "overview", "room", "targeting", "hand", "payment", "search",
    "resolution", "intruder", "private", "reference", "reconnect", "dead", "end",
]

results = {"passed": [], "failed": [], "warnings": [], "matrix_cases": 0}


def record(name, passed, detail=""):
    entry = f"{name}: {'PASS' if passed else 'FAIL'}"
    if detail:
        entry += f" — {detail}"
    results["passed" if passed else "failed"].append(entry)


def warning(name, detail):
    results["warnings"].append(f"{name}: WARN — {detail}")


async def matrix_checks(browser):
    """Render each scene in every viewport and catch layout regressions."""
    for vp in VIEWPORTS:
        context = await browser.new_context(
            viewport={"width": vp["width"], "height": vp["height"]},
            device_scale_factor=1,
            is_mobile=vp["width"] <= 844,
            has_touch=True,
        )
        page = await context.new_page()
        errors = []
        page.on("pageerror", lambda exc, bucket=errors: bucket.append(str(exc)))
        page.on(
            "console",
            lambda msg, bucket=errors: bucket.append(f"console.{msg.type}: {msg.text}")
            if msg.type == "error" else None,
        )

        for scene in SCENES:
            results["matrix_cases"] += 1
            await page.goto(f"{PROTO}#{scene}", wait_until="domcontentloaded")
            await page.wait_for_timeout(60)
            metrics = await page.evaluate("""() => {
                const app = document.getElementById('concept-app');
                const stage = document.getElementById('main-stage');
                const doc = document.documentElement;
                const body = document.body;
                const stageStyle = getComputedStyle(stage);
                const device = document.querySelector('.device');
                const actions = [...document.querySelectorAll('button,input,[role="tab"]')]
                  .filter(el => {
                    const r = el.getBoundingClientRect();
                    const s = getComputedStyle(el);
                    return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none';
                  })
                  .map(el => {
                    const r = el.getBoundingClientRect();
                    return {
                      label: el.getAttribute('aria-label') || el.textContent.trim().slice(0,40) || el.tagName,
                      width: Math.round(r.width * 10) / 10,
                      height: Math.round(r.height * 10) / 10
                    };
                  });
                return {
                  scene: app?.dataset.scene,
                  docScrollW: doc.scrollWidth,
                  bodyScrollW: body.scrollWidth,
                  clientW: doc.clientWidth,
                  stageWidth: stage?.getBoundingClientRect().width || 0,
                  stageHeight: stage?.getBoundingClientRect().height || 0,
                  deviceWidth: device?.clientWidth || 0,
                  stageScrollHeight: stage?.scrollHeight || 0,
                  stageClientHeight: stage?.clientHeight || 0,
                  stageOverflowY: stageStyle.overflowY,
                  actions
                };
            }""")

            prefix = f"{vp['name']} {vp['width']}x{vp['height']} [{scene}]"
            record(f"Matrix render {prefix}", metrics["scene"] == scene, f"scene={metrics['scene']}")
            record(
                f"No page overflow {prefix}",
                max(metrics["docScrollW"], metrics["bodyScrollW"]) <= metrics["clientW"] + 1,
                f"scroll={max(metrics['docScrollW'], metrics['bodyScrollW'])}, client={metrics['clientW']}",
            )
            record(
                f"Usable main stage {prefix}",
                abs(metrics["stageWidth"] - metrics["deviceWidth"]) <= 1 and metrics["stageHeight"] >= 90,
                f"stage={metrics['stageWidth']:.0f}x{metrics['stageHeight']:.0f}; device={metrics['deviceWidth']:.0f}",
            )
            too_small = [
                a for a in metrics["actions"]
                if a["width"] < 44 or a["height"] < 44
            ]
            record(
                f"44px primary targets {prefix}",
                not too_small,
                "all visible controls >=44x44" if not too_small else f"undersized={too_small[:4]}",
            )

        record(
            f"No browser errors [{vp['name']}]",
            not errors,
            "none" if not errors else str(errors[:4]),
        )
        await context.close()


async def semantic_and_interaction_checks(browser):
    context = await browser.new_context(viewport={"width": 390, "height": 844}, has_touch=True)
    page = await context.new_page()
    errors = []
    page.on("pageerror", lambda exc: errors.append(str(exc)))

    await page.goto(f"{PROTO}#overview", wait_until="domcontentloaded")
    await page.wait_for_timeout(100)

    # Non-color contract: each status must carry a visible word/symbol and a
    # distinguishable pattern, border, or shape in addition to decorative hue.
    non_color = await page.evaluate("""() => {
      const style = sel => getComputedStyle(document.querySelector(sel));
      const text = sel => document.querySelector(sel)?.textContent.trim() || '';
      return {
        systemWords: [...document.querySelectorAll('.system-pill')].map(x => x.textContent.trim()),
        fire: {text:text('.marker.fire'), image:style('.marker.fire').backgroundImage},
        malfunction: {text:text('.marker.malfunction'), image:style('.marker.malfunction').backgroundImage},
        secure: {text:text('.marker.secure'), border:style('.marker.secure').borderTopStyle},
        noise: {text:text('.marker.noise'), border:style('.marker.noise').borderTopStyle},
        currentText: getComputedStyle(document.querySelector('.room-shell.current .room'),'::before').content,
        health: text('.vitals'),
        contamination: text('.hand-card.contamination'),
        contaminationBorder: style('.hand-card.contamination').borderTopStyle,
        roster: text('.roster-line')
      };
    }""")
    record(
        "Life Support has text and symbol redundancy",
        all(any(word in item for word in ("Active", "Damaged", "Inactive")) for item in non_color["systemWords"][:3])
        and all(any(mark in item for mark in ("✓", "!", "×")) for item in non_color["systemWords"][:3]),
        str(non_color["systemWords"][:3]),
    )
    record("Fire has symbol and hatch", bool(non_color["fire"]["text"]) and "gradient" in non_color["fire"]["image"], str(non_color["fire"]))
    record("Malfunction has symbol and crosshatch", bool(non_color["malfunction"]["text"]) and non_color["malfunction"]["image"].count("gradient") >= 2, str(non_color["malfunction"]))
    record("Secure has symbol and double border", bool(non_color["secure"]["text"]) and non_color["secure"]["border"] == "double", str(non_color["secure"]))
    record("Noise has symbol and dashed border", bool(non_color["noise"]["text"]) and non_color["noise"]["border"] == "dashed", str(non_color["noise"]))
    record("Current Room has explicit label", "CURRENT" in non_color["currentText"], non_color["currentText"])
    record("Vitals use numbers and segments", "HP" in non_color["health"] and "O₂" in non_color["health"], non_color["health"])
    record("Contamination has text and double border", "CONTAMINATION" in non_color["contamination"] and non_color["contaminationBorder"] == "double", non_color["contaminationBorder"])

    # Public roster may expose total card count, but not private composition or Backpack/Objectives.
    forbidden_public = [term for term in ("Contamination", "Backpack", "Objective", "Action card") if term.lower() in non_color["roster"].lower()]
    record("Public roster is privacy-safe", not forbidden_public and "cards" in non_color["roster"], f"forbidden={forbidden_public}; roster={non_color['roster']}")

    # Room geometry is a rules-fidelity invariant, not a decorative choice. Check
    # the rendered polygon, regular pointy-top proportions, six axes, and the
    # visible space reserved for Corridors between adjacent hex edges.
    geometry = await page.evaluate(r"""() => {
      const shells = [...document.querySelectorAll('.room-shell')];
      const expectedPoints = [[50,0],[100,25],[100,75],[50,100],[0,75],[0,25]];
      const parsePolygon = value => {
        const body = value.match(/^polygon\((.*)\)$/)?.[1] || '';
        return body.split(',').map(pair => pair.trim().split(/\s+/).map(v => parseFloat(v)));
      };
      const polygons = shells.map(shell => parsePolygon(getComputedStyle(shell).clipPath));
      const exactPointyHexes = polygons.every(points =>
        points.length === 6 && points.every((point, i) =>
          point.length === 2 && point.every((value, axis) => Math.abs(value - expectedPoints[i][axis]) < .01)
        )
      );
      const shellRect = shells[0].getBoundingClientRect();
      const ratio = shellRect.width / shellRect.height;
      const directionNames = [...document.querySelectorAll('.corridor[data-direction]')]
        .map(path => path.dataset.direction).sort();
      const center = document.querySelector('.r-life').getBoundingClientRect();
      const centerPoint = {x:center.left + center.width/2, y:center.top + center.height/2};
      const neighbors = {NW:'.r-landing',NE:'.r-server',E:'.r-storage',SE:'.r-nest',SW:'.r-reactor',W:'.r-armory'};
      const expectedAngles = {NW:-120,NE:-60,E:0,SE:60,SW:120,W:180};
      const axes = Object.entries(neighbors).map(([direction, selector]) => {
        const rect = document.querySelector(selector).getBoundingClientRect();
        const dx = rect.left + rect.width/2 - centerPoint.x;
        const dy = rect.top + rect.height/2 - centerPoint.y;
        let angle = Math.atan2(dy, dx) * 180 / Math.PI;
        if (direction === 'W' && angle < 0) angle += 360;
        return {
          direction,
          angle,
          expected:expectedAngles[direction],
          gap:Math.hypot(dx,dy) - shellRect.width
        };
      });
      return {polygons, exactPointyHexes, ratio, directionNames, axes};
    }""")
    expected_directions = ["E", "NE", "NW", "SE", "SW", "W"]
    record(
        "Every Room boundary has six pointy-top vertices",
        geometry["exactPointyHexes"] and all(len(points) == 6 for points in geometry["polygons"]),
        f"polygons={geometry['polygons']}",
    )
    record(
        "Room proportions form regular pointy-top hexagons",
        abs(geometry["ratio"] - (3 ** 0.5 / 2)) < 0.01,
        f"width/height={geometry['ratio']:.5f}; expected={3 ** 0.5 / 2:.5f}",
    )
    record(
        "Corridors use exactly the six canonical directions",
        geometry["directionNames"] == expected_directions,
        f"directions={geometry['directionNames']}",
    )
    record(
        "Neighbor Rooms align to the six hex axes",
        all(abs(axis["angle"] - axis["expected"]) < 0.25 for axis in geometry["axes"]),
        f"axes={geometry['axes']}",
    )
    record(
        "All six Room edges preserve visible Corridor gaps",
        all(axis["gap"] >= 20 for axis in geometry["axes"]),
        f"gaps={[round(axis['gap'], 2) for axis in geometry['axes']]}",
    )

    # Room focus: choosing Armory must focus Armory without moving the Character.
    await page.locator('[data-room="armory"]').click()
    await page.wait_for_timeout(80)
    focus_state = await page.evaluate("""() => ({
      scene: document.getElementById('concept-app').dataset.scene,
      armoryFocused: document.querySelector('.r-armory')?.classList.contains('focused'),
      lifeCurrent: document.querySelector('.r-life')?.classList.contains('current'),
      context: document.querySelector('.context-copy strong')?.textContent.trim(),
      armoryLabel: document.querySelector('.r-armory .room')?.getAttribute('aria-label')
    })""")
    record(
        "One-tap Room focus preserves Character position",
        focus_state == {
            "scene": "room", "armoryFocused": True, "lifeCurrent": True,
            "context": "Armory", "armoryLabel": "Focused. Armory. Unassigned Room. ♨",
        },
        str(focus_state),
    )

    # Legal targeting: only two connected destinations are actionable.
    await page.goto(f"{PROTO}#targeting", wait_until="domcontentloaded")
    targeting = await page.evaluate("""() => ({
      targets: [...document.querySelectorAll('.room-shell.target')].map(x => x.querySelector('.room').dataset.room),
      targetLabels: [...document.querySelectorAll('.room-shell.target .room')].map(x => x.getAttribute('aria-label')),
      invalidInteractive: [...document.querySelectorAll('.room-shell.invalid .room')].filter(x => x.hasAttribute('data-room') || x.tabIndex >= 0).length,
      moveText: [...document.querySelectorAll('.room-shell.target .room')].map(x => getComputedStyle(x,'::after').content)
    })""")
    record(
        "Targeting exposes only legal destinations",
        set(targeting["targets"]) == {"armory", "storage"} and targeting["invalidInteractive"] == 0,
        str(targeting),
    )
    record(
        "Legal targets remain explicit without color",
        all("Legal Move destination" in x for x in targeting["targetLabels"]) and all("MOVE" in x for x in targeting["moveText"]),
        str(targeting["moveText"]),
    )

    # Hand card controls lead to a real inspection state instead of a dead control.
    await page.goto(f"{PROTO}#overview", wait_until="domcontentloaded")
    await page.locator('.hand-card').first.click()
    scene = await page.locator('#concept-app').get_attribute('data-scene')
    record("Hand card opens inspection", scene == "hand", f"scene={scene}")

    # Payment preserves exact choice and does not accept Contamination.
    await page.goto(f"{PROTO}#payment", wait_until="domcontentloaded")
    confirm = page.locator('[data-pay-confirm]')
    record("Payment starts uncommitted", await confirm.is_disabled(), "confirm disabled")
    pay_cards = page.locator('[data-pay-card]')
    await pay_cards.nth(0).click()
    await pay_cards.nth(1).click()
    record("Exactly two eligible Action cards enable payment", not await confirm.is_disabled(), "confirm enabled")
    contamination = page.locator('.payment-card.contam')
    record("Contamination is excluded from Action-card payment", await contamination.get_attribute('aria-disabled') == 'true' and await contamination.get_attribute('tabindex') == '-1', "aria-disabled=true")

    # Search requires an explicit choice.
    await page.goto(f"{PROTO}#search", wait_until="domcontentloaded")
    search_confirm = page.locator('[data-search-confirm]')
    record("Search starts uncommitted", await search_confirm.is_disabled(), "confirm disabled")
    await page.locator('[data-choice]').first.click()
    record("Search choice enables explicit gain", not await search_confirm.is_disabled(), "confirm enabled")

    # Pan and pinch are navigation and must update the map without selecting a Room.
    await page.goto(f"{PROTO}#overview", wait_until="domcontentloaded")
    viewport = page.locator('#map-viewport')
    box = await viewport.bounding_box()
    before_scene = await page.locator('#concept-app').get_attribute('data-scene')
    await page.mouse.move(box["x"] + 170, box["y"] + 150)
    await page.mouse.down()
    await page.mouse.move(box["x"] + 215, box["y"] + 176, steps=5)
    await page.mouse.up()
    pan = await page.evaluate("() => getComputedStyle(document.getElementById('facility')).getPropertyValue('--map-x').trim()")
    after_scene = await page.locator('#concept-app').get_attribute('data-scene')
    record("Map drag pans without tactical selection", pan not in ("", "0px") and before_scene == after_scene == "overview", f"x={pan}, scene={after_scene}")

    cdp = await context.new_cdp_session(page)
    center_x, center_y = box["x"] + box["width"] / 2, box["y"] + box["height"] / 2
    def touch_points(distance):
        return [
            {"x": center_x - distance / 2, "y": center_y, "radiusX": 4, "radiusY": 4, "id": 0},
            {"x": center_x + distance / 2, "y": center_y, "radiusX": 4, "radiusY": 4, "id": 1},
        ]
    await cdp.send("Input.dispatchTouchEvent", {"type": "touchStart", "touchPoints": touch_points(80)})
    for distance in (100, 125, 150):
        await cdp.send("Input.dispatchTouchEvent", {"type": "touchMove", "touchPoints": touch_points(distance)})
        await page.wait_for_timeout(25)
    await cdp.send("Input.dispatchTouchEvent", {"type": "touchEnd", "touchPoints": []})
    scale = await page.evaluate("() => getComputedStyle(document.getElementById('facility')).getPropertyValue('--map-scale').trim()")
    record("Two-point pinch changes free map scale", scale not in ("", ".49", "0.49", ".5", "0.5"), f"scale={scale}")

    # Keyboard and live status feedback.
    await page.goto(f"{PROTO}#overview", wait_until="domcontentloaded")
    await page.keyboard.press("Tab")
    focus = await page.evaluate("""() => {
      const el=document.activeElement, s=getComputedStyle(el); return {tag:el.tagName,label:el.getAttribute('aria-label')||el.textContent.trim(),outline:s.outlineStyle};
    }""")
    record("Keyboard focus is visible and named", focus["tag"] in ("BUTTON", "INPUT") and bool(focus["label"]) and focus["outline"] != "none", str(focus))
    await page.goto(f"{PROTO}#overview", wait_until="domcontentloaded")
    await page.evaluate("() => render('payment')")
    live = await page.locator('#live-region').inner_text()
    record("Scene changes announce without focus theft", "Pay action cost" in live, live)

    # Grayscale itself is a developer audit mode; test content remains present.
    await page.goto(f"{PROTO}#targeting", wait_until="domcontentloaded")
    await page.evaluate("() => document.getElementById('prototype-page').classList.add('grayscale')")
    gray = await page.evaluate("""() => ({
      filter:getComputedStyle(document.getElementById('concept-app')).filter,
      target:getComputedStyle(document.querySelector('.room-shell.target .room'),'::after').content,
      damaged:document.querySelector('.system-pill.damaged').textContent.trim(),
      current:getComputedStyle(document.querySelector('.room-shell.current .room'),'::before').content
    })""")
    record("Grayscale mode retains labels and patterns", gray["filter"] != "none" and "MOVE" in gray["target"] and "Damaged" in gray["damaged"] and "CURRENT" in gray["current"], str(gray))

    record("No semantic-test browser errors", not errors, "none" if not errors else str(errors[:4]))
    await context.close()

    # Reduced-motion behavior in a dedicated emulated context.
    reduced = await browser.new_context(viewport={"width": 390, "height": 844}, reduced_motion="reduce")
    reduced_page = await reduced.new_page()
    await reduced_page.goto(f"{PROTO}#overview", wait_until="domcontentloaded")
    duration = await reduced_page.evaluate("() => getComputedStyle(document.getElementById('facility')).transitionDuration")
    record("Reduced-motion preference suppresses map transition", duration in ("0s", "1e-06s", "0.001ms"), f"duration={duration}")
    await reduced.close()


async def capture_screens(browser):
    if not CAPTURE:
        return
    CAPTURE_DIR.mkdir(parents=True, exist_ok=True)
    shots = [
        ("overview-390x844.png", 390, 844, "overview", False),
        ("targeting-grayscale-390x844.png", 390, 844, "targeting", True),
        ("payment-320x568.png", 320, 568, "payment", False),
        ("room-landscape-844x390.png", 844, 390, "room", False),
        ("prototype-desktop-1280x900.png", 1280, 900, "overview", False),
    ]
    for filename, width, height, scene, grayscale in shots:
        context = await browser.new_context(viewport={"width": width, "height": height})
        page = await context.new_page()
        await page.goto(f"{PROTO}#{scene}", wait_until="domcontentloaded")
        if grayscale:
            await page.evaluate("() => document.getElementById('prototype-page').classList.add('grayscale')")
        await page.screenshot(path=str(CAPTURE_DIR / filename), full_page=True)
        await context.close()
    record("Representative screenshots captured", True, f"{len(shots)} files in {CAPTURE_DIR.relative_to(ROOT)}")
    grayscale_path = CAPTURE_DIR / "targeting-grayscale-390x844.png"
    with Image.open(grayscale_path).convert("RGB") as image:
        red, green, blue = image.split()
        max_channel_spread = max(
            cast(tuple[int, int], ImageChops.difference(red, green).getextrema())[1],
            cast(tuple[int, int], ImageChops.difference(green, blue).getextrema())[1],
            cast(tuple[int, int], ImageChops.difference(red, blue).getextrema())[1],
        )
    record(
        "Grayscale capture contains neutral RGB pixels only",
        max_channel_spread <= 1,
        f"maximum channel spread={max_channel_spread}",
    )


async def run():
    if not PROTO_PATH.exists():
        raise SystemExit(f"prototype missing: {PROTO_PATH}")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        await matrix_checks(browser)
        await semantic_and_interaction_checks(browser)
        await capture_screens(browser)
        await browser.close()


asyncio.run(run())
print(json.dumps(results, indent=2))
print(
    f"\n=== SUMMARY: {len(results['passed'])} passed, "
    f"{len(results['failed'])} failed, {len(results['warnings'])} warnings; "
    f"{results['matrix_cases']} scene/viewport combinations ==="
)
sys.exit(1 if results["failed"] else 0)
