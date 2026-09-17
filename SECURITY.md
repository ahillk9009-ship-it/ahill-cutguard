# Security

CutGuard v0.1 is an alpha. It invokes local FFmpeg/ffprobe binaries without shell interpolation and restricts input protocols to file/pipe. This is not a sandbox for malicious media; keep FFmpeg current and process untrusted files in an isolated environment.

Reports escape input-derived text and do not load remote scripts, fonts or images. Reports embed source frames and file names; do not upload private reports publicly.

For vulnerabilities, use the repository's private vulnerability reporting facility when the maintainer enables it. Do not include sensitive footage or exploit details in a public issue. No private reporting address or repository endpoint has been configured in this source bundle yet.
