# Card Extraction Notes

**Purpose:** Durable, TTS-specific record of workflow lessons, icon meanings, and processing rules discovered during vision-based card extraction. QA evidence referenced here remains under `docs/qa/`.

**Canonical Icon Glossary:** See `docs/rules/icon-glossary.md` for the authoritative icon reference from rulebook p.40. Do not invent icon names — use the glossary.

---

## Icon Resolution Lessons

Canonical icon names, artwork descriptions, and meanings live only in
`docs/rules/icon-glossary.md`. This note records the extraction procedure and failure modes, not a
second glossary.

- Card art may use a visual variant of a canonical semantic icon. An exact crop match confirms an
  identifier, but a mismatch alone does not disprove it; compare official definitions, card
  anatomy, applicable component references, same-title later artwork, and source edition/prototype
  provenance. Approved source-specific aliases live in
  `docs/qa/card-symbol-semantic-resolutions.json`; normalize rules text to the semantic token while
  retaining literal art descriptions in evidence. Never generalize an alias by color/shape alone.
- Separate the narrow fact established by a correction from adjacent assumptions. For example,
  confirming that a crossed-out-gun card glyph means `notInCombat` did not establish that the
  rulebook glossary used the same artwork.
- Similar silhouettes are easy to confuse without the glossary. The Lander was once read as an
  Intruder, and `shootDieCritical` was once read from surrounding semantics instead of morphology.
  Treat these as reasons to compare pixels, not as alternate icon definitions.

---

## Rotation Workflow

1. **Check orientation BEFORE reporting** — vision model must confirm card is upright
2. **Rotate on disk, not in-memory** — use PIL to rotate the file permanently, then re-verify
3. **Starting Item cards are landscape** — text "STARTING ITEM / CHARACTER" runs left-to-right in horizontal orientation
4. **Action cards are portrait** — vertical orientation
5. **If vision reports rotation needed:**
   - 90° CW = `Image.ROTATE_270` in PIL
   - 90° CCW = `Image.ROTATE_90` in PIL
   - 180° = `Image.ROTATE_180` in PIL
6. **Re-verify after rotation** — don't trust the first rotation direction report; confirm text is readable

---

## Vision Prompt Format

**Vision backend policy:** Use native `openai-codex:gpt-5.6-sol` at `max` reasoning for this project.
Do not downgrade, use Qwen, route images through an auxiliary vision backend, or modify shared
model/provider configuration. Prefer one persistent verified session and submit 2–4 explicitly labeled
assets per turn, requiring a separate persisted result for every asset ID. Use one-image turns for
dense/large assets, strict gates, focused comparisons, or retries after omission/cross-image confusion.
Preserve provider/model/reasoning/session provenance for any extraction that could enter canonical data.
If Sol Max cannot receive the images or provenance cannot be verified, stop and report the tooling
failure rather than silently substituting another model. Historical model output is evidence of what
an earlier tool reported, not evidence of what the pixels contain; revalidate dependent claims before
relying on them.

**Luna Max evaluation:** A blinded 12-image native trial of `gpt-5.6-luna` at reasoning effort
`max` is not approval for unattended canonical promotion. Luna scored 82.120 overall and 85.180 on
eight human-approved cards, but none of its five high-confidence promoted sidecars matched the
approved sidecar exactly. It also made a confident `lander`→`character` error, missed known Ammo
icons, and false-promoted deliberately ambiguous creature art. On the exact dense help-sheet image
used in the earlier model trial, Luna scored 72 versus Sol's 88. Luna may assist OCR or queue triage,
but every canonical candidate still requires independent icon, punctuation, schema, and
classification verification. Evidence: `docs/qa/vision-model-trial/luna-max/report.md`.

**Sol reasoning-effort mini comparison:** The same two frozen icon-stress cards scored 68.859 at
`high`, 69.099 at `xhigh`, and 80.166 at `max`, with 0/2 exact sidecars at every effort. X-High nearly
doubled median latency without a material outcome change. Max improved prose/aggregate scoring but
confidently promoted a wrong semantic icon on both cards (`lander`→`autodestruction` and
`shootDieCritical`→`shootDieAmmoLoss`). These two cases are not a production qualification; they do
show that more reasoning does not replace morphology-first icon comparison or deterministic sidecar
validation. Evidence: `docs/qa/vision-model-trial/sol-xhigh-mini/report.md`,
`docs/qa/vision-model-trial/sol-max-mini/report.md`.

**Required elements:**
- Include the complete relevant icon glossary in every vision turn.
- Assign every submitted image a stable asset ID; require exactly one separate result per ID and reconcile submitted/returned counts.
- Require morphology before meaning for each proposed icon: location, outer shape, internal marks, colors, closest plausible alternative, and one visible discriminating feature. If no discriminating feature is visible, flag it uncertain.
- Tell model: "False promotion is worse than deferral. If an icon is not established by visible morphology and the authoritative glossary, describe it literally as [ICON: color shape glyph] and flag UNCERTAIN — do not guess meaning."
- Transcribe visible text verbatim, preserving capitalization, headings, punctuation, and meaningful line or panel structure. Use `[illegible]` or `[clipped]`; never reconstruct expected text.
- Keep `readConfidence`, `classificationConfidence`, `uncertainties`, and `promotionDecision` separate. Self-reported high confidence never bypasses icon comparison, provenance, schema, or source-conflict gates.

**Icon reporting format:**
- Icons mixed with body text → embed inline like words: "Move the [SHIP] by 1 space in any direction."
- Bare/standalone icons (corner icons, etc.) → report with position: "Upper right: [CROSSED-OUT-GUN]"
- NO separate Icons summary line — no counting, no list
- Unknown icons → describe literally: "[ICON: white gun with red X] (UNCERTAIN)"

### Ambiguous canonical-icon comparison

- Do not let surrounding rules text decide an icon's identity. Semantic context can bias the read.
- Crop the disputed glyph with enough surrounding text to preserve its location, then build a labeled contact sheet containing every plausible canonical glossary image at a comparable scale.
- Match the internal glyph morphology first; use card semantics only as a secondary consistency check.
- Exact morphology is sufficient to confirm an identifier, but not necessary: printed cards can use artwork variants of a glossary icon. If no exact crop matches, consult the official definition/card anatomy and the user before declaring the icon unknown.
- Automatic Shotgun demonstrated the failure mode: the second effect's red triangle was temporarily treated as an unknown Burst glyph because of rulebook context, but direct comparison of the white skull/jagged mark against all six Shoot-die images proved it is `shootDieCritical`.
- Retain the contact sheet as QA evidence when a user correction changes or confirms the identifier. Example: `docs/qa/card-icon-comparisons/automatic-shotgun-shoot-die.png`.
- Never add or remove punctuation from a full-card view alone. Crop and upscale the exact word/icon boundary first. The period after EXPLOSIVES' first `[grenadeToken]` was present and the original JSON was correct; a full-card reread missed it.
- Preserve panel headings structurally with line breaks. Do not turn a printed heading into prose by inventing a colon. CHAIN OF COMMAND prints `COMMAND` and `REACTION` without colons; its JSON now retains those headings on separate lines.

**Compact output format:**
```
**Card N: filename.png**

MEDIA:/path/to/file.png

- **Title:** ...
- **Body:** ... (verbatim, icons embedded inline like [SHIP], [CHARACTER])
- **Footer:** ...
- **Upper right:** [ICON NAME] (if bare icon exists)
- **Cat:** Action card / Starting Item card / etc.
```

### Human-gated review of quarantined or unsorted components

- Work on exactly one asset per approval cycle. Do not inspect or present the next asset until the
  user approves the current one.
- Analyze the original pixels from scratch. A filename, current directory, prior model output, or
  tentative label is not evidence of component identity. Use parsed TTS object metadata or manifests
  only when provenance or component type cannot be established from the asset itself.
- Check orientation before presentation. If correction is needed, rotate the source file on disk and
  verify the saved result is upright before reporting it.
- Present the filename, absolute `MEDIA:` path, exact visible text with inline icons, proposed identity
  and destination/category, and only genuine uncertainties or conflicts; end with a direct approval
  question.
- Before approval, do not move, rename, delete, catalog, or write canonical data for the asset.
- Do not delegate these approval-gated reviews to subagents, batch workers, or unattended background
  jobs. The active agent must retain the one-item review state and stop at the approval gate.
- After approval, perform only the approved classification/catalog operation and the minimal structured
  sidecar the component requires. Verify changed files and structured data before reporting success;
  then present the next item and stop again for approval.

---

## WebUI Image Caching

- **Issue:** MEDIA: tags in WebUI may serve cached versions of rotated files
- **Symptom:** File on disk is correctly rotated, but preview shows old orientation
- **Workaround:** Hard-refresh browser, or add `?v=timestamp` query param to force reload
- **Verification:** Use `file` command or vision_analyze to confirm disk state

---

## Card Type Identification

- **Starting Item cards:** "STARTING ITEM / CHARACTER" header, no body text, art-only, landscape orientation
- **Action cards:** Have TITLE, BODY TEXT with game effect, FOOTER with character name, portrait orientation
- **Reaction panels:** Some action cards have REACTION section (e.g. CHAIN OF COMMAND)
- **Source filenames and folders are not authoritative:** identify the character/component from pixels and, when the escalation trigger applies, official sources. `combat-engineer-021.png` was actually the Heavy Gun Operator's Automatic Shotgun and was cataloged accordingly.
- **Preserve source fidelity:** transcribe each source exactly as it appears. If TTS card art differs from an official source, retain both transcriptions and record the discrepancy rather than silently rewriting either source.
- **Canonical implementation data is a separate decision:** cross-reference extracted assets against the applicable official rulebook, component references, and current official FAQ/errata before promoting text into game data.
- **Multi-owner action sheet:** `cards/character/heavy-gun-operator-045.jpg` is a 9×5 source sheet whose split children visibly contain action cards for several printed owners (including Recon, Heavy Gun Operator, Combat Engineer, Officer, and Medical Support). Its directory/name is source provenance only; classify every child from its printed footer.
- **Split-edge contamination:** some generated cells from that sheet contain visible text from a neighboring card. Keep the extra pixels in `visibleText`; do not fold them into the card body or force a canonical sidecar.
- **Focused icon verification:** a model can report `high` while confusing visually different glossary symbols (the `intruder`/`lander` pair was caught this way). For any new sidecar that claims glossary tokens, compare the actual card pixels directly against the labeled official glossary crops; defer mismatches or uncertain matches.
- **Large-provider inputs:** native uploads around 16–24 MB / 70–92 megapixels may repeatedly overload the vision provider. A high-quality, aspect-preserving derivative bounded to 4096 px is sufficient for broad component inspection; preserve the original source unchanged and record both source/upload dimensions and the transform in durable vision evidence.

---

## Source Authority and Conflict Resolution

Canonical data must come from the **most authoritative and up-to-date applicable source**, not merely the easiest source to extract.

Routine human review is intentionally lightweight: compare the card face with the established icon
glossary and present the transcription for approval. Do **not** add official-source searches or extra
consultation when the image and glossary produce a clear, high-confidence result. Escalate to the
source-authority workflow below only when confidence is low, an element is unknown, or evidence
conflicts. This trigger keeps ordinary review focused without weakening conflict resolution.

1. Current official FAQ, errata, amendment, or replacement text that explicitly overrides earlier material
2. Current official rulebook and official final component/card references
3. Older official material, with its edition/date recorded
4. TTS or other mod assets (secondary evidence; potentially prototype, stale, or misfiled)
5. Project interpretation or adaptation (must be explicitly labeled and approved)

Required process:

- When the escalation trigger applies, cross-reference the disputed text, icon, ownership, or classification against official sources before treating it as canonical.
- Establish source version, date, edition, and applicability; “newer” controls only when it is official and applies to the same component/rule.
- Preserve each conflicting source verbatim and document the exact differences.
- Do not silently pick whichever source supports the current extraction or implementation.
- If official sources conflict without a clear supersession rule, source dates/applicability are uncertain, or the choice would require interpretation, stop and involve a human. Record the human decision and its evidence rather than presenting it as publisher text.
- User/owner knowledge is valuable evidence for locating sources and resolving project policy, but does not silently rewrite official text.

**Never** assign meaning to an icon based on vision-model description alone. If the applicable official sources do not resolve it, describe it literally, flag it UNCERTAIN, and escalate when canonical data depends on the answer.

---

## File Paths

- Card images: `/home/smithers/nemesis-retaliation/assets/tts-mod/extract/v2-dl/tree/cards/`
- Icon templates: `/home/smithers/nemesis-retaliation/assets/tts-mod/icon-templates/`
- Rules corpus: `/home/smithers/nemesis-retaliation/docs/rules/`
- This document: `/home/smithers/nemesis-retaliation/assets/tts-mod/notes/card-extraction.md`
- Current progress and approval gates: `/home/smithers/nemesis-retaliation/todo.md`
