# Production art integration

## Intent

The game-facing asset set is independently authored, deterministic SVG. Collected publisher and community imagery remains local, gitignored research material and is never loaded by the game.

The physical playmat reference informed only high-level usability: a dark low-glare substrate, bounded operational regions, strong room silhouettes, restrained labels, and high-contrast state markers. No photograph, illustration, sculpt, logo, character design, or distinctive composition was copied.

## Runtime architecture

- `scripts/generate_game_art.py` is the source generator.
- `assets/generated/` contains 42 compact SVG outputs.
- `js/assets.js` maps semantic game IDs to files, preloads canvas images, exposes card/control icons, and provides procedural marker fallbacks.
- `js/render.js` draws the generated play surface, room plates, character tokens, intruder tokens, and board-state symbols without changing tactical geometry or hit testing.
- `js/ui.js` uses the same semantic registry for player dashboards, cards, objectives, items, and action controls.
- `css/style.css` supplies the common card and dashboard frames while preserving text labels and accessible button names.

## Integrated coverage

| Family | Current production form | Coverage |
| --- | --- | --- |
| Play surface | Original 7x5 facility mat, sector bands, telemetry rails, deck grid | Complete for current board |
| Rooms | 24 ID-specific octagonal floor plates with family glyphs and color coding | Complete for current data |
| Corridors and empty slots | Procedural deck corridors, noise symbol, legal-slot and movement overlays | Complete for current renderer |
| Player characters | Six class-coded vector portraits/top-down tokens and color rings | Complete for current roster |
| Primeblood intruders | Larva, Drone, Adult, and Queen tactical tokens | Complete for current roster |
| Board states | Fire, malfunction, secure, computer, item, noise, health, and oxygen symbols | Complete for exposed states |
| Player dashboards | Portrait, class identity, health/oxygen/cards/contamination/wound/larva states | Complete for current UI |
| Action controls | Semantic vector icon plus retained text for all current actions | Complete for current actions |
| Hand cards | Action and contamination visual treatments with semantic icons | Complete as functional card art |
| Objectives and items | Mission/private objective treatments and red/yellow/green/support item frames | Complete as functional card art |
| Other card families | No game-facing event, exploration, intruder-attack, or wound frames yet | Missing; requirements are itemized in `ART-INVENTORY.md` |

## Remaining authored-art gaps

These are intentionally not filled by copied reference imagery:

1. Unique illustrations for the 90 individual item cards. Current cards distinguish category and gameplay function, not every item visually.
2. Unique class-deck illustrations and per-action scene art. Current cards use strong semantic symbols.
3. Full-body character presentation art, dashboard scenes, alternate poses, wounds, contamination, death, and directional animation frames.
4. Additional entities: Robot/UAV variants, eggs/nest, corpses, doors, terrain, weapons, armor, and environmental props.
5. Individual event, exploration, intruder-attack, serious-wound, weakness, contamination-scan, and help-card faces when those UI surfaces are implemented.
6. Environmental variants for fire spread, darkness, smoke, decompression, contamination, malfunction severity, and powered/unpowered states.
7. Expansion and stretch-goal content: alternate characters and alien races catalogued in `asset-requirements.yml` but not present in base-game data.
8. Original presentation/key art, marketing compositions, loading art, audio, and animation.

These gaps should be filled by commissioned/project-owned art or independently generated geometry and illustration. A direct publisher asset may replace a generated form only after its license or written permission is recorded in the source catalogue.

## Verification

Run:

    python3 scripts/generate_game_art.py
    node --check js/assets.js
    node --check js/render.js
    node --check js/ui.js
    python3 docs/qa/art_asset_qa.py
    python3 docs/qa/4browser_qa.py

`art_asset_qa.py` produces desktop and responsive screenshots plus `art-assets-results.json`. It asserts 35/35 runtime canvas images loaded, SVG icons have usable geometry, cards and portraits resolve, the canvas is nonblank and chromatically varied, active layouts do not overflow, and there are no console or request failures.
