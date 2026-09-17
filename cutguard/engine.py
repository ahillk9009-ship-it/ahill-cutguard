from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
import csv
import json
import tempfile
from . import __version__
from .models import Config
from .subtitles import inspect_srt
from .video import ScanError, probe, inspect_video, attach_evidence
from .report import render


def scan(video=None, srt=None, output='cutguard-report', config=None, duration=None, progress=None):
    config = config or Config()
    progress = progress or (lambda message: None)
    if not video and not srt:
        raise ValueError('영상 또는 SRT 파일을 선택하세요.')
    if duration is not None:
        import math
        if not math.isfinite(duration) or duration <= 0:
            raise ValueError('영상 길이는 유한한 양수여야 합니다.')
    paths = [Path(p).resolve() for p in (video, srt) if p]
    for path in paths:
        if not path.is_file():
            raise ValueError(f'파일을 찾을 수 없습니다: {path.name}')
    output = Path(output).resolve()
    # Never replace a user's existing report or media file.
    if output.exists():
        raise ValueError('출력 경로가 이미 있습니다. 새 폴더 이름을 지정하세요.')
    findings, warnings, meta, subtitle = [], [], None, None
    if video:
        video = Path(video).resolve()
        progress('영상 정보를 읽는 중…')
        meta = probe(video, min(config.timeout, 60))
        duration = meta['duration']
        progress('검은 화면·정지 구간·짧은 컷을 검사하는 중…')
        findings.extend(inspect_video(video, meta, config))
    if srt:
        progress('자막을 검사하는 중…')
        cues, issues = inspect_srt(Path(srt).resolve(), duration, config)
        subtitle = {'name': Path(srt).name, 'cue_count': len(cues), 'duration_reference': duration}
        findings.extend(issues)
        if duration is None:
            warnings.append('영상 길이가 없어 자막의 영상 길이 초과 검사는 생략했습니다.')
    findings.sort(key=lambda f: (f.start, f.end, f.code))
    if video:
        progress('이전·구간·이후 근거 프레임을 추출하는 중…')
        warnings.extend(attach_evidence(video, meta, findings, config))
        visual_count = sum(i.code in ('black', 'freeze', 'short_cut') for i in findings)
        if visual_count > config.thumbnails:
            warnings.append(f'영상 후보 {visual_count}개 중 처음 {config.thumbnails}개에만 근거 이미지를 생성했습니다. 전체 목록은 유지됩니다.')
    report = {'schema_version': '1.0', 'version': __version__,
              'created_at': datetime.now(timezone.utc).isoformat(), 'media': meta,
              'subtitle': subtitle, 'config': asdict(config), 'warnings': warnings,
              'findings': [asdict(f) for f in findings]}
    html = render(report)
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.cutguard-', dir=output.parent) as temp:
        temp = Path(temp)
        (temp / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
        (temp / 'report.html').write_text(html, encoding='utf-8')
        with (temp / 'markers.csv').open('w', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['start_seconds', 'end_seconds', 'code', 'severity', 'title', 'detail'])
            for item in findings:
                writer.writerow([f'{item.start:.6f}', f'{item.end:.6f}', item.code, item.severity, item.title, item.detail])
        # mkdir is exclusive even if another process creates the target during scanning.
        output.mkdir()
        for name in ('report.json', 'report.html', 'markers.csv'):
            (temp / name).replace(output / name)
    progress('검사 완료')
    return report
