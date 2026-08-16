# Continuous Fire source-fidelity audit

- TTS card face: `assets/tts-mod/extract/v2-dl/tree/cards/character/heavy-gun-operator-035.png`.
- TTS object: `CardCustom` GUID `f97ad0`, card ID `570500`, FaceURL in the Heavy Gun Operator action deck (`c8f207`).
- Printed text: `If you have [ammoToken] on your BF Gun, discard any [actionCard] to deal 1 Hit in an adjacent Corridor per [actionCard]. Then, you may Burst with the BF Gun.`
- The ammo-token and action-card symbols were confirmed against the canonical page-40 glossary crops. Comparison: `docs/qa/card-icon-comparisons/continuous-fire-icons.png`.
- The current official rulebook identifies Automatic Shotgun, not BF Gun, as the Heavy Gun Operator Character Item. BF Gun and Continuous Fire are absent from the current official rulebook and FAQ.

Decision: treat Continuous Fire as an obsolete/prototype TTS action card tied to the rejected BF Gun prototype. Do not add it to canonical card data. Retain the extracted TTS face and this audit as provenance.
