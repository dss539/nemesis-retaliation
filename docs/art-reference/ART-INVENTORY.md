# Master art inventory

This is the repository overview for every currently known production-art requirement. It expands the grouped taxonomy in `asset-requirements.yml`, adds every concrete room and game-data card, links the current game-facing art where one exists, and explicitly marks missing unique art.

Regenerate and validate it with `python3 scripts/generate_art_inventory.py --check`.

## Status definitions

- `complete` — current art fulfills this functional production slot.
- `partial` — a functional treatment exists, but a dedicated variant or illustration is still needed.
- `template-only` — a reusable frame/icon exists; the unique illustration is missing.
- `missing` — no current game-facing art exists.
- `deferred` — known expansion/future requirement; no current art is expected yet.

Reusable overlays, symbols, and material treatments are tracked once. Cards and named rooms are tracked individually because they need unique faces or plates.

## Summary

Total atomic inventory rows: 740

Rows with missing or partially missing authored art: 522

| Status | Count |
| --- | ---: |
| complete | 177 |
| partial | 62 |
| template-only | 226 |
| missing | 234 |
| deferred | 41 |

| Category | Count |
| --- | ---: |
| board-ui | 47 |
| card | 331 |
| character | 79 |
| dashboard | 14 |
| dice | 7 |
| entity | 61 |
| fx | 13 |
| icon | 54 |
| map | 85 |
| presentation | 5 |
| token | 32 |
| ui | 12 |

Machine-readable version: [art-inventory.csv](art-inventory.csv)

## Board Ui

| ID | Family | Piece | Scope | Priority | Status | Missing art? | Current art | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| req-anti-aircraft-aa-state | Anti-aircraft/lander area | AA-state | base-game | high | missing | yes | — | Dedicated board-information treatment is missing. |
| req-anti-aircraft-available | Anti-aircraft/lander area | available | base-game | high | missing | yes | — | Dedicated board-information treatment is missing. |
| req-anti-aircraft-escaped | Anti-aircraft/lander area | escaped | base-game | high | missing | yes | — | Dedicated board-information treatment is missing. |
| req-anti-aircraft-lander-arrival | Anti-aircraft/lander area | lander-arrival | base-game | high | missing | yes | — | Dedicated board-information treatment is missing. |
| req-anti-aircraft-launch | Anti-aircraft/lander area | launch | base-game | high | missing | yes | — | Dedicated board-information treatment is missing. |
| req-anti-aircraft-unavailable | Anti-aircraft/lander area | unavailable | base-game | high | missing | yes | — | Dedicated board-information treatment is missing. |
| req-computer-room-available | Computer terminal room indicator | available | base-game | high | complete | no | [art](../../js/render.js) | Functional board/HUD treatment; bespoke illustration may still be needed. |
| req-computer-room-broken | Computer terminal room indicator | broken | base-game | high | complete | no | [art](../../js/render.js) | Functional board/HUD treatment; bespoke illustration may still be needed. |
| req-computer-room-offline | Computer terminal room indicator | offline | base-game | high | missing | yes | — | Dedicated board-information treatment is missing. |
| req-computer-room-used | Computer terminal room indicator | used | base-game | high | missing | yes | — | Dedicated board-information treatment is missing. |
| req-intruder-board-queen-health | Intruder and Queen board | Queen-health | base-game | high | missing | yes | — | Dedicated board-information treatment is missing. |
| req-intruder-board-bag-development | Intruder and Queen board | bag-development | base-game | high | missing | yes | — | Dedicated board-information treatment is missing. |
| req-intruder-board-health | Intruder and Queen board | health | base-game | high | missing | yes | — | Dedicated board-information treatment is missing. |
| req-intruder-board-pool | Intruder and Queen board | pool | base-game | high | missing | yes | — | Dedicated board-information treatment is missing. |
| req-intruder-board-weaknesses | Intruder and Queen board | weaknesses | base-game | high | missing | yes | — | Dedicated board-information treatment is missing. |
| req-objective-track-choice-position | Objective choice/progress track | choice-position | base-game | high | partial | partial | [art](../../js/render.js) | Functional board/HUD treatment; bespoke illustration may still be needed. |
| req-objective-track-locked | Objective choice/progress track | locked | base-game | high | partial | partial | [art](../../js/render.js) | Functional board/HUD treatment; bespoke illustration may still be needed. |
| req-objective-track-progress | Objective choice/progress track | progress | base-game | high | partial | partial | [art](../../js/render.js) | Functional board/HUD treatment; bespoke illustration may still be needed. |
| req-objective-track-resolved | Objective choice/progress track | resolved | base-game | high | partial | partial | [art](../../js/render.js) | Functional board/HUD treatment; bespoke illustration may still be needed. |
| req-reactor-autodestruction-active | Reactor/autodestruction area | autodestruction-active | base-game | high | partial | partial | [art](../../js/render.js) | Functional board/HUD treatment; bespoke illustration may still be needed. |
| req-reactor-countdown | Reactor/autodestruction area | countdown | base-game | high | partial | partial | [art](../../js/render.js) | Functional board/HUD treatment; bespoke illustration may still be needed. |
| req-reactor-normal | Reactor/autodestruction area | normal | base-game | high | partial | partial | [art](../../js/render.js) | Functional board/HUD treatment; bespoke illustration may still be needed. |
| req-reactor-overheating | Reactor/autodestruction area | overheating | base-game | high | partial | partial | [art](../../js/render.js) | Functional board/HUD treatment; bespoke illustration may still be needed. |
| req-room-destruction-cannot-break | Room damage information | cannot-break | base-game | high | complete | no | [art](../../js/render.js) | Functional board/HUD treatment; bespoke illustration may still be needed. |
| req-room-destruction-destroyed | Room damage information | destroyed | base-game | high | missing | yes | — | Dedicated board-information treatment is missing. |
| req-room-destruction-malfunction | Room damage information | malfunction | base-game | high | complete | no | [art](../../js/render.js) | Functional board/HUD treatment; bespoke illustration may still be needed. |
| req-room-destruction-normal | Room damage information | normal | base-game | high | complete | no | [art](../../js/render.js) | Functional board/HUD treatment; bespoke illustration may still be needed. |
| req-item-search-area-depleted | Room search/item areas | depleted | base-game | high | complete | no | [art](../../js/render.js) | Functional board/HUD treatment; bespoke illustration may still be needed. |
| req-item-search-area-green | Room search/item areas | green | base-game | high | complete | no | [art](../../js/render.js) | Functional board/HUD treatment; bespoke illustration may still be needed. |
| req-item-search-area-red | Room search/item areas | red | base-game | high | complete | no | [art](../../js/render.js) | Functional board/HUD treatment; bespoke illustration may still be needed. |
| req-item-search-area-yellow | Room search/item areas | yellow | base-game | high | complete | no | [art](../../js/render.js) | Functional board/HUD treatment; bespoke illustration may still be needed. |
| req-time-track-end-state | Round/time track | end-state | base-game | critical | complete | no | [art](../../js/render.js) | Functional board/HUD treatment; bespoke illustration may still be needed. |
| req-time-track-event-phase | Round/time track | event-phase | base-game | critical | complete | no | [art](../../js/render.js) | Functional board/HUD treatment; bespoke illustration may still be needed. |
| req-time-track-lander-window | Round/time track | lander-window | base-game | critical | missing | yes | — | Dedicated board-information treatment is missing. |
| req-time-track-round-marker | Round/time track | round-marker | base-game | critical | complete | no | [art](../../js/render.js) | Functional board/HUD treatment; bespoke illustration may still be needed. |
| req-life-support-active | Section life support and oxygen | active | base-game | critical | partial | partial | [art](../../js/render.js) | Functional board/HUD treatment; bespoke illustration may still be needed. |
| req-life-support-inactive | Section life support and oxygen | inactive | base-game | critical | partial | partial | [art](../../js/render.js) | Functional board/HUD treatment; bespoke illustration may still be needed. |
| req-life-support-oxygen-track | Section life support and oxygen | oxygen-track | base-game | critical | partial | partial | [art](../../js/render.js) | Functional board/HUD treatment; bespoke illustration may still be needed. |
| req-life-support-suffocation | Section life support and oxygen | suffocation | base-game | critical | partial | partial | [art](../../js/render.js) | Functional board/HUD treatment; bespoke illustration may still be needed. |
| req-board-sectors-a | Sector/Section overlays | A | base-game | high | complete | no | [art](../../js/render.js) | Functional board/HUD treatment; bespoke illustration may still be needed. |
| req-board-sectors-b | Sector/Section overlays | B | base-game | high | complete | no | [art](../../js/render.js) | Functional board/HUD treatment; bespoke illustration may still be needed. |
| req-board-sectors-c | Sector/Section overlays | C | base-game | high | complete | no | [art](../../js/render.js) | Functional board/HUD treatment; bespoke illustration may still be needed. |
| req-board-sectors-inactive | Sector/Section overlays | inactive | base-game | high | complete | no | [art](../../js/render.js) | Functional board/HUD treatment; bespoke illustration may still be needed. |
| req-board-sectors-oxygen-warning | Sector/Section overlays | oxygen-warning | base-game | high | missing | yes | — | Dedicated board-information treatment is missing. |
| req-room-security-cannot-secure | Secure and cannot-secure areas | cannot-secure | base-game | high | complete | no | [art](../../js/render.js) | Functional board/HUD treatment; bespoke illustration may still be needed. |
| req-room-security-secure | Secure and cannot-secure areas | secure | base-game | high | complete | no | [art](../../js/render.js) | Functional board/HUD treatment; bespoke illustration may still be needed. |
| req-room-security-security-count | Secure and cannot-secure areas | security-count | base-game | high | complete | no | [art](../../js/render.js) | Functional board/HUD treatment; bespoke illustration may still be needed. |

## Card

| ID | Family | Piece | Scope | Priority | Status | Missing art? | Current art | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| card-action-combatEngineer-10 | Character action cards | Combat Engineer #10: special | base-game | critical | template-only | yes | [art](../../assets/generated/cards/action.svg) · [art2](../../assets/generated/ui-symbols.svg#i-gear) | Functional frame and icon exist; unique card illustration is missing. |
| card-action-combatEngineer-01 | Character action cards | Combat Engineer #1: move | base-game | critical | template-only | yes | [art](../../assets/generated/cards/action.svg) · [art2](../../assets/generated/ui-symbols.svg#i-move) | Functional frame and icon exist; unique card illustration is missing. |
| card-action-combatEngineer-02 | Character action cards | Combat Engineer #2: move | base-game | critical | template-only | yes | [art](../../assets/generated/cards/action.svg) · [art2](../../assets/generated/ui-symbols.svg#i-move) | Functional frame and icon exist; unique card illustration is missing. |
| card-action-combatEngineer-03 | Character action cards | Combat Engineer #3: move | base-game | critical | template-only | yes | [art](../../assets/generated/cards/action.svg) · [art2](../../assets/generated/ui-symbols.svg#i-move) | Functional frame and icon exist; unique card illustration is missing. |
| card-action-combatEngineer-04 | Character action cards | Combat Engineer #4: shoot | base-game | critical | template-only | yes | [art](../../assets/generated/cards/action.svg) · [art2](../../assets/generated/ui-symbols.svg#i-shoot) | Functional frame and icon exist; unique card illustration is missing. |
| card-action-combatEngineer-05 | Character action cards | Combat Engineer #5: search | base-game | critical | template-only | yes | [art](../../assets/generated/cards/action.svg) · [art2](../../assets/generated/ui-symbols.svg#i-search) | Functional frame and icon exist; unique card illustration is missing. |
| card-action-combatEngineer-06 | Character action cards | Combat Engineer #6: move | base-game | critical | template-only | yes | [art](../../assets/generated/cards/action.svg) · [art2](../../assets/generated/ui-symbols.svg#i-move) | Functional frame and icon exist; unique card illustration is missing. |
| card-action-combatEngineer-07 | Character action cards | Combat Engineer #7: cautiousMove | base-game | critical | template-only | yes | [art](../../assets/generated/cards/action.svg) · [art2](../../assets/generated/ui-symbols.svg#i-cautious) | Functional frame and icon exist; unique card illustration is missing. |
| card-action-combatEngineer-08 | Character action cards | Combat Engineer #8: shoot | base-game | critical | template-only | yes | [art](../../assets/generated/cards/action.svg) · [art2](../../assets/generated/ui-symbols.svg#i-shoot) | Functional frame and icon exist; unique card illustration is missing. |
| card-action-combatEngineer-09 | Character action cards | Combat Engineer #9: useRoom | base-game | critical | template-only | yes | [art](../../assets/generated/cards/action.svg) · [art2](../../assets/generated/ui-symbols.svg#i-room) | Functional frame and icon exist; unique card illustration is missing. |
| card-action-contractor-10 | Character action cards | Contractor #10: special | base-game | critical | template-only | yes | [art](../../assets/generated/cards/action.svg) · [art2](../../assets/generated/ui-symbols.svg#i-gear) | Functional frame and icon exist; unique card illustration is missing. |
| card-action-contractor-01 | Character action cards | Contractor #1: move | base-game | critical | template-only | yes | [art](../../assets/generated/cards/action.svg) · [art2](../../assets/generated/ui-symbols.svg#i-move) | Functional frame and icon exist; unique card illustration is missing. |
| card-action-contractor-02 | Character action cards | Contractor #2: move | base-game | critical | template-only | yes | [art](../../assets/generated/cards/action.svg) · [art2](../../assets/generated/ui-symbols.svg#i-move) | Functional frame and icon exist; unique card illustration is missing. |
| card-action-contractor-03 | Character action cards | Contractor #3: move | base-game | critical | template-only | yes | [art](../../assets/generated/cards/action.svg) · [art2](../../assets/generated/ui-symbols.svg#i-move) | Functional frame and icon exist; unique card illustration is missing. |
| card-action-contractor-04 | Character action cards | Contractor #4: shoot | base-game | critical | template-only | yes | [art](../../assets/generated/cards/action.svg) · [art2](../../assets/generated/ui-symbols.svg#i-shoot) | Functional frame and icon exist; unique card illustration is missing. |
| card-action-contractor-05 | Character action cards | Contractor #5: search | base-game | critical | template-only | yes | [art](../../assets/generated/cards/action.svg) · [art2](../../assets/generated/ui-symbols.svg#i-search) | Functional frame and icon exist; unique card illustration is missing. |
| card-action-contractor-06 | Character action cards | Contractor #6: move | base-game | critical | template-only | yes | [art](../../assets/generated/cards/action.svg) · [art2](../../assets/generated/ui-symbols.svg#i-move) | Functional frame and icon exist; unique card illustration is missing. |
| card-action-contractor-07 | Character action cards | Contractor #7: cautiousMove | base-game | critical | template-only | yes | [art](../../assets/generated/cards/action.svg) · [art2](../../assets/generated/ui-symbols.svg#i-cautious) | Functional frame and icon exist; unique card illustration is missing. |
| card-action-contractor-08 | Character action cards | Contractor #8: shoot | base-game | critical | template-only | yes | [art](../../assets/generated/cards/action.svg) · [art2](../../assets/generated/ui-symbols.svg#i-shoot) | Functional frame and icon exist; unique card illustration is missing. |
| card-action-contractor-09 | Character action cards | Contractor #9: useRoom | base-game | critical | template-only | yes | [art](../../assets/generated/cards/action.svg) · [art2](../../assets/generated/ui-symbols.svg#i-room) | Functional frame and icon exist; unique card illustration is missing. |
| card-action-heavyGunOperator-10 | Character action cards | Heavy Gun Operator #10: special | base-game | critical | template-only | yes | [art](../../assets/generated/cards/action.svg) · [art2](../../assets/generated/ui-symbols.svg#i-gear) | Functional frame and icon exist; unique card illustration is missing. |
| card-action-heavyGunOperator-01 | Character action cards | Heavy Gun Operator #1: move | base-game | critical | template-only | yes | [art](../../assets/generated/cards/action.svg) · [art2](../../assets/generated/ui-symbols.svg#i-move) | Functional frame and icon exist; unique card illustration is missing. |
| card-action-heavyGunOperator-02 | Character action cards | Heavy Gun Operator #2: move | base-game | critical | template-only | yes | [art](../../assets/generated/cards/action.svg) · [art2](../../assets/generated/ui-symbols.svg#i-move) | Functional frame and icon exist; unique card illustration is missing. |
| card-action-heavyGunOperator-03 | Character action cards | Heavy Gun Operator #3: move | base-game | critical | template-only | yes | [art](../../assets/generated/cards/action.svg) · [art2](../../assets/generated/ui-symbols.svg#i-move) | Functional frame and icon exist; unique card illustration is missing. |
| card-action-heavyGunOperator-04 | Character action cards | Heavy Gun Operator #4: shoot | base-game | critical | template-only | yes | [art](../../assets/generated/cards/action.svg) · [art2](../../assets/generated/ui-symbols.svg#i-shoot) | Functional frame and icon exist; unique card illustration is missing. |
| card-action-heavyGunOperator-05 | Character action cards | Heavy Gun Operator #5: search | base-game | critical | template-only | yes | [art](../../assets/generated/cards/action.svg) · [art2](../../assets/generated/ui-symbols.svg#i-search) | Functional frame and icon exist; unique card illustration is missing. |
| card-action-heavyGunOperator-06 | Character action cards | Heavy Gun Operator #6: move | base-game | critical | template-only | yes | [art](../../assets/generated/cards/action.svg) · [art2](../../assets/generated/ui-symbols.svg#i-move) | Functional frame and icon exist; unique card illustration is missing. |
| card-action-heavyGunOperator-07 | Character action cards | Heavy Gun Operator #7: cautiousMove | base-game | critical | template-only | yes | [art](../../assets/generated/cards/action.svg) · [art2](../../assets/generated/ui-symbols.svg#i-cautious) | Functional frame and icon exist; unique card illustration is missing. |
| card-action-heavyGunOperator-08 | Character action cards | Heavy Gun Operator #8: shoot | base-game | critical | template-only | yes | [art](../../assets/generated/cards/action.svg) · [art2](../../assets/generated/ui-symbols.svg#i-shoot) | Functional frame and icon exist; unique card illustration is missing. |
| card-action-heavyGunOperator-09 | Character action cards | Heavy Gun Operator #9: useRoom | base-game | critical | template-only | yes | [art](../../assets/generated/cards/action.svg) · [art2](../../assets/generated/ui-symbols.svg#i-room) | Functional frame and icon exist; unique card illustration is missing. |
| card-action-medicalSupport-10 | Character action cards | Medical Support #10: special | base-game | critical | template-only | yes | [art](../../assets/generated/cards/action.svg) · [art2](../../assets/generated/ui-symbols.svg#i-gear) | Functional frame and icon exist; unique card illustration is missing. |
| card-action-medicalSupport-01 | Character action cards | Medical Support #1: move | base-game | critical | template-only | yes | [art](../../assets/generated/cards/action.svg) · [art2](../../assets/generated/ui-symbols.svg#i-move) | Functional frame and icon exist; unique card illustration is missing. |
| card-action-medicalSupport-02 | Character action cards | Medical Support #2: move | base-game | critical | template-only | yes | [art](../../assets/generated/cards/action.svg) · [art2](../../assets/generated/ui-symbols.svg#i-move) | Functional frame and icon exist; unique card illustration is missing. |
| card-action-medicalSupport-03 | Character action cards | Medical Support #3: move | base-game | critical | template-only | yes | [art](../../assets/generated/cards/action.svg) · [art2](../../assets/generated/ui-symbols.svg#i-move) | Functional frame and icon exist; unique card illustration is missing. |
| card-action-medicalSupport-04 | Character action cards | Medical Support #4: shoot | base-game | critical | template-only | yes | [art](../../assets/generated/cards/action.svg) · [art2](../../assets/generated/ui-symbols.svg#i-shoot) | Functional frame and icon exist; unique card illustration is missing. |
| card-action-medicalSupport-05 | Character action cards | Medical Support #5: search | base-game | critical | template-only | yes | [art](../../assets/generated/cards/action.svg) · [art2](../../assets/generated/ui-symbols.svg#i-search) | Functional frame and icon exist; unique card illustration is missing. |
| card-action-medicalSupport-06 | Character action cards | Medical Support #6: move | base-game | critical | template-only | yes | [art](../../assets/generated/cards/action.svg) · [art2](../../assets/generated/ui-symbols.svg#i-move) | Functional frame and icon exist; unique card illustration is missing. |
| card-action-medicalSupport-07 | Character action cards | Medical Support #7: cautiousMove | base-game | critical | template-only | yes | [art](../../assets/generated/cards/action.svg) · [art2](../../assets/generated/ui-symbols.svg#i-cautious) | Functional frame and icon exist; unique card illustration is missing. |
| card-action-medicalSupport-08 | Character action cards | Medical Support #8: shoot | base-game | critical | template-only | yes | [art](../../assets/generated/cards/action.svg) · [art2](../../assets/generated/ui-symbols.svg#i-shoot) | Functional frame and icon exist; unique card illustration is missing. |
| card-action-medicalSupport-09 | Character action cards | Medical Support #9: useRoom | base-game | critical | template-only | yes | [art](../../assets/generated/cards/action.svg) · [art2](../../assets/generated/ui-symbols.svg#i-room) | Functional frame and icon exist; unique card illustration is missing. |
| card-action-officer-10 | Character action cards | Officer #10: special | base-game | critical | template-only | yes | [art](../../assets/generated/cards/action.svg) · [art2](../../assets/generated/ui-symbols.svg#i-gear) | Functional frame and icon exist; unique card illustration is missing. |
| card-action-officer-01 | Character action cards | Officer #1: move | base-game | critical | template-only | yes | [art](../../assets/generated/cards/action.svg) · [art2](../../assets/generated/ui-symbols.svg#i-move) | Functional frame and icon exist; unique card illustration is missing. |
| card-action-officer-02 | Character action cards | Officer #2: move | base-game | critical | template-only | yes | [art](../../assets/generated/cards/action.svg) · [art2](../../assets/generated/ui-symbols.svg#i-move) | Functional frame and icon exist; unique card illustration is missing. |
| card-action-officer-03 | Character action cards | Officer #3: move | base-game | critical | template-only | yes | [art](../../assets/generated/cards/action.svg) · [art2](../../assets/generated/ui-symbols.svg#i-move) | Functional frame and icon exist; unique card illustration is missing. |
| card-action-officer-04 | Character action cards | Officer #4: shoot | base-game | critical | template-only | yes | [art](../../assets/generated/cards/action.svg) · [art2](../../assets/generated/ui-symbols.svg#i-shoot) | Functional frame and icon exist; unique card illustration is missing. |
| card-action-officer-05 | Character action cards | Officer #5: search | base-game | critical | template-only | yes | [art](../../assets/generated/cards/action.svg) · [art2](../../assets/generated/ui-symbols.svg#i-search) | Functional frame and icon exist; unique card illustration is missing. |
| card-action-officer-06 | Character action cards | Officer #6: move | base-game | critical | template-only | yes | [art](../../assets/generated/cards/action.svg) · [art2](../../assets/generated/ui-symbols.svg#i-move) | Functional frame and icon exist; unique card illustration is missing. |
| card-action-officer-07 | Character action cards | Officer #7: cautiousMove | base-game | critical | template-only | yes | [art](../../assets/generated/cards/action.svg) · [art2](../../assets/generated/ui-symbols.svg#i-cautious) | Functional frame and icon exist; unique card illustration is missing. |
| card-action-officer-08 | Character action cards | Officer #8: shoot | base-game | critical | template-only | yes | [art](../../assets/generated/cards/action.svg) · [art2](../../assets/generated/ui-symbols.svg#i-shoot) | Functional frame and icon exist; unique card illustration is missing. |
| card-action-officer-09 | Character action cards | Officer #9: useRoom | base-game | critical | template-only | yes | [art](../../assets/generated/cards/action.svg) · [art2](../../assets/generated/ui-symbols.svg#i-room) | Functional frame and icon exist; unique card illustration is missing. |
| card-action-recon-10 | Character action cards | Recon #10: special | base-game | critical | template-only | yes | [art](../../assets/generated/cards/action.svg) · [art2](../../assets/generated/ui-symbols.svg#i-gear) | Functional frame and icon exist; unique card illustration is missing. |
| card-action-recon-01 | Character action cards | Recon #1: move | base-game | critical | template-only | yes | [art](../../assets/generated/cards/action.svg) · [art2](../../assets/generated/ui-symbols.svg#i-move) | Functional frame and icon exist; unique card illustration is missing. |
| card-action-recon-02 | Character action cards | Recon #2: move | base-game | critical | template-only | yes | [art](../../assets/generated/cards/action.svg) · [art2](../../assets/generated/ui-symbols.svg#i-move) | Functional frame and icon exist; unique card illustration is missing. |
| card-action-recon-03 | Character action cards | Recon #3: move | base-game | critical | template-only | yes | [art](../../assets/generated/cards/action.svg) · [art2](../../assets/generated/ui-symbols.svg#i-move) | Functional frame and icon exist; unique card illustration is missing. |
| card-action-recon-04 | Character action cards | Recon #4: shoot | base-game | critical | template-only | yes | [art](../../assets/generated/cards/action.svg) · [art2](../../assets/generated/ui-symbols.svg#i-shoot) | Functional frame and icon exist; unique card illustration is missing. |
| card-action-recon-05 | Character action cards | Recon #5: search | base-game | critical | template-only | yes | [art](../../assets/generated/cards/action.svg) · [art2](../../assets/generated/ui-symbols.svg#i-search) | Functional frame and icon exist; unique card illustration is missing. |
| card-action-recon-06 | Character action cards | Recon #6: move | base-game | critical | template-only | yes | [art](../../assets/generated/cards/action.svg) · [art2](../../assets/generated/ui-symbols.svg#i-move) | Functional frame and icon exist; unique card illustration is missing. |
| card-action-recon-07 | Character action cards | Recon #7: cautiousMove | base-game | critical | template-only | yes | [art](../../assets/generated/cards/action.svg) · [art2](../../assets/generated/ui-symbols.svg#i-cautious) | Functional frame and icon exist; unique card illustration is missing. |
| card-action-recon-08 | Character action cards | Recon #8: shoot | base-game | critical | template-only | yes | [art](../../assets/generated/cards/action.svg) · [art2](../../assets/generated/ui-symbols.svg#i-shoot) | Functional frame and icon exist; unique card illustration is missing. |
| card-action-recon-09 | Character action cards | Recon #9: useRoom | base-game | critical | template-only | yes | [art](../../assets/generated/cards/action.svg) · [art2](../../assets/generated/ui-symbols.svg#i-room) | Functional frame and icon exist; unique card illustration is missing. |
| req-card-action-basic-action | Character action cards | basic-action | base-game | critical | template-only | yes | [art](../../assets/generated/cards/action.svg) | Functional shared treatment; unique class/card art is missing. |
| req-card-action-card-back | Character action cards | card-back | base-game | critical | complete | no | [art](../../assets/generated/cards/action.svg) | Original generic action treatment. |
| req-card-action-cost | Character action cards | cost | base-game | critical | template-only | yes | [art](../../assets/generated/cards/action.svg) | Functional shared treatment; unique class/card art is missing. |
| req-card-action-six-class-frames | Character action cards | six-class-frames | base-game | critical | template-only | yes | [art](../../assets/generated/cards/action.svg) | Functional shared treatment; unique class/card art is missing. |
| req-card-action-special-action | Character action cards | special-action | base-game | critical | template-only | yes | [art](../../assets/generated/cards/action.svg) | Functional shared treatment; unique class/card art is missing. |
| req-card-contamination-card-back | Contamination cards | card-back | base-game | high | partial | partial | [art](../../assets/generated/cards/contamination.svg) | Functional treatment exists; scan/code face variants are not authored. |
| req-card-contamination-clean | Contamination cards | clean | base-game | high | partial | partial | [art](../../assets/generated/cards/contamination.svg) | Functional treatment exists; scan/code face variants are not authored. |
| req-card-contamination-hidden | Contamination cards | hidden | base-game | high | partial | partial | [art](../../assets/generated/cards/contamination.svg) | Functional treatment exists; scan/code face variants are not authored. |
| req-card-contamination-infected-code | Contamination cards | infected-code | base-game | high | partial | partial | [art](../../assets/generated/cards/contamination.svg) | Functional treatment exists; scan/code face variants are not authored. |
| req-card-contamination-scanned | Contamination cards | scanned | base-game | high | partial | partial | [art](../../assets/generated/cards/contamination.svg) | Functional treatment exists; scan/code face variants are not authored. |
| card-event-ev7 | Event cards | Alarm | base-game | critical | missing | yes | — | Unique card illustration is missing. |
| card-event-ev15 | Event cards | Blocked Passage | base-game | critical | missing | yes | — | Unique card illustration is missing. |
| card-event-ev6 | Event cards | Breeding | base-game | critical | missing | yes | — | Unique card illustration is missing. |
| card-event-ev16 | Event cards | Contamination Leak | base-game | critical | missing | yes | — | Unique card illustration is missing. |
| card-event-ev17 | Event cards | Emergency Lighting | base-game | critical | missing | yes | — | Unique card illustration is missing. |
| card-event-ev4 | Event cards | Fire Outbreak | base-game | critical | missing | yes | — | Unique card illustration is missing. |
| card-event-ev13 | Event cards | Heat Wave | base-game | critical | missing | yes | — | Unique card illustration is missing. |
| card-event-ev8 | Event cards | Hull Breach | base-game | critical | missing | yes | — | Unique card illustration is missing. |
| card-event-ev12 | Event cards | Infestation | base-game | critical | missing | yes | — | Unique card illustration is missing. |
| card-event-ev14 | Event cards | Intruder Surge | base-game | critical | missing | yes | — | Unique card illustration is missing. |
| card-event-ev11 | Event cards | Malfunction | base-game | critical | missing | yes | — | Unique card illustration is missing. |
| card-event-ev10 | Event cards | Nest Awakening | base-game | critical | missing | yes | — | Unique card illustration is missing. |
| card-event-ev19 | Event cards | Nest Defense | base-game | critical | missing | yes | — | Unique card illustration is missing. |
| card-event-ev9 | Event cards | Power Surge | base-game | critical | missing | yes | — | Unique card illustration is missing. |
| card-event-ev20 | Event cards | Queen Awakening | base-game | critical | missing | yes | — | Unique card illustration is missing. |
| card-event-ev1 | Event cards | Reactor Overheating | base-game | critical | missing | yes | — | Unique card illustration is missing. |
| card-event-ev2 | Event cards | Scent of Prey | base-game | critical | missing | yes | — | Unique card illustration is missing. |
| card-event-ev3 | Event cards | Short Circuit | base-game | critical | missing | yes | — | Unique card illustration is missing. |
| card-event-ev5 | Event cards | System Failure | base-game | critical | missing | yes | — | Unique card illustration is missing. |
| card-event-ev18 | Event cards | Tremor | base-game | critical | missing | yes | — | Unique card illustration is missing. |
| req-card-event-card-back | Event cards | card-back | base-game | critical | missing | yes | — | No game-facing card artwork exists for this family. |
| req-card-event-card-front | Event cards | card-front | base-game | critical | missing | yes | — | No game-facing card artwork exists for this family. |
| req-card-event-movement-routing | Event cards | movement-routing | base-game | critical | missing | yes | — | No game-facing card artwork exists for this family. |
| req-card-event-room-effects | Event cards | room-effects | base-game | critical | missing | yes | — | No game-facing card artwork exists for this family. |
| card-exploration-ex1 | Exploration cards | Exploration ex1 | base-game | critical | missing | yes | — | Unique card illustration is missing. |
| card-exploration-ex10 | Exploration cards | Exploration ex10 | base-game | critical | missing | yes | — | Unique card illustration is missing. |
| card-exploration-ex11 | Exploration cards | Exploration ex11 | base-game | critical | missing | yes | — | Unique card illustration is missing. |
| card-exploration-ex12 | Exploration cards | Exploration ex12 | base-game | critical | missing | yes | — | Unique card illustration is missing. |
| card-exploration-ex2 | Exploration cards | Exploration ex2 | base-game | critical | missing | yes | — | Unique card illustration is missing. |
| card-exploration-ex3 | Exploration cards | Exploration ex3 | base-game | critical | missing | yes | — | Unique card illustration is missing. |
| card-exploration-ex4 | Exploration cards | Exploration ex4 | base-game | critical | missing | yes | — | Unique card illustration is missing. |
| card-exploration-ex5 | Exploration cards | Exploration ex5 | base-game | critical | missing | yes | — | Unique card illustration is missing. |
| card-exploration-ex6 | Exploration cards | Exploration ex6 | base-game | critical | missing | yes | — | Unique card illustration is missing. |
| card-exploration-ex7 | Exploration cards | Exploration ex7 | base-game | critical | missing | yes | — | Unique card illustration is missing. |
| card-exploration-ex8 | Exploration cards | Exploration ex8 | base-game | critical | missing | yes | — | Unique card illustration is missing. |
| card-exploration-ex9 | Exploration cards | Exploration ex9 | base-game | critical | missing | yes | — | Unique card illustration is missing. |
| req-card-exploration-card-back | Exploration cards | card-back | base-game | critical | missing | yes | — | No game-facing card artwork exists for this family. |
| req-card-exploration-corridor-layout | Exploration cards | corridor-layout | base-game | critical | missing | yes | — | No game-facing card artwork exists for this family. |
| req-card-exploration-entrance-effect | Exploration cards | entrance-effect | base-game | critical | missing | yes | — | No game-facing card artwork exists for this family. |
| req-card-exploration-room-type | Exploration cards | room-type | base-game | critical | missing | yes | — | No game-facing card artwork exists for this family. |
| card-item-green_gen_4 | Green item cards | Adrenaline Shot | base-game | critical | template-only | yes | [art](../../assets/generated/cards/green-item.svg) | Category frame exists; unique item illustration is missing. |
| card-item-green_gen_11 | Green item cards | Air Filter | base-game | critical | template-only | yes | [art](../../assets/generated/cards/green-item.svg) | Category frame exists; unique item illustration is missing. |
| card-item-green_gen_19 | Green item cards | Antibiotics | base-game | critical | template-only | yes | [art](../../assets/generated/cards/green-item.svg) | Category frame exists; unique item illustration is missing. |
| card-item-green_gen_13 | Green item cards | Antidote | base-game | critical | template-only | yes | [art](../../assets/generated/cards/green-item.svg) | Category frame exists; unique item illustration is missing. |
| card-item-green_gen_1 | Green item cards | Antiseptic | base-game | critical | template-only | yes | [art](../../assets/generated/cards/green-item.svg) | Category frame exists; unique item illustration is missing. |
| card-item-green_gen_0 | Green item cards | Bandages | base-game | critical | template-only | yes | [art](../../assets/generated/cards/green-item.svg) | Category frame exists; unique item illustration is missing. |
| card-item-green_gen_18 | Green item cards | Burn Cream | base-game | critical | template-only | yes | [art](../../assets/generated/cards/green-item.svg) | Category frame exists; unique item illustration is missing. |
| card-item-green_gen_25 | Green item cards | Compass | base-game | critical | template-only | yes | [art](../../assets/generated/cards/green-item.svg) | Category frame exists; unique item illustration is missing. |
| card-item-green_gen_12 | Green item cards | Decontamination Wipes | base-game | critical | template-only | yes | [art](../../assets/generated/cards/green-item.svg) | Category frame exists; unique item illustration is missing. |
| card-item-green_gen_16 | Green item cards | Disinfectant Spray | base-game | critical | template-only | yes | [art](../../assets/generated/cards/green-item.svg) | Category frame exists; unique item illustration is missing. |
| card-item-green_gen_22 | Green item cards | Emergency Beacon | base-game | critical | template-only | yes | [art](../../assets/generated/cards/green-item.svg) | Category frame exists; unique item illustration is missing. |
| card-item-green_gen_26 | Green item cards | Emergency Map | base-game | critical | template-only | yes | [art](../../assets/generated/cards/green-item.svg) | Category frame exists; unique item illustration is missing. |
| card-item-green_gen_9 | Green item cards | Emergency Rations | base-game | critical | template-only | yes | [art](../../assets/generated/cards/green-item.svg) | Category frame exists; unique item illustration is missing. |
| card-item-green_gen_3 | Green item cards | Energy Drink | base-game | critical | template-only | yes | [art](../../assets/generated/cards/green-item.svg) | Category frame exists; unique item illustration is missing. |
| card-item-green_gen_8 | Green item cards | First Aid Kit | base-game | critical | template-only | yes | [art](../../assets/generated/cards/green-item.svg) | Category frame exists; unique item illustration is missing. |
| card-item-green_gen_21 | Green item cards | Flare Gun | base-game | critical | template-only | yes | [art](../../assets/generated/cards/green-item.svg) | Category frame exists; unique item illustration is missing. |
| card-item-green_gen_5 | Green item cards | Herbal Remedy | base-game | critical | template-only | yes | [art](../../assets/generated/cards/green-item.svg) | Category frame exists; unique item illustration is missing. |
| card-item-medpackStarter | Green item cards | Medpack | base-game | critical | template-only | yes | [art](../../assets/generated/cards/green-item.svg) | Category frame exists; unique item illustration is missing. |
| card-item-green_gen_7 | Green item cards | Morphine | base-game | critical | template-only | yes | [art](../../assets/generated/cards/green-item.svg) | Category frame exists; unique item illustration is missing. |
| card-item-oxygenTank | Green item cards | Oxygen Tank | base-game | critical | template-only | yes | [art](../../assets/generated/cards/green-item.svg) | Category frame exists; unique item illustration is missing. |
| card-item-green_gen_2 | Green item cards | Painkillers | base-game | critical | template-only | yes | [art](../../assets/generated/cards/green-item.svg) | Category frame exists; unique item illustration is missing. |
| card-item-scanner | Green item cards | Scanner | base-game | critical | template-only | yes | [art](../../assets/generated/cards/green-item.svg) | Category frame exists; unique item illustration is missing. |
| card-item-green_gen_23 | Green item cards | Signal Mirror | base-game | critical | template-only | yes | [art](../../assets/generated/cards/green-item.svg) | Category frame exists; unique item illustration is missing. |
| card-item-green_gen_6 | Green item cards | Splint | base-game | critical | template-only | yes | [art](../../assets/generated/cards/green-item.svg) | Category frame exists; unique item illustration is missing. |
| card-item-green_gen_14 | Green item cards | Stim Pack | base-game | critical | template-only | yes | [art](../../assets/generated/cards/green-item.svg) | Category frame exists; unique item illustration is missing. |
| card-item-green_gen_20 | Green item cards | Survival Kit | base-game | critical | template-only | yes | [art](../../assets/generated/cards/green-item.svg) | Category frame exists; unique item illustration is missing. |
| card-item-green_gen_24 | Green item cards | Thermal Blanket | base-game | critical | template-only | yes | [art](../../assets/generated/cards/green-item.svg) | Category frame exists; unique item illustration is missing. |
| card-item-green_gen_17 | Green item cards | Tourniquet | base-game | critical | template-only | yes | [art](../../assets/generated/cards/green-item.svg) | Category frame exists; unique item illustration is missing. |
| card-item-green_gen_15 | Green item cards | Vitamins | base-game | critical | template-only | yes | [art](../../assets/generated/cards/green-item.svg) | Category frame exists; unique item illustration is missing. |
| card-item-green_gen_10 | Green item cards | Water Filter | base-game | critical | template-only | yes | [art](../../assets/generated/cards/green-item.svg) | Category frame exists; unique item illustration is missing. |
| req-card-item-green-card-back | Green item cards | card-back | base-game | critical | template-only | yes | [art](../../assets/generated/cards/green-item.svg) | Functional category frame; unique item illustration is missing. |
| req-card-item-green-card-front | Green item cards | card-front | base-game | critical | template-only | yes | [art](../../assets/generated/cards/green-item.svg) | Functional category frame; unique item illustration is missing. |
| req-card-item-green-medical | Green item cards | medical | base-game | critical | template-only | yes | [art](../../assets/generated/cards/green-item.svg) | Functional category frame; unique item illustration is missing. |
| req-card-item-green-one-use | Green item cards | one-use | base-game | critical | template-only | yes | [art](../../assets/generated/cards/green-item.svg) | Functional category frame; unique item illustration is missing. |
| req-card-item-green-tactical-belt | Green item cards | tactical-belt | base-game | critical | template-only | yes | [art](../../assets/generated/cards/green-item.svg) | Functional category frame; unique item illustration is missing. |
| card-intruder-attack-ia10 | Intruder attack cards | Acid Spit | base-game | critical | missing | yes | — | Unique card illustration is missing. |
| card-intruder-attack-ia2 | Intruder attack cards | Bite | base-game | critical | missing | yes | — | Unique card illustration is missing. |
| card-intruder-attack-ia12 | Intruder attack cards | Charge | base-game | critical | missing | yes | — | Unique card illustration is missing. |
| card-intruder-attack-ia14 | Intruder attack cards | Claw | base-game | critical | missing | yes | — | Unique card illustration is missing. |
| card-intruder-attack-ia5 | Intruder attack cards | Crush | base-game | critical | missing | yes | — | Unique card illustration is missing. |
| card-intruder-attack-ia1 | Intruder attack cards | Deadly Claws | base-game | critical | missing | yes | — | Unique card illustration is missing. |
| card-intruder-attack-ia11 | Intruder attack cards | Gnaw | base-game | critical | missing | yes | — | Unique card illustration is missing. |
| card-intruder-attack-ia6 | Intruder attack cards | Grasp | base-game | critical | missing | yes | — | Unique card illustration is missing. |
| card-intruder-attack-ia16 | Intruder attack cards | Headbutt | base-game | critical | missing | yes | — | Unique card illustration is missing. |
| card-intruder-attack-ia3 | Intruder attack cards | Infecting | base-game | critical | missing | yes | — | Unique card illustration is missing. |
| card-intruder-attack-ia18 | Intruder attack cards | Maul | base-game | critical | missing | yes | — | Unique card illustration is missing. |
| card-intruder-attack-ia8 | Intruder attack cards | Pounce | base-game | critical | missing | yes | — | Unique card illustration is missing. |
| card-intruder-attack-ia15 | Intruder attack cards | Punch | base-game | critical | missing | yes | — | Unique card illustration is missing. |
| card-intruder-attack-ia4 | Intruder attack cards | Rend | base-game | critical | missing | yes | — | Unique card illustration is missing. |
| card-intruder-attack-ia7 | Intruder attack cards | Slash | base-game | critical | missing | yes | — | Unique card illustration is missing. |
| card-intruder-attack-ia13 | Intruder attack cards | Spit | base-game | critical | missing | yes | — | Unique card illustration is missing. |
| card-intruder-attack-ia9 | Intruder attack cards | Tail Whip | base-game | critical | missing | yes | — | Unique card illustration is missing. |
| card-intruder-attack-ia17 | Intruder attack cards | Tear | base-game | critical | missing | yes | — | Unique card illustration is missing. |
| card-intruder-attack-ia19 | Intruder attack cards | Thrash | base-game | critical | missing | yes | — | Unique card illustration is missing. |
| card-intruder-attack-ia20 | Intruder attack cards | Venom | base-game | critical | missing | yes | — | Unique card illustration is missing. |
| req-card-intruder-attack-adult | Intruder attack cards | adult | base-game | critical | missing | yes | — | No game-facing card artwork exists for this family. |
| req-card-intruder-attack-card-back | Intruder attack cards | card-back | base-game | critical | missing | yes | — | No game-facing card artwork exists for this family. |
| req-card-intruder-attack-drone | Intruder attack cards | drone | base-game | critical | missing | yes | — | No game-facing card artwork exists for this family. |
| req-card-intruder-attack-primeblood | Intruder attack cards | primeblood | base-game | critical | missing | yes | — | No game-facing card artwork exists for this family. |
| req-card-intruder-attack-queen | Intruder attack cards | queen | base-game | critical | missing | yes | — | No game-facing card artwork exists for this family. |
| req-card-weakness-face-down | Intruder weakness cards | face-down | base-game | medium | missing | yes | — | No game-facing card artwork exists for this family. |
| req-card-weakness-revealed | Intruder weakness cards | revealed | base-game | medium | missing | yes | — | No game-facing card artwork exists for this family. |
| req-card-weakness-three-weakness-types | Intruder weakness cards | three-weakness-types | base-game | medium | missing | yes | — | No game-facing card artwork exists for this family. |
| card-objective-mission-mo1 | Mission objective cards | Official Order | base-game | high | template-only | yes | [art](../../assets/generated/cards/objective.svg) | Unique card illustration is missing. |
| card-objective-mission-mo2 | Mission objective cards | Official Order | base-game | high | template-only | yes | [art](../../assets/generated/cards/objective.svg) | Unique card illustration is missing. |
| card-objective-mission-mo3 | Mission objective cards | Official Order | base-game | high | template-only | yes | [art](../../assets/generated/cards/objective.svg) | Unique card illustration is missing. |
| card-objective-mission-mo4 | Mission objective cards | Official Order | base-game | high | template-only | yes | [art](../../assets/generated/cards/objective.svg) | Unique card illustration is missing. |
| card-objective-mission-mo5 | Mission objective cards | Ulterior Motive | base-game | high | template-only | yes | [art](../../assets/generated/cards/objective.svg) | Unique card illustration is missing. |
| card-objective-mission-mo6 | Mission objective cards | Ulterior Motive | base-game | high | template-only | yes | [art](../../assets/generated/cards/objective.svg) | Unique card illustration is missing. |
| card-objective-mission-mo7 | Mission objective cards | Ulterior Motive | base-game | high | template-only | yes | [art](../../assets/generated/cards/objective.svg) | Unique card illustration is missing. |
| req-card-objective-mission-card-back | Mission objective/task cards | card-back | base-game | high | template-only | yes | [art](../../assets/generated/cards/objective.svg) | Functional objective treatment; unique card illustration is missing. |
| req-card-objective-mission-objective | Mission objective/task cards | objective | base-game | high | template-only | yes | [art](../../assets/generated/cards/objective.svg) | Functional objective treatment; unique card illustration is missing. |
| req-card-objective-mission-player-count | Mission objective/task cards | player-count | base-game | high | template-only | yes | [art](../../assets/generated/cards/objective.svg) | Functional objective treatment; unique card illustration is missing. |
| req-card-objective-mission-resolved | Mission objective/task cards | resolved | base-game | high | template-only | yes | [art](../../assets/generated/cards/objective.svg) | Functional objective treatment; unique card illustration is missing. |
| req-card-objective-mission-task | Mission objective/task cards | task | base-game | high | template-only | yes | [art](../../assets/generated/cards/objective.svg) | Functional objective treatment; unique card illustration is missing. |
| card-objective-mission-mt7 | Mission task cards | Eradication | base-game | high | template-only | yes | [art](../../assets/generated/cards/objective.svg) | Unique card illustration is missing. |
| card-objective-mission-mt3 | Mission task cards | Escort Mission | base-game | high | template-only | yes | [art](../../assets/generated/cards/objective.svg) | Unique card illustration is missing. |
| card-objective-mission-mt5 | Mission task cards | Essential Data | base-game | high | template-only | yes | [art](../../assets/generated/cards/objective.svg) | Unique card illustration is missing. |
| card-objective-mission-mt6 | Mission task cards | Facility Restart | base-game | high | template-only | yes | [art](../../assets/generated/cards/objective.svg) | Unique card illustration is missing. |
| card-objective-mission-mt4 | Mission task cards | Perimeter Clearing | base-game | high | template-only | yes | [art](../../assets/generated/cards/objective.svg) | Unique card illustration is missing. |
| card-objective-mission-mt1 | Mission task cards | Primary Samples | base-game | high | template-only | yes | [art](../../assets/generated/cards/objective.svg) | Unique card illustration is missing. |
| card-objective-mission-mt2 | Mission task cards | Reconnaissance | base-game | high | template-only | yes | [art](../../assets/generated/cards/objective.svg) | Unique card illustration is missing. |
| card-objective-mission-mt8 | Mission task cards | The Supply Route | base-game | high | template-only | yes | [art](../../assets/generated/cards/objective.svg) | Unique card illustration is missing. |
| req-card-help-cleanup | Player help/phase cards | cleanup | base-game | high | missing | yes | — | No game-facing card artwork exists for this family. |
| req-card-help-event-phase | Player help/phase cards | event-phase | base-game | high | missing | yes | — | No game-facing card artwork exists for this family. |
| req-card-help-intruder-phase | Player help/phase cards | intruder-phase | base-game | high | missing | yes | — | No game-facing card artwork exists for this family. |
| req-card-help-player-number | Player help/phase cards | player-number | base-game | high | missing | yes | — | No game-facing card artwork exists for this family. |
| req-card-help-player-phase | Player help/phase cards | player-phase | base-game | high | missing | yes | — | No game-facing card artwork exists for this family. |
| card-objective-private-po4 | Private objective cards | Clean-Up | base-game | high | template-only | yes | [art](../../assets/generated/cards/objective.svg) | Unique card illustration is missing. |
| card-objective-private-po10 | Private objective cards | Data Thief | base-game | high | template-only | yes | [art](../../assets/generated/cards/objective.svg) | Unique card illustration is missing. |
| card-objective-private-po13 | Private objective cards | Explorer | base-game | high | template-only | yes | [art](../../assets/generated/cards/objective.svg) | Unique card illustration is missing. |
| card-objective-private-po5 | Private objective cards | Faceoff | base-game | high | template-only | yes | [art](../../assets/generated/cards/objective.svg) | Unique card illustration is missing. |
| card-objective-private-po11 | Private objective cards | Firebug | base-game | high | template-only | yes | [art](../../assets/generated/cards/objective.svg) | Unique card illustration is missing. |
| card-objective-private-po15 | Private objective cards | Last Stand | base-game | high | template-only | yes | [art](../../assets/generated/cards/objective.svg) | Unique card illustration is missing. |
| card-objective-private-po7 | Private objective cards | Lone Wolf | base-game | high | template-only | yes | [art](../../assets/generated/cards/objective.svg) | Unique card illustration is missing. |
| card-objective-private-po12 | Private objective cards | Pacifist | base-game | high | template-only | yes | [art](../../assets/generated/cards/objective.svg) | Unique card illustration is missing. |
| card-objective-private-po6 | Private objective cards | Sabotage | base-game | high | template-only | yes | [art](../../assets/generated/cards/objective.svg) | Unique card illustration is missing. |
| card-objective-private-po1 | Private objective cards | Self-Serving | base-game | high | template-only | yes | [art](../../assets/generated/cards/objective.svg) | Unique card illustration is missing. |
| card-objective-private-po8 | Private objective cards | Survivor | base-game | high | template-only | yes | [art](../../assets/generated/cards/objective.svg) | Unique card illustration is missing. |
| card-objective-private-po2 | Private objective cards | The Great Hunt | base-game | high | template-only | yes | [art](../../assets/generated/cards/objective.svg) | Unique card illustration is missing. |
| card-objective-private-po14 | Private objective cards | Tomb Raider | base-game | high | template-only | yes | [art](../../assets/generated/cards/objective.svg) | Unique card illustration is missing. |
| card-objective-private-po3 | Private objective cards | Veni, Vidi, Vici | base-game | high | template-only | yes | [art](../../assets/generated/cards/objective.svg) | Unique card illustration is missing. |
| req-card-objective-private-card-back | Private objective cards | card-back | base-game | high | template-only | yes | [art](../../assets/generated/cards/objective.svg) | Functional objective treatment; unique card illustration is missing. |
| req-card-objective-private-chosen | Private objective cards | chosen | base-game | high | template-only | yes | [art](../../assets/generated/cards/objective.svg) | Functional objective treatment; unique card illustration is missing. |
| req-card-objective-private-hidden | Private objective cards | hidden | base-game | high | template-only | yes | [art](../../assets/generated/cards/objective.svg) | Functional objective treatment; unique card illustration is missing. |
| req-card-objective-private-objective | Private objective cards | objective | base-game | high | template-only | yes | [art](../../assets/generated/cards/objective.svg) | Functional objective treatment; unique card illustration is missing. |
| req-card-objective-private-player-count | Private objective cards | player-count | base-game | high | template-only | yes | [art](../../assets/generated/cards/objective.svg) | Functional objective treatment; unique card illustration is missing. |
| req-card-objective-private-rejected | Private objective cards | rejected | base-game | high | template-only | yes | [art](../../assets/generated/cards/objective.svg) | Functional objective treatment; unique card illustration is missing. |
| card-objective-private-po9 | Private objective cards | 标本 Collector | base-game | high | template-only | yes | [art](../../assets/generated/cards/objective.svg) | Unique card illustration is missing. |
| card-item-red_gen_17 | Red item cards |  Riot Gun | base-game | critical | template-only | yes | [art](../../assets/generated/cards/red-item.svg) | Category frame exists; unique item illustration is missing. |
| card-item-red_gen_12 | Red item cards | Armor Piercing Rounds | base-game | critical | template-only | yes | [art](../../assets/generated/cards/red-item.svg) | Category frame exists; unique item illustration is missing. |
| card-item-rifle | Red item cards | Assault Rifle | base-game | critical | template-only | yes | [art](../../assets/generated/cards/red-item.svg) | Category frame exists; unique item illustration is missing. |
| card-item-automaticShotgun | Red item cards | Automatic Shotgun | base-game | critical | template-only | yes | [art](../../assets/generated/cards/red-item.svg) | Category frame exists; unique item illustration is missing. |
| card-item-red_gen_18 | Red item cards | Battle Rifle | base-game | critical | template-only | yes | [art](../../assets/generated/cards/red-item.svg) | Category frame exists; unique item illustration is missing. |
| card-item-red_gen_0 | Red item cards | Combat Knife | base-game | critical | template-only | yes | [art](../../assets/generated/cards/red-item.svg) | Category frame exists; unique item illustration is missing. |
| card-item-red_gen_13 | Red item cards | Combat Machete | base-game | critical | template-only | yes | [art](../../assets/generated/cards/red-item.svg) | Category frame exists; unique item illustration is missing. |
| card-item-red_gen_4 | Red item cards | Combat Shotgun | base-game | critical | template-only | yes | [art](../../assets/generated/cards/red-item.svg) | Category frame exists; unique item illustration is missing. |
| card-item-red_gen_6 | Red item cards | Crossbow | base-game | critical | template-only | yes | [art](../../assets/generated/cards/red-item.svg) | Category frame exists; unique item illustration is missing. |
| card-item-flamethrower | Red item cards | Flamethrower | base-game | critical | template-only | yes | [art](../../assets/generated/cards/red-item.svg) | Category frame exists; unique item illustration is missing. |
| card-item-red_gen_8 | Red item cards | Flashbang | base-game | critical | template-only | yes | [art](../../assets/generated/cards/red-item.svg) | Category frame exists; unique item illustration is missing. |
| card-item-red_gen_10 | Red item cards | Frag Grenade | base-game | critical | template-only | yes | [art](../../assets/generated/cards/red-item.svg) | Category frame exists; unique item illustration is missing. |
| card-item-grenadeLauncher | Red item cards | Grenade Launcher | base-game | critical | template-only | yes | [art](../../assets/generated/cards/red-item.svg) | Category frame exists; unique item illustration is missing. |
| card-item-red_gen_5 | Red item cards | Heavy Machine Gun | base-game | critical | template-only | yes | [art](../../assets/generated/cards/red-item.svg) | Category frame exists; unique item illustration is missing. |
| card-item-red_gen_11 | Red item cards | Incendiary Rounds | base-game | critical | template-only | yes | [art](../../assets/generated/cards/red-item.svg) | Category frame exists; unique item illustration is missing. |
| card-item-red_gen_19 | Red item cards | Laser Pistol | base-game | critical | template-only | yes | [art](../../assets/generated/cards/red-item.svg) | Category frame exists; unique item illustration is missing. |
| card-item-militaryTaser | Red item cards | Military Taser | base-game | critical | template-only | yes | [art](../../assets/generated/cards/red-item.svg) | Category frame exists; unique item illustration is missing. |
| card-item-red_gen_16 | Red item cards | Net Launcher | base-game | critical | template-only | yes | [art](../../assets/generated/cards/red-item.svg) | Category frame exists; unique item illustration is missing. |
| card-item-pistol | Red item cards | Pistol | base-game | critical | template-only | yes | [art](../../assets/generated/cards/red-item.svg) | Category frame exists; unique item illustration is missing. |
| card-item-red_gen_3 | Red item cards | Plasma Pistol | base-game | critical | template-only | yes | [art](../../assets/generated/cards/red-item.svg) | Category frame exists; unique item illustration is missing. |
| card-item-red_gen_2 | Red item cards | Pulse Rifle | base-game | critical | template-only | yes | [art](../../assets/generated/cards/red-item.svg) | Category frame exists; unique item illustration is missing. |
| card-item-smg | Red item cards | SMG | base-game | critical | template-only | yes | [art](../../assets/generated/cards/red-item.svg) | Category frame exists; unique item illustration is missing. |
| card-item-red_gen_9 | Red item cards | Smoke Grenade | base-game | critical | template-only | yes | [art](../../assets/generated/cards/red-item.svg) | Category frame exists; unique item illustration is missing. |
| card-item-sniperRifle | Red item cards | Sniper Rifle | base-game | critical | template-only | yes | [art](../../assets/generated/cards/red-item.svg) | Category frame exists; unique item illustration is missing. |
| card-item-sonicGun | Red item cards | Sonic Gun | base-game | critical | template-only | yes | [art](../../assets/generated/cards/red-item.svg) | Category frame exists; unique item illustration is missing. |
| card-item-red_gen_15 | Red item cards | Speargun | base-game | critical | template-only | yes | [art](../../assets/generated/cards/red-item.svg) | Category frame exists; unique item illustration is missing. |
| card-item-red_gen_1 | Red item cards | Stun Baton | base-game | critical | template-only | yes | [art](../../assets/generated/cards/red-item.svg) | Category frame exists; unique item illustration is missing. |
| card-item-red_gen_14 | Red item cards | Tactical Batons | base-game | critical | template-only | yes | [art](../../assets/generated/cards/red-item.svg) | Category frame exists; unique item illustration is missing. |
| card-item-tacticalHatchet | Red item cards | Tactical Hatchet | base-game | critical | template-only | yes | [art](../../assets/generated/cards/red-item.svg) | Category frame exists; unique item illustration is missing. |
| card-item-red_gen_7 | Red item cards | Taser | base-game | critical | template-only | yes | [art](../../assets/generated/cards/red-item.svg) | Category frame exists; unique item illustration is missing. |
| req-card-item-red-ammo | Red item cards | ammo | base-game | critical | template-only | yes | [art](../../assets/generated/cards/red-item.svg) | Functional category frame; unique item illustration is missing. |
| req-card-item-red-card-back | Red item cards | card-back | base-game | critical | template-only | yes | [art](../../assets/generated/cards/red-item.svg) | Functional category frame; unique item illustration is missing. |
| req-card-item-red-card-front | Red item cards | card-front | base-game | critical | template-only | yes | [art](../../assets/generated/cards/red-item.svg) | Functional category frame; unique item illustration is missing. |
| req-card-item-red-heavy | Red item cards | heavy | base-game | critical | template-only | yes | [art](../../assets/generated/cards/red-item.svg) | Functional category frame; unique item illustration is missing. |
| req-card-item-red-one-use | Red item cards | one-use | base-game | critical | template-only | yes | [art](../../assets/generated/cards/red-item.svg) | Functional category frame; unique item illustration is missing. |
| req-card-item-red-weapon | Red item cards | weapon | base-game | critical | template-only | yes | [art](../../assets/generated/cards/red-item.svg) | Functional category frame; unique item illustration is missing. |
| card-wound-sw1 | Serious wound cards | Blindness | base-game | high | missing | yes | — | Unique card illustration is missing. |
| card-wound-sw24 | Serious wound cards | Broken Jaw | base-game | high | missing | yes | — | Unique card illustration is missing. |
| card-wound-sw2 | Serious wound cards | Broken Ribs | base-game | high | missing | yes | — | Unique card illustration is missing. |
| card-wound-sw8 | Serious wound cards | Collapsed Lung | base-game | high | missing | yes | — | Unique card illustration is missing. |
| card-wound-sw3 | Serious wound cards | Concussion | base-game | high | missing | yes | — | Unique card illustration is missing. |
| card-wound-sw7 | Serious wound cards | Cracked Skull | base-game | high | missing | yes | — | Unique card illustration is missing. |
| card-wound-sw18 | Serious wound cards | Crushed Fingers | base-game | high | missing | yes | — | Unique card illustration is missing. |
| card-wound-sw25 | Serious wound cards | Crushed Windpipe | base-game | high | missing | yes | — | Unique card illustration is missing. |
| card-wound-sw13 | Serious wound cards | Deep Wound | base-game | high | missing | yes | — | Unique card illustration is missing. |
| card-wound-sw17 | Serious wound cards | Dislocated Shoulder | base-game | high | missing | yes | — | Unique card illustration is missing. |
| card-wound-sw11 | Serious wound cards | EYES | base-game | high | missing | yes | — | Unique card illustration is missing. |
| card-wound-sw14 | Serious wound cards | Fractured Arm | base-game | high | missing | yes | — | Unique card illustration is missing. |
| card-wound-sw27 | Serious wound cards | General Trauma | base-game | high | missing | yes | — | Unique card illustration is missing. |
| card-wound-sw4 | Serious wound cards | Internal Bleeding | base-game | high | missing | yes | — | Unique card illustration is missing. |
| card-wound-sw10 | Serious wound cards | Loss of Vision | base-game | high | missing | yes | — | Unique card illustration is missing. |
| card-wound-sw9 | Serious wound cards | Nerve Damage | base-game | high | missing | yes | — | Unique card illustration is missing. |
| card-wound-sw21 | Serious wound cards | Perforated Eardrum | base-game | high | missing | yes | — | Unique card illustration is missing. |
| card-wound-sw23 | Serious wound cards | Punctured Lung | base-game | high | missing | yes | — | Unique card illustration is missing. |
| card-wound-sw19 | Serious wound cards | Ruptured Spleen | base-game | high | missing | yes | — | Unique card illustration is missing. |
| card-wound-sw16 | Serious wound cards | Severe Burns | base-game | high | missing | yes | — | Unique card illustration is missing. |
| card-wound-sw22 | Serious wound cards | Severed Tendon | base-game | high | missing | yes | — | Unique card illustration is missing. |
| card-wound-sw5 | Serious wound cards | Shattered Hand | base-game | high | missing | yes | — | Unique card illustration is missing. |
| card-wound-sw20 | Serious wound cards | Spinal Injury | base-game | high | missing | yes | — | Unique card illustration is missing. |
| card-wound-sw6 | Serious wound cards | Sprained Ankle | base-game | high | missing | yes | — | Unique card illustration is missing. |
| card-wound-sw26 | Serious wound cards | Torn Ligament | base-game | high | missing | yes | — | Unique card illustration is missing. |
| card-wound-sw15 | Serious wound cards | Torn Muscle | base-game | high | missing | yes | — | Unique card illustration is missing. |
| card-wound-sw12 | Serious wound cards | Weak Spot | base-game | high | missing | yes | — | Unique card illustration is missing. |
| req-card-wound-active | Serious wound cards | active | base-game | high | missing | yes | — | No game-facing card artwork exists for this family. |
| req-card-wound-body-location | Serious wound cards | body-location | base-game | high | missing | yes | — | No game-facing card artwork exists for this family. |
| req-card-wound-card-back | Serious wound cards | card-back | base-game | high | missing | yes | — | No game-facing card artwork exists for this family. |
| req-card-wound-treated | Serious wound cards | treated | base-game | high | missing | yes | — | No game-facing card artwork exists for this family. |
| card-starting-automaticShotgun | Starting item cards | Automatic Shotgun | base-game | critical | template-only | yes | [art](../../assets/generated/cards/red-item.svg) | Category frame exists; unique item illustration is missing. |
| card-starting-medpackStarter | Starting item cards | Medpack | base-game | critical | template-only | yes | [art](../../assets/generated/cards/green-item.svg) | Category frame exists; unique item illustration is missing. |
| card-starting-tacticalHatchet | Starting item cards | Tactical Hatchet | base-game | critical | template-only | yes | [art](../../assets/generated/cards/red-item.svg) | Category frame exists; unique item illustration is missing. |
| req-card-starting-item-equipment | Starting item cards | equipment | base-game | critical | template-only | yes | [art](../../assets/generated/cards/yellow-item.svg) | Functional category frame; unique item illustration is missing. |
| req-card-starting-item-heavy | Starting item cards | heavy | base-game | critical | template-only | yes | [art](../../assets/generated/cards/yellow-item.svg) | Functional category frame; unique item illustration is missing. |
| card-starting-officerPistol | Starting item cards | officerPistol | base-game | critical | template-only | yes | [art](../../assets/generated/cards/yellow-item.svg) | Category frame exists; unique item illustration is missing. |
| req-card-starting-item-one-use | Starting item cards | one-use | base-game | critical | template-only | yes | [art](../../assets/generated/cards/yellow-item.svg) | Functional category frame; unique item illustration is missing. |
| card-starting-reconScanner | Starting item cards | reconScanner | base-game | critical | template-only | yes | [art](../../assets/generated/cards/yellow-item.svg) | Category frame exists; unique item illustration is missing. |
| req-card-starting-item-tactical-belt | Starting item cards | tactical-belt | base-game | critical | template-only | yes | [art](../../assets/generated/cards/yellow-item.svg) | Functional category frame; unique item illustration is missing. |
| req-card-starting-item-weapon | Starting item cards | weapon | base-game | critical | template-only | yes | [art](../../assets/generated/cards/yellow-item.svg) | Functional category frame; unique item illustration is missing. |
| card-item-yellow_gen_5 | Yellow item cards | Ammo Belt | base-game | critical | template-only | yes | [art](../../assets/generated/cards/yellow-item.svg) | Category frame exists; unique item illustration is missing. |
| card-item-yellow_gen_18 | Yellow item cards | Bolt Cutters | base-game | critical | template-only | yes | [art](../../assets/generated/cards/yellow-item.svg) | Category frame exists; unique item illustration is missing. |
| card-item-yellow_gen_10 | Yellow item cards | Breach Charge | base-game | critical | template-only | yes | [art](../../assets/generated/cards/yellow-item.svg) | Category frame exists; unique item illustration is missing. |
| card-item-yellow_gen_2 | Yellow item cards | Crowbar | base-game | critical | template-only | yes | [art](../../assets/generated/cards/yellow-item.svg) | Category frame exists; unique item illustration is missing. |
| card-item-yellow_gen_14 | Yellow item cards | Data Link | base-game | critical | template-only | yes | [art](../../assets/generated/cards/yellow-item.svg) | Category frame exists; unique item illustration is missing. |
| card-item-ductTape | Yellow item cards | Duct Tape | base-game | critical | template-only | yes | [art](../../assets/generated/cards/yellow-item.svg) | Category frame exists; unique item illustration is missing. |
| card-item-yellow_gen_19 | Yellow item cards | Fire Extinguisher | base-game | critical | template-only | yes | [art](../../assets/generated/cards/yellow-item.svg) | Category frame exists; unique item illustration is missing. |
| card-item-yellow_gen_6 | Yellow item cards | Grenade Pouch | base-game | critical | template-only | yes | [art](../../assets/generated/cards/yellow-item.svg) | Category frame exists; unique item illustration is missing. |
| card-item-yellow_gen_8 | Yellow item cards | Hazmat Suit | base-game | critical | template-only | yes | [art](../../assets/generated/cards/yellow-item.svg) | Category frame exists; unique item illustration is missing. |
| card-item-heavyArmor | Yellow item cards | Heavy Armor | base-game | critical | template-only | yes | [art](../../assets/generated/cards/yellow-item.svg) | Category frame exists; unique item illustration is missing. |
| card-item-yellow_gen_20 | Yellow item cards | Insulated Suit | base-game | critical | template-only | yes | [art](../../assets/generated/cards/yellow-item.svg) | Category frame exists; unique item illustration is missing. |
| card-item-yellow_gen_4 | Yellow item cards | Med Kit Carrier | base-game | critical | template-only | yes | [art](../../assets/generated/cards/yellow-item.svg) | Category frame exists; unique item illustration is missing. |
| card-item-yellow_gen_12 | Yellow item cards | Motion Detector | base-game | critical | template-only | yes | [art](../../assets/generated/cards/yellow-item.svg) | Category frame exists; unique item illustration is missing. |
| card-item-yellow_gen_15 | Yellow item cards | Override Key | base-game | critical | template-only | yes | [art](../../assets/generated/cards/yellow-item.svg) | Category frame exists; unique item illustration is missing. |
| card-item-perimeterSecurityDevice | Yellow item cards | Perimeter Security Device | base-game | critical | template-only | yes | [art](../../assets/generated/cards/yellow-item.svg) | Category frame exists; unique item illustration is missing. |
| card-item-yellow_gen_16 | Yellow item cards | Power Drill | base-game | critical | template-only | yes | [art](../../assets/generated/cards/yellow-item.svg) | Category frame exists; unique item illustration is missing. |
| card-item-yellow_gen_21 | Yellow item cards | Pressure Suit | base-game | critical | template-only | yes | [art](../../assets/generated/cards/yellow-item.svg) | Category frame exists; unique item illustration is missing. |
| card-item-yellow_gen_22 | Yellow item cards | Reinforced Boots | base-game | critical | template-only | yes | [art](../../assets/generated/cards/yellow-item.svg) | Category frame exists; unique item illustration is missing. |
| card-item-yellow_gen_9 | Yellow item cards | Reinforced Gloves | base-game | critical | template-only | yes | [art](../../assets/generated/cards/yellow-item.svg) | Category frame exists; unique item illustration is missing. |
| card-item-yellow_gen_3 | Yellow item cards | Repair Kit | base-game | critical | template-only | yes | [art](../../assets/generated/cards/yellow-item.svg) | Category frame exists; unique item illustration is missing. |
| card-item-serverRobot | Yellow item cards | Server Robot | base-game | critical | template-only | yes | [art](../../assets/generated/cards/yellow-item.svg) | Category frame exists; unique item illustration is missing. |
| card-item-yellow_gen_13 | Yellow item cards | Signal Booster | base-game | critical | template-only | yes | [art](../../assets/generated/cards/yellow-item.svg) | Category frame exists; unique item illustration is missing. |
| card-item-yellow_gen_17 | Yellow item cards | Sledgehammer | base-game | critical | template-only | yes | [art](../../assets/generated/cards/yellow-item.svg) | Category frame exists; unique item illustration is missing. |
| card-item-yellow_gen_24 | Yellow item cards | Spare Parts | base-game | critical | template-only | yes | [art](../../assets/generated/cards/yellow-item.svg) | Category frame exists; unique item illustration is missing. |
| card-item-technicalRobot | Yellow item cards | Technical Robot | base-game | critical | template-only | yes | [art](../../assets/generated/cards/yellow-item.svg) | Category frame exists; unique item illustration is missing. |
| card-item-yellow_gen_11 | Yellow item cards | Thermal Goggles | base-game | critical | template-only | yes | [art](../../assets/generated/cards/yellow-item.svg) | Category frame exists; unique item illustration is missing. |
| card-item-yellow_gen_0 | Yellow item cards | Tool Kit | base-game | critical | template-only | yes | [art](../../assets/generated/cards/yellow-item.svg) | Category frame exists; unique item illustration is missing. |
| card-item-yellow_gen_23 | Yellow item cards | Traction Cleats | base-game | critical | template-only | yes | [art](../../assets/generated/cards/yellow-item.svg) | Category frame exists; unique item illustration is missing. |
| card-item-yellow_gen_7 | Yellow item cards | Utility Belt | base-game | critical | template-only | yes | [art](../../assets/generated/cards/yellow-item.svg) | Category frame exists; unique item illustration is missing. |
| card-item-yellow_gen_1 | Yellow item cards | Welding Torch | base-game | critical | template-only | yes | [art](../../assets/generated/cards/yellow-item.svg) | Category frame exists; unique item illustration is missing. |
| req-card-item-yellow-card-back | Yellow item cards | card-back | base-game | critical | template-only | yes | [art](../../assets/generated/cards/yellow-item.svg) | Functional category frame; unique item illustration is missing. |
| req-card-item-yellow-card-front | Yellow item cards | card-front | base-game | critical | template-only | yes | [art](../../assets/generated/cards/yellow-item.svg) | Functional category frame; unique item illustration is missing. |
| req-card-item-yellow-equipment | Yellow item cards | equipment | base-game | critical | template-only | yes | [art](../../assets/generated/cards/yellow-item.svg) | Functional category frame; unique item illustration is missing. |
| req-card-item-yellow-one-use | Yellow item cards | one-use | base-game | critical | template-only | yes | [art](../../assets/generated/cards/yellow-item.svg) | Functional category frame; unique item illustration is missing. |
| req-card-item-yellow-tactical-belt | Yellow item cards | tactical-belt | base-game | critical | template-only | yes | [art](../../assets/generated/cards/yellow-item.svg) | Functional category frame; unique item illustration is missing. |

## Character

| ID | Family | Piece | Scope | Priority | Status | Missing art? | Current art | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| req-char-bioexpert-action-card-frame | Bioenhancement Expert | action-card-frame | base-game | critical | missing | yes | — | Not represented in current game data or generated roster. |
| req-char-bioexpert-dashboard | Bioenhancement Expert | dashboard | base-game | critical | missing | yes | — | Not represented in current game data or generated roster. |
| req-char-bioexpert-full-body | Bioenhancement Expert | full-body | base-game | critical | missing | yes | — | Not represented in current game data or generated roster. |
| req-char-bioexpert-model-turnaround | Bioenhancement Expert | model-turnaround | base-game | critical | missing | yes | — | Not represented in current game data or generated roster. |
| req-char-bioexpert-portrait | Bioenhancement Expert | portrait | base-game | critical | missing | yes | — | Not represented in current game data or generated roster. |
| req-char-bioexpert-tactical-token | Bioenhancement Expert | tactical-token | base-game | critical | missing | yes | — | Not represented in current game data or generated roster. |
| req-char-state-active | Character tactical states | active | base-game | critical | complete | no | [art](../../js/render.js) | Rendered with selection/active rings. |
| req-char-state-dead | Character tactical states | dead | base-game | critical | partial | partial | [art](../../js/render.js) · [art2](../../js/ui.js) | State is text/color-redundant; dedicated variant art is missing. |
| req-char-state-disconnected | Character tactical states | disconnected | base-game | critical | partial | partial | [art](../../js/render.js) · [art2](../../js/ui.js) | State is text/color-redundant; dedicated variant art is missing. |
| req-char-state-escaped | Character tactical states | escaped | base-game | critical | partial | partial | [art](../../js/render.js) · [art2](../../js/ui.js) | State is text/color-redundant; dedicated variant art is missing. |
| req-char-state-heavily-injured | Character tactical states | heavily-injured | base-game | critical | partial | partial | [art](../../js/render.js) · [art2](../../js/ui.js) | State is text/color-redundant; dedicated variant art is missing. |
| req-char-state-hidden | Character tactical states | hidden | base-game | critical | missing | yes | — | Dedicated state treatment is missing. |
| req-char-state-injured | Character tactical states | injured | base-game | critical | partial | partial | [art](../../js/render.js) · [art2](../../js/ui.js) | State is text/color-redundant; dedicated variant art is missing. |
| req-char-state-moved | Character tactical states | moved | base-game | critical | missing | yes | — | Dedicated state treatment is missing. |
| req-char-state-selected | Character tactical states | selected | base-game | critical | complete | no | [art](../../js/render.js) | Rendered with selection/active rings. |
| req-char-engineer-action-card-frame | Combat Engineer | action-card-frame | base-game | critical | template-only | yes | [art](../../assets/generated/cards/action.svg) | Shared functional frame; unique class treatment is missing. |
| req-char-engineer-dashboard | Combat Engineer | dashboard | base-game | critical | partial | partial | [art](../../assets/generated/characters/combatEngineer.svg) | Functional dashboard uses the portrait; unique dashboard scene is not authored. |
| req-char-engineer-full-body | Combat Engineer | full-body | base-game | critical | missing | yes | — | Unique authored character art is required. |
| req-char-engineer-model-turnaround | Combat Engineer | model-turnaround | base-game | critical | missing | yes | — | Unique authored character art is required. |
| game-char-combatEngineer-portrait | Combat Engineer | portrait | base-game | critical | complete | no | [art](../../assets/generated/characters/combatEngineer.svg) | Concrete current-roster asset. |
| req-char-engineer-portrait | Combat Engineer | portrait | base-game | critical | complete | no | [art](../../assets/generated/characters/combatEngineer.svg) | Original class-coded vector asset. |
| game-char-combatEngineer-tactical-token | Combat Engineer | tactical-token | base-game | critical | complete | no | [art](../../assets/generated/characters/combatEngineer.svg) | Concrete current-roster asset. |
| req-char-engineer-tactical-token | Combat Engineer | tactical-token | base-game | critical | complete | no | [art](../../assets/generated/characters/combatEngineer.svg) | Original class-coded vector asset. |
| game-char-contractor-portrait | Contractor | portrait | base-game | critical | complete | no | [art](../../assets/generated/characters/contractor.svg) | Concrete current-roster asset. |
| game-char-contractor-tactical-token | Contractor | tactical-token | base-game | critical | complete | no | [art](../../assets/generated/characters/contractor.svg) | Concrete current-roster asset. |
| game-char-heavyGunOperator-portrait | Heavy Gun Operator | portrait | base-game | critical | complete | no | [art](../../assets/generated/characters/heavyGunOperator.svg) | Concrete current-roster asset. |
| game-char-heavyGunOperator-tactical-token | Heavy Gun Operator | tactical-token | base-game | critical | complete | no | [art](../../assets/generated/characters/heavyGunOperator.svg) | Concrete current-roster asset. |
| req-char-heavy-gunner-action-card-frame | Heavy Gunner | action-card-frame | base-game | critical | template-only | yes | [art](../../assets/generated/cards/action.svg) | Shared functional frame; unique class treatment is missing. |
| req-char-heavy-gunner-dashboard | Heavy Gunner | dashboard | base-game | critical | partial | partial | [art](../../assets/generated/characters/heavyGunOperator.svg) | Functional dashboard uses the portrait; unique dashboard scene is not authored. |
| req-char-heavy-gunner-full-body | Heavy Gunner | full-body | base-game | critical | missing | yes | — | Unique authored character art is required. |
| req-char-heavy-gunner-model-turnaround | Heavy Gunner | model-turnaround | base-game | critical | missing | yes | — | Unique authored character art is required. |
| req-char-heavy-gunner-portrait | Heavy Gunner | portrait | base-game | critical | complete | no | [art](../../assets/generated/characters/heavyGunOperator.svg) | Original class-coded vector asset. |
| req-char-heavy-gunner-tactical-token | Heavy Gunner | tactical-token | base-game | critical | complete | no | [art](../../assets/generated/characters/heavyGunOperator.svg) | Original class-coded vector asset. |
| req-char-legacy-action-card-frame | Legacy and stretch-goal characters | action-card-frame | future | future | deferred | deferred | — | Not in current base-game scope. |
| req-char-legacy-dashboard | Legacy and stretch-goal characters | dashboard | future | future | deferred | deferred | — | Not in current base-game scope. |
| req-char-legacy-portrait | Legacy and stretch-goal characters | portrait | future | future | deferred | deferred | — | Not in current base-game scope. |
| req-char-legacy-tactical-token | Legacy and stretch-goal characters | tactical-token | future | future | deferred | deferred | — | Not in current base-game scope. |
| req-char-medic-action-card-frame | Medical Support | action-card-frame | base-game | critical | template-only | yes | [art](../../assets/generated/cards/action.svg) | Shared functional frame; unique class treatment is missing. |
| req-char-medic-dashboard | Medical Support | dashboard | base-game | critical | partial | partial | [art](../../assets/generated/characters/medicalSupport.svg) | Functional dashboard uses the portrait; unique dashboard scene is not authored. |
| req-char-medic-full-body | Medical Support | full-body | base-game | critical | missing | yes | — | Unique authored character art is required. |
| req-char-medic-model-turnaround | Medical Support | model-turnaround | base-game | critical | missing | yes | — | Unique authored character art is required. |
| game-char-medicalSupport-portrait | Medical Support | portrait | base-game | critical | complete | no | [art](../../assets/generated/characters/medicalSupport.svg) | Concrete current-roster asset. |
| req-char-medic-portrait | Medical Support | portrait | base-game | critical | complete | no | [art](../../assets/generated/characters/medicalSupport.svg) | Original class-coded vector asset. |
| game-char-medicalSupport-tactical-token | Medical Support | tactical-token | base-game | critical | complete | no | [art](../../assets/generated/characters/medicalSupport.svg) | Concrete current-roster asset. |
| req-char-medic-tactical-token | Medical Support | tactical-token | base-game | critical | complete | no | [art](../../assets/generated/characters/medicalSupport.svg) | Original class-coded vector asset. |
| req-char-officer-action-card-frame | Officer | action-card-frame | base-game | critical | template-only | yes | [art](../../assets/generated/cards/action.svg) | Shared functional frame; unique class treatment is missing. |
| req-char-officer-dashboard | Officer | dashboard | base-game | critical | partial | partial | [art](../../assets/generated/characters/officer.svg) | Functional dashboard uses the portrait; unique dashboard scene is not authored. |
| req-char-officer-full-body | Officer | full-body | base-game | critical | missing | yes | — | Unique authored character art is required. |
| req-char-officer-model-turnaround | Officer | model-turnaround | base-game | critical | missing | yes | — | Unique authored character art is required. |
| game-char-officer-portrait | Officer | portrait | base-game | critical | complete | no | [art](../../assets/generated/characters/officer.svg) | Concrete current-roster asset. |
| req-char-officer-portrait | Officer | portrait | base-game | critical | complete | no | [art](../../assets/generated/characters/officer.svg) | Original class-coded vector asset. |
| game-char-officer-tactical-token | Officer | tactical-token | base-game | critical | complete | no | [art](../../assets/generated/characters/officer.svg) | Concrete current-roster asset. |
| req-char-officer-tactical-token | Officer | tactical-token | base-game | critical | complete | no | [art](../../assets/generated/characters/officer.svg) | Original class-coded vector asset. |
| req-player-color-blue | Player identity colors | blue | base-game | critical | complete | no | [art](../../assets/generated/ui-symbols.svg) | Semantic color mapping with text/icon redundancy. |
| req-player-color-green | Player identity colors | green | base-game | critical | complete | no | [art](../../assets/generated/ui-symbols.svg) | Semantic color mapping with text/icon redundancy. |
| req-player-color-purple | Player identity colors | purple | base-game | critical | complete | no | [art](../../assets/generated/ui-symbols.svg) | Semantic color mapping with text/icon redundancy. |
| req-player-color-red | Player identity colors | red | base-game | critical | complete | no | [art](../../assets/generated/ui-symbols.svg) | Semantic color mapping with text/icon redundancy. |
| req-player-color-yellow | Player identity colors | yellow | base-game | critical | complete | no | [art](../../assets/generated/ui-symbols.svg) | Semantic color mapping with text/icon redundancy. |
| req-char-recon-action-card-frame | Recon | action-card-frame | base-game | critical | template-only | yes | [art](../../assets/generated/cards/action.svg) | Shared functional frame; unique class treatment is missing. |
| req-char-recon-dashboard | Recon | dashboard | base-game | critical | partial | partial | [art](../../assets/generated/characters/recon.svg) | Functional dashboard uses the portrait; unique dashboard scene is not authored. |
| req-char-recon-full-body | Recon | full-body | base-game | critical | missing | yes | — | Unique authored character art is required. |
| req-char-recon-model-turnaround | Recon | model-turnaround | base-game | critical | missing | yes | — | Unique authored character art is required. |
| game-char-recon-portrait | Recon | portrait | base-game | critical | complete | no | [art](../../assets/generated/characters/recon.svg) | Concrete current-roster asset. |
| req-char-recon-portrait | Recon | portrait | base-game | critical | complete | no | [art](../../assets/generated/characters/recon.svg) | Original class-coded vector asset. |
| game-char-recon-tactical-token | Recon | tactical-token | base-game | critical | complete | no | [art](../../assets/generated/characters/recon.svg) | Concrete current-roster asset. |
| req-char-recon-tactical-token | Recon | tactical-token | base-game | critical | complete | no | [art](../../assets/generated/characters/recon.svg) | Original class-coded vector asset. |
| req-char-sharpshooter-action-card-frame | Sharpshooter | action-card-frame | future | future | deferred | deferred | — | Not in current base-game scope. |
| req-char-sharpshooter-dashboard | Sharpshooter | dashboard | future | future | deferred | deferred | — | Not in current base-game scope. |
| req-char-sharpshooter-full-body | Sharpshooter | full-body | future | future | deferred | deferred | — | Not in current base-game scope. |
| req-char-sharpshooter-model-turnaround | Sharpshooter | model-turnaround | future | future | deferred | deferred | — | Not in current base-game scope. |
| req-char-sharpshooter-portrait | Sharpshooter | portrait | future | future | deferred | deferred | — | Not in current base-game scope. |
| req-char-sharpshooter-tactical-token | Sharpshooter | tactical-token | future | future | deferred | deferred | — | Not in current base-game scope. |
| req-char-uav-action-card-frame | UAV Operator | action-card-frame | future | future | deferred | deferred | — | Not in current base-game scope. |
| req-char-uav-dashboard | UAV Operator | dashboard | future | future | deferred | deferred | — | Not in current base-game scope. |
| req-char-uav-drone | UAV Operator | drone | future | future | deferred | deferred | — | Not in current base-game scope. |
| req-char-uav-full-body | UAV Operator | full-body | future | future | deferred | deferred | — | Not in current base-game scope. |
| req-char-uav-model-turnaround | UAV Operator | model-turnaround | future | future | deferred | deferred | — | Not in current base-game scope. |
| req-char-uav-portrait | UAV Operator | portrait | future | future | deferred | deferred | — | Not in current base-game scope. |
| req-char-uav-tactical-token | UAV Operator | tactical-token | future | future | deferred | deferred | — | Not in current base-game scope. |

## Dashboard

| ID | Family | Piece | Scope | Priority | Status | Missing art? | Current art | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| req-dashboard-character-ammo | Character dashboard | ammo | base-game | critical | partial | partial | [art](../../js/ui.js) · [art2](../../css/style.css) | Functional responsive dashboard; unique illustrated surface variants remain. |
| req-dashboard-character-backpack | Character dashboard | backpack | base-game | critical | partial | partial | [art](../../js/ui.js) · [art2](../../css/style.css) | Functional responsive dashboard; unique illustrated surface variants remain. |
| req-dashboard-character-hand-slots | Character dashboard | hand-slots | base-game | critical | partial | partial | [art](../../js/ui.js) · [art2](../../css/style.css) | Functional responsive dashboard; unique illustrated surface variants remain. |
| req-dashboard-character-health-track | Character dashboard | health-track | base-game | critical | partial | partial | [art](../../js/ui.js) · [art2](../../css/style.css) | Functional responsive dashboard; unique illustrated surface variants remain. |
| req-dashboard-character-oxygen | Character dashboard | oxygen | base-game | critical | partial | partial | [art](../../js/ui.js) · [art2](../../css/style.css) | Functional responsive dashboard; unique illustrated surface variants remain. |
| req-dashboard-character-portrait | Character dashboard | portrait | base-game | critical | partial | partial | [art](../../js/ui.js) · [art2](../../css/style.css) | Functional responsive dashboard; unique illustrated surface variants remain. |
| req-dashboard-character-tactical-belt | Character dashboard | tactical-belt | base-game | critical | partial | partial | [art](../../js/ui.js) · [art2](../../css/style.css) | Functional responsive dashboard; unique illustrated surface variants remain. |
| req-dashboard-character-wounds | Character dashboard | wounds | base-game | critical | partial | partial | [art](../../js/ui.js) · [art2](../../css/style.css) | Functional responsive dashboard; unique illustrated surface variants remain. |
| req-dashboard-team-lander | Shared mission/board dashboard | lander | base-game | high | partial | partial | [art](../../js/ui.js) · [art2](../../css/style.css) | Functional responsive dashboard; unique illustrated surface variants remain. |
| req-dashboard-team-life-support | Shared mission/board dashboard | life-support | base-game | high | partial | partial | [art](../../js/ui.js) · [art2](../../css/style.css) | Functional responsive dashboard; unique illustrated surface variants remain. |
| req-dashboard-team-objectives | Shared mission/board dashboard | objectives | base-game | high | partial | partial | [art](../../js/ui.js) · [art2](../../css/style.css) | Functional responsive dashboard; unique illustrated surface variants remain. |
| req-dashboard-team-phase | Shared mission/board dashboard | phase | base-game | high | partial | partial | [art](../../js/ui.js) · [art2](../../css/style.css) | Functional responsive dashboard; unique illustrated surface variants remain. |
| req-dashboard-team-reactor | Shared mission/board dashboard | reactor | base-game | high | partial | partial | [art](../../js/ui.js) · [art2](../../css/style.css) | Functional responsive dashboard; unique illustrated surface variants remain. |
| req-dashboard-team-round | Shared mission/board dashboard | round | base-game | high | partial | partial | [art](../../js/ui.js) · [art2](../../css/style.css) | Functional responsive dashboard; unique illustrated surface variants remain. |

## Dice

| ID | Family | Piece | Scope | Priority | Status | Missing art? | Current art | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| req-dice-combat-all-faces | Combat dice | all faces | base-game | critical | missing | yes | — | Dedicated die-face and animation art is missing. |
| req-dice-combat-hit | Combat dice | hit | base-game | critical | missing | yes | — | Dedicated die-face and animation art is missing. |
| req-dice-combat-miss | Combat dice | miss | base-game | critical | missing | yes | — | Dedicated die-face and animation art is missing. |
| req-dice-combat-roll-animation | Combat dice | roll-animation | base-game | critical | missing | yes | — | Dedicated die-face and animation art is missing. |
| req-dice-combat-special | Combat dice | special | base-game | critical | missing | yes | — | Dedicated die-face and animation art is missing. |
| req-dice-noise-all-faces | Noise die | all faces | base-game | critical | missing | yes | — | Dedicated die-face and animation art is missing. |
| req-dice-noise-roll-animation | Noise die | roll-animation | base-game | critical | missing | yes | — | Dedicated die-face and animation art is missing. |

## Entity

| ID | Family | Piece | Scope | Priority | Status | Missing art? | Current art | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| req-corpses-body-token | Corpses and casualties | body-token | base-game | medium | missing | yes | — | No current production art is linked. |
| req-corpses-intruder-corpses | Corpses and casualties | intruder-corpses | base-game | medium | missing | yes | — | No current production art is linked. |
| req-corpses-marine-corpses | Corpses and casualties | marine-corpses | base-game | medium | missing | yes | — | No current production art is linked. |
| req-intruder-eggs-destroyed-nest | Eggs and Nest | destroyed-nest | base-game | high | missing | yes | — | No current production art is linked. |
| req-intruder-eggs-egg-model | Eggs and Nest | egg-model | base-game | high | missing | yes | — | No current production art is linked. |
| req-intruder-eggs-egg-token | Eggs and Nest | egg-token | base-game | high | missing | yes | — | No current production art is linked. |
| req-intruder-eggs-nest-damage | Eggs and Nest | nest-damage | base-game | high | missing | yes | — | No current production art is linked. |
| req-intruder-eggs-nest-room | Eggs and Nest | nest-room | base-game | high | complete | no | [art](../../assets/generated/rooms/nest.svg) | Original Nest room plate. |
| req-insider-character | Insider | character | future | future | deferred | deferred | — | Not in current base-game scope. |
| req-insider-iconography | Insider | iconography | future | future | deferred | deferred | — | Not in current base-game scope. |
| req-insider-infection-state | Insider | infection-state | future | future | deferred | deferred | — | Not in current base-game scope. |
| req-insider-tokens | Insider | tokens | future | future | deferred | deferred | — | Not in current base-game scope. |
| game-intruder-larva-silhouette | Larva | silhouette | base-game | critical | complete | no | [art](../../assets/generated/intruders/larva.svg) | Concrete current-roster asset. |
| game-intruder-larva-top-down-token | Larva | top-down-token | base-game | critical | complete | no | [art](../../assets/generated/intruders/larva.svg) | Concrete current-roster asset. |
| req-neoflesh-bag-tokens | Neoflesh Cult | bag-tokens | future | future | deferred | deferred | — | Not in current base-game scope. |
| req-neoflesh-cultist | Neoflesh Cult | cultist | future | future | deferred | deferred | — | Not in current base-game scope. |
| req-neoflesh-delver | Neoflesh Cult | delver | future | future | deferred | deferred | — | Not in current base-game scope. |
| req-neoflesh-exploder | Neoflesh Cult | exploder | future | future | deferred | deferred | — | Not in current base-game scope. |
| req-neoflesh-queen | Neoflesh Cult | queen | future | future | deferred | deferred | — | Not in current base-game scope. |
| req-neoflesh-ranged-delver | Neoflesh Cult | ranged-delver | future | future | deferred | deferred | — | Not in current base-game scope. |
| req-neoflesh-shield-robot-delver | Neoflesh Cult | shield-robot-delver | future | future | deferred | deferred | — | Not in current base-game scope. |
| req-neoflesh-twitchling | Neoflesh Cult | twitchling | future | future | deferred | deferred | — | Not in current base-game scope. |
| req-intruder-primeblood-bag-token | Prime Blood | bag-token | base-game | critical | missing | yes | — | No current production art is linked. |
| req-intruder-primeblood-model | Prime Blood | model | base-game | critical | missing | yes | — | No current production art is linked. |
| req-intruder-primeblood-silhouette | Prime Blood | silhouette | base-game | critical | missing | yes | — | No current production art is linked. |
| req-intruder-primeblood-top-down-token | Prime Blood | top-down-token | base-game | critical | missing | yes | — | No current production art is linked. |
| req-intruder-primeblood-wounded | Prime Blood | wounded | base-game | critical | missing | yes | — | No current production art is linked. |
| req-intruder-adult-bag-token | Primeblood Adult | bag-token | base-game | critical | missing | yes | — | Unique entity art is required. |
| req-intruder-adult-model | Primeblood Adult | model | base-game | critical | missing | yes | — | Unique entity art is required. |
| req-intruder-adult-silhouette | Primeblood Adult | silhouette | base-game | critical | complete | no | [art](../../assets/generated/intruders/adult.svg) | Original tactical silhouette. |
| req-intruder-adult-top-down-token | Primeblood Adult | top-down-token | base-game | critical | complete | no | [art](../../assets/generated/intruders/adult.svg) | Original tactical silhouette. |
| req-intruder-adult-wounded | Primeblood Adult | wounded | base-game | critical | missing | yes | — | Unique entity art is required. |
| req-intruder-drone-bag-token | Primeblood Drone | bag-token | base-game | critical | missing | yes | — | Unique entity art is required. |
| req-intruder-drone-model | Primeblood Drone | model | base-game | critical | missing | yes | — | Unique entity art is required. |
| req-intruder-drone-silhouette | Primeblood Drone | silhouette | base-game | critical | complete | no | [art](../../assets/generated/intruders/drone.svg) | Original tactical silhouette. |
| req-intruder-drone-top-down-token | Primeblood Drone | top-down-token | base-game | critical | complete | no | [art](../../assets/generated/intruders/drone.svg) | Original tactical silhouette. |
| req-intruder-drone-wounded | Primeblood Drone | wounded | base-game | critical | missing | yes | — | Unique entity art is required. |
| req-intruder-queen-bag-token | Primeblood Queen | bag-token | base-game | critical | missing | yes | — | Unique entity art is required. |
| req-intruder-queen-boss-health | Primeblood Queen | boss-health | base-game | critical | partial | partial | [art](../../assets/generated/intruders/queen.svg) | Queen token and hit count exist; dedicated boss board is missing. |
| req-intruder-queen-model | Primeblood Queen | model | base-game | critical | missing | yes | — | Unique entity art is required. |
| req-intruder-queen-silhouette | Primeblood Queen | silhouette | base-game | critical | complete | no | [art](../../assets/generated/intruders/queen.svg) | Original tactical silhouette. |
| req-intruder-queen-top-down-token | Primeblood Queen | top-down-token | base-game | critical | complete | no | [art](../../assets/generated/intruders/queen.svg) | Original tactical silhouette. |
| req-intruder-queen-wounded | Primeblood Queen | wounded | base-game | critical | missing | yes | — | Unique entity art is required. |
| req-sangrevores-iconography | Sangrevores | iconography | future | future | deferred | deferred | — | Not in current base-game scope. |
| req-sangrevores-queen | Sangrevores | queen | future | future | deferred | deferred | — | Not in current base-game scope. |
| req-sangrevores-race-models | Sangrevores | race-models | future | future | deferred | deferred | — | Not in current base-game scope. |
| req-sangrevores-tokens | Sangrevores | tokens | future | future | deferred | deferred | — | Not in current base-game scope. |
| req-robot-active | Security Robot | active | base-game | high | partial | partial | [art](../../assets/generated/ui-symbols.svg#i-robot) | Semantic robot symbol exists; dedicated entity art is missing. |
| req-robot-destroyed | Security Robot | destroyed | base-game | high | missing | yes | — | No current production art is linked. |
| req-robot-inactive | Security Robot | inactive | base-game | high | missing | yes | — | No current production art is linked. |
| req-robot-model | Security Robot | model | base-game | high | missing | yes | — | No current production art is linked. |
| req-robot-portrait | Security Robot | portrait | base-game | high | partial | partial | [art](../../assets/generated/ui-symbols.svg#i-robot) | Semantic robot symbol exists; dedicated entity art is missing. |
| req-robot-top-down-token | Security Robot | top-down-token | base-game | high | missing | yes | — | No current production art is linked. |
| req-uav-active | UAV | active | future | future | deferred | deferred | — | Not in current base-game scope. |
| req-uav-damaged | UAV | damaged | future | future | deferred | deferred | — | Not in current base-game scope. |
| req-uav-model | UAV | model | future | future | deferred | deferred | — | Not in current base-game scope. |
| req-uav-top-down-token | UAV | top-down-token | future | future | deferred | deferred | — | Not in current base-game scope. |
| req-xyrians-iconography | Xyrians | iconography | future | future | deferred | deferred | — | Not in current base-game scope. |
| req-xyrians-queen | Xyrians | queen | future | future | deferred | deferred | — | Not in current base-game scope. |
| req-xyrians-race-models | Xyrians | race-models | future | future | deferred | deferred | — | Not in current base-game scope. |
| req-xyrians-tokens | Xyrians | tokens | future | future | deferred | deferred | — | Not in current base-game scope. |

## Fx

| ID | Family | Piece | Scope | Priority | Status | Missing art? | Current art | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| req-fx-combat-acid | Combat effects | acid | base-game | medium | missing | yes | — | Unique authored presentation/effect art is required. |
| req-fx-combat-blood | Combat effects | blood | base-game | medium | missing | yes | — | Unique authored presentation/effect art is required. |
| req-fx-combat-death | Combat effects | death | base-game | medium | missing | yes | — | Unique authored presentation/effect art is required. |
| req-fx-combat-explosion | Combat effects | explosion | base-game | medium | missing | yes | — | Unique authored presentation/effect art is required. |
| req-fx-combat-impact | Combat effects | impact | base-game | medium | missing | yes | — | Unique authored presentation/effect art is required. |
| req-fx-combat-muzzle-flash | Combat effects | muzzle-flash | base-game | medium | missing | yes | — | Unique authored presentation/effect art is required. |
| req-fx-combat-repel | Combat effects | repel | base-game | medium | missing | yes | — | Unique authored presentation/effect art is required. |
| req-fx-environment-darkness | Environmental effects | darkness | base-game | medium | missing | yes | — | Unique authored presentation/effect art is required. |
| req-fx-environment-emergency-lighting | Environmental effects | emergency-lighting | base-game | medium | missing | yes | — | Unique authored presentation/effect art is required. |
| req-fx-environment-fire | Environmental effects | fire | base-game | medium | missing | yes | — | Unique authored presentation/effect art is required. |
| req-fx-environment-oxygen-failure | Environmental effects | oxygen-failure | base-game | medium | missing | yes | — | Unique authored presentation/effect art is required. |
| req-fx-environment-smoke | Environmental effects | smoke | base-game | medium | missing | yes | — | Unique authored presentation/effect art is required. |
| req-fx-environment-sparks | Environmental effects | sparks | base-game | medium | missing | yes | — | Unique authored presentation/effect art is required. |

## Icon

| ID | Family | Piece | Scope | Priority | Status | Missing art? | Current art | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| req-icon-actions-cautious-move | Action and cost symbols | cautious-move | base-game | critical | complete | no | [art](../../assets/generated/ui-symbols.svg) | Semantic vector symbol and visible text label. |
| req-icon-actions-cost-1 | Action and cost symbols | cost-1 | base-game | critical | missing | yes | — | Dedicated semantic icon is missing. |
| req-icon-actions-cost-2 | Action and cost symbols | cost-2 | base-game | critical | missing | yes | — | Dedicated semantic icon is missing. |
| req-icon-actions-discard-card | Action and cost symbols | discard-card | base-game | critical | missing | yes | — | Dedicated semantic icon is missing. |
| req-icon-actions-melee | Action and cost symbols | melee | base-game | critical | complete | no | [art](../../assets/generated/ui-symbols.svg) | Semantic vector symbol and visible text label. |
| req-icon-actions-move | Action and cost symbols | move | base-game | critical | complete | no | [art](../../assets/generated/ui-symbols.svg) | Semantic vector symbol and visible text label. |
| req-icon-actions-pass | Action and cost symbols | pass | base-game | critical | complete | no | [art](../../assets/generated/ui-symbols.svg) | Semantic vector symbol and visible text label. |
| req-icon-actions-room-action | Action and cost symbols | room-action | base-game | critical | complete | no | [art](../../assets/generated/ui-symbols.svg) | Semantic vector symbol and visible text label. |
| req-icon-actions-search | Action and cost symbols | search | base-game | critical | complete | no | [art](../../assets/generated/ui-symbols.svg) | Semantic vector symbol and visible text label. |
| req-icon-actions-shoot | Action and cost symbols | shoot | base-game | critical | complete | no | [art](../../assets/generated/ui-symbols.svg) | Semantic vector symbol and visible text label. |
| req-icon-entities-adult | Entity silhouettes | adult | base-game | critical | complete | no | [art](../../assets/generated/ui-symbols.svg) | Semantic vector symbol and visible text label. |
| req-icon-entities-character | Entity silhouettes | character | base-game | critical | complete | no | [art](../../assets/generated/ui-symbols.svg) | Semantic vector symbol and visible text label. |
| req-icon-entities-corpse | Entity silhouettes | corpse | base-game | critical | missing | yes | — | Dedicated semantic icon is missing. |
| req-icon-entities-drone | Entity silhouettes | drone | base-game | critical | complete | no | [art](../../assets/generated/ui-symbols.svg) | Semantic vector symbol and visible text label. |
| req-icon-entities-egg | Entity silhouettes | egg | base-game | critical | missing | yes | — | Dedicated semantic icon is missing. |
| req-icon-entities-primeblood | Entity silhouettes | primeblood | base-game | critical | missing | yes | — | Dedicated semantic icon is missing. |
| req-icon-entities-queen | Entity silhouettes | queen | base-game | critical | complete | no | [art](../../assets/generated/ui-symbols.svg) | Semantic vector symbol and visible text label. |
| req-icon-entities-robot | Entity silhouettes | robot | base-game | critical | complete | no | [art](../../assets/generated/ui-symbols.svg) | Semantic vector symbol and visible text label. |
| req-icon-hazards-autodestruction | Hazard symbols | autodestruction | base-game | critical | missing | yes | — | Dedicated semantic icon is missing. |
| req-icon-hazards-contamination | Hazard symbols | contamination | base-game | critical | complete | no | [art](../../assets/generated/ui-symbols.svg) | Semantic vector symbol and visible text label. |
| req-icon-hazards-darkness | Hazard symbols | darkness | base-game | critical | missing | yes | — | Dedicated semantic icon is missing. |
| req-icon-hazards-fire | Hazard symbols | fire | base-game | critical | complete | no | [art](../../assets/generated/ui-symbols.svg) | Semantic vector symbol and visible text label. |
| req-icon-hazards-infected | Hazard symbols | infected | base-game | critical | complete | no | [art](../../assets/generated/ui-symbols.svg) | Semantic vector symbol and visible text label. |
| req-icon-hazards-malfunction | Hazard symbols | malfunction | base-game | critical | complete | no | [art](../../assets/generated/ui-symbols.svg) | Semantic vector symbol and visible text label. |
| req-icon-hazards-noise | Hazard symbols | noise | base-game | critical | complete | no | [art](../../assets/generated/ui-symbols.svg) | Semantic vector symbol and visible text label. |
| req-icon-hazards-suffocation | Hazard symbols | suffocation | base-game | critical | missing | yes | — | Dedicated semantic icon is missing. |
| req-icon-health-death | Health and injury symbols | death | base-game | critical | complete | no | [art](../../assets/generated/ui-symbols.svg) | Semantic vector symbol and visible text label. |
| req-icon-health-heal | Health and injury symbols | heal | base-game | critical | missing | yes | — | Dedicated semantic icon is missing. |
| req-icon-health-health | Health and injury symbols | health | base-game | critical | complete | no | [art](../../assets/generated/ui-symbols.svg) | Semantic vector symbol and visible text label. |
| req-icon-health-heavily-injured | Health and injury symbols | heavily-injured | base-game | critical | missing | yes | — | Dedicated semantic icon is missing. |
| req-icon-health-injured | Health and injury symbols | injured | base-game | critical | missing | yes | — | Dedicated semantic icon is missing. |
| req-icon-health-serious-wound | Health and injury symbols | serious-wound | base-game | critical | complete | no | [art](../../assets/generated/ui-symbols.svg) | Semantic vector symbol and visible text label. |
| req-icon-map-broken-door | Map symbols | broken-door | base-game | critical | missing | yes | — | Dedicated semantic icon is missing. |
| req-icon-map-cannot-break | Map symbols | cannot-break | base-game | critical | missing | yes | — | Dedicated semantic icon is missing. |
| req-icon-map-cannot-secure | Map symbols | cannot-secure | base-game | critical | missing | yes | — | Dedicated semantic icon is missing. |
| req-icon-map-corridor-directions | Map symbols | corridor-directions | base-game | critical | missing | yes | — | Dedicated semantic icon is missing. |
| req-icon-map-door | Map symbols | door | base-game | critical | missing | yes | — | Dedicated semantic icon is missing. |
| req-icon-map-room-types-a-b-c-random | Map symbols | room-types-A-B-C-random | base-game | critical | missing | yes | — | Dedicated semantic icon is missing. |
| req-icon-map-secure | Map symbols | secure | base-game | critical | missing | yes | — | Dedicated semantic icon is missing. |
| req-icon-objectives-escape | Objective and mission symbols | escape | base-game | high | complete | no | [art](../../assets/generated/ui-symbols.svg) | Semantic vector symbol and visible text label. |
| req-icon-objectives-failure | Objective and mission symbols | failure | base-game | high | complete | no | [art](../../assets/generated/ui-symbols.svg) | Semantic vector symbol and visible text label. |
| req-icon-objectives-mission | Objective and mission symbols | mission | base-game | high | complete | no | [art](../../assets/generated/ui-symbols.svg) | Semantic vector symbol and visible text label. |
| req-icon-objectives-private | Objective and mission symbols | private | base-game | high | complete | no | [art](../../assets/generated/ui-symbols.svg) | Semantic vector symbol and visible text label. |
| req-icon-objectives-success | Objective and mission symbols | success | base-game | high | complete | no | [art](../../assets/generated/ui-symbols.svg) | Semantic vector symbol and visible text label. |
| req-icon-objectives-survival | Objective and mission symbols | survival | base-game | high | complete | no | [art](../../assets/generated/ui-symbols.svg) | Semantic vector symbol and visible text label. |
| req-icon-objectives-task | Objective and mission symbols | task | base-game | high | complete | no | [art](../../assets/generated/ui-symbols.svg) | Semantic vector symbol and visible text label. |
| req-icon-resources-ammo | Resource symbols | ammo | base-game | critical | complete | no | [art](../../assets/generated/ui-symbols.svg) | Semantic vector symbol and visible text label. |
| req-icon-resources-backpack | Resource symbols | backpack | base-game | critical | complete | no | [art](../../assets/generated/ui-symbols.svg) | Semantic vector symbol and visible text label. |
| req-icon-resources-computer | Resource symbols | computer | base-game | critical | complete | no | [art](../../assets/generated/ui-symbols.svg) | Semantic vector symbol and visible text label. |
| req-icon-resources-heavy | Resource symbols | heavy | base-game | critical | missing | yes | — | Dedicated semantic icon is missing. |
| req-icon-resources-one-use | Resource symbols | one-use | base-game | critical | missing | yes | — | Dedicated semantic icon is missing. |
| req-icon-resources-oxygen | Resource symbols | oxygen | base-game | critical | complete | no | [art](../../assets/generated/ui-symbols.svg) | Semantic vector symbol and visible text label. |
| req-icon-resources-search | Resource symbols | search | base-game | critical | complete | no | [art](../../assets/generated/ui-symbols.svg) | Semantic vector symbol and visible text label. |
| req-icon-resources-tactical-belt | Resource symbols | tactical-belt | base-game | critical | missing | yes | — | Dedicated semantic icon is missing. |

## Map

| ID | Family | Piece | Scope | Priority | Status | Missing art? | Current art | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| req-corridor-tiles-blocked | Corridor tiles | blocked | base-game | critical | partial | partial | [art](../../js/render.js) | Functional geometry/state exists only in generalized form. |
| req-corridor-tiles-corner | Corridor tiles | corner | base-game | critical | partial | partial | [art](../../js/render.js) | Functional geometry/state exists only in generalized form. |
| req-corridor-tiles-dark | Corridor tiles | dark | base-game | critical | partial | partial | [art](../../js/render.js) | Functional geometry/state exists only in generalized form. |
| req-corridor-tiles-explored | Corridor tiles | explored | base-game | critical | complete | no | [art](../../js/render.js) | Procedural tactical corridor rendering. |
| req-corridor-tiles-junction | Corridor tiles | junction | base-game | critical | partial | partial | [art](../../js/render.js) | Functional geometry/state exists only in generalized form. |
| req-corridor-tiles-lit | Corridor tiles | lit | base-game | critical | complete | no | [art](../../js/render.js) | Procedural tactical corridor rendering. |
| req-corridor-tiles-noisy | Corridor tiles | noisy | base-game | critical | complete | no | [art](../../js/render.js) | Procedural tactical corridor rendering. |
| req-corridor-tiles-occupied | Corridor tiles | occupied | base-game | critical | complete | no | [art](../../js/render.js) | Procedural tactical corridor rendering. |
| req-corridor-tiles-straight | Corridor tiles | straight | base-game | critical | complete | no | [art](../../js/render.js) | Procedural tactical corridor rendering. |
| req-corridor-tiles-unexplored | Corridor tiles | unexplored | base-game | critical | missing | yes | — | Dedicated corridor treatment is missing. |
| req-landing-zone-deployment-zones | Landing Zone | deployment-zones | base-game | critical | partial | partial | [art](../../assets/generated/rooms/landingZone.svg) | Player placement works; dedicated deployment-zone art is missing. |
| req-landing-zone-escape-status | Landing Zone | escape-status | base-game | critical | missing | yes | — | No current production art is linked. |
| req-landing-zone-lander-status | Landing Zone | lander-status | base-game | critical | missing | yes | — | No current production art is linked. |
| req-landing-zone-room-art | Landing Zone | room-art | base-game | critical | complete | no | [art](../../assets/generated/rooms/landingZone.svg) | Original room plate. |
| req-corridor-floor-kit-conduits | Modular corridor material kit | conduits | base-game | critical | complete | no | [art](../../assets/generated/board/facility-playmat.svg) | Original geometric material vocabulary. |
| req-corridor-floor-kit-damage | Modular corridor material kit | damage | base-game | critical | missing | yes | — | Dedicated material variant is missing. |
| req-corridor-floor-kit-grating | Modular corridor material kit | grating | base-game | critical | complete | no | [art](../../assets/generated/board/facility-playmat.svg) | Original geometric material vocabulary. |
| req-corridor-floor-kit-hazard-stripes | Modular corridor material kit | hazard-stripes | base-game | critical | complete | no | [art](../../assets/generated/board/facility-playmat.svg) | Original geometric material vocabulary. |
| req-corridor-floor-kit-metal-panels | Modular corridor material kit | metal-panels | base-game | critical | complete | no | [art](../../assets/generated/board/facility-playmat.svg) | Original geometric material vocabulary. |
| req-corridor-floor-kit-rails | Modular corridor material kit | rails | base-game | critical | complete | no | [art](../../assets/generated/board/facility-playmat.svg) | Original geometric material vocabulary. |
| req-room-floor-kit-conduits | Modular room floor material kit | conduits | base-game | critical | complete | no | [art](../../assets/generated/board/facility-playmat.svg) | Original geometric material vocabulary. |
| req-room-floor-kit-damage | Modular room floor material kit | damage | base-game | critical | missing | yes | — | Dedicated material variant is missing. |
| req-room-floor-kit-decals | Modular room floor material kit | decals | base-game | critical | complete | no | [art](../../assets/generated/board/facility-playmat.svg) | Original geometric material vocabulary. |
| req-room-floor-kit-grating | Modular room floor material kit | grating | base-game | critical | complete | no | [art](../../assets/generated/board/facility-playmat.svg) | Original geometric material vocabulary. |
| req-room-floor-kit-hazard-stripes | Modular room floor material kit | hazard-stripes | base-game | critical | complete | no | [art](../../assets/generated/board/facility-playmat.svg) | Original geometric material vocabulary. |
| req-room-floor-kit-metal-panels | Modular room floor material kit | metal-panels | base-game | critical | complete | no | [art](../../assets/generated/board/facility-playmat.svg) | Original geometric material vocabulary. |
| req-room-floor-kit-stains | Modular room floor material kit | stains | base-game | critical | missing | yes | — | Dedicated material variant is missing. |
| req-room-floor-kit-vents | Modular room floor material kit | vents | base-game | critical | complete | no | [art](../../assets/generated/board/facility-playmat.svg) | Original geometric material vocabulary. |
| req-room-tiles-random-disabled | Random room tiles | disabled | base-game | critical | partial | partial | [art](../../js/render.js) | Disabled state relies on subdued rendering rather than unique art. |
| req-room-tiles-random-explored | Random room tiles | explored | base-game | critical | complete | no | [art](../../js/render.js) | Shared tactical room-state rendering. |
| req-room-tiles-random-legal-target | Random room tiles | legal-target | base-game | critical | complete | no | [art](../../js/render.js) | Shared tactical room-state rendering. |
| req-room-tiles-random-selected | Random room tiles | selected | base-game | critical | complete | no | [art](../../js/render.js) | Shared tactical room-state rendering. |
| req-room-tiles-random-unexplored | Random room tiles | unexplored | base-game | critical | complete | no | [art](../../js/render.js) | Shared tactical room-state rendering. |
| req-room-walls-broken-door | Room and corridor boundary treatment | broken-door | base-game | critical | missing | yes | — | Dedicated door-state art is missing. |
| req-room-walls-closed-door | Room and corridor boundary treatment | closed-door | base-game | critical | missing | yes | — | Dedicated door-state art is missing. |
| req-room-walls-doorway | Room and corridor boundary treatment | doorway | base-game | critical | complete | no | [art](../../js/render.js) | Procedural flat-top hexagonal boundaries and passages. |
| req-room-walls-open-passage | Room and corridor boundary treatment | open-passage | base-game | critical | complete | no | [art](../../js/render.js) | Procedural flat-top hexagonal boundaries and passages. |
| req-room-walls-sealed-door | Room and corridor boundary treatment | sealed-door | base-game | critical | missing | yes | — | Dedicated door-state art is missing. |
| req-room-walls-wall | Room and corridor boundary treatment | wall | base-game | critical | complete | no | [art](../../js/render.js) | Procedural flat-top hexagonal boundaries and passages. |
| game-room-airlock | Room plates | Airlock | base-game | critical | complete | no | [art](../../assets/generated/rooms/airlock.svg) | Concrete room plate from current game data. |
| game-room-armory | Room plates | Armory | base-game | critical | complete | no | [art](../../assets/generated/rooms/armory.svg) | Concrete room plate from current game data. |
| game-room-commsRoom | Room plates | Communications Room | base-game | critical | complete | no | [art](../../assets/generated/rooms/commsRoom.svg) | Concrete room plate from current game data. |
| game-room-coolingSystem | Room plates | Cooling System | base-game | critical | complete | no | [art](../../assets/generated/rooms/coolingSystem.svg) | Concrete room plate from current game data. |
| game-room-drillingRoom | Room plates | Drilling Room | base-game | critical | complete | no | [art](../../assets/generated/rooms/drillingRoom.svg) | Concrete room plate from current game data. |
| game-room-engineRoom | Room plates | Engine Room | base-game | critical | complete | no | [art](../../assets/generated/rooms/engineRoom.svg) | Concrete room plate from current game data. |
| game-room-escapeShuttle | Room plates | Escape Shuttle | base-game | critical | complete | no | [art](../../assets/generated/rooms/escapeShuttle.svg) | Concrete room plate from current game data. |
| game-room-gunneryRoom | Room plates | Gunnery Room | base-game | critical | complete | no | [art](../../assets/generated/rooms/gunneryRoom.svg) | Concrete room plate from current game data. |
| game-room-hibernatorium | Room plates | Hibernatorium | base-game | critical | complete | no | [art](../../assets/generated/rooms/hibernatorium.svg) | Concrete room plate from current game data. |
| game-room-laboratory | Room plates | Laboratory | base-game | critical | complete | no | [art](../../assets/generated/rooms/laboratory.svg) | Concrete room plate from current game data. |
| game-room-landingZone | Room plates | Landing Zone | base-game | critical | complete | no | [art](../../assets/generated/rooms/landingZone.svg) | Concrete room plate from current game data. |
| game-room-lifeSupportControlA | Room plates | Life Support Control "A" | base-game | critical | complete | no | [art](../../assets/generated/rooms/lifeSupportControlA.svg) | Concrete room plate from current game data. |
| game-room-lifeSupportControlB | Room plates | Life Support Control "B" | base-game | critical | complete | no | [art](../../assets/generated/rooms/lifeSupportControlB.svg) | Concrete room plate from current game data. |
| game-room-lifeSupportControlC | Room plates | Life Support Control "C" | base-game | critical | complete | no | [art](../../assets/generated/rooms/lifeSupportControlC.svg) | Concrete room plate from current game data. |
| game-room-powerGenerator | Room plates | Power Generator | base-game | critical | complete | no | [art](../../assets/generated/rooms/powerGenerator.svg) | Concrete room plate from current game data. |
| game-room-reactor | Room plates | Reactor | base-game | critical | complete | no | [art](../../assets/generated/rooms/reactor.svg) | Concrete room plate from current game data. |
| game-room-serverRoom | Room plates | Server Room | base-game | critical | complete | no | [art](../../assets/generated/rooms/serverRoom.svg) | Concrete room plate from current game data. |
| game-room-shelter | Room plates | Shelter | base-game | critical | complete | no | [art](../../assets/generated/rooms/shelter.svg) | Concrete room plate from current game data. |
| game-room-sprinklersControl | Room plates | Sprinklers Control | base-game | critical | complete | no | [art](../../assets/generated/rooms/sprinklersControl.svg) | Concrete room plate from current game data. |
| game-room-storageRoom | Room plates | Storage Room | base-game | critical | complete | no | [art](../../assets/generated/rooms/storageRoom.svg) | Concrete room plate from current game data. |
| game-room-surgeryRoom | Room plates | Surgery Room | base-game | critical | complete | no | [art](../../assets/generated/rooms/surgeryRoom.svg) | Concrete room plate from current game data. |
| game-room-technicalCorridorEntrance | Room plates | Technical Corridor Entrance | base-game | critical | complete | no | [art](../../assets/generated/rooms/technicalCorridorEntrance.svg) | Concrete room plate from current game data. |
| game-room-nest | Room plates | The Nest | base-game | critical | complete | no | [art](../../assets/generated/rooms/nest.svg) | Concrete room plate from current game data. |
| game-room-wasteDisposal | Room plates | Waste Disposal | base-game | critical | complete | no | [art](../../assets/generated/rooms/wasteDisposal.svg) | Concrete room plate from current game data. |
| req-room-tiles-a-disabled | Section A room tiles | disabled | base-game | critical | partial | partial | [art](../../js/render.js) | Disabled state relies on subdued rendering rather than unique art. |
| req-room-tiles-a-explored | Section A room tiles | explored | base-game | critical | complete | no | [art](../../js/render.js) | Shared tactical room-state rendering. |
| req-room-tiles-a-legal-target | Section A room tiles | legal-target | base-game | critical | complete | no | [art](../../js/render.js) | Shared tactical room-state rendering. |
| req-room-tiles-a-selected | Section A room tiles | selected | base-game | critical | complete | no | [art](../../js/render.js) | Shared tactical room-state rendering. |
| req-room-tiles-a-unexplored | Section A room tiles | unexplored | base-game | critical | complete | no | [art](../../js/render.js) | Shared tactical room-state rendering. |
| req-room-tiles-b-disabled | Section B room tiles | disabled | base-game | critical | partial | partial | [art](../../js/render.js) | Disabled state relies on subdued rendering rather than unique art. |
| req-room-tiles-b-explored | Section B room tiles | explored | base-game | critical | complete | no | [art](../../js/render.js) | Shared tactical room-state rendering. |
| req-room-tiles-b-legal-target | Section B room tiles | legal-target | base-game | critical | complete | no | [art](../../js/render.js) | Shared tactical room-state rendering. |
| req-room-tiles-b-selected | Section B room tiles | selected | base-game | critical | complete | no | [art](../../js/render.js) | Shared tactical room-state rendering. |
| req-room-tiles-b-unexplored | Section B room tiles | unexplored | base-game | critical | complete | no | [art](../../js/render.js) | Shared tactical room-state rendering. |
| req-room-tiles-c-disabled | Section C room tiles | disabled | base-game | critical | partial | partial | [art](../../js/render.js) | Disabled state relies on subdued rendering rather than unique art. |
| req-room-tiles-c-explored | Section C room tiles | explored | base-game | critical | complete | no | [art](../../js/render.js) | Shared tactical room-state rendering. |
| req-room-tiles-c-legal-target | Section C room tiles | legal-target | base-game | critical | complete | no | [art](../../js/render.js) | Shared tactical room-state rendering. |
| req-room-tiles-c-selected | Section C room tiles | selected | base-game | critical | complete | no | [art](../../js/render.js) | Shared tactical room-state rendering. |
| req-room-tiles-c-unexplored | Section C room tiles | unexplored | base-game | critical | complete | no | [art](../../js/render.js) | Shared tactical room-state rendering. |
| req-tactical-grid-corridor-gap | Tactical placement information | corridor-gap | base-game | critical | complete | no | [art](../../js/render.js) | Procedural geometry shared by display and hit testing. |
| req-tactical-grid-hover | Tactical placement information | hover | base-game | critical | complete | no | [art](../../js/render.js) | Procedural geometry shared by display and hit testing. |
| req-tactical-grid-legal-exploration-highlight | Tactical placement information | legal-exploration-highlight | base-game | critical | complete | no | [art](../../js/render.js) | Procedural geometry shared by display and hit testing. |
| req-tactical-grid-legal-move-highlight | Tactical placement information | legal-move-highlight | base-game | critical | complete | no | [art](../../js/render.js) | Procedural geometry shared by display and hit testing. |
| req-tactical-grid-octagonal-room-outline | Tactical placement information | octagonal-room-outline | base-game | critical | complete | no | [art](../../js/render.js) | Procedural geometry shared by display and hit testing. |
| req-tactical-grid-path-preview | Tactical placement information | path-preview | base-game | critical | missing | yes | — | Path-preview art is not implemented. |
| req-tactical-grid-selection | Tactical placement information | selection | base-game | critical | complete | no | [art](../../js/render.js) | Procedural geometry shared by display and hit testing. |

## Presentation

| ID | Family | Piece | Scope | Priority | Status | Missing art? | Current art | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| req-branding-box-art-inspired-key-art | Game presentation | box-art-inspired-key-art | base-game | medium | missing | yes | — | Unique authored presentation/effect art is required. |
| req-branding-credits | Game presentation | credits | base-game | medium | missing | yes | — | Unique authored presentation/effect art is required. |
| req-branding-loading | Game presentation | loading | base-game | medium | missing | yes | — | Unique authored presentation/effect art is required. |
| req-branding-logo | Game presentation | logo | base-game | medium | missing | yes | — | Unique authored presentation/effect art is required. |
| req-branding-title-screen | Game presentation | title-screen | base-game | medium | missing | yes | — | Unique authored presentation/effect art is required. |

## Token

| ID | Family | Piece | Scope | Priority | Status | Missing art? | Current art | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| req-token-ammo-ammo-types | Ammo markers | ammo-types | base-game | high | missing | yes | — | Dedicated token art is missing. |
| req-token-ammo-empty | Ammo markers | empty | base-game | high | missing | yes | — | Dedicated token art is missing. |
| req-token-ammo-loaded | Ammo markers | loaded | base-game | high | missing | yes | — | Dedicated token art is missing. |
| req-token-doors-broken | Door components | broken | base-game | critical | missing | yes | — | Dedicated token art is missing. |
| req-token-doors-closed | Door components | closed | base-game | critical | missing | yes | — | Dedicated token art is missing. |
| req-token-doors-open | Door components | open | base-game | critical | missing | yes | — | Dedicated token art is missing. |
| req-token-doors-sealed | Door components | sealed | base-game | critical | missing | yes | — | Dedicated token art is missing. |
| req-token-fire-normal | Fire markers | normal | base-game | critical | complete | no | [art](../../assets/generated/ui-symbols.svg) | Procedural marker uses the shared vector symbol. |
| req-token-fire-room-placement | Fire markers | room-placement | base-game | critical | complete | no | [art](../../assets/generated/ui-symbols.svg) | Procedural marker uses the shared vector symbol. |
| req-token-fire-spreading | Fire markers | spreading | base-game | critical | complete | no | [art](../../assets/generated/ui-symbols.svg) | Procedural marker uses the shared vector symbol. |
| req-token-health-character-health | Health/hit markers | character-health | base-game | high | partial | partial | [art](../../assets/generated/ui-symbols.svg) · [art2](../../js/ui.js) | Functional HUD/label exists; dedicated physical-style token is missing. |
| req-token-health-intruder-hit | Health/hit markers | intruder-hit | base-game | high | partial | partial | [art](../../assets/generated/ui-symbols.svg) · [art2](../../js/ui.js) | Functional HUD/label exists; dedicated physical-style token is missing. |
| req-token-health-queen-health | Health/hit markers | queen-health | base-game | high | partial | partial | [art](../../assets/generated/ui-symbols.svg) · [art2](../../js/ui.js) | Functional HUD/label exists; dedicated physical-style token is missing. |
| req-token-bag-adult | Intruder bag tokens | adult | base-game | critical | missing | yes | — | Dedicated token art is missing. |
| req-token-bag-blank | Intruder bag tokens | blank | base-game | critical | missing | yes | — | Dedicated token art is missing. |
| req-token-bag-drone | Intruder bag tokens | drone | base-game | critical | missing | yes | — | Dedicated token art is missing. |
| req-token-bag-primeblood | Intruder bag tokens | primeblood | base-game | critical | missing | yes | — | Dedicated token art is missing. |
| req-token-bag-queen | Intruder bag tokens | queen | base-game | critical | missing | yes | — | Dedicated token art is missing. |
| req-token-bag-values | Intruder bag tokens | values | base-game | critical | missing | yes | — | Dedicated token art is missing. |
| req-token-malfunction-normal | Malfunction markers | normal | base-game | critical | complete | no | [art](../../assets/generated/ui-symbols.svg) | Procedural marker uses the shared vector symbol. |
| req-token-malfunction-room-placement | Malfunction markers | room-placement | base-game | critical | complete | no | [art](../../assets/generated/ui-symbols.svg) | Procedural marker uses the shared vector symbol. |
| req-token-noise-accumulated | Noise markers | accumulated | base-game | critical | complete | no | [art](../../assets/generated/ui-symbols.svg) | Procedural marker uses the shared vector symbol. |
| req-token-noise-corridor-placement | Noise markers | corridor-placement | base-game | critical | complete | no | [art](../../assets/generated/ui-symbols.svg) | Procedural marker uses the shared vector symbol. |
| req-token-noise-single | Noise markers | single | base-game | critical | complete | no | [art](../../assets/generated/ui-symbols.svg) | Procedural marker uses the shared vector symbol. |
| req-token-objective-choice | Objective/mission markers | choice | base-game | high | partial | partial | [art](../../assets/generated/ui-symbols.svg) · [art2](../../js/ui.js) | Functional HUD/label exists; dedicated physical-style token is missing. |
| req-token-objective-mission-task | Objective/mission markers | mission-task | base-game | high | partial | partial | [art](../../assets/generated/ui-symbols.svg) · [art2](../../js/ui.js) | Functional HUD/label exists; dedicated physical-style token is missing. |
| req-token-objective-progress | Objective/mission markers | progress | base-game | high | partial | partial | [art](../../assets/generated/ui-symbols.svg) · [art2](../../js/ui.js) | Functional HUD/label exists; dedicated physical-style token is missing. |
| req-token-round-first-player-robot | Round/phase/first-player markers | first-player-robot | base-game | high | partial | partial | [art](../../assets/generated/ui-symbols.svg) · [art2](../../js/ui.js) | Functional HUD/label exists; dedicated physical-style token is missing. |
| req-token-round-phase | Round/phase/first-player markers | phase | base-game | high | partial | partial | [art](../../assets/generated/ui-symbols.svg) · [art2](../../js/ui.js) | Functional HUD/label exists; dedicated physical-style token is missing. |
| req-token-round-round | Round/phase/first-player markers | round | base-game | high | partial | partial | [art](../../assets/generated/ui-symbols.svg) · [art2](../../js/ui.js) | Functional HUD/label exists; dedicated physical-style token is missing. |
| req-token-secure-single | Secure markers | single | base-game | high | complete | no | [art](../../assets/generated/ui-symbols.svg) | Procedural marker uses the shared vector symbol. |
| req-token-secure-stacked | Secure markers | stacked | base-game | high | complete | no | [art](../../assets/generated/ui-symbols.svg) | Procedural marker uses the shared vector symbol. |

## Ui

| ID | Family | Piece | Scope | Priority | Status | Missing art? | Current art | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| req-ui-legibility-colorblind-redundancy | Accessibility overlays | colorblind-redundancy | base-game | critical | complete | no | [art](../../css/style.css) | Text/icon redundancy and interactive states are implemented. |
| req-ui-legibility-disabled | Accessibility overlays | disabled | base-game | critical | complete | no | [art](../../css/style.css) | Text/icon redundancy and interactive states are implemented. |
| req-ui-legibility-focus | Accessibility overlays | focus | base-game | critical | complete | no | [art](../../css/style.css) | Text/icon redundancy and interactive states are implemented. |
| req-ui-legibility-high-contrast | Accessibility overlays | high-contrast | base-game | critical | complete | no | [art](../../css/style.css) | Text/icon redundancy and interactive states are implemented. |
| req-ui-legibility-text-labels | Accessibility overlays | text-labels | base-game | critical | complete | no | [art](../../css/style.css) | Text/icon redundancy and interactive states are implemented. |
| req-ui-panels-cards | HUD and panel surfaces | cards | base-game | critical | complete | no | [art](../../css/style.css) | Original responsive HUD surface. |
| req-ui-panels-log | HUD and panel surfaces | log | base-game | critical | complete | no | [art](../../css/style.css) | Original responsive HUD surface. |
| req-ui-panels-marine-terminal | HUD and panel surfaces | marine-terminal | base-game | critical | complete | no | [art](../../css/style.css) | Original responsive HUD surface. |
| req-ui-panels-modal | HUD and panel surfaces | modal | base-game | critical | complete | no | [art](../../css/style.css) | Original responsive HUD surface. |
| req-ui-panels-phase-banner | HUD and panel surfaces | phase-banner | base-game | critical | complete | no | [art](../../css/style.css) | Original responsive HUD surface. |
| req-ui-panels-players | HUD and panel surfaces | players | base-game | critical | complete | no | [art](../../css/style.css) | Original responsive HUD surface. |
| req-ui-panels-tooltip | HUD and panel surfaces | tooltip | base-game | critical | missing | yes | — | Dedicated tooltip surface is missing. |
