"""Visual/asset QA for the generated game-art integration."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import json

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs" / "qa"
results = {"errors": [], "failed_requests": [], "checks": {}}


def host_game(page, name, players="2"):
    page.goto("http://127.0.0.1:8889/?v=art-assets", wait_until="networkidle")
    page.click("text=Host Game")
    page.evaluate("n => document.getElementById('num-players').value = n", players)
    page.fill("#host-name", name)
    page.click("text=Create Game")
    page.wait_for_selector("#host-code:not(:has-text('Generating'))", timeout=10000)
    page.click("text=Start Game")
    page.wait_for_function("GameArt.loaded === true", timeout=10000)
    page.wait_for_timeout(300)


def collect_checks(page, prefix):
    checks = page.evaluate("""() => {
        const canvas = document.getElementById('game-canvas');
        const ctx = canvas.getContext('2d');
        const pixels = ctx.getImageData(0, 0, canvas.width, canvas.height).data;
        const colors = new Set();
        let opaque = 0;
        const stride = Math.max(4, Math.floor(pixels.length / 20000 / 4) * 4);
        for (let i = 0; i < pixels.length; i += stride) {
            if (pixels[i + 3] > 0) opaque++;
            colors.add(`${pixels[i] >> 4},${pixels[i+1] >> 4},${pixels[i+2] >> 4}`);
        }
        const iconBoxes = [...document.querySelectorAll('.game-icon')].map(el => el.getBoundingClientRect());
        const portraits = [...document.querySelectorAll('.character-portrait')];
        return {
            artLoaded: GameArt.loaded,
            runtimeImages: [...GameArt.images.values()].filter(image => image.complete && image.naturalWidth > 0).length,
            runtimeImageTotal: GameArt.images.size,
            canvasWidth: canvas.width,
            canvasHeight: canvas.height,
            sampledColorBuckets: colors.size,
            sampledOpaquePixels: opaque,
            icons: iconBoxes.length,
            visibleIcons: iconBoxes.filter(box => box.width >= 1 && box.height >= 1).length,
            zeroSizeIcons: iconBoxes.filter(box => box.width < 1 || box.height < 1).length,
            portraits: portraits.length,
            brokenPortraits: portraits.filter(image => !image.complete || !image.naturalWidth).length,
            cardArt: document.querySelectorAll('.card-art').length,
            handCards: document.querySelectorAll('.hand-card').length,
            bodyOverflow: document.documentElement.scrollWidth > window.innerWidth + 1,
            screenActive: document.getElementById('game-screen').classList.contains('active'),
            mobileNavVisible: getComputedStyle(document.getElementById('mobile-nav')).display !== 'none'
        };
    }""")
    results["checks"][prefix] = checks
    assert checks["artLoaded"]
    assert checks["runtimeImages"] == checks["runtimeImageTotal"] == 35
    assert checks["sampledColorBuckets"] > 40
    assert checks["sampledOpaquePixels"] > 100
    assert checks["icons"] > 20 and checks["visibleIcons"] >= (20 if prefix == "desktop" else 12)
    if prefix == "desktop":
        assert checks["zeroSizeIcons"] == 0
    assert checks["portraits"] >= 1 and checks["brokenPortraits"] == 0
    assert checks["cardArt"] >= checks["handCards"] >= 5
    assert not checks["bodyOverflow"]
    assert checks["screenActive"]


with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=True)

    desktop = browser.new_page(viewport={"width": 1440, "height": 900}, device_scale_factor=1)
    desktop.on("console", lambda msg: results["errors"].append(f"desktop console: {msg.text}") if msg.type == "error" else None)
    desktop.on("pageerror", lambda err: results["errors"].append(f"desktop page: {err}"))
    desktop.on("requestfailed", lambda req: results["failed_requests"].append(req.url))
    host_game(desktop, "ArtQA", "5")
    desktop.evaluate("""() => {
        const state = window.nemesisEngine.state;
        const room = state.rooms.landingZone;
        room.markers.fire = true;
        room.markers.malfunction = true;
        room.markers.secure = ['qa1', 'qa2'];
        state.intruders = ['larva','drone','adult','queen'].map((type, index) => ({
            id: `art_${type}`, type, hits: index, location: {type:'room', id:'landingZone'}
        }));
        if (state.corridors[0]) state.corridors[0].noise = true;
        state.players[0].backpack = ['pistol', 'oxygenTank'];
        state.players[0].contaminationInHand.push({id:'qa-contam', infected:false});
        UI.updateState(state);
    }""")
    desktop.wait_for_timeout(300)
    collect_checks(desktop, "desktop")
    desktop.screenshot(path=str(OUT / "art-assets-desktop.png"))

    mobile = browser.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=2, is_mobile=True, has_touch=True)
    mobile.on("console", lambda msg: results["errors"].append(f"mobile console: {msg.text}") if msg.type == "error" else None)
    mobile.on("pageerror", lambda err: results["errors"].append(f"mobile page: {err}\n{getattr(err, 'stack', '')}"))
    mobile.on("requestfailed", lambda req: results["failed_requests"].append(req.url))
    host_game(mobile, "MobileQA", "2")
    collect_checks(mobile, "mobile-board")
    assert results["checks"]["mobile-board"]["mobileNavVisible"]
    mobile.screenshot(path=str(OUT / "art-assets-mobile-board.png"))
    mobile.evaluate("UI.switchTab('cards')")
    mobile.wait_for_timeout(200)
    mobile_cards = mobile.evaluate("""() => ({
        rightVisible: getComputedStyle(document.getElementById('right-panel')).display !== 'none',
        art: document.querySelectorAll('#card-area .card-art').length,
        overflow: document.documentElement.scrollWidth > window.innerWidth + 1
    })""")
    results["checks"]["mobile-cards"] = mobile_cards
    assert mobile_cards["rightVisible"] and mobile_cards["art"] >= 5 and not mobile_cards["overflow"]
    mobile.screenshot(path=str(OUT / "art-assets-mobile-cards.png"))

    browser.close()

results["errors"] = list(dict.fromkeys(results["errors"]))
results["failed_requests"] = list(dict.fromkeys(results["failed_requests"]))
assert not results["errors"], results["errors"]
assert not results["failed_requests"], results["failed_requests"]
(OUT / "art-assets-results.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
print(json.dumps(results, indent=2))
