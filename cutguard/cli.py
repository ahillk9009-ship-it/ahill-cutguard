import argparse
from pathlib import Path
import sys
from . import __version__
from .engine import scan
from .models import Config
from .video import ScanError


def main(argv=None):
    parser = argparse.ArgumentParser(prog='cutguard', description='Local video and SRT quality checks. No source modification.')
    parser.add_argument('--version', action='version', version=__version__)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('doctor', help='Check Python, FFmpeg and optional Tkinter')
    sub.add_parser('gui', help='Open the desktop file picker (Tkinter required)')
    check = sub.add_parser('scan', help='Inspect local video and/or SRT')
    check.add_argument('video', nargs='?', type=Path)
    check.add_argument('--srt', type=Path)
    check.add_argument('--out', type=Path, default=Path('cutguard-report'))
    check.add_argument('--duration', type=float, help='Video duration for SRT-only checks, in seconds')
    for option, default in [('black-min', 0.08), ('freeze-min', 1.0), ('scene-threshold', 0.3), ('short-cut-max', 0.12), ('cps-max', 15.0), ('timeout', 1800.0)]:
        check.add_argument('--' + option, type=float, default=default)
    check.add_argument('--line-max', type=int, default=22)
    check.add_argument('--thumbnails', type=int, default=24, help='Maximum visual findings with evidence (0 disables; max 200)')
    check.add_argument('--fail-on', choices=['none', 'error', 'any'], default='none', help='Exit 1 when selected findings exist; execution failures exit 2')
    review = sub.add_parser('review', help='Create or update a report-bound review file')
    review.add_argument('report', type=Path)
    review.add_argument('--load', type=Path)
    review.add_argument('--out', type=Path, required=True)
    review.add_argument('--finding', type=int)
    review.add_argument('--status', choices=['pending','approved','needs_fix'], default='pending')
    review.add_argument('--note', default='')
    compare = sub.add_parser('compare', help='Compare findings at similar timeline positions')
    compare.add_argument('before', type=Path)
    compare.add_argument('after', type=Path)
    compare.add_argument('--out', type=Path, required=True)
    compare.add_argument('--tolerance', type=float, default=0.12)
    args = parser.parse_args(argv)
    try:
        if args.command == 'doctor':
            from .doctor import doctor_command
            return doctor_command(args)
        if args.command == 'review':
            from .review import review_command
            review_command(args)
            return 0
        if args.command == 'compare':
            from .compare import compare_command
            compare_command(args)
            return 0
        if args.command == 'gui':
            from .gui import launch
            launch()
            return 0
        config = Config(**{key: getattr(args, key) for key in Config.__dataclass_fields__})
        report = scan(args.video, args.srt, args.out, config, args.duration,
                      progress=lambda message: print(message, file=sys.stderr))
        print(f'{len(report["findings"])} findings | {args.out.resolve() / "report.html"}')
        return int(args.fail_on == 'any' and bool(report['findings']) or
                   args.fail_on == 'error' and any(f['severity'] == 'error' for f in report['findings']))
    except (ValueError, OSError, ScanError, ImportError) as exc:
        print(f'CutGuard: {exc}', file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print('CutGuard: cancelled', file=sys.stderr)
        return 130
