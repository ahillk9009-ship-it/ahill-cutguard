# Changelog

## Unreleased

- Use the report's recorded version in the HTML header, matching the footer instead of displaying a fixed `0.1`. Existing reports and review JSON are unchanged.

## 0.2.2 — 2026-09-17

- First public GitHub alpha pre-release, with a source ZIP and documented verification limits; no PyPI or standalone executable distribution.
- Record workstation launcher, native file selection and scan completion checks; manual report visuals and review-file interactions remain unverified.

- Fail-closed local release gate with structured evidence; skipped tests cannot pass.
- Add real-browser and Windows Tk acceptance scripts and non-publishing CI jobs; source import commit `4c05c3f` passed Ubuntu/Windows Chromium, Windows Tk and packaging checks.
- Record remote test evidence and remaining OS-dialog/default-browser limits.
- Include the original synthetic demo video, verified against the handoff blob SHA and byte size, completing the 68-file source set.
- Handle missing GUI display with an actionable CLI error instead of a traceback.
- Add source-distribution manifest for tests, QA and examples.


## 0.2.1 — 2026-09-17

- Reject malformed external reports, invalid schemas and non-finite/negative times before output.
- Add read-only doctor command and Windows prerequisite-check launcher.
- Expand regression tests to 32; document pre-publication gates and GitHub target.


## 0.2.0 — 2026-09-17

- Report-bound review JSON with status, notes, import/export controls and CLI.
- Time-based revision comparison with setting/scope compatibility checks.
- Added normal/faulty/intentional synthetic fixtures and 9 regression tests.
- Browser controls remain experimental; Windows GUI remains unverified.


## 0.1.0 — 2026-09-16

- Initial alpha: FFmpeg black/freeze/short-cut candidates.
- SRT format, overlaps, duration, reading speed, line and ordering checks.
- Portable Korean HTML evidence report, versioned JSON and generic CSV.
- CLI with CI exit codes, Python API, optional Tk desktop launcher.
- Synthetic reproducible fixture and unittest suite.
- No public release, real-world benchmark or Windows validation claimed.
