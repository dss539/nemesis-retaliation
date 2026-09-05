# 334-repair source-to-rule mapping — owner review packet

**Status:** proposal awaiting owner decision. No concise-corpus text has been changed. No approval decision has been made.

**Prepared:** 2026-09-04

## What this packet is

Every one of the 334 independently confirmed repair claims in `audit/repair/` is mapped to exactly one concrete concise-corpus edit. The mapping is split into seven cluster files (the same seven mutually exclusive clusters recorded in the repair sidecars). Each cluster file contains:

1. a per-ID table: verbatim source quote → target record → exact proposed sentence(s) → preserved boundary/open question;
2. `## Consolidated edits by target record`: the actual proposed text, one block per record, with the list of IDs each block satisfies;
3. `## Flags`: ambiguity, variant conflicts, partial existing coverage, and gameplay-consequence notes — listed, not acted on;
4. `## Closure`: mechanically counted `IDs assigned = IDs in table = IDs in consolidated blocks`.

| Proposal | Cluster file | IDs | Target records touched |
|---|---|---|---|
| P1 | `clusters/c1-reference.md` | 14 | FND-011, INT-001, INT-011 |
| P2 | `clusters/c2-endgame.md` | 68 | INT-011 (Objective / Mission Task source-occurrence table), FND-012, INT-010 |
| P3 | `clusters/c3-facility.md` | 72 | ACT-EXPLORE-001, FND-012, ACT-ROOM-001 (per-Room Help table), INT-009, INT-003, ACT-MOVE-001 Doors, RT-015, FND-008, INT-001 |
| P4 | `clusters/c4-character.md` | 58 | ACT-CARD-001 (per-card occurrence table), ITM-001, ACT-ROBOT-001, FND-009 (Anti-Aircraft secrecy), RT-012, INT-009 |
| P5 | `clusters/c5-items.md` | 52 | ITM-009 (exact Item-card occurrence table), ITM-002, ITM-005, INT-006, ACT-TRADE-001 |
| P6 | `clusters/c6-intruder.md` | 51 | RT-009 (Event-card table), INT-004 (Attack-card table), INT-007 (Queen Health), ACT-SHOOT/BURST/MELEE-001, ITM-005, FND-012, RT-012, ACT-ROOM-001, INT-003, INT-008 |
| P7 | `clusters/c7-setup.md` | 19 | FND-008, FND-009, FND-010, FND-011, ACT-TACTICAL-001, `icon-glossary.md` |
| **Total** | | **334** | |

Cluster ID lists are the `clusters/*.ids` files; they were regenerated from the `Cluster:` line of every `audit/repair/*.repair.md` sidecar and sum to 334. Each cluster file's closure line was verified against its `.ids` list (every ID appears in both the table and a consolidated block).

## Common treatment rules applied in every cluster

- **Verbatim over paraphrase.** Proposed sentences carry the source's quantities, modality (`must`/`may`/`cannot`), actor, and timing. Unresolved glyphs stay as the fragment's literal `[unresolved …]` / `[ICON: …]` / `[R..-I..]` tokens; no icon meaning is invented.
- **Card faces become occurrence tables.** Action, Item, Event, Attack, Queen Health, Exploration, Room Help, Objective, and Mission Task faces are added as one row per exact source occurrence (source path / unit ID), not merged by title.
- **Official vs. TTS variants stay separate.** Where a TTS face and an official occurrence share a title but differ (e.g. FACILITY RESTART, THE SUPPLY ROUTE, PRIMARY SAMPLES, SELF-SERVING, FLAMETHROWER, PLASMA GUN, TACTICAL HATCHET), both rows are added and the conflict is preserved. The TTS wording never replaces official wording.
- **Open questions are preserved, not closed.** Each block names the `OQ-*` / `SEM-Q-*` entries it touches and states that the edit does not resolve them.
- **Partial existing coverage is flagged, not dropped.** Where a drafter believed a fragment was partly covered already, it is listed under Flags for coordinator re-check; the ID still has a proposed edit.

## Items needing your attention before or at approval

These are the material judgment calls surfaced in the Flags sections. Full text is in each cluster file.

1. **Packaging-only sub-facts (P7).** `RB-P04-031` "8 Drones in 4 poses" and `RB-P05-034` "36 Adults in 6 poses": proposal keeps the model counts, drops the pose counts as packaging. `RB-P08-009` "place them on the table": the connect-the-border-pieces rule is kept; the surface wording is not made a mechanic.
2. **Facility-wide effects through Closed Doors (P3, `RB-P22-011`).** The rulebook p. 22 note says effects calling out "any object in the Facility" still work through Closed Doors. This sits beside the existing general blocking bullet in the Doors subsection; the proposal adds it as an explicit exception without reconciling scope further.
3. **Robot Malfunction wording conflict (P4).** Rulebook p. 37 and the Robot-card "even with a [malfunction]" faces are recorded as conflicting source assertions; no default chosen.
4. **Same-title Objective / Mission Task conflicts (P2).** Ten title groups have official/TTS differences (see P2 Flags). Each is added as separate rows; `OBJ-36` INSIDER INFORMATION stays metadata-only (partially occluded official copy).
5. **Item source conflicts (P5).** FLAMETHROWER, PLASMA GUN, TACTICAL HATCHET each have two TTS occurrences with different bodies; Yellow Robot Controller class conflict remains non-dispatchable under ITM-003.
6. **Flavor text on Private Objectives (P2).** Five personal-objective faces include dialogue text; the proposal records the operative condition only and flags the flavor text for your call on whether it should appear in the corpus at all.
7. **Explicitly base-game-irrelevant but retained (P3).** `RB-P24-044`/`045` (Insider icon has no base-game function / ignore it) are proposed as a boundary note so the icon cannot acquire a fabricated effect.

## Exact effect of approval

Approving a P-item authorizes, for that cluster only:

1. applying the consolidated edits in that cluster file to the named `docs/rules/` records (one repair commit, separate from verdict recording);
2. running the normal gate;
3. freshly rereading the corpus and performing the single allowed re-check per repaired ID;
4. moving each passing repaired fragment back to the audit root without its repair sidecar, so it can receive one fresh verifier verdict;
5. mechanical reconciliation and status updates.

Approval does **not** authorize: resolving any open question or preserved conflict; promoting TTS wording over official; semantic-layer work; implementation; pushing; or a pull request. Flags marked "coordinator re-check required" will be re-checked against the frozen corpus before the edit is applied, and any ID found already fully covered will be reported to you rather than silently dropped.

## Reply syntax

- `Approve P1-P7.`
- `Approve P1, P3, P7; hold P2, P4-P6.`
- `Amend P7: keep the pose counts.` (or any per-item amendment)
- `Defer.`
