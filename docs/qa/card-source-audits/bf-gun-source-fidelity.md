# BF Gun source-fidelity audit

- TTS object GUID: `427c1a`, named `BF GUN`, in the Heavy Gun Operator bag.
- FaceURL: `assets/tts-mod/extract/v2-dl/tree/cards/character/heavy-gun-operator-025.png`.
- BackURL: `assets/tts-mod/extract/v2-dl/tree/cards/character/heavy-gun-operator-038.png` (`STARTING ITEM — HEAVY GUN OPERATOR`).
- The face uses a purple exclamation-mark result that does not match the current official page-40 `burstDieAdditionalEffects` glyph (four corner brackets). Comparison: `docs/qa/card-icon-comparisons/bf-gun-special-result.png`.
- The current official rulebook identifies Automatic Shotgun, not BF Gun, as the Heavy Gun Operator Character Item. BF Gun is absent from the current rulebook and FAQ.

Decision: treat BF Gun as an obsolete/prototype TTS starting item and do not add it to canonical card data. Retain both TTS images and this audit as provenance.
