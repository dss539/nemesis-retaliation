# Automatic Shotgun — Source-Fidelity Audit

## Scope and authority

This audit compares the extracted Tabletop Simulator card against the official base-game sources. Authority order is:

1. Official FAQ/errata.
2. Official rulebook and its component images/text.
3. TTS mod assets and metadata.

The TTS asset is useful extraction evidence but is not authoritative when it conflicts with the official sources.

## Primary-source evidence

### Official rulebook

Source: `docs/rulebooks/Nemesis_RT_Rulebook_official.pdf`, page 3.

- PDF metadata: 40 pages; created and modified 2025-07-23; Adobe InDesign 20.4 / Adobe PDF Library 17.0.
- SHA-256: `e3cda0d7a91bd090cec45dbc8ce89e2015e2202173357c374ff49365f9c29ddd`.
- The page-3 component image visibly prints:
  - `AUTOMATIC SHOTGUN`
  - `RANGED WEAPON, HEAVY`
- The component is grouped among `7 Character Item cards` and visibly associated with `HEAVY GUN OPERATOR — CHARACTER ITEM`.
- The PDF text layer states (`docs/rulebooks/rulebook_text.txt`, lines 149–156):
  - `HEAVY GUN OPERATOR`
  - `CHARACTER ITEM`
  - `Shoot: Before Shooting, deal 1 Hit more.`
  - `[shootDieCritical]: Spend [ammoToken] if able.` (the extracted text drops both icons; the red triangular glyph's visible portion matches the page-40 `shootDieCritical` crop)
  - `Automatic shotgun`
  - `RANGED WEAPON, HEAVY`

Visual evidence: `docs/qa/card-icon-comparisons/automatic-shotgun-official-rulebook-p3.png` and `automatic-shotgun-official-icon.png`.

### Official FAQ/errata v1.2

Source: `docs/rulebooks/Nemesis_RT_FAQ_v1.2.pdf`.

- SHA-256: `611ae20dc0b3e04f3c0d99f294a92fc95460c042565b12d1c808b1282ae0e0d8`.
- A direct text extraction contains zero matches for `Automatic Shotgun`, `shotgun`, `Heavy Gun Operator`, `RANGED WEAPON, RIFLE`, or `RANGED WEAPON, HEAVY`.
- Therefore the FAQ supplies no override to the rulebook card.

## TTS evidence

TTS face pixels: `cards/character/heavy-gun-operator/starting-item/automatic-shotgun.png`.

TTS back pixels: `docs/qa/card-source-audits/automatic-shotgun-tts-back.png`. This back visibly prints `STARTING ITEM — COMBAT ENGINEER`; it is retained as provenance for the obsolete/misnested TTS object, not as a standalone catalog component.

The extracted TTS card visibly prints:

- `AUTOMATIC SHOTGUN`
- `RANGED WEAPON, RIFLE`
- `Shoot: On Hit deal 1 more.`
- `[shootDieCritical]: Spend [ammoToken].`
- lower-center `[ammoSlot]`

The TTS save record is `CardCustom` GUID `2059a7`, description `AUTOMATIC SHOTGUN`, card ID `431200`. Its FaceURL is the Automatic Shotgun image and its BackURL is the `STARTING ITEM — COMBAT ENGINEER` image above. It is incorrectly nested under Bag GUID `284e9d`, nickname `Combat Engineer` (`assets/tts-mod/extract/v2/classification.json`, lines 52891–52935). That bad parent metadata caused the original Combat Engineer routing and is independent evidence that this TTS record cannot establish final character ownership or canonical wording. The formerly cataloged `cards/character/combat-engineer/starting-item.*` entry was removed after human approval because the BackURL is not an independent component.

## Finding

Status: source conflict, resolved by authority hierarchy.

The TTS card is an obsolete/prototype variant. It conflicts with the official rulebook in character routing, type line, first effect wording, and the final `if able` clause. The official FAQ does not amend the rulebook.

For the faithful digital edition, canonical game data must use:

- Character: Heavy Gun Operator
- Component class: Character Item
- Type line: `RANGED WEAPON, HEAVY`
- Effect: `Shoot: Before Shooting, deal 1 Hit more. [shootDieCritical]: Spend [ammoToken] if able.`

The TTS image and its exact transcription should be retained only as provenance/reference and must not silently feed canonical rules data.

## Change state

This audit does not alter `automatic-shotgun.json`; a schema/provenance decision is required before replacing its TTS transcription with canonical official data.
