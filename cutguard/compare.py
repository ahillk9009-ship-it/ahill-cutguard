"""Time-based candidate comparison. Disappearance is not proof of repair."""
import math
import json
from .review import save_new


def compare_reports(before, after, tolerance=0.12):
    if not math.isfinite(tolerance) or tolerance < 0:
        raise ValueError('비교 허용 오차는 유한한 0 이상의 값이어야 합니다.')
    for key in ('black_min','freeze_min','scene_threshold','short_cut_max','cps_max','line_max'):
        if before['config'].get(key) != after['config'].get(key):
            raise ValueError('검사 설정이 달라 비교할 수 없습니다: ' + key)
    if bool(before.get('media')) != bool(after.get('media')) or bool(before.get('subtitle')) != bool(after.get('subtitle')):
        raise ValueError('영상/자막 검사 범위가 달라 비교할 수 없습니다.')
    remaining, disappeared, used = [], [], set()
    for i, old in enumerate(before['findings']):
        candidates=[]
        for j,new in enumerate(after['findings']):
            if j in used or old['code'] != new['code']: continue
            if old.get('cue') != new.get('cue'): continue
            ds=abs(old['start']-new['start']); de=abs(old['end']-new['end'])
            if max(ds,de) <= tolerance: candidates.append((ds+de,j))
        if candidates:
            _,j=min(candidates); used.add(j)
            remaining.append({'before_index':i,'after_index':j,'code':old['code']})
        else: disappeared.append({'before_index':i,'finding':old})
    added=[{'after_index':j,'finding':f} for j,f in enumerate(after['findings']) if j not in used]
    return {'schema_version':'1.0','tolerance_seconds':tolerance,'remaining':remaining,
            'no_longer_detected':disappeared,'newly_detected':added,
            'notice':'미검출은 수정 완료의 증명이 아닙니다. 타임라인 이동·다른 영상·검사 한계로 달라질 수 있습니다. 검토 승인은 다른 보고서로 자동 이전하지 않습니다.'}


def compare_command(args):
    from .validation import read_report
    before=read_report(args.before)
    after=read_report(args.after)
    result=compare_reports(before,after,args.tolerance)
    save_new(args.out,result)
    print(f"유지 {len(result['remaining'])} / 미검출 {len(result['no_longer_detected'])} / 신규 {len(result['newly_detected'])}")
