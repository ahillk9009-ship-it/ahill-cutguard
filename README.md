# Ahill CutGuard

**Local-first video and subtitle QC with reviewable evidence.**

CutGuard turns suspicious video segments into time-coded review candidates, with before/during/after images, a portable Korean HTML report, JSON and generic CSV markers. Built for short-form editors who need to inspect stray cuts, black frames, freezes, and subtitle timing/reading problems.

**Status: v0.2.2 alpha.** Rule-based inspection, not an AI model or automatic editor. It never edits source media, calls a paid API, or uploads your footage. No Python runtime dependencies; video checks require an external FFmpeg installation.

[한국어 시작 안내](QUICKSTART_KO.md) · [Architecture](docs/ARCHITECTURE.md) · [Validation](docs/VALIDATION.md) · [Roadmap](docs/ROADMAP.md)

## Quick start

Requirements: Python 3.10+; FFmpeg and ffprobe on PATH for video inspection (tested with FFmpeg 6.1.1). Tkinter is optional, for the desktop launcher only.

From the extracted source folder, no Python package installation is required:

```bash
python -m cutguard scan examples/dummy-lab/media/02-faulty.mp4 --srt examples/dummy-lab/media/02-faulty.srt --out my-first-report
```

Or install the package locally:

```bash
python -m pip install .
cutguard scan input.mp4 --srt subtitles.srt --out review-001
```

The package is not published on PyPI. The `ahill-cutguard` distribution name has not been reserved.

Desktop launcher:

```bash
python -m cutguard gui
```

Windows: double-click `START_WINDOWS.bat` after installing Python (including Tcl/Tk) and FFmpeg. The launcher selects input files and an output parent folder, then opens the report in your default browser. Windows CI passed the real Tk event-loop/SRT scan smoke test; OS dialogs, batch-file launching and opening the default browser still require workstation checks.

## Checks

| Check | Default | Interpretation |
|---|---|---|
| Black segments | ≥ 0.08 s; ≥ 98% pixels below threshold 0.10 | Review intentional fades/blackouts |
| Freeze segments | ≥ 1 s; FFmpeg noise threshold -50 dB | Static shots/titles can be intentional |
| Very short shots | ≤ 0.12 s between detected scene changes | Candidate stray cut, not a proof of an error |
| Scene changes | FFmpeg scene score > 0.3 | Configurable; misses subtle transitions |
| SRT structure, duplicate indices, reversed/zero durations | Strict timestamp parser | Error |
| Subtitle overlaps | Any positive overlap | Review; simultaneous captions may be intentional |
| Subtitle out-of-bounds | End after supplied/probed video duration | Error |
| Reading speed | > 15 non-whitespace visible characters/s | Configurable heuristic, not a platform standard |
| Line length and count | > 22 characters/line; > 2 lines | Review; no font or screen geometry analysis |

SRT input supports UTF-8/BOM and CP949 fallback. Normalize Korean text to NFC for character counting. Empty or malformed blocks are reported, not silently ignored. Advanced SRT coordinate extensions are not supported.

## Outputs

- `report.html`: self-contained report with embedded JPEG evidence, category filters and review decisions and JSON export/import. Share the HTML as a file; no server or internet required. Review edits are not automatically saved: export the review JSON, then import it into this exact report.
- `report.json`: schema version `1.0`, settings, media metadata, findings and embedded evidence. No absolute source paths.
- `markers.csv`: generic seconds-based reference table. **Not** a tested Premiere/Resolve marker import format.

Existing output paths are rejected rather than overwritten. Evidence is limited to the first 24 visual findings by default (3 frames per finding); all findings remain in JSON/HTML. Reports may contain sensitive source frames and file names.

## CLI examples

```bash
# SRT only: no FFmpeg required
python -m cutguard scan --srt captions.srt --duration 30 --out captions-review

# Customize thresholds; skip frame extraction for a faster pass
python -m cutguard scan reel.mp4 --freeze-min 2 --short-cut-max 0.10 --cps-max 18 --thumbnails 0 --out reel-review

# CI: return 1 for structural/range errors, 2 for execution failure
python -m cutguard scan reel.mp4 --srt captions.srt --out ci-report --fail-on error
```

`--fail-on any` fails on review candidates too; default `none` returns 0 after a completed scan even when findings exist. `--timeout` (default 1800 s) applies per video scan; probe has a 60 s cap and evidence frames a 60 s per-frame cap. It is not a whole-job deadline.

## Python API

```python
from cutguard.engine import scan
from cutguard.models import Config
report = scan(video="reel.mp4", srt="captions.srt", output="review",
              config=Config(cps_max=18, thumbnails=6))
```

## Reproduce validation

```bash
python scripts/make_demo.py demo
python -m unittest discover -s tests -v
python -m cutguard scan demo/demo.mp4 --srt demo/demo.srt --out demo-check
```

The demo is generated with FFmpeg lavfi (no client footage). The fixture is not a real-world accuracy benchmark. See `docs/VALIDATION.md` for exact tested scope.

## Known boundaries

- Full video decode, analysis scaled to width 320px. Small artifacts may be lost. HDR/color-managed accuracy has not been established.
- Times are presentation seconds relative to the first video frame, not frame numbers or SMPTE drop-frame codes. VFR, edit lists and unusual timestamp offsets need further validation. First and last shots are excluded from short-cut detection unless bracketed by detected transitions.
- Evidence frames use requested times; actual decoded frames may differ by a frame. Each evidence extraction decodes up to its target time, so extraction can be slow for long videos; reduce `--thumbnails`.
- No audio alignment, OCR/burned-in captions, safe-area geometry, motion ghosting, identity consistency or automatic fixes in v0.2.
- No validated editor adapters, MCP server, model integration or online service yet.
- No live progress percentage, GUI cancellation yet.
- FFmpeg dependencies, behavior, and license are separate from this package; no FFmpeg binary is bundled.

## Open-source maintenance

MIT license for CutGuard code and original synthetic fixture setup. Contributions: [CONTRIBUTING.md](CONTRIBUTING.md). Please report reproducible failures with a minimal sample you may legally share. Private/client footage is not needed. Security: [SECURITY.md](SECURITY.md).

This project is independent and is not an official OpenAI product. No user/download/accuracy claims are made. The OSS support preparation checklist lives in `docs/OSS_READINESS_KO.md`.

## Technical references

- [FFmpeg blackdetect](https://ffmpeg.org/ffmpeg-filters.html#blackdetect)
- [FFmpeg freezedetect](https://ffmpeg.org/ffmpeg-filters.html#freezedetect)
- [FFmpeg select](https://ffmpeg.org/ffmpeg-filters.html#select_002c-aselect)
- [OpenTimelineIO](https://github.com/AcademySoftwareFoundation/OpenTimelineIO) — possible future adapter foundation; not included in v0.2.

## Review and revision comparison (0.2)

In the HTML report select Pending / Approved intentional effect / Needs fix, add a note, and export review JSON. Reopen the same report and import it. Decisions are SHA-256-bound to the report and never remove detections. Actual Chromium download/import, filtering, mismatch rejection and narrow-viewport overflow checks passed on Ubuntu and Windows CI. OS file-picker interaction, other browsers and full visual review remain unverified. CLI persistence is tested.

```bash
python -m cutguard review examples/faulty-v020/report.json --finding 3 --status needs_fix --note "stray cut" --out my-review.json
python -m cutguard review examples/faulty-v020/report.json --load my-review.json --finding 0 --status approved --note "intentional captions" --out my-review-2.json
python -m cutguard compare examples/faulty-v020/report.json examples/clean-v020/report.json --out my-comparison.json
```

Finding indices are zero-based. The comparison returns remaining, no_longer_detected and newly_detected items with a configurable time tolerance. It rejects different detector settings or video/subtitle check scopes. It does not align shifted edits or prove repair. Reviews are not carried across reports. Outputs must be new files.

Current verification and publication assessment: [docs/RELEASE_VERIFICATION_KO.md](docs/RELEASE_VERIFICATION_KO.md). The repository remains private; public release is not authorized. This is an experimental alpha, not a production reliability claim.

## Installation diagnosis (0.2.1)

Run `python -m cutguard doctor` or double-click `CHECK_WINDOWS.bat`. It checks Python, FFmpeg/ffprobe availability and optional Tkinter import. It does not install software or prove that the GUI works. Video-ready returns 0, missing prerequisites returns 1. SRT-only CLI does not require FFmpeg. Invalid external report JSON is rejected with exit 2 before creating output.

## Release gates

`python qa/local_gate.py` runs all local tests and fails if any test is skipped or FFmpeg is unavailable. The source import commit `4c05c3f` passed tests and release-check: Windows Tk, Ubuntu/Windows Chromium and wheel/sdist metadata. See [verification evidence and limits](docs/RELEASE_VERIFICATION_KO.md) and [qa/README_KO.md](qa/README_KO.md). The original `demo/demo.mp4` is included with its handoff blob SHA and byte size verified, completing the 68-file source set. The full 33-test suite also passed locally on Windows with FFmpeg. See [PR #1](https://github.com/ahillk9009-ship-it/ahill-cutguard/pull/1) for the latest commit's CI and merge status. No automatic publishing is configured. OS-dialog and default-browser workstation checks remain outstanding, so this is an experimental alpha, not a validated stable release.
