# Contributing

Start with a small reproducible editing problem. A false positive on intentional footage is as useful as a missed error. Open an issue before a large change; include OS, Python/FFmpeg versions, the exact command, thresholds, expected and actual time ranges. Use synthetic or explicitly shareable samples only.

## Development

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
```

Core uses Python standard library only. FFmpeg is required for integration tests. Tests skip video cases if the tools are missing; maintainers must run the full suite before release. Keep machine-readable finding codes stable. New detectors must include positive, negative and boundary fixtures and describe likely false positives. Do not add network calls or media uploads to the default flow.

## Pull requests

Explain the user problem, behavior change, validation, and limitations. Keep fixtures small and generated when possible. Include a changelog entry for user-visible changes. Contributions are under the repository MIT license.

## Release checklist

- Run the full suite with FFmpeg, inspect generated HTML, smoke-test source and wheel installations.
- Test Windows desktop flow and report any untested platform explicitly.
- Bump package/project versions together, update CHANGELOG and validation environment.
- Publish release notes, source archive and wheel after maintainer review.
- Respond to issues, record fixes, and preserve compatibility or document breaking changes.
