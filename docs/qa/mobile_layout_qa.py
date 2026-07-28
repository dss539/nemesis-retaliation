#!/usr/bin/env python3
"""Focused mobile layout regression for zoom, pan, and overflow scrolling."""

import os
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_URL = os.environ.get("MOBILE_QA_URL", "http://127.0.0.1:8891/?mobile-qa=1")
CAPTURE_SCREENSHOTS = os.environ.get("MOBILE_QA_SCREENSHOTS", "1") != "0"
ROOT = Path(__file__).resolve().parents[2]


def check(condition, message, failures):
    if not condition:
        failures.append(message)


def pinch_map(context, page, start_distance=80, end_distance=170):
    """Dispatch a real two-point touch gesture through Chromium's input stack."""
    box = page.evaluate("""() => {
        const wrapper = document.getElementById('canvas-wrapper').getBoundingClientRect();
        const canvas = document.getElementById('game-canvas').getBoundingClientRect();
        return {
            x: (Math.max(wrapper.left, canvas.left) + Math.min(wrapper.right, canvas.right)) / 2,
            y: (Math.max(wrapper.top, canvas.top) + Math.min(wrapper.bottom, canvas.bottom)) / 2
        };
    }""")
    cdp = context.new_cdp_session(page)

    def points(distance):
        return [
            {"x": box["x"] - distance / 2, "y": box["y"], "radiusX": 4, "radiusY": 4, "id": 0},
            {"x": box["x"] + distance / 2, "y": box["y"], "radiusX": 4, "radiusY": 4, "id": 1},
        ]

    cdp.send("Input.dispatchTouchEvent", {
        "type": "touchStart", "touchPoints": points(start_distance)
    })
    for step in range(1, 4):
        distance = start_distance + (end_distance - start_distance) * step / 3
        cdp.send("Input.dispatchTouchEvent", {"type": "touchMove", "touchPoints": points(distance)})
        page.wait_for_timeout(30)
    cdp.send("Input.dispatchTouchEvent", {"type": "touchEnd", "touchPoints": []})
    page.wait_for_timeout(100)


def exercise_viewport(browser, name, width, height):
    context = browser.new_context(
        viewport={"width": width, "height": height},
        device_scale_factor=2,
        is_mobile=True,
        has_touch=True,
    )
    page = context.new_page()
    errors = []
    page.on("pageerror", lambda exc: errors.append(str(exc)))
    page.goto(BASE_URL, wait_until="networkidle")

    page.evaluate("""() => {
        document.getElementById('lobby-screen').classList.remove('active');
        document.getElementById('game-screen').classList.add('active');
        Renderer.init('game-canvas');
        Renderer.setState({
            corridors: [], rooms: {}, intruders: [], players: [],
            robot: { revealed: false }, round: 1,
            autodestruction: { active: false, token: null }, landerRound: 8
        });
        UI.switchTab('board');
    }""")
    page.wait_for_timeout(200)

    failures = []
    viewport = page.locator('meta[name="viewport"]').get_attribute("content") or ""
    check("user-scalable=no" not in viewport and "maximum-scale=1" not in viewport,
          f"{name}: browser pinch zoom is disabled", failures)

    initial_map_metrics = page.evaluate("""() => {
        const wrapper = document.getElementById('canvas-wrapper');
        const canvas = document.getElementById('game-canvas');
        const rect = canvas.getBoundingClientRect();
        return {
            wrapperWidth: wrapper.clientWidth,
            canvasWidth: rect.width,
            canvasHeight: rect.height,
            centerWidth: document.getElementById('center-panel').getBoundingClientRect().width,
            mobileNavDisplay: getComputedStyle(document.getElementById('mobile-nav')).display
        };
    }""")
    check(initial_map_metrics["canvasWidth"] >= initial_map_metrics["wrapperWidth"] - 2,
          f"{name}: fitted map is squeezed narrower than its panel", failures)
    check(abs(initial_map_metrics["canvasWidth"] / initial_map_metrics["canvasHeight"] - 1500 / 1050) < 0.01,
          f"{name}: fitted map does not preserve its aspect ratio", failures)
    check(initial_map_metrics["mobileNavDisplay"] != "none",
          f"{name}: touch-first viewport did not activate the tabbed layout", failures)
    check(initial_map_metrics["centerWidth"] >= width - 2,
          f"{name}: tabbed board does not use the viewport width", failures)

    zoom_in = page.locator('[data-map-zoom="in"]')
    zoom_out = page.locator('[data-map-zoom="out"]')
    fit = page.locator('[data-map-zoom="fit"]')
    check(zoom_in.count() == 1 and zoom_out.count() == 1 and fit.count() == 1,
          f"{name}: map zoom controls are missing", failures)

    if zoom_in.count() == 1:
        zoom_in.click()
        first_step = page.evaluate("""() => ({
            zoom: Renderer.mapZoom,
            label: document.getElementById('map-zoom-level').textContent
        })""")
        check(abs(first_step["zoom"] - 1.1) < 0.001 and first_step["label"] == "110%",
              f"{name}: zoom controls do not step by 10%", failures)

        zoom_out.click()
        zoom_out.click()
        zoom_out_step = page.evaluate("() => Renderer.mapZoom")
        check(abs(zoom_out_step - 0.9) < 0.001,
              f"{name}: zoom-out control does not step by 10%", failures)
        fit.click()

        for _ in range(30):
            if zoom_in.is_disabled():
                break
            zoom_in.click()
        page.wait_for_timeout(100)
        map_metrics = page.evaluate("""() => {
            const wrapper = document.getElementById('canvas-wrapper');
            const canvas = document.getElementById('game-canvas');
            wrapper.scrollLeft = 120;
            wrapper.scrollTop = 80;
            return {
                wrapperWidth: wrapper.clientWidth,
                wrapperHeight: wrapper.clientHeight,
                scrollWidth: wrapper.scrollWidth,
                scrollHeight: wrapper.scrollHeight,
                scrollLeft: wrapper.scrollLeft,
                scrollTop: wrapper.scrollTop,
                touchAction: getComputedStyle(canvas).touchAction,
                zoom: Renderer.mapZoom
            };
        }""")
        check(map_metrics["zoom"] > 1, f"{name}: zoom-in does not increase map scale", failures)
        check(map_metrics["scrollWidth"] > map_metrics["wrapperWidth"],
              f"{name}: zoomed map does not overflow horizontally for panning", failures)
        check(map_metrics["scrollHeight"] > map_metrics["wrapperHeight"],
              f"{name}: zoomed map does not overflow vertically for panning", failures)
        check(map_metrics["scrollLeft"] > 0 and map_metrics["scrollTop"] > 0,
              f"{name}: zoomed map cannot be panned by scrolling", failures)
        check("pan-x" in map_metrics["touchAction"] and "pan-y" in map_metrics["touchAction"],
              f"{name}: canvas touch handling blocks native panning", failures)

        # A tap after zoom/pan must still map to the renderer's base coordinates.
        tap_point = page.evaluate("""() => {
            const wrapper = document.getElementById('canvas-wrapper');
            const canvas = document.getElementById('game-canvas');
            wrapper.scrollLeft = canvas.offsetLeft;
            wrapper.scrollTop = canvas.offsetTop;
            window.__mobileTarget = null;
            const targetPosition = { x: 0, y: 0 };
            Renderer.setMovementTargets([
                { kind: 'explore', direction: 'SE', position: targetPosition }
            ], target => { window.__mobileTarget = target; });
            const geometry = Renderer.roomGeometry(targetPosition);
            const rect = canvas.getBoundingClientRect();
            return {
                x: rect.left + (geometry.cx / 1500) * rect.width,
                y: rect.top + (geometry.cy / 1050) * rect.height
            };
        }""")
        page.touchscreen.tap(tap_point["x"], tap_point["y"])
        selected = page.evaluate("() => window.__mobileTarget")
        check(selected is not None and selected["position"] == {"x": 0, "y": 0},
              f"{name}: map tap coordinates break after zoom/pan", failures)

        fit.click()
        fit_metrics = page.evaluate("""() => {
            const wrapper = document.getElementById('canvas-wrapper');
            const canvas = document.getElementById('game-canvas');
            return {
                zoom: Renderer.mapZoom,
                label: document.getElementById('map-zoom-level').textContent,
                centerDeltaX: Math.abs(
                    canvas.offsetLeft + canvas.offsetWidth / 2
                    - wrapper.scrollLeft - wrapper.clientWidth / 2
                ),
                centerDeltaY: Math.abs(
                    canvas.offsetTop + canvas.offsetHeight / 2
                    - wrapper.scrollTop - wrapper.clientHeight / 2
                )
            };
        }""")
        check(fit_metrics["zoom"] == 1 and fit_metrics["label"] == "100%",
              f"{name}: Fit does not restore 100% map scale", failures)
        check(fit_metrics["centerDeltaX"] <= 2 and fit_metrics["centerDeltaY"] <= 2,
              f"{name}: Fit does not recenter the map", failures)

        pinch_map(context, page)
        pinch_metrics = page.evaluate("""() => ({
            zoom: Renderer.mapZoom,
            label: document.getElementById('map-zoom-level').textContent
        })""")
        check(pinch_metrics["zoom"] > 1.5,
              f"{name}: two-finger pinch does not zoom the tactical map", failures)
        check(pinch_metrics["label"] != "100%",
              f"{name}: pinch zoom does not update its visible zoom level", failures)
        check(abs(pinch_metrics["zoom"] * 10 - round(pinch_metrics["zoom"] * 10)) > 0.01,
              f"{name}: pinch zoom is incorrectly snapping to 10% levels", failures)

        pinch_map(context, page, start_distance=170, end_distance=80)
        pinch_out_zoom = page.evaluate("() => Renderer.mapZoom")
        check(pinch_out_zoom < pinch_metrics["zoom"] - 0.5,
              f"{name}: inward pinch does not zoom the tactical map out", failures)

        fit.click()
        page.locator('#canvas-wrapper').dispatch_event(
            "wheel", {"deltaY": -100, "ctrlKey": True}
        )
        wheel_step = page.evaluate("() => Renderer.mapZoom")
        check(abs(wheel_step - 1.1) < 0.001,
              f"{name}: wheel/trackpad zoom does not step by 10%", failures)
        fit.click()

        if CAPTURE_SCREENSHOTS:
            screenshot = ROOT / "docs" / "qa" / f"mobile-layout-{name}.png"
            page.screenshot(path=str(screenshot), full_page=True)

    # Oversized content in the board and cards panels must remain reachable.
    scroll_metrics = page.evaluate("""() => {
        const center = document.getElementById('center-panel');
        const tall = document.createElement('div');
        tall.id = 'mobile-overflow-probe';
        tall.style.cssText = 'height:1200px;min-height:1200px;width:1px;flex:0 0 auto';
        center.appendChild(tall);
        center.scrollTop = center.scrollHeight;

        UI.switchTab('cards');
        const right = document.getElementById('right-panel');
        const sideTall = document.createElement('div');
        sideTall.style.cssText = 'height:1400px;min-height:1400px';
        right.appendChild(sideTall);
        right.scrollTop = right.scrollHeight;
        return {
            centerScrollable: center.scrollHeight > center.clientHeight && center.scrollTop > 0,
            panelScrollable: right.scrollHeight > right.clientHeight && right.scrollTop > 0,
            bodyOverflowY: getComputedStyle(document.body).overflowY,
            centerOverflowY: getComputedStyle(center).overflowY,
            panelOverflowY: getComputedStyle(right).overflowY
        };
    }""")
    check(scroll_metrics["centerScrollable"], f"{name}: oversized board content is unreachable", failures)
    check(scroll_metrics["panelScrollable"], f"{name}: oversized panel content is unreachable", failures)
    check(scroll_metrics["bodyOverflowY"] != "hidden", f"{name}: page scrolling is globally disabled", failures)
    check(scroll_metrics["centerOverflowY"] in ("auto", "scroll"), f"{name}: board panel cannot scroll", failures)

    context.close()
    return failures, errors


def exercise_layout_mode(browser, name, width, height, expected_tabbed):
    context = browser.new_context(viewport={"width": width, "height": height})
    page = context.new_page()
    errors = []
    page.on("pageerror", lambda exc: errors.append(str(exc)))
    page.goto(BASE_URL, wait_until="networkidle")
    page.evaluate("""() => {
        document.getElementById('lobby-screen').classList.remove('active');
        document.getElementById('game-screen').classList.add('active');
        Renderer.init('game-canvas');
        Renderer.setState({
            corridors: [], rooms: {}, intruders: [], players: [],
            robot: { revealed: false }, round: 1,
            autodestruction: { active: false, token: null }, landerRound: 8
        });
        UI.switchTab('board');
    }""")
    page.wait_for_timeout(150)

    metrics = page.evaluate("""() => {
        const center = document.getElementById('center-panel');
        const left = document.getElementById('left-panel');
        const right = document.getElementById('right-panel');
        const wrapper = document.getElementById('canvas-wrapper');
        const canvas = document.getElementById('game-canvas');
        return {
            navDisplay: getComputedStyle(document.getElementById('mobile-nav')).display,
            centerWidth: center.getBoundingClientRect().width,
            leftDisplay: getComputedStyle(left).display,
            rightDisplay: getComputedStyle(right).display,
            wrapperWidth: wrapper.clientWidth,
            canvasWidth: canvas.getBoundingClientRect().width
        };
    }""")

    failures = []
    if expected_tabbed:
        check(metrics["navDisplay"] != "none", f"{name}: compact viewport did not activate tabs", failures)
        check(metrics["leftDisplay"] == "none" and metrics["rightDisplay"] == "none",
              f"{name}: compact viewport still shows desktop side panels", failures)
        check(metrics["centerWidth"] >= width - 2,
              f"{name}: compact board does not use the viewport width", failures)
    else:
        check(metrics["navDisplay"] == "none", f"{name}: wide desktop incorrectly shows tabs", failures)
        check(metrics["leftDisplay"] != "none" and metrics["rightDisplay"] != "none",
              f"{name}: wide desktop incorrectly hides side panels", failures)
        check(metrics["centerWidth"] < width,
              f"{name}: wide desktop lost its side-panel layout", failures)
    check(metrics["canvasWidth"] >= metrics["wrapperWidth"] - 2,
          f"{name}: board is squeezed narrower than its panel", failures)

    context.close()
    return failures, errors


def exercise_desktop(browser):
    context = browser.new_context(viewport={"width": 1280, "height": 900})
    page = context.new_page()
    errors = []
    page.on("pageerror", lambda exc: errors.append(str(exc)))
    page.goto(BASE_URL, wait_until="networkidle")
    page.evaluate("""() => {
        document.getElementById('lobby-screen').classList.remove('active');
        document.getElementById('game-screen').classList.add('active');
        Renderer.init('game-canvas');
        Renderer.setState({
            corridors: [], rooms: {}, intruders: [], players: [],
            robot: { revealed: false }, round: 1,
            autodestruction: { active: false, token: null }, landerRound: 8
        });
        window.__desktopClickCount = 0;
        const originalHandleClick = Renderer.handleClick.bind(Renderer);
        Renderer.handleClick = event => {
            window.__desktopClickCount += 1;
            originalHandleClick(event);
        };
    }""")
    page.wait_for_timeout(200)

    failures = []
    wrapper = page.locator('#canvas-wrapper')
    wrapper.hover()
    page.mouse.wheel(0, -100)
    page.wait_for_timeout(100)
    wheel_zoom = page.evaluate("() => Renderer.mapZoom")
    check(abs(wheel_zoom - 1.1) < 0.001,
          "desktop: ordinary mouse-wheel scrolling does not zoom by 10%", failures)

    drag_start = page.evaluate("""() => {
        Renderer.setMapZoom(3);
        const wrapper = document.getElementById('canvas-wrapper');
        wrapper.scrollLeft = 200;
        wrapper.scrollTop = 150;
        const rect = wrapper.getBoundingClientRect();
        return {
            x: rect.left + rect.width / 2,
            y: rect.top + rect.height / 2,
            left: wrapper.scrollLeft,
            top: wrapper.scrollTop
        };
    }""")
    page.mouse.move(drag_start["x"], drag_start["y"])
    page.mouse.down(button="left")
    page.mouse.move(drag_start["x"] - 90, drag_start["y"] - 70, steps=5)
    page.mouse.up(button="left")
    page.wait_for_timeout(100)
    drag_result = page.evaluate("""() => {
        const wrapper = document.getElementById('canvas-wrapper');
        return {
            left: wrapper.scrollLeft,
            top: wrapper.scrollTop,
            clicks: window.__desktopClickCount
        };
    }""")
    check(drag_result["left"] > drag_start["left"] and drag_result["top"] > drag_start["top"],
          "desktop: left-click dragging does not pan the map", failures)
    check(drag_result["clicks"] == 0,
          "desktop: map drag dispatches an accidental tactical click", failures)

    page.wait_for_timeout(550)
    page.mouse.click(drag_start["x"], drag_start["y"], button="left")
    click_count = page.evaluate("() => window.__desktopClickCount")
    check(click_count == 1,
          "desktop: stationary left click no longer reaches tactical hit handling", failures)

    context.close()
    return failures, errors


def main():
    all_failures = []
    all_errors = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        for name, width, height in (
            ("narrow-touch-portrait", 390, 844),
            ("narrow-touch-landscape", 844, 390),
            ("wide-touch-landscape", 1180, 600),
        ):
            failures, errors = exercise_viewport(browser, name, width, height)
            all_failures.extend(failures)
            all_errors.extend(f"{name}: {error}" for error in errors)
        for name, width, height, expected_tabbed in (
            ("narrow-fine-pointer", 1000, 800, True),
            ("wide-fine-pointer", 1280, 900, False),
        ):
            failures, errors = exercise_layout_mode(
                browser, name, width, height, expected_tabbed
            )
            all_failures.extend(failures)
            all_errors.extend(f"{name}: {error}" for error in errors)
        failures, errors = exercise_desktop(browser)
        all_failures.extend(failures)
        all_errors.extend(f"desktop: {error}" for error in errors)
        browser.close()

    if all_errors:
        all_failures.extend(f"browser error: {error}" for error in all_errors)
    if all_failures:
        print("mobile layout QA failed:")
        for failure in all_failures:
            print(f"- {failure}")
        raise SystemExit(1)
    print("interaction QA passed: mobile pinch/pan/scroll + desktop wheel zoom/drag pan")


if __name__ == "__main__":
    main()
