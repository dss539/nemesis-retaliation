# Art reference library

This directory describes the visual assets needed by the digital adaptation and the source material collected to inform original production art.

## Files

- `asset-requirements.yml` — 84 grouped production requirements, including variants and priorities.
- `ART-INVENTORY.md` — human-readable master inventory with every atomic piece, status, and current-art link.
- `art-inventory.csv` — machine-readable version of the same master inventory.
- `source-plan.json` — reproducible list of official manuals, Gamefound updates, publisher pages, selected BGG images, and forum references.
- `source-catalogue.csv` — generated asset-by-asset catalogue with source URL, creator, rights note, tags, dimensions, hash, and local reference path.
- `coverage-report.md` — generated comparison of requirements against collected references.
- `../../scripts/collect_art_references.py` — collector, normalizer, deduplicator, and contact-sheet generator.
- `../../scripts/generate_game_art.py` — deterministic generator for the original game-facing SVG set.
- `../../scripts/generate_art_inventory.py` — deterministic inventory generator and link/completeness validator.
- `production-assets.md` — shipped asset architecture, current integration coverage, and remaining production gaps.

Downloaded images, JSON metadata, and contact sheets live under the gitignored `art-references/` directory. They are deliberately not published with the web game.

## Scope

The base-game production set includes:

1. Six player characters: portrait, full body, top-down tactical token/model, dashboard, action-card treatment, and state variants.
2. Primeblood Drone, Adult/Warrior, Prime Blood, Queen, Eggs/Nest, Robot, corpses, and entity state variants.
3. All modular room/corridor families, flat-top hexagonal room boundaries, door states, room-floor/corridor material kits, and legal tactical targeting overlays.
4. Informational board regions: sectors, life support/oxygen, reactor/autodestruction, lander/anti-aircraft, time/round, objective progress, intruder/Queen state, item search, terminals, room damage, and security.
5. Every major card family: six character action decks, starting items, three item colors, events, exploration, intruder attacks, mission/private objectives, wounds, contamination, weaknesses, and help cards.
6. Dashboards, dice, tokens, markers, icons, HUD surfaces, accessibility states, effects, and presentation art.

Research uncovered additional future families and they were added rather than discarded: UAV Operator, Sharpshooter, legacy/stretch-goal characters, Neoflesh Cult, Xyrians, Sangrevores, Insider, security robots/UAVs, terrain, corpses, alternate nests/eggs, and expansion iconography.

## Source taxonomy

- `official-manual`: final or near-final instructional presentation rendered from official PDFs.
- `official-gamefound`: campaign concepts, votes, sculpts, prototypes, development, and production updates.
- `official-publisher`: publisher-hosted key art/gallery material.
- `community-bgg`: selected final-component photos with BGG username attribution.
- `community-forum`: public forum references; attribution remains on the source page when direct metadata is unavailable.

Tags distinguish `concept-art`, `prototype`, `final-components`, `paint-reference`, and other roles. Campaign concepts are not treated as final specifications.

## Rights and derivation policy

Public accessibility is not a reuse license. Unless a row documents a specific license, assume all rights are reserved.

Use collected material to understand component identity, gameplay information hierarchy, silhouette needs, visual tone, and practical color/readability constraints. Do not ship the collected files, trace them, copy character designs, reproduce distinctive compositions, or train a model on them without authorization. Production assets should be independently authored and reviewed for substantial similarity. Obtain written permission or an appropriate license for any direct reuse.

## Game-facing production art

The web game does not load anything from `art-references/`. Its current visual layer is independently generated from geometric primitives and gameplay semantics under `assets/generated/`.

Runtime mapping is centralized in `js/assets.js`; canvas drawing remains in `js/render.js`, while cards, dashboards, and controls consume the same semantic IDs through `js/ui.js`. Every generated image has a procedural fallback, so a delayed or failed SVG request does not block play or hit testing.

Regenerate and validate the committed art with:

    python3 scripts/generate_game_art.py
    python3 scripts/generate_art_inventory.py --check
    python3 docs/qa/art_asset_qa.py

The asset QA covers desktop and mobile layouts, image loads, icon dimensions, canvas pixel diversity, failed requests, console errors, and overflow. The established `docs/qa/4browser_qa.py` remains the multiplayer synchronization regression.

## Rebuild

The collector needs Pillow and PyMuPDF. Example:

    python3 -m pip install --target .art-tooling pymupdf
    PYTHONPATH=.art-tooling python3 scripts/collect_art_references.py

After verification, remove `.art-tooling`; it is temporary and must not be committed.
