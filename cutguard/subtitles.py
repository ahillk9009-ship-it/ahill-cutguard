"""Strict SRT parsing; malformed blocks are visible findings, never silently lost."""
import re
import unicodedata
from pathlib import Path
from .models import Cue, Finding, Config

TIME = r'(\d{2,}):([0-5]\d):([0-5]\d)[,.](\d{3})'
RANGE = re.compile(r'^' + TIME + r'\s*-->\s*' + TIME + r'\s*$')


def seconds(parts):
    h, m, s, ms = map(int, parts)
    return h * 3600 + m * 60 + s + ms / 1000


def parse_srt(text):
    cues, findings = [], []
    text = text.lstrip('\ufeff').replace('\r\n', '\n').replace('\r', '\n').strip()
    if not text:
        return [], [Finding('srt_empty', 0, 0, '빈 자막 파일', '자막 내용이 없습니다.', 'error')]
    seen = set()
    for index, block in enumerate(re.split(r'\n\s*\n', text), 1):
        lines = block.splitlines()
        number = lines[0].strip() if lines else str(index)
        match = RANGE.fullmatch(lines[1].strip()) if len(lines) >= 2 else None
        if not number.isdigit() or not match or len(lines) < 3:
            findings.append(Finding('srt_parse', 0, 0, '자막 형식 오류',
                                    f'블록 {index}: 번호·시간·본문 형식을 확인하세요.', 'error'))
            continue
        start, end = seconds(match.groups()[:4]), seconds(match.groups()[4:])
        cue = Cue(number, start, end, '\n'.join(lines[2:]))
        cues.append(cue)
        if number in seen:
            findings.append(Finding('srt_duplicate', start, max(start, end), '중복 자막 번호',
                                    f'자막 {number} 번호가 반복됩니다.', 'error', number))
        seen.add(number)
    return cues, findings


def visible_text(text):
    return unicodedata.normalize('NFC', re.sub(r'<[^>]*>', '', text))


def check_cues(cues, duration, config=Config()):
    findings = []
    for i, cue in enumerate(cues):
        def add(code, title, detail, severity='review'):
            findings.append(Finding(code, cue.start, max(cue.start, cue.end), title, detail, severity, cue.number))
        text = visible_text(cue.text)
        length = sum(not c.isspace() for c in text)
        span = cue.end - cue.start
        if span <= 0:
            add('srt_duration', '자막 표시 시간 오류', '종료 시간이 시작 시간보다 늦어야 합니다.', 'error')
        elif length / span > config.cps_max:
            add('srt_speed', '자막 읽기 속도 검토',
                f'{length / span:.1f}자/초 · 설정 {config.cps_max:g}자/초 초과. 공백·태그 제외.')
        if duration is not None and cue.end > duration + 0.001:
            add('srt_out_of_bounds', '영상 길이를 넘는 자막', f'영상 종료 {duration:.3f}초 이후까지 표시됩니다.', 'error')
        if not text.strip():
            add('srt_no_text', '빈 자막 본문', '표시 가능한 본문이 없습니다.', 'error')
        if any(len(line) > config.line_max for line in text.splitlines()):
            add('srt_line_length', '긴 자막 줄 검토', f'한 줄이 설정 {config.line_max}자를 초과합니다. 실제 화면 폭 검사는 아닙니다.')
        if len(text.splitlines()) > 2:
            add('srt_lines', '자막 줄 수 검토', '본문이 3줄 이상입니다.')
        if i and cue.start < cues[i - 1].start:
            add('srt_order', '자막 시간 순서 오류', '파일에 기록된 시작 시간이 역순입니다.', 'error')
    # Track the furthest-ending prior cue: nested overlaps are not missed.
    active = None
    for cue in sorted((c for c in cues if c.end > c.start), key=lambda c: c.start):
        if active and cue.start < active.end - 0.000001:
            findings.append(Finding('srt_overlap', cue.start, min(cue.end, active.end), '자막 시간 겹침',
                                    f'자막 {active.number}과 {cue.number}이 동시에 표시됩니다. 의도된 중첩인지 확인하세요.', 'review', cue.number))
        if active is None or cue.end > active.end:
            active = cue
    return findings


def inspect_srt(path, duration, config):
    path = Path(path)
    try:
        text = path.read_text(encoding='utf-8-sig')
    except UnicodeDecodeError:
        text = path.read_text(encoding='cp949')
    cues, findings = parse_srt(text)
    return cues, findings + check_cues(cues, duration, config)
