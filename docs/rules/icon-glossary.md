# Nemesis: Retaliation — Canonical Icon Glossary

**Source:** Official rulebook, page 40 (icon glossary).
**Supporting rules:** Shoot and Burst results, page 33; Noise Hazard result, page 24; Number of Characters symbol, page 10 and the official Objectives Help Sheet.
**Authority:** This glossary is the authoritative reference for icon identifiers used in card extraction and game data.

The printed page-40 glossary contains **49 distinct icons**. This project also records one official Objective-card metadata symbol from page 10 and the Objectives Help Sheet, for **50 identifiers total**. Bold camelCase terms below are project identifiers. Where page 40 groups several variants under one printed label, the identifiers distinguish visible variants without inventing additional rules meaning.

---

## Dice Icons

### Shoot Die Results

Page 40 groups these as **“Shoot die icons — Specific results on a Shoot die.”** Page 33 supplies the names of the two symbolic results.

- **shootDie2** — Red triangle with white “2” (`assets/icons/dice/shoot-die-2.png`)
- **shootDie3** — Red triangle with white “3” (`assets/icons/dice/shoot-die-3.png`)
- **shootDie4** — Red triangle with white “4” (`assets/icons/dice/shoot-die-4.png`)
- **shootDie5** — Red triangle with white “5” (`assets/icons/dice/shoot-die-5.png`)
- **shootDieAmmoLoss** — Red triangle with three white cartridges; “You’ve lost too many bullets,” so spend Ammo (`assets/icons/dice/shoot-die-ammo-loss.png`)
- **shootDieCritical** — Red triangle with white skull; Critical hit (`assets/icons/dice/shoot-die-critical.png`)

### Burst Die Results

Page 40 groups these as **“Burst die icons — Specific results on a Burst die.”**

- **burstDie1** — Purple square with white “1” (`assets/icons/dice/burst-die-1.png`)
- **burstDie2** — Purple square with white “2” (`assets/icons/dice/burst-die-2.png`)
- **burstDie3** — Purple square with white “3” (`assets/icons/dice/burst-die-3.png`)
- **burstDie4** — Purple square with white “4” (`assets/icons/dice/burst-die-4.png`)
- **burstDieAdditionalEffects** — Purple square with four white corner marks; check the used Weapon or Action for additional effects (`assets/icons/dice/burst-die-additional-effects.png`)

#### Pre-release die-result artwork

Canonical identifiers encode the game result, not a promise that every source uses identical final artwork. Source-scoped reviewed aliases are recorded in `docs/qa/card-symbol-semantic-resolutions.json`. In the audited pre-release/prototype weapon faces, a purple square with a white exclamation mark is `burstDieAdditionalEffects`, and a red triangle with an older curved ammunition-magazine motif is `shootDieAmmoLoss`. Preserve the literal artwork in provenance while using the canonical semantic token in rules text. Do not apply either mapping to every purple exclamation or red triangle by appearance alone; the source tuple must be approved in the resolution registry.

### Noise Die Results

Page 40 groups these as **“Noise die icons — Specific results on a Noise die.”**

- **noiseDie1** — Yellow triangle with black “1” (`assets/icons/dice/noise-die-1.png`)
- **noiseDie2** — Yellow triangle with black “2” (`assets/icons/dice/noise-die-2.png`)
- **noiseDie3** — Yellow triangle with black “3” (`assets/icons/dice/noise-die-3.png`)
- **noiseDie4** — Yellow triangle with black “4” (`assets/icons/dice/noise-die-4.png`)
- **noiseDieHazard** — Yellow Hazard-result symbol (`assets/icons/dice/noise-die-hazard.png`)

---

## Map-Related Icons

### Item Types

Page 40 labels these, in order, **“Red, Yellow, Green Item — An Item of a specific type.”**

- **redItem** — Red item-type badge with three white cartridges (`assets/icons/map/red-item.png`)
- **yellowItem** — Yellow item-type badge with a white wrench (`assets/icons/map/yellow-item.png`)
- **greenItem** — Green item-type badge with a white cross (`assets/icons/map/green-item.png`)

### Markers and Tokens

- **computer** — Computer; shows whether a specific Room has computer-system access (`assets/icons/map/computer.png`)
- **fire** — Fire marker (`assets/icons/map/fire.png`)
- **malfunction** — Malfunction marker; shows whether a Room, Robot, or Heavy Item is broken (`assets/icons/map/malfunction.png`)
- **noise** — Noise marker (`assets/icons/map/noise.png`)
- **secure** — Secure token (`assets/icons/map/secure.png`)

### Corridors

Page 40 prints **three**, not six, Corridor icons. Corridors are undirected, so each icon represents one hex-grid axis. The rulebook says the rotation is important but does not print separate names for the three variants.

- **corridorEW** — E–W horizontal axis (`assets/icons/map/corridor-e-w.png`)
- **corridorNESW** — NE–SW diagonal axis (`assets/icons/map/corridor-ne-sw.png`)
- **corridorNWSE** — NW–SE diagonal axis (`assets/icons/map/corridor-nw-se.png`)

### Systems and Facility Tokens

- **lifeSupportActive** — Active Life Support Systems token (`assets/icons/map/life-support-active.png`)
- **lifeSupportInactive** — Inactive Life Support Systems token, crossed out (`assets/icons/map/life-support-inactive.png`)
- **hibernatoriumActive** — Active Hibernatorium token (`assets/icons/map/hibernatorium-active.png`)
- **hibernatoriumInactive** — Inactive Hibernatorium token, crossed out (`assets/icons/map/hibernatorium-inactive.png`)
- **lander** — Lander token (`assets/icons/map/lander.png`)
- **autodestruction** — Autodestruction token; white three-lobed warning symbol (`assets/icons/map/autodestruction.png`)

---

## Tactical Gear Tokens

- **oxygenToken** — Yellow Oxygen Tactical Gear token (`assets/icons/tactical-gear/oxygen-token.png`)
- **ammoToken** — Red Ammo Tactical Gear token (`assets/icons/tactical-gear/ammo-token.png`)
- **grenadeToken** — Purple Grenade Tactical Gear token (`assets/icons/tactical-gear/grenade-token.png`)
- **medpackToken** — Green Medpack Tactical Gear token (`assets/icons/tactical-gear/medpack-token.png`)

---

## Tactical Gear Slots

- **ammoSlot** — Red Tactical Gear slot for an Ammo token (`assets/icons/tactical-gear-slots/ammo-slot.png`)
- **grenadeSlot** — Purple Tactical Gear slot for a Grenade token (`assets/icons/tactical-gear-slots/grenade-slot.png`)
- **oxygenSlot** — Yellow Tactical Gear slot for an Oxygen token (`assets/icons/tactical-gear-slots/oxygen-slot.png`)
- **medpackSlot** — Green Tactical Gear slot for a Medpack token (`assets/icons/tactical-gear-slots/medpack-slot.png`)
- **anySlot** — Grey Tactical Gear slot for any token (`assets/icons/tactical-gear-slots/any-slot.png`)

---

## General Icons

- **character** — Character (`assets/icons/general/character.png`)
- **oxygen** — Oxygen in the Character supply, represented by numbers on the Character’s Oxygen counter (`assets/icons/general/oxygen.png`)
- **characterHealth** — Character Health points (`assets/icons/general/character-health.png`)
- **actionCard** — Action card (`assets/icons/general/action-card.png`)
- **robot** — Robot (`assets/icons/general/robot.png`)
- **notInCombat** — Not In Combat; an Action with this icon cannot be performed in a Room with Intruders (`assets/icons/general/not-in-combat.png`). Page 40 shows a white Intruder silhouette inside a red prohibition circle; printed Action cards may instead show a white gun crossed by a red X. These visually different symbols are artwork variants of the same semantic icon.
- **intruder** — Intruder (`assets/icons/general/intruder.png`)

---

## Objective Metadata Icons

The official rulebook calls the following the **Number of Characters symbol** (page 10). During Objective setup, remove cards whose printed threshold is higher than the number of Characters taking part. The official Objectives Help Sheet visibly pairs this symbol with thresholds such as `2+`, `3+`, `4+`, and `5+`. It is a setup/player-count marker, not the page-40 **Character** entity icon.

- **numberOfCharacters** — Number of Characters symbol; white person above cyan-blue concentric rings (`assets/icons/objectives/number-of-characters.png`)

---

## Usage in Card Data

Use the camelCase identifiers above.

- Inline icon: `"Discard 1 [ammoToken]."`
- Bare corner icon: `"upperRight": "notInCombat"`

```json
{
  "body": "Discard a [fire]. OR Discard 1 [grenadeToken] to resolve [shootDieCritical] against all [intruder] in an adjacent Corridor.",
  "upperRight": "notInCombat"
}
```

## Extraction Notes

The PNGs were re-derived from the official PDF’s page 40 at 400 DPI. The previous 20×20 dice files were not reused. Crops retain the source page background and native rendered size; punctuation and neighboring text are excluded. Category counts are:

- `assets/icons/dice/` — 16 files
- `assets/icons/map/` — 17 files
- `assets/icons/tactical-gear/` — 4 files
- `assets/icons/tactical-gear-slots/` — 5 files
- `assets/icons/general/` — 7 files
- `assets/icons/objectives/` — 1 file
