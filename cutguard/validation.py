"""Validate external report files before review/comparison operations."""
import json
import math
from pathlib import Path


def read_report(path):
    try:
        report = json.loads(Path(path).read_text(encoding='utf-8-sig'))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError('UTF-8 JSON 보고서 형식이 올바르지 않습니다.') from exc
    if not isinstance(report, dict) or report.get('schema_version') != '1.0':
        raise ValueError('지원하는 CutGuard 보고서 schema_version은 1.0입니다.')
    if not isinstance(report.get('config'), dict) or not isinstance(report.get('findings'), list):
        raise ValueError('보고서 config 또는 findings가 없거나 형식이 잘못되었습니다.')
    for key in ('black_min','freeze_min','scene_threshold','short_cut_max','cps_max','line_max'):
        value = report['config'].get(key)
        if type(value) not in (int,float) or not math.isfinite(value) or value <= 0:
            raise ValueError('유효하지 않은 보고서 설정: ' + key)
    for kind in ('media','subtitle'):
        if report.get(kind) is not None and not isinstance(report[kind], dict):
            raise ValueError('유효하지 않은 보고서 입력 정보: ' + kind)
    for index, item in enumerate(report['findings']):
        if not isinstance(item,dict) or not isinstance(item.get('code'),str) or not item['code']:
            raise ValueError(f'유효하지 않은 검사 항목: {index}')
        for key in ('start','end'):
            value=item.get(key)
            if type(value) not in (int,float) or not math.isfinite(value) or value < 0:
                raise ValueError(f'검사 항목 {index}의 시간이 올바르지 않습니다.')
        if item['end'] < item['start']:
            raise ValueError(f'검사 항목 {index}의 시간 범위가 역순입니다.')
        if item.get('cue') is not None and not isinstance(item['cue'],str):
            raise ValueError(f'검사 항목 {index}의 자막 번호가 올바르지 않습니다.')
    return report
