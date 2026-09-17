# Roadmap

These are planned, not implemented features.

## After 0.2 — Trust and editor workflow

- Field validation with at least 5 editors and 20 shareable clips (internal target, not an OSS program requirement).
- Labeled positive/negative examples and precision/recall by detector; include intentional flashes, fades, title cards, fast action and low-motion shots.
- Validate the implemented review import/export in real browsers and add timeline alignment to comparison.
- Validate variable frame rate, rotated/HDR media and nonzero timestamp offsets.
- Speed up evidence extraction with a batched decode.
- Validate one editor marker adapter end-to-end before claiming support.

## 0.3 — Korean caption workflow

- Optional word alignment; measure Korean alignment error on licensed references.
- Caption layout/safe-area checks with explicit font and canvas information.
- Export proposed SRT changes to a new file for review.

## Later

- Optional MCP interface after core/API stabilization.
- Identity/wardrobe consistency research with authorized reference images and labeled angle/lighting changes.
- Windows installer after reliable platform smoke tests.

Do not claim automatic fixes, human-equivalent judgment or model-independent identity accuracy without a benchmark.
