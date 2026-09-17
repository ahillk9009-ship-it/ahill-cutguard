# Validation record — 2026-09-16

## Executed locally

- Python 3.12.14, Linux, FFmpeg/ffprobe 6.1.1.
- `python -m unittest discover -s tests -v`: **19 tests passed**, including FFmpeg integration; no skips in this environment.
- Wheel built successfully with setuptools; installed without dependencies into a new isolated venv. The installed `cutguard` entrypoint was run outside the source tree and produced a valid subtitle report.
- Synthetic 7-second, 25 fps fixture detected:
  - white 2-frame cut: 2.000–2.080 s;
  - black segment: 4.080–4.400 s;
  - blue static segment: 4.400–6.000 s.
- Combined demo: 9 findings (3 video, 6 subtitle), 1 structural/range error and 8 review candidates. This counts findings, not unique defects.
- Video SHA-256 remained unchanged after scanning. A moving test pattern returned no visual findings.
- Corrupted media returned execution error 2 and no clean report. Existing report paths were protected. CI error findings returned exit code 1.
- SRT tests cover BOM/CRLF, CP949, malformed timestamps, empty input, nested overlaps, touching intervals, duplicate IDs, ordering, reversed duration, video bounds and Korean reading speed.
- HTML escaping tested for injected file names and warning text.

## Not established

- Accuracy/precision/recall on real productions, speed gains, or user adoption.
- Windows execution, macOS execution, interactive Tk GUI, or hosted GitHub Actions runs.
- Full browser visual/interaction inspection: attempted, but the environment had no Chromium binary and browser download timed out. HTML generation/escaping passed; visual layout and browser controls still require manual review.
- VFR/HDR/rotated media, arbitrary codecs, offset-timestamp correctness or long-form performance.
- Premiere/Resolve import, AI/identity checks, speech synchronization, or automatic repair.

This fixture is a regression test, not an evaluation dataset. Passing it does not imply all real defects will be found or that reported candidates are mistakes.

## 0.2.0 follow-up — 2026-09-17

28 unittest tests passed (19 prior + 9 review/comparison tests), no skips. Review export/import and wrong-report rejection passed in a simulated DOM using Node. This is not a real-browser test. Dummy faulty report: 7 findings; clean reference: 0; comparison: 0 remaining, 7 no-longer-detected, 0 new. A disappearance is not proof of repair. Windows GUI and real-browser testing remain outstanding. New wheel installed and CLI smoke-tested.

## 0.2.1 pre-publication — 2026-09-17

32 unittest tests passed, no skips. Four additional tests cover malformed external reports, BOM JSON, invalid times and missing FFmpeg diagnosis. Live cloud browser bootstrap succeeded but opening the local report was rejected by browser URL security policy; no bypass attempted. Actual browser import/download/visual checks remain unverified. Windows GUI cannot be tested in this Linux runtime.
