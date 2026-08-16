# Qwen-Derived Vision Cleanup

Date: 2026-08-14

## Scope

This audit identifies project claims that materially depended on earlier Qwen vision reads and
rechecks them through native `openai-codex:gpt-5.6-sol` image input. Qwen output is retained only
as historical provenance; it is not accepted as pixel evidence for this project.

Each GPT-5.6 invocation:

- received exactly one local image through `hermes chat --image`;
- was explicitly told to use only the attached pixels and not read project files or prior sessions;
- used high reasoning with no tool calls;
- recorded its provider, model, prompt, response, and session ID in a redacted JSONL export under
  `docs/qa/qwen-derived-vision-cleanup-sessions/`.

## OQ-011 room-tile revalidation

### Server Room

Image: `assets/tts-mod/extract/v2-dl/tree/tiles/room/server-room-001.png`

GPT-5.6 session: `20260814_043518_dc629e`

Result:

- red Item badge present;
- yellow Item badge present;
- cyan/blue Computer monitor icons present;
- no blue Item badge present.

This supports OQ-011's conclusion that a cyan Computer icon was conflated with a fourth Item color.

### Technical Corridor Entrance

Image: `assets/tts-mod/extract/v2-dl/tree/tiles/room/technical-corridor-entrance-006.jpg`

Primary GPT-5.6 session: `20260814_043614_8285f5`

Blind confirmation session: `20260814_043846_906106`

Both invocations independently report:

- exactly three yellow/gold hexagonal badges;
- each badge contains a white wrench glyph;
- no red, green, or blue Item badge;
- cyan/blue illumination is decorative rather than a discrete badge.

Correction: the earlier Qwen-derived statement that this tile has no Item icons was false. OQ-011
now records three yellow Item icons. Its central conclusion remains unchanged: the tile provides no
evidence for a fourth blue Item type.

## Sample Item-card revalidation

These three images had been used as examples when establishing the color-deck versus Heavy Item
taxonomy. They are not part of the 18-entry human-approved character-card JSON catalog. Their broad
classification as self-contained portrait Item cards remains supported, but Qwen's exact reads
contained punctuation and icon-identification errors.

### Ammo Magazine

Image: `assets/tts-mod/extract/v2-dl/tree/cards/game/reditem-148_cards/card-00.png`

GPT-5.6 session: `20260814_043723_9a2b44`

Pixel transcription:

- Title: `AMMO MAGAZINE`
- Type line: `ONE USE ONLY,` / `SPECIAL WEAPON`
- Body:
  - `You can use this Item for free`
  - `immediately after gaining it.`
  - `Gain up to 2 [red ammo-like icon]`

Classification: self-contained Item; it does not direct the player to gain another card.

Qwen cleanup: Qwen had rendered a period after the terminal icon. GPT-5.6 reports no printed period
there. Until a dedicated punctuation crop or human review establishes otherwise, the period must not
be promoted as exact card text.

### Anti-Aircraft Codes

Image: `assets/tts-mod/extract/v2-dl/tree/cards/game/reditem-148_cards/card-01.png`

GPT-5.6 session: `20260814_043748_666f3a`

Pixel transcription:

- Title: `ANTI-AIRCRAFT` / `CODES` followed by a white crossed angular/aircraft-like glyph over a
  red diamond
- Type line: `ONE USE ONLY`
- Body:
  - `Only in [cyan Computer-like icon] Room without [gray cogwheel icon]`
  - `Take both Anti-Aircraft tokens`
  - `and place them in any order.`

Classification: self-contained Item; it directs interaction with Anti-Aircraft tokens, not gaining
another card.

Qwen cleanup:

- Qwen inserted a colon after the cogwheel condition; GPT-5.6 sees no colon.
- Qwen described the title-area glyph as a red X over an aircraft. GPT-5.6 instead sees crossed white
  angular/aircraft-like forms over a red diamond and declines to assign a definitive game meaning
  from pixels alone.

### Duct Tape

Image: `assets/tts-mod/extract/v2-dl/tree/cards/game/yellowitem-145_cards/card-00.png`

GPT-5.6 session: `20260814_043814_c697e2`

Pixel transcription:

- Title: `DUCT TAPE`
- Type line: `ONE USE ONLY`
- Body:
  - `Discard a [gray cogwheel icon]`
  - `OR`
  - `Place this Item and 1 another`
  - `Heavy Item under a Heavy Item`
  - `in your Hand slot.`

Classification: self-contained Item.

Qwen cleanup: Qwen confidently labeled the upper-right glyph as a handgun crossed by a red X and
assigned a not-weapon meaning. GPT-5.6 sees a white angular overlapping/crossed-item symbol under a
large red X and explicitly marks its exact meaning uncertain. The earlier semantic claim is rejected.

## Other known Qwen-influenced work

### Tactical Gear token colors

- `tokens/ammo-008.png`: native GPT-5.6 session `20260814_044620_8981cb` reports a deep
  red/crimson token with six upright ammunition cartridges (98% confidence).
- `tokens/grenade-003.png`: native GPT-5.6 session `20260814_044633_54d562` reports a
  purple/violet token with an orange/bronze grenade-like glyph and `+2` (95% confidence).

These results independently preserve the live extraction guidance Ammo=red and Grenade=purple.
Redacted session exports are stored with the other audit evidence.

- Early Combat Engineer card reads were subsequently re-audited one at a time and approved by the
  user. The approved JSON remains in place; no Qwen-only uncertainty remains in the 18-entry catalog.
- Qwen-era reads of `officer-001.png`, `officer-008.png`, and
  `heavy-gun-operator-045_cards/card-00.png` were exploratory. A repository search found no live
  rule/card record that cites those paths or depends on those reads, so there is no canonical data
  to rewrite; future use requires a fresh GPT-5.6 read.
- The first icon crops were replaced by a verified 49-icon extraction from the official rulebook.
- `unsorted/card-176.jpg` remains in the quarantined review queue. The controlled GPT-versus-Qwen
  benchmark is retained under `docs/qa/vision-model-trial/`, but the benchmark is not itself human
  approval to catalog or reclassify the component.
- The cancelled worker's root-level `analyze_card_176.py` was an unused partial artifact and was
  removed.

## Durable policy outcome

Project extraction notes and the reusable `extract-game-mod-assets` skill now require native GPT-5.6
for Nemesis: Retaliation vision work, one image per invocation, explicit provider/model/session
provenance, and revalidation of historical Qwen-dependent claims. The controlled comparison remains
as QA evidence; Qwen is not a production option for this project.
