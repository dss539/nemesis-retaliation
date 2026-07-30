# Digital Adaptations

This ledger records only deliberate, source-explicit digital adaptations that are intended to remain.

It must never contain:

- bugs or incomplete rules implementation;
- QA failures or latent failures;
- known differences that must be repaired for rules faithfulness;
- presentation facts such as using a digital board; or
- multiplayer/session policies.

## Recorded adaptations

### DA-001 — Action resolution UI order: target before payment

- **Tabletop:** the player declares an action and discards its card cost, then resolves the effect.
- **Digital:** the UI sequences declare → target → pay → confirm as one cancellable transaction; the card cost is chosen and paid at confirm, before any effect resolves.
- **Why:** prevents paying for an action that turns out to have no valid target on a touch UI.
- **Rules outcome:** identical — cost is always fully paid before the effect resolves; the player always chooses which cards to discard (no auto-pay).
- **Reference:** `docs/design/play-area-design.md`, Action/card loop.

Implementation failures belong in QA evidence and the project issue tracker, where their required disposition is repair—not acceptance as a “deviation.”
