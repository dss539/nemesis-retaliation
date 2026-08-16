# Obsolete game implementation (archived 2026-08-07)

This is the ENTIRE first-pass web implementation of Nemesis: Retaliation that was built
before we had authoritative card data. It is archived for reference ONLY. It is NOT the
source of truth for game content and must not be treated as one.

## Why it's quarantined
The game model in `js/data.js` was hand-authored from a partial reading and is wrong in
material ways. Example: it models red/yellow/green item-deck cards as if the card itself
IS a heavy weapon (e.g. `automaticShotgun: type:'red', traits:['RANGED WEAPON','HEAVY']`).
The extracted TTS-mod card images show this is incorrect: the red/yellow/green item-deck
cards are all small, portrait, self-contained cards (e.g. AMMO MAGAZINE, DUCT TAPE,
ANTI-AIRCRAFT CODES). They are NOT the heavy/armor items. Heavy items are physically
larger, horizontal cards that come from the equipment deck, not the color decks.

## Contents
- `js/`  — all game logic and data (data.js, engine.js, network.js, render.js, ui.js, main.js, assets.js)
- `css/` — style.css
- `index.html` — entry point / lobby / game screens
- `scripts/` — art-inventory generation scripts

## Canonical sources (use these instead)
- Extracted TTS mod assets: `assets/tts-mod/extract/v2-dl/tree/` (card images, tokens, tiles)
- TTS save + Lua: `assets/tts-mod/extract/v2/` (objects.json, lua_script.lua, classification.json)
- Official rulebooks: `docs/rulebooks/` (PDFs + extracted text)
- Rules corpus: `docs/rules/`

The active project now lives at the repo root, rebuilt from these canonical sources.
