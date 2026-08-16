# TTS Mod Asset Extraction Notes

This is the detailed operational record for the v2 extraction. Start with
`assets/tts-mod/readme.md`; use this file when working on extraction, classification, cleanup,
or expansion recovery.

**Status:** v1 extraction archived to `assets/archive/tts-mod-v1/`. The v2 workspace is under
`assets/tts-mod/extract/`.

**v2 COMPLETE (2026-08-04):** base-only asset tree built at
`/home/smithers/nemesis-retaliation/assets/tts-mod/extract/v2-dl/tree/` — 444 files, 0.93 GB, fresh downloads.
**Do NOT re-download.** Remaining work: one-card-at-a-time vision extraction (see §12) and
feeding human-approved canonical card data into the rebuilt implementation.

**Goal for v2:** re-extract art assets from the Nemesis: Retaliation TTS mod with correct
classification, correct orientation, human-readable names, and — critically — **BASE GAME
ONLY** (exclude Sangrevore, Xyrians, Contractors, Insider, Stretch Goals/Neoflesh content
as far as the mod structure allows).

---

## 1. Source material

- Steam Workshop item **3256296893** "Nemesis Retaliation (Script assisted)" (TTS appid 306130).
  The official prototype mod 3245600308 is DEAD (stale cloud-3 CDN, all 403) — don't use it.
- Save file already downloaded: `/home/smithers/nemesis-retaliation/assets/tts-mod/extract/nemesis_script_mod.bin` (3,026,208 bytes).
  If lost, re-fetch via steamworkshopdownloader.io details API (see skill
  `extract-game-mod-assets`, reference `tts-mod-extraction.md` — steamcmd anonymous is blocked).
- All 1079 asset URLs are on `steamusercontent-a.akamaihd.net` and were alive as of 2026-08-01.
- v1 downloaded set (2.0 GB, magic-byte-typed, renamed) is intact in `assets/archive/tts-mod-v1/`
  — you may be able to reuse the files and only redo classification/naming, saving the download.
  `assets/archive/tts-mod-v1/manifest.json` maps URL→dir→(stale hash filename; files were later renamed
  to sequential names, so match by directory + hash prefix or re-derive).

## 2. TTS save binary format (hard-won)

Not JSON. Custom typed binary tree. Read as bytes; decode text runs as latin-1 (NEVER utf-8).

Type markers (each followed by null-terminated key name):
- `0x01` float: key + 8-byte LE double
- `0x02` string: key + `\0` + 4-byte LE length + raw bytes
- `0x03` object/array-element: key (or index string like "0","1") + `\0` + 4-byte LE content length
- `0x04` array: key + `\0` + 4-byte LE content length; elements are `0x03`-indexed
- `0x07` byte/enum: key + 1 byte   |  `0x08` bool: key + 1 byte  |  `0x10` int32: key + 4 bytes
- `0x00` terminator/padding

**You MUST handle 0x07/0x08/0x10** in any linear scanner or you lose field alignment
(this caused v1's first parse to return garbage).

Layout of the file:
- Header: SaveName, GameMode, VersionNumber (v14.2.1), Table/Sky settings, TabStates,
  AudioLibrary (URL→title pairs for music).
- **~offset 40,883 → 811,330: GLOBAL Lua script (~770 KB). UNDER-EXPLORED — SEE §5.**
- offset 811,331: `0x04 ObjectStates` array (2,214,864 bytes) — all game objects.

Object fields (in order): GUID, Name (object type), Transform (posX/Y/Z, rot, scale),
Nickname, Description, GMNotes, ColorDiffuse, then type-specific: FaceURL/BackURL (cards/decks
via nested CustomDeck), ImageURL (tokens/figurines), DiffuseURL/MeshURL/ColliderURL (models),
AssetbundleURL, PDFUrl, CardID, ContainedObjects (nested array of child objects).

Object type counts w/ URLs: CardCustom 717+, Deck, Card, Custom_Tile, Custom_Model,
Custom_Token, DeckCustom, Custom_Model_Bag, Figurine_Custom, Custom_Assetbundle, Custom_PDF (8), etc.
1079 unique URLs, ~4272 URL references (decks share face/back URLs across cards).

## 3. What went wrong in v1 (do not repeat)

1. **Nickname stickiness.** A linear scanner kept "current nickname" and only updated on
   non-empty values. Most cards inside decks have EMPTY nicknames, so they inherited the last
   named object (often an unrelated deck like "Noise" or the "Half" ammo token). Result:
   item cards filed under cards/status/noise/, the play-area border filed as cards/status/half-001,
   the same junk nickname scattered across cards/, tokens/, tiles/ by object type.
   **Fix: parse the tree properly (recursive, ContainedObjects-aware) and classify by
   GMNotes tag + global-Lua deck role + vision content, NOT by nickname.**
2. **Trusting save metadata over content.** The save genuinely lacks per-card names for most
   deck cards (CardID → shared CustomDeck face/back only). Only ~123 URLs have Description
   values (weapon/item template cards: "GATLING GUN", etc.). Everything else needs
   content-based (vision) naming.
3. **Rotation ignored.** Some stored images are rotated 90° (e.g. character-select cards,
   full-ammo token: stored 90° CW, need 90° CCW to be upright). Detect + fix before analysis.
4. **v1 file naming**: 55 files got real names from Descriptions; 1024 got sequential
   `<dirname>-NNN.ext` names. Directory tree shape was decent (cards/character/<name>/ etc.)
   but contents polluted by (1).

## 4. Text extraction findings

- **Tesseract is unreliable on this art.** Empty or garbage on most cards at any rotation,
  threshold, upscale, or PSM. It may provide secondary punctuation evidence on isolated crops,
  but it is not an authoritative transcription source.
- **Use native `openai-codex:gpt-5.6-sol` at `max` reasoning for this project. Do not downgrade or use Qwen for vision.** A controlled blind
  trial on `unsorted/card-176.jpg` scored GPT-5.6 88/100 and Qwen 56/100; Qwen guessed icon
  meanings, normalized formatting, and overstated confidence. See
  `docs/qa/vision-model-trial/report.md`.
- **Earlier model reads are not canonical evidence.** Preserve them only as provenance and
  revalidate any claim that still depends on them with Sol Max, exact crops/glossary
  comparisons, official sources where the normal escalation trigger applies, or human review.
- **Reuse one verified Sol Max session and batch carefully.** Submit 2–4 explicitly labeled assets
  per turn, require one independent result per asset ID, persist each result, and reconcile submitted
  and returned IDs/counts before continuing. Use one-image turns for dense/large assets, strict gates,
  focused comparisons, or retries after omission/cross-image confusion. If pixels are stripped or the
  backend rejects image input, report a tooling failure; do not interpret the refusal as image content.
- Give every vision turn the icon glossary, card anatomy, exact output schema, and a strict
  requirement to use `[illegible]` rather than guess. Require unambiguous rotation phrasing:
  "rotate the FILE 90° CW/CCW to make it upright" (an early read reported a rotation backwards).
- **Sol Max confidence is not evidence.** Require morphology before labels, the closest plausible
  alternative for every icon, and one visible feature that rules that alternative out. If pixels do
  not discriminate, retain a literal unknown and defer. Keep read confidence, classification
  confidence, uncertainties, and promotion decision separate; false promotion is worse than deferral.

## 5. UNDER-EXPLORED GOLD (start here for v2 classification)

1. **Global Lua script (~770 KB, offsets ~40883–811330).** Contains GUID→role mappings like
   `CustomDeck = gO('831e19')`, `missionTaskDeck = gO('eabc1d')`, `characterDraftDeck = gO('2abdf6')`,
   `startItemDeck = gO('f71196')`, `attacksDeck = gO('34c73e')`, `greenItemsDeck = gO('17400d')` …
   plus the whole scripted-setup logic. Extract the full script, index every `gO('xxxxxx')`
   assignment → you get authoritative functional roles for deck GUIDs. The setup script may
   also reveal which decks/bags belong to which expansion (it has lifeform options like
   "Primebloods" in LuaScriptState — suggests selectable intruder factions = expansion switch).
2. **GMNotes tags (1289 non-empty).** Per-object functional tags, e.g. "event", "eventDiscard".
   Enumerate all distinct GMNotes values — likely a ready-made taxonomy (event/item/objective/…).
3. **Transform positions.** Every object has posX/posZ. The TTS table is spatially organized;
   expansion content usually sits in separate table zones/bags. Cluster objects by position and
   correlate with bag/deck membership to separate base-game from expansion staging areas.
4. **ContainedObjects hierarchy.** Parse it properly: bag→contents and deck→cards edges give
   provenance (a card inside `shamblerBag` is expansion content, period).

## 6. Base-game vs expansion separation (v2 requirement)

The user only wants BASE Nemesis: Retaliation content. Signals:
- Base characters (per repo `js/data.js` / AGENTS.md, 6): Officer, Medical Support,
  Heavy Gun Operator, Combat Engineer, Recon, Contractor(+Sharpshooter/Bioenhancment Expert
  appear base-adjacent — verify against base rulebook roster on p.16-18).
  Clearly expansion: Hunter, Janitor, Lab Rat, Medic, Pilot, Psychologist, Scientist, Scout,
  Sentry, Soldier, Survivor, Xenobiologist, Hacker, Mechanic, Captain, CEO, Android, Convict,
  Bounty Hunter, Laika, Consultant, UAV Operator (Contractors expansion roster; verify).
- Base intruders: larva, drone (creeper?), adult, queen, egg (verify vs base rulebook p.30-32).
  Expansion intruder bags in the mod: shamblerBag, fleshbeastBag, butcherBag, metagorgerBag
  (Sangrevore?), kingBag/kingTokenBag, motherbrainBag, cultistBag, twitchlingBag,
  firespitterBag, ironcladBag, crawlmineBag, slasherBag, ghoulBag, specterBag, shadowBag
  (Neoflesh Cult / SG per SG rulebook mentions of Motherbrain+Crawlmine+Slasher+Ironclad),
  plus insider* (Insider expansion) and "Primebloods"/"Crimson Despot" content (event cards
  referencing Crimson Despot = expansion lifeform).
- Cross-check names against expansion rulebook PDFs in `docs/rulebooks/` (Sangrevore, Xyrians,
  Contractors, Insider, SG, SS) — pdftotext each and grep the candidate name.
- Honest caveat: full separation may be impossible purely from structure; the global Lua
  setup script + bag membership + rulebook cross-check should get ~95% there. Ambiguous
  items go to an `unsorted-maybe-expansion/` quarantine, not silently included.

## 7. Icon glossary & card anatomy (for vision prompts)

- `icon-templates/` (this dir): 39 icon crops extracted from the official rulebook p.40 icon
  glossary (300 DPI render). Regenerate any page:
  `pdftoppm -png -r 300 -f 40 -l 40 docs/rulebooks/Nemesis_RT_Rulebook_official.pdf out`.
  Not yet captured: Secure token, Lander, Autodestruction, Intruder, Oxygen(stat), Health,
  Robot, Hibernatorium-inactive. ALSO: the mod's own token images (archive tokens/ dirs) are
  higher-quality icon references than the rulebook prints — mine them as templates too.
- Canonical icon vocabulary (rulebook p.40): Shoot/Burst/Noise die faces; Red/Yellow/Green
  Item; Computer; Fire; Malfunction; Noise marker; Secure token; **3 Corridor orientations
  (E-W, NE-SW, NW-SE) — MUST be distinguished, rotation is meaningful**; Life Support
  active/inactive; Hibernatorium active/inactive; Lander; Autodestruction; Oxygen/Ammo/
  Grenade/Medpack gear tokens + 5 slot types; Character; Oxygen; Health; Action card; Robot;
  Not In Combat (page 40: crossed-out Intruder; Action cards may use crossed-out gun); Intruder.
- Action card anatomy (rulebook p.13): A=Not-In-Combat icon (top-right), B=Title,
  C=Effect(s) (may be two alternatives split by an OR banner), D=Reaction effect (separate
  panel, vertical "REACTION" label), E=Character label (footer, colored text).
- Event card anatomy: A=intruder movement line, B=main effect, C=secondary effect.
- Exploration cards: room placement header, hex room diagram (with corridor exits by
  direction, in-corridor markers like noise, in-room icons), Reminder line, Entrance Effect.
- Item cards: charge/slot boxes on top, art, TITLE + type line (e.g. "TECH ARMOR"),
  on-gain effect, framed passive effects panel.
- Open icon questions (user-confirmed unknowns): queenhealth conditional prefix (intruder head +
  blob-with-plus) and diamond/beacon placement marker (Motherbrain content → check SG
  rulebook); BOOM! left-column row-key icons may be die faces, not intruder symbols.

## 8. Download mechanics (reuse from v1)

- Downloader script archived at `/home/smithers/nemesis-retaliation/assets/tts-mod/extract/download_and_catalog.py`.
- Parallel curl (12 workers) initially failed 100%: DNS handed some workers a dead Akamai
  edge (23.209.188.141, SYN-SENT forever). Fix: `--resolve steamusercontent-a.akamaihd.net:443:23.62.61.236`
  (verify IP still good: `dig +short steamusercontent-a.akamaihd.net`), plus `-4 --retry 3
  --connect-timeout 15`.
- Download temp files to the SAME filesystem as the destination (`os.rename` across /tmp →
  home fails EXDEV; use shutil.move or same-fs tmp dir).
- CDN serves no extensions: type by magic bytes (PNG/JPG/OBJ '# Blender'/UnityFS .asset3d/
  ID3 mp3/%PDF/RIFF-WEBP/PK zip). v1 tally: 674 png, 310 jpg, 65 obj, 22 asset3d, 8 pdf = 1079,
  2.00 GB, 27 s wall.
- `.obj`/.asset3d are 3D models, PDFs are rulebook scans — catalog, don't treat as card art.

## 9. Session environment notes

- Use a native GPT-5.6 image attachment through the active session's supported image path. Do not
  route project images to Qwen. Keep one image per invocation.
- For human-gated card review, if the active session cannot deliver the image to native GPT-5.6,
  stop and report the tooling failure. Do not start a substitute worker or mutate global provider or
  auxiliary-vision configuration during extraction.
- `execute_code` is the reliable way to run Python (approval prompts don't surface in the
  user's WebUI). It has been seen intermittently blocked with a cron-mode error; terminal
  works for simple commands (avoid `rm -rf` and heredocs — approval gates).
- Tesseract + pytesseract + poppler-utils installed (system + hermes venv). scipy in venv.
  cv2 NOT installed.
- The hermes-agent venv python is what execute_code uses: /home/smithers/.hermes/hermes-agent/venv.

## 10. Suggested v2 plan

1. Write a proper recursive parser for the save (handle all type markers, recurse
   ContainedObjects, keep parent chain). Emit one record per object: GUID, type, parent chain,
   nickname, description, GMNotes, transform, URLs, CardID.
2. Extract the global Lua script; index `gO('guid')` role assignments + setup logic; join
   roles onto the object records. Enumerate GMNotes taxonomy.
3. Classify every object: role (from Lua/GMNotes/bag membership) × base-vs-expansion
   (from §6 signals). Quarantine ambiguous.
4. Build tree: base-game only, cards/<role>/<deck>/, tokens/, tiles/, models/, rulebooks/;
   `expansion/` and `unsorted-maybe-expansion/` kept separate.
5. Orientation pass, then ONE-card-at-a-time vision extraction (schema: FILE, ROTATION-FIX,
   TITLE, BODY TEXT verbatim w/ canonical [ICON:*] placeholders from §7 vocabulary, SECTIONS,
   FOOTER, ICONS w/ spatial positions, TRUE CATEGORY). Review each with the user; iterate the
   prompt; scale ONLY when the user green-lights.
6. Card database (JSON) generated from validated extractions feeds `js/data.js` later.

## 12. v2 COMPLETED — parser corrections & pipeline (2026-08-04)

**Parser corrections (v1 spec was wrong in 3 places — see `extract/v2_parse.py`):**
1. File starts with a **4-byte header** (`20 2d 2e 00`) before the first type marker.
2. Object/array `0x03`/`0x04` length fields are **declared length = actual payload + 4**
   (they count the length field itself). Verified on 3 fields (visibleColor 38→34, TabStates
   el "0" 109→105, el "1" 110→106). Payload includes the trailing 0x00 terminator.
3. Undocumented marker **`0x12` = uint64 (8 bytes)** — used for Steam IDs (OwnerSteamID etc.).
   Handle it or lose alignment.
Also: some string lengths include a trailing NUL — `rstrip(b'\x00')` before decode.

**Parse results:** 196 top-level objects, 1800 records with parent chains, 1094 unique URLs
(5757 refs incl. nested; 4077 after excluding ContainedObjects attribution — child URLs belong
to child records, not containers). LuaScript 766,268 chars + LuaScriptState 799 chars extracted.
Artifacts in `/home/smithers/nemesis-retaliation/assets/tts-mod/extract/v2/`: `objects.json`, `lua_script.lua`,
`lua_script_state.lua`, `lua_roles.json` (159 role assignments), `gmnotes_taxonomy.json`
(172 distinct tags), `classification.json`, `url_verdicts.json`.

**Classification (v2_classify.py) — Lua-authoritative:** GUIDs named in
`recallNeoflesh`/`recallSangrevores`/`recallCarnomorph` = expansion; base role GUIDs
(attacksDeck/eventDeck/explorationDeck/queenHealthDeck/intruder bags as first-assigned) = base.
**Critical pitfalls learned:**
- `mech_roles` re-added expansion GUIDs (shadowBag/taintedDeck/mutationDeck/contaminationDeck/
  noiseBag-7cb24e) to base_guids after the subtraction — **subtract expansion_guids AGAIN after
  mech_roles**.
- The gameBox (a64f43) is the storage box and CONTAINS the expansion boxes — it must be a
  **neutral ancestor** (skip in inheritance) or it stamps `base` on NeofleshExpansion/Hunter etc.
- **Ancestor inheritance must run BEFORE nickname/GMNotes fallback**, or contained expansion
  content (cards in expansion decks, Carnomorph figure models) gets `base` from its GMNotes tag
  ('adult'/'queen'/'event' tags look base).
- Expansion decks (per-lifeform exploration/attack/event/queenHealth copies) have **fully
  disjoint URL sets** from base decks — no shared card images.
- locLaika is NOT a base mechanic (it's the Contractors-expansion dog).
- Final verdicts: 857 base / 881 expansion / 55 junk (trashBag, prototo, Other, Prototype stuff)
  / 7 unknown (quarantined to `unsorted/`).

**Downloads (v2_download.py):** Akamai edge IPs changed — current DNS (104.120.129.x) works,
old pinned 23.62.61.236 is stale. Fresh downloads, 12 workers, magic-byte retype.
770 jobs → 444 base files (0.93 GB) + 6 unsorted. The two "failures" in failures.json are
empty-string URL entries (empty DiffuseURL fields), not real assets.

**Tree (v2_tree.py):** `v2-dl/tree/` — 444 files, 0.93 GB:
`cards/character/` (53 — per-character action decks, correct kit routing), `cards/game/` (182 —
action/event/attack/exploration/item decks), `tiles/room/` (23 — room tiles by room name),
`models/` + `models/character/` + `models/intruder/`, `tokens/` + `tokens/character/` +
`tokens/intruder/`, `bags/`, `figures/`, `rulebooks/` (3 PDFs), `tiles/table/`, `tokens/table/`.
manifest.json + catalog.md at root. Primary-record selection must prefer Card records over
their Deck container, or kit cards file under `cards/game/action-discard` instead of
`cards/character/<name>/`.

Current card-transcription progress and approval gates are tracked only in `todo.md`; the active
source-authority policy is in the root `readme.md`, with card-specific procedures in
`assets/tts-mod/notes/card-extraction.md`.

## 13. Improvement list + open questions carried from v1 review

Improvements: glossary-matched icon names; distinguish 3 corridor orientations; distinct
placeholders for visually distinct icons; spatial icon reporting (which corridor/room);
unambiguous rotation phrasing; one-image-per-GPT-5.6-invocation; fix stale manifest after any rename;
for disputed small icons, build a labeled contact sheet from every plausible canonical crop and
match internal glyph morphology before using surrounding rules semantics.
Open questions: BOOM! row-key icons (die faces?); queenhealth Motherbrain icons;
purpose of art-only "CHARACTER DRAFT" card; why
vision_analyze strips images (Hermes-side context management?).

## 14. v3 category cleanup + sheet splitting (2026-08-05)

**Folder renames (base decks, live-deck names not "-discard"):** attack, event, exploration,
greenitem, reditem, yellowitem, seriouswound. The `-discard` GMNotes tag is the mod's saved-state
label for a single object that toggles between live-deck and discard-pile roles (Lua
`returnDiscardToDeck(discard, deck)` physically moves the discard object back onto the live deck).
Base decks are ONE object serving both roles; the tag reflects saved state, not a separate pile.
Expansion decks DO have separate per-lifeform discard objects (see §15).

**Reference cards:** 9 player-help cards (playerHelpBag d8a0fb) + intruderHelp (1e58e7) moved to
`cards/reference/`. **Unknown cards:** 7 verdict=unknown records moved to `unsorted/` for review.

**Sprite-sheet splitting:** 13 sheets (grid>1) split into individual card PNGs at native res, each
in a `<sheet>_cards/` subfolder. Grid geometry read from the save's CustomDeck NumWidth/NumHeight.
All sheets divide cleanly into integer cells. Split cells are named `card-NN.png` by grid position
(row-major, top-left=0) — real per-card names come from the vision phase, NOT from card_id%100
(that mapping is unreliable: multiple distinct named cards share face index 0 on the same sheet).

**action folder resolved:** 12 files were actually objectiveCoopDeck (e22eaa) cards → moved to
`cards/game/objectiveCoop/`; 1 was contaminationDeck (7e89ea) → `cards/game/contamination/`;
action-154.jpg (9x5 sheet) split, base cells 10-14 (Repairs, Rest, +3 anonymous) kept in
`cards/game/action/`; action-discard-001.jpg is the shared action-deck card BACK → `action/back.jpg`.

## 15. EXPANSION CONTENT — deliberately excluded, re-add later

The tree is BASE-ONLY. When expansions are added, re-extract from the save. Key facts for that work:

- **Per-lifeform expansion decks are separate objects with DISJOINT card-image URLs** from base.
  Each expansion has its own attack/event/exploration/queenHealth decks + intruder bags, all tagged
  `*Discard` and nested under the gameBox (a64f43) inside a named expansion bag:
  - Carnomorph: bag 164dc0 (attackDeck 9aefbc, eventDeck 0da709/d3c7fc, explorationDeck 2e8e9d)
  - Sangrevores: bag 3edcd3 (attackDeck 3a25fc, eventDeck 58aa1c, explorationDeck dd1eda, contaminationDeck ebef8b)
  - Neoflesh: bag d63508 (attackDeck 61a87c, eventDeck abbdd0, explorationDeck a24dc8)
  - Plus per-character action decks (Hunter, Janitor, Lab Rat, Medic, Pilot, Psychologist, Scientist,
    Scout, Sentry, Soldier, Survivor, Xenobiologist, Hacker, Mechanic, Captain, CEO, Android, Convict,
    Bounty Hunter, Sharpshooter, Bioenhancment Expert, UAV Operator, etc.) — each a separate
    `actionDiscard` deck object with its own 5-face sheet.
- **action-154.jpg (9x5 sheet) is SHARED base+expansion.** Base cells 10-14 (Contractor: Repairs,
  Rest, +3). Expansion cells 15+ (Bioenhancment Expert, UAV Operator, etc.). The full split is in
  `/tmp/action154_split/` (may be gone after reboot) — re-split from the sheet if needed.
- **action-discard-001.jpg is the shared action-deck card BACK** (273 cards base+expansion reference
  it as BackURL). Already saved as `cards/game/action/back.jpg`.
- **Expansion intruder bags** (from Lua roles): shamblerBag/fleshbeastBag/butcherBag/metagorgerBag
  (Sangrevore), kingBag/kingTokenBag/motherbrainBag/cultistBag/twitchlingBag/firespitterBag/
  ironcladBag/crawlmineBag/slasherBag/ghoulBag/specterBag/shadowBag (Neoflesh Cult/SG), insider*
  (Insider), xyrian* (Xyrians), "Primebloods"/"Crimson Despot" event content.
- **Classification pitfall (from v2):** the gameBox (a64f43) is a neutral ancestor — skip it in
  inheritance or it stamps `base` on expansion content. Re-subtract expansion GUIDs AFTER the
  mechanical-roles pass. Expansion decks have fully disjoint URL sets from base — if they "share"
  URLs with base records, it's a mis-inheritance bug, not reality.

## How to resume in a clean session

1. Read `assets/tts-mod/readme.md`, then this file for the detailed extraction workflow.
2. Read the project TODO list: `/home/smithers/nemesis-retaliation/todo.md` — this is the living
   task list for what is done, next, or gated. Update it when project state changes.
3. Read repo `AGENTS.md` and skill `extract-game-mod-assets` (+ its reference file).
4. Confirm save file exists: `/home/smithers/nemesis-retaliation/assets/tts-mod/extract/nemesis_script_mod.bin` (3,026,208 B).
5. Start with §10 step 1-2 (parser + global Lua mining) — pure local Python, no tokens, no
   downloads. Show the user the extracted deck-role table and GMNotes taxonomy BEFORE
   downloading or classifying anything.
6. Remember the working agreement: ONE sample → user review → iterate → scale. Never batch
   experiments without approval. Keep a running improvement list in the session.
