# CutGuard contributor instructions

Keep the core local-first with no implicit network calls or source media mutation. Do not label a heuristic candidate as a confirmed editing error. Preserve stable finding codes and JSON schema compatibility. Prefer standard-library implementation unless a dependency solves a measured requirement.

Validate changes with `python -m unittest discover -s tests -v`. Video integration tests require FFmpeg and ffprobe; report skips rather than claiming a full pass. Include a normal/intentional-edit case when adding a detector. Do not add private footage, secrets, or generated usage metrics to the repository.

For user-visible changes, update README and CHANGELOG. Publish only when the maintainer has authorized publication. Do not claim untested editor or platform support.
