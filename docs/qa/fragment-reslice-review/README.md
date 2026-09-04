# Five-fragment reslice proposal — owner review

**Status:** proposal only; no canonical audit fragment, manifest entry, source-extraction record, or concise-corpus rule has been changed.

**Prepared:** 2026-09-04

## Decision requested

Approve, reject, or amend each proposed action:

| Proposal | Current audit ID | Defect | Proposed action after approval |
|---|---|---|---|
| P1 | `OBJ-29` | The official help-sheet occurrence is physically occluded; the slice includes hidden PDF text-layer metadata as though it were reviewable source content. | Retire this occurrence from the rules-verification manifest. Keep its existing source-extraction provenance record unchanged. Do not infer or install the hidden rule text. |
| P2 | `OBJ-31` | Same defect: no complete operative assertion is visible. | Same treatment as P1. |
| P3 | `OBJ-32` | Same defect; even the visible top-instruction badge is only partial. | Same treatment as P1. |
| P4 | `CARD-character-heavy-gun-operator-character-heavy-gun-operator-045_cards-card-13.png` | The canonical slice stops after the title, although its own source image contains a complete face. | Replace the slice with the full pixel-bound Demolition record in `proposed/...card-13.png.txt`, then send that one fragment to one fresh verifier. Preserve its selector-gap/source-variant status; do not assert it as a selected physical copy. |
| P5 | `CARD-game-missionTaskDeck-game-missionTaskDeck-160_cards-card-08.png` | The slice omits the player threshold, footer, literal icon morphology, and explicit conflict with the official same-title card. | Replace it with the full source-variant slice in `proposed/...card-08.png.txt`, then send that one fragment to one fresh verifier. Keep the unmatched badge unresolved and preserve the official/TTS conflict. |

**Recommended approval:** P1–P5 as written. If approved, the three non-verifiable official occurrences leave the verification manifest, reducing its total from 2,129 to 2,126. The source-extraction records remain intact. P4 and P5 remain within that 2,126-entry manifest and receive one fresh verdict each.

An alternative for P1–P3 is to keep the visible-only remnants in the manifest. That preserves a 2,129 count but creates vacuous reviews of fragments that contain no complete rule. This packet does not recommend that alternative.

## Why P1–P3 must not be completed

The official Objectives Sheet page 2 renders to 3,438 × 3,438 at 300 DPI with SHA-256 `ecf8bea81aaea62326f8be6f5619c7573e7d7cecb9d576554bfa5ca35be29f04`. Its upper-left private-objective cards are physically stacked. The extraction authority records:

- `AN OLD FEUD`: two later cards cover the right portion; threshold, icons, most title, substantial conditions, and footer are not directly visible.
- `GREENER PASTURES`: three later cards cover the right portion; the same material fields are not directly visible.
- `HOSTILE TAKEOVER`: the front `CORPORATE CONTRACT` card covers the title, threshold, condition icons, most conditions, and footer; only part of the top-instruction badge is visible.

The PDF text layer supplies title/threshold/condition locators, but `objective-help-sheet.json` already labels them `occluded metadata only; not visible face transcription`. They are provenance, not visible card text. The proposed records under `proposed/` show the complete visible boundary and therefore why no rules-audit replacement can honestly be cut.

Independent TTS card variants exist and are already separate audit records:

- `...objectiveMissonDeck-162_cards-card-14.png` — `AN OLD FEUD`
- `...objectiveMissonDeck-162_cards-card-13.png` — `GREENER PASTURES`
- `...objectiveMissonDeck-162_cards-card-15.png` — `HOSTILE TAKEOVER`

Those variants use different wording from the official PDF metadata and remain independently preserved. They cannot be substituted into the physically occluded official occurrences.

## P4 evidence

Source image:

- Path: `assets/tts-mod/extract/v2-dl/tree/cards/character/heavy-gun-operator-045_cards/card-13.png`
- SHA-256: `b3b209538a4ac8554ae6e5230f4a98b1fa1ff3bd8f89b3ccfbee53d115997e9e`
- Dimensions: 1,052 × 1,433

The complete visible face reads:

> DEMOLITION
> Remove 1 Door.
> OR
> Place a [malfunction] in your Room.
> HEAVY GUN OPERATOR

The source-bound selected extraction records a native `openai-codex:gpt-5.6-sol` Max blind/adjudication pair. Its icon comparison matches the cog-like glyph to the authoritative `malfunction` crop by the same eight broad squared teeth, annular body, and circular central void. The selected evidence remains `promotionDecision: defer` because physical selector/promotion gates are separate; the reslice does not erase that boundary.

## P5 evidence and conflict

Source image:

- Path: `assets/tts-mod/extract/v2-dl/tree/cards/game/missionTaskDeck-160_cards/card-08.png`
- SHA-256: `e3f3266defff5ad4ade7327a85ebc8878d10bcd18ad85816212c60300472ad68`
- Dimensions: 1,136 × 1,525

The visible face contains:

- a source-local person-over-rings glyph followed by `2+`;
- title `FACILITY RESTART`;
- `The Hibernatorium must be [hibernatorium-active]`;
- `and at least 2 Life Support / Systems must be [unresolved source-local badge].`;
- `AND`;
- `The Facility cannot be destroyed.`;
- footer `MISSION TASK`.

The unresolved badge is fully present in this source image. It is a horizontal cyan-and-white bilateral badge with rounded white end masses, a cyan connector, and a narrow upright central slot/tab. Prior Sol Max comparison records it as a no-match to the official Life Support active glyph; the inactive reference is also a different base morphology with a diagonal slash. The proposal therefore preserves a literal unresolved token rather than guessing `active` or `inactive`.

This TTS face materially conflicts with official Objective Help Sheet unit `P1-MT-FACILITY-RESTART`, which instead requires the Hibernatorium state (by Life Support Control C) **and** the Reactor to be shut down. The two source variants must remain separate.

The earlier exact-source blocker at “Systems must be” belongs to a different prototype source, `assets/tts-mod/extract/v2-dl/tree/cards/game/missionTaskDeck-023.png` (SHA-256 `eaa728ca02c48c33e27e99fe2ef58c9668e7b8532316d3c6d3c93248a86b627a`). It must not be conflated with this generated `card-08.png` face, where a source-local badge is visibly present.

## Exact effect of approval

Approval authorizes only:

1. the manifest/provenance treatment stated in P1–P3;
2. installation of the two proposed replacement slices in P4–P5;
3. one fresh independent verifier verdict for P4 and P5;
4. mechanical reconciliation and status updates.

Approval does **not** authorize corpus repair, resolution of the Facility Restart source conflict, semantic-layer work, implementation, pushing, or a pull request.

Reply examples:

- `Approve P1-P5.`
- `Approve P4-P5; keep P1-P3 pending.`
- `Amend P5: ...`
