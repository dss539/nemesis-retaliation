# Life Support token state classification

Assets:

- `assets/tts-mod/extract/v2-dl/tree/unsorted/token-011.png`
- `assets/tts-mod/extract/v2-dl/tree/unsorted/token-012.png`

Native pixel reads:

- token-011: `openai-codex:gpt-5.6-sol`, session `20260815_042635_dbfe44`
- token-012: `openai-codex:gpt-5.6-sol`, session `20260815_042901_1d4b38`
- focused icon comparison: `openai-codex:gpt-5.6-sol`, session `20260815_043307_72048f`

Each read used one image and zero tool calls. Redacted exports are stored beside this record.

Raw TTS provenance:

Three top-level anonymous `Custom_Token` objects (`f77dd8`, `f9e4aa`, and `9b7225`) share the same state structure.

- Primary `CustomImage.ImageURL` is token-011.
- Primary tags are `LifeSupportOff` and `Toggle`.
- `States.1.CustomImage.ImageURL` is token-012.
- State 1 tags are `LifeSupport` and `Toggle`; two state records also carry the nickname `Life Support`.
- Both states are locked, non-stackable tokens with thickness `0.14500030875205994`.

Pixel and morphology findings:

- Both files are 561×238 RGBA UV-style token textures.
- token-011 is the gray/off texture; token-012 is the cyan/on texture.
- A labeled comparison against the verified `lifeSupportInactive`, `lifeSupportActive`, `oxygen`, and `oxygenToken` glossary images found that both central glyphs match `lifeSupportActive` after rotation (97–99% confidence).
- The gray/off TTS texture does not contain the canonical inactive icon’s defining prohibition slash. It communicates the off state through gray artwork and TTS state tags, not through the glossary’s crossed-out `lifeSupportInactive` glyph.

Classification:

- token-011 → `tokens/status/life-support-inactive.png`
- token-012 → `tokens/status/life-support-active.png`

This is a source-art difference, not an unresolved identity.
