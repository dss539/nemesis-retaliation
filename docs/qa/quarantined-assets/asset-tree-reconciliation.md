# Asset-tree reconciliation verification

Scope: post-review integrity audit for `assets/tts-mod/extract/v2-dl/tree/`.

The first full audit found older bookkeeping drift that predated the final quarantined-item moves:

- five previously approved card source images had been moved into canonical/QA locations without retaining extraction-tree copies;
- six manifest byte sizes were stale after prior rotations or other verified image rewrites;
- the catalog omitted five generated cards directly under `cards/game/action/`.

No approved canonical card data or classification was changed. Byte-identical copies were restored at the original manifest paths from these approved artifacts:

- `combat-engineer-010.png` ← `cards/character/combat-engineer/action/explosives.png`
- `combat-engineer-012.png` ← `docs/qa/card-source-audits/automatic-shotgun-tts-back.png`
- `combat-engineer-017.png` ← `cards/character/combat-engineer/action/chain-of-command.png`
- `combat-engineer-020.png` ← `cards/character/combat-engineer/action/pyrotechnics.png`
- `combat-engineer-021.png` ← `cards/character/heavy-gun-operator/starting-item/automatic-shotgun.png`

The manifest sizes were reconciled to the current verified files for `combat-engineer-012.png`, `combat-engineer-021.png`, `greenitem-029.png`, `heavy-gun-operator-025.png`, `heavy-gun-operator-038.png`, and `contractor-052.jpg`. The catalog now identifies 444 manifest assets separately from generated sprite-sheet splits.

Final deterministic checks:

- manifest entries: 444
- unique URLs: 444
- unique paths: 444
- manifest bytes: 930,117,659
- missing files: 0
- size mismatches: 0
- decode/format failures: 0
- formats checked: 197 PNG, 180 JPEG, 54 OBJ, 10 Unity asset bundles, 3 PDF
- catalog section count mismatches: 0
- direct files represented by catalog sections: 449 (444 manifest assets plus 5 direct generated action cards; nested generated split folders are additional)
- files remaining directly under `unsorted/`: 0

All five restored files were SHA-256 verified byte-identical to their stated sources.
