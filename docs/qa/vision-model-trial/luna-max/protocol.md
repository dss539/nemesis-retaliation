# Luna Max native-vision experiment protocol

Date: 2026-08-15
Model route: `openai-codex:gpt-5.6-luna`
Reasoning effort: `max`
Input route: Hermes CLI native `--image` attachment; auxiliary vision is prohibited.

## Question

Can Luna Max reliably perform the Nemesis: Retaliation asset workflow: pixel-faithful OCR, canonical glossary-icon mapping, component categorization, minimal sidecar construction, and conservative deferral when pixels do not support a high-confidence result?

## Blinding and isolation

- One image per fresh Hermes process.
- Each source is exposed through a neutral temporary filename.
- `--safe-mode` prevents repository rules, user memory, skills, plugins, and project context from entering the model prompt.
- The prompt contains the complete canonical icon glossary because production extraction requires it.
- The model is prohibited from tools, filenames, notes, sidecars, neighboring files, rulebooks, web sources, and prior transcripts.
- Ground truth is frozen by source and sidecar SHA-256 in `sample.json` before inference.
- Raw stdout/stderr, parsed output, latency, return code, model route, reasoning level, and prompt hash are retained.

## Sample

Twelve cases:

- Eight human-approved card/image sidecar pairs spanning action cards, starting items, a dense help card, inline icons, standalone icons, punctuation, and panel structure.
- The exact dense Objective Help Sheet used in the 2026-08-13 Sol-vs-Qwen trial, enabling a direct comparison with Sol's previously scored 88/100 result.
- One known Life Support status texture.
- One deferred/clipped help sheet that should remain deferred if material details are unresolved.
- One ambiguous creature/bag image that should not receive a pixel-unsupported canonical function or filename.

## Scoring

Human-approved cards are scored programmatically out of 100:

- Parseable schema: 5
- Exact title: 5
- Printed text/type-line fidelity: 40
- Canonical icon fidelity: 20
- Minimal sidecar fidelity: 20
- Correct promote/defer decision: 10

The dense historical comparator uses its existing conservative rubric:

- Exact readable text and printed formatting: 30
- Icon/symbol handling: 20
- Compliance and uncertainty discipline: 20
- Structural/layout accuracy: 15
- Completeness: 15

Known and ambiguous non-card/deferred cases are manually scored against the frozen expectations in `sample.json`, with special weight on avoiding invented identity or function.

## Decision bands

- 90–100: production candidate for high-confidence first-pass extraction, still subject to established verification gates.
- 80–89: useful reviewer/triage model; not trusted for unattended canonical promotion.
- 70–79: assistive only; material review burden remains.
- Below 70: unsuitable for this workflow.

Regardless of aggregate score, any repeated semantic icon guessing, invented unreadable text, or confident promotion of the deliberately ambiguous cases is a critical failure for unattended use.
