# Architecture

`cli.py` / `gui.py` → `engine.scan()` → `video.py` + `subtitles.py` → `report.py`.

`models.py` contains validated immutable settings and finding/cue types. Engine validates local inputs and an unused output path, probes media, runs one analysis pass, inspects subtitles, attaches bounded visual evidence, and serializes three outputs. Originals are read only. Intermediate reports are staged in a temporary sibling directory, then moved into a newly created output directory. The last move sequence is not a filesystem transaction; an I/O failure can leave a partial output directory.

Video analysis: normalize presentation timestamps with `setpts=PTS-STARTPTS`, scale to width 320, run blackdetect and freezedetect, select scene-score transitions, parse FFmpeg stderr. Adjacent scene-change times define shot intervals. This is not a learned defect classifier. Thresholds and FFmpeg version influence results. Frame references are requested presentation times, not exact returned frame timestamps.

Subtitle analysis: strict SRT blocks → NFC-normalized visible text → independently test time validity, bounds, order, speed and line counts. Sorted intervals track the furthest-ending prior cue to detect nested overlaps. Reports show one prior overlapping cue per later cue, not every overlapping pair.

JSON schema v1 fields: `schema_version`, `version`, UTC `created_at`, `media` or null, `subtitle` or null, `config`, `warnings`, `findings`. A finding has `code`, `start`, `end` (seconds), `title`, `detail`, `severity` (`error` or `review`), optional `cue`, and `evidence` entries with label, requested time, JPEG data URI. Malformed blocks have no usable time and are reported at 0. There is no confidence score because no calibrated model exists.

No mandatory third-party Python dependency. FFmpeg binaries are external and not distributed here. Future editor adapters should consume the JSON rather than scraping HTML. Keep core checks independent from any AI provider or editor.

Review v1: exact canonical report SHA-256 binding, zero-based indices, states pending/approved/needs_fix and notes up to 2000 characters. Comparison is one-to-one nearest-time matching by code/cue and both boundaries within tolerance, with detector configuration and check-scope guards. No inferred repair or automatic review transfer.
