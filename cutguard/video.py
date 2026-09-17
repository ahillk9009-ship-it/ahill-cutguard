"""FFmpeg-based heuristics. No shell execution, network input, or source changes."""
import base64
from collections import deque
from fractions import Fraction
import json
import math
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
from .models import Finding


class ScanError(RuntimeError):
    pass


def run(args, timeout):
    try:
        result = subprocess.run(args, capture_output=True, timeout=timeout)
    except FileNotFoundError as exc:
        raise ScanError(f'{args[0]} 실행 파일이 없습니다. FFmpeg/ffprobe를 PATH에 설치하세요.') from exc
    except subprocess.TimeoutExpired as exc:
        raise ScanError('처리 제한 시간을 초과했습니다. --timeout 값을 늘려 다시 실행하세요.') from exc
    if result.returncode:
        raise ScanError(result.stderr.decode('utf-8', errors='replace')[-1800:])
    return result.stdout


def require_tools():
    for name in ('ffmpeg', 'ffprobe'):
        if not shutil.which(name):
            raise ScanError(f'{name}을 찾을 수 없습니다. FFmpeg/ffprobe 설치 후 PATH를 확인하세요.')


def probe(path, timeout):
    require_tools()
    payload = run(['ffprobe', '-v', 'error', '-protocol_whitelist', 'file,pipe',
                   '-select_streams', 'v:0', '-show_streams', '-show_format', '-of', 'json', str(path)], timeout)
    data = json.loads(payload)
    if not data.get('streams'):
        raise ScanError('영상 스트림을 찾을 수 없습니다.')
    stream = data['streams'][0]
    try:
        duration = float(stream.get('duration') or data['format']['duration'])
        fps = float(Fraction(stream.get('avg_frame_rate', '0/1')))
        if not math.isfinite(duration) or duration <= 0 or not math.isfinite(fps) or fps <= 0:
            raise ValueError()
    except (KeyError, ValueError, ZeroDivisionError) as exc:
        raise ScanError('유효한 영상 길이 또는 프레임레이트를 읽을 수 없습니다.') from exc
    return {'name': Path(path).name, 'duration': duration, 'fps': fps,
            'width': stream['width'], 'height': stream['height'],
            'codec': stream.get('codec_name', 'unknown'), 'timeline_origin': 'first decoded video frame'}


NUMBER = r'(-?\d+(?:\.\d+)?(?:e[+-]?\d+)?)'


def parse_log(lines, duration, config):
    findings, scenes = [], []
    freeze_start = None
    for line in lines:
        match = re.search(r'black_start:' + NUMBER + r'\s+black_end:' + NUMBER, line)
        if match:
            start, end = map(float, match.groups())
            start, end = max(0, start), min(duration, end)
            if end - start >= config.black_min - 0.001:
                findings.append(Finding('black', start, end, '검은 화면 후보',
                                        f'{end-start:.3f}초 · 의도된 암전·페이드인지 확인하세요.'))
        match = re.search(r'freeze_start:\s*' + NUMBER, line)
        if match:
            freeze_start = max(0, float(match[1]))
        match = re.search(r'freeze_end:\s*' + NUMBER, line)
        if match and freeze_start is not None:
            end = min(duration, float(match[1]))
            if end - freeze_start >= config.freeze_min - 0.001:
                findings.append(Finding('freeze', freeze_start, end, '정지 화면 후보',
                                        '영상 변화가 적은 구간입니다. 스틸컷·타이틀이면 정상일 수 있습니다.'))
            freeze_start = None
        if 'showinfo' in line:
            match = re.search(r'pts_time:\s*' + NUMBER, line)
            if match:
                scenes.append(float(match[1]))
    if freeze_start is not None and duration - freeze_start >= config.freeze_min - 0.001:
        findings.append(Finding('freeze', freeze_start, duration, '정지 화면 후보', '영상 끝까지 변화가 적은 구간입니다.'))
    # Only shots bracketed by detected transitions; first/last shots are excluded.
    scenes = sorted(set(t for t in scenes if 0 <= t <= duration))
    for start, end in zip(scenes, scenes[1:]):
        if 0 < end - start <= config.short_cut_max + 0.000001:
            findings.append(Finding('short_cut', start, end, '매우 짧은 컷 후보',
                                    f'{end-start:.3f}초 · 장면 변화 사이의 짧은 구간입니다. 잔여 프레임인지 확인하세요.'))
    return findings


def inspect_video(path, meta, config):
    filters = (f'setpts=PTS-STARTPTS,scale=320:-2,'
               f'blackdetect=d={config.black_min}:pix_th=0.10:pic_th=0.98,'
               f'freezedetect=n=-50dB:d={config.freeze_min},'
               f"select='gt(scene,{config.scene_threshold})',showinfo")
    command = ['ffmpeg', '-nostdin', '-hide_banner', '-nostats', '-v', 'info',
               '-protocol_whitelist', 'file,pipe', '-i', str(path), '-map', '0:v:0', '-an', '-sn',
               '-vf', filters, '-fps_mode', 'vfr', '-f', 'null', '-']
    # Stream logs to disk so long clips cannot exhaust memory with stderr.
    with tempfile.TemporaryFile(mode='w+b') as log:
        try:
            result = subprocess.run(command, stdout=subprocess.DEVNULL, stderr=log, timeout=config.timeout)
        except subprocess.TimeoutExpired as exc:
            raise ScanError('영상 검사 시간 초과. --timeout 값을 늘리세요.') from exc
        log.seek(0)
        if result.returncode:
            tail = b''.join(deque(log, maxlen=12)).decode('utf-8', errors='replace')
            raise ScanError(f'영상 검사 실패: {tail}')
        return parse_log((line.decode('utf-8', errors='replace') for line in log), meta['duration'], config)


def thumbnail(path, second, timeout):
    data = run(['ffmpeg', '-nostdin', '-hide_banner', '-v', 'error',
                '-protocol_whitelist', 'file,pipe', '-i', str(path), '-ss', f'{second:.6f}',
                '-map', '0:v:0', '-frames:v', '1', '-vf', 'scale=320:-2', '-threads', '1',
                '-f', 'image2pipe', '-c:v', 'mjpeg', '-'], timeout)
    if not data:
        raise ScanError('근거 프레임을 추출하지 못했습니다.')
    return 'data:image/jpeg;base64,' + base64.b64encode(data).decode('ascii')


def attach_evidence(path, meta, findings, config):
    warnings = []
    count = 0
    for item in findings:
        if item.code not in ('black', 'freeze', 'short_cut') or count >= config.thumbnails:
            continue
        positions = [('이전', item.start - 0.15), ('구간', (item.start + item.end) / 2), ('이후', item.end + 0.15)]
        for label, second in positions:
            second = min(max(0, second), max(0, meta['duration'] - 1 / meta['fps']))
            try:
                uri = thumbnail(path, second, min(config.timeout, 60))
                item.evidence.append({'label': label, 'time': round(second, 6), 'image': uri})
            except ScanError as exc:
                warnings.append(f'{item.code} {second:.3f}s: {exc}')
        count += 1
    return warnings
