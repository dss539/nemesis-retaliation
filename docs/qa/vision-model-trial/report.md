# Vision-model trial: card-176

Date: 2026-08-13
Image: `assets/tts-mod/extract/v2-dl/tree/unsorted/card-176.jpg`
Models: `openai-codex:gpt-5.6-sol` and `ollama-cloud:qwen3.5:397b`

## Method

Each model received the same original 2132×2142 JPEG through Hermes CLI's native `/image` attachment path and the same blind prompt. The prompt prohibited reading files, using tools, consulting prior context, and guessing unreadable text. Both native sessions report zero tool calls. The model/provider identities are recorded in the session exports.

Ground truth was checked after both runs against enlarged image crops, independent Tesseract passes, and the official rulebook's reproduction of the same Objective Help Sheet. Official text was used to identify icon semantics that pixels alone did not resolve; it was not exposed to either model during extraction.

The first one-shot attempts were invalid because they did not deliver pixels: GPT's auxiliary vision route had no configured provider, while Qwen's session lacked `vision_analyze`. Those refusal outputs are retained as `*-invalid-aux-*` and are excluded from model-quality scoring.

## Conservative rubric

- Exact readable text and printed formatting: 30
- Icon/symbol handling: 20
- Compliance and uncertainty discipline: 20
- Structural/layout accuracy: 15
- Completeness: 15

Manual criterion scores for this one image:

| Model | Text | Icons | Discipline | Structure | Completeness | Total |
|---|---:|---:|---:|---:|---:|---:|
| GPT-5.6 | 27 | 14 | 19 | 14 | 14 | 88/100 |
| Qwen 3.5 397B | 21 | 6 | 8 | 8 | 13 | 56/100 |

These scores compare one difficult reference sheet, not the models' universal vision quality.

## Findings

### GPT-5.6

Strengths:

- Preserved printed line breaks, line-end hyphenation, capitalization, and punctuation much more faithfully.
- Correctly identified the sheet and its two major regions.
- Withheld words replaced by uncertain pictograms instead of inventing nouns.
- Described the Escort Mission icon as an uncertain rounded/mechanical figure. The official source confirms it is the Robot, so this was appropriately conservative.
- Described the Facility Restart symbol without guessing a printed word.
- Clearly separated unreadable/overlapped material from transcribed text.

Remaining issues:

- Some symbols were described rather than correctly identified, including the Robot, Lander, Character, activation-state, and player-count imagery.
- The Objective-choice draw symbol was rendered as a boxed `A`; exact visual identity remains better represented as an icon placeholder unless matched to the glossary.
- A few punctuation glyphs may be normalized (`—` versus the printed dash).

### Qwen 3.5 397B

Strengths:

- Correctly identified the component, main headings, major definitions, card titles, and most large mission text.
- Recovered the broad two-column structure and most mission-task content.

Material problems:

- Violated the explicit no-guess rule by naming several uncertain icons from context.
- Misidentified the Escort Mission Robot icon as a `marine icon`.
- Called player-count imagery a marine/helmet symbol and reported a flame/fire icon without sufficient pixel evidence.
- Suggested the Facility Restart icon meant `secured` or `activated`, inserting candidate words where the image contains a symbol.
- Normalized paragraph flow, line breaks, hyphenation, apostrophes, and dash punctuation despite the verbatim requirement.
- Introduced at least one punctuation error: `Life Support Control C)`.
- Produced an internally inconsistent layout count: “10 objective cards,” followed by rows totaling 13 cards; the actual sheet shows seven overlapping Mission Objective cards above eight Mission Task cards.
- The confidence statement was too high relative to its semantic icon errors and layout error.

## Conclusion

GPT-5.6 was decisively better for this card-extraction workflow. Its main advantage was not just text recognition: it obeyed the uncertainty policy and avoided converting unclear icons into confident game terms. Qwen recovered much of the prose but made exactly the class of contextual icon guesses that previously caused concern.

For production review, use GPT-5.6 for vision extraction and retain the established safeguards: one image at a time, direct glossary matching for icons, explicit uncertainty, and human approval for unresolved or low-confidence elements. This trial is not authorization to use Qwen for further vision work.

## Evidence

- Frozen prompt: `prompt.txt`
- GPT native session: `gpt-5.6-native-session.jsonl` (`20260813_191417_9379c3`)
- Qwen native session: `qwen3.5-397b-native-session.jsonl` (`20260813_191417_64fb19`)
- Enlarged crops: `top.png`, `middle.png`, `bottom.png`, `facility-restart.png`
- Excluded routing failures: `gpt-5.6-invalid-aux-attempt.txt`, `qwen3.5-397b-invalid-aux-attempt.txt`
