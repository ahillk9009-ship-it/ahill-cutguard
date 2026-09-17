"""Portable HTML evidence report; all input content is escaped."""
from collections import Counter
import html
import json
from .review import blank_review
from .review_ui import SCRIPT
from .models import timestamp


def render(report):
    e = html.escape
    findings = report['findings']
    review_data = json.dumps(blank_review(report), ensure_ascii=True).replace('<', '\u003c')
    cards = []
    for index, item in enumerate(findings):
        figures = ''.join('<figure><img loading="lazy" alt="' + e(frame['label']) + ' 근거 프레임" src="' + frame['image'] + '"><figcaption>' + e(frame['label']) + ' · ' + timestamp(frame['time']) + '</figcaption></figure>' for frame in item['evidence'])
        cue = f' · 자막 {e(item["cue"])}' if item['cue'] else ''
        cards.append(f'''<article class="finding" data-kind="{e(item['severity'])}">
<div class="card-top"><span class="badge {e(item['severity'])}">{'오류' if item['severity']=='error' else '검토 후보'}</span><span class="code">{e(item['code'])}</span></div>
<h3>{e(item['title'])}</h3><p class="time">{timestamp(item['start'])} — {timestamp(item['end'])}{cue}</p>
<p>{e(item['detail'])}</p><div class="frames">{figures}</div>
<div class="review-row" data-index="{index}"><label>판정 <select aria-label="항목 {index} 판정"><option value="pending">미검토</option><option value="approved">정상 연출로 승인</option><option value="needs_fix">수정 필요</option></select></label><label>메모<textarea aria-label="항목 {index} 메모" maxlength="2000" rows="2"></textarea></label></div></article>''')
    counts = Counter(i['severity'] for i in findings)
    meta = report['media']
    warnings = ''.join('<li>' + e(w) + '</li>' for w in report['warnings'])
    notes = '<aside><strong>처리 참고</strong><ul>' + warnings + '</ul></aside>' if warnings else ''
    media_line = f"{meta['width']} × {meta['height']} · {meta['fps']:.3f} fps · {timestamp(meta['duration'])}" if meta else '자막 단독 검사 · 영상 길이 관련 검사는 지정된 경우에만 수행'
    source_name = meta['name'] if meta else report['subtitle']['name']
    config = report['config']
    return f'''<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; img-src data:; style-src 'unsafe-inline'; script-src 'unsafe-inline'; base-uri 'none'; form-action 'none'">
<title>CutGuard · {e(source_name)}</title><style>
:root{{color-scheme:dark;--bg:#101419;--panel:#1b222a;--muted:#adb8c4;--green:#adf5c4}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:#f4f6f8;font:15px/1.65 system-ui,-apple-system,"Malgun Gothic",sans-serif}}main{{max-width:1060px;margin:auto;padding:48px 24px 70px}}header{{border-bottom:1px solid #39434e;padding-bottom:30px}}.brand{{letter-spacing:.15em;font-size:12px;color:var(--green);font-weight:800}}h1{{font-size:clamp(32px,5vw,52px);line-height:1.15;letter-spacing:-.04em;margin:12px 0}}h2{{font-size:22px}}h3{{font-size:20px;margin:12px 0 3px}}p{{margin:6px 0 14px}}.muted,.code,small,figcaption{{color:var(--muted)}}.filename{{overflow-wrap:anywhere}}.stats{{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin:25px 0}}.stat{{background:var(--panel);border:1px solid #34404b;padding:18px;border-radius:14px}}.stat strong{{display:block;font-size:34px;line-height:1.2}}.stat span{{color:var(--muted);font-size:13px}}.toolbar{{display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin:22px 0}}button{{font:inherit;border:1px solid #526170;border-radius:22px;padding:7px 18px;background:transparent;color:white;cursor:pointer}}button[aria-pressed="true"]{{background:var(--green);color:#101419;border-color:var(--green)}}button:focus-visible,input:focus-visible{{outline:3px solid #86bcff;outline-offset:3px}}.finding{{background:var(--panel);border:1px solid #35414c;border-radius:18px;padding:24px;margin:16px 0}}.finding[hidden]{{display:none}}.card-top{{display:flex;justify-content:space-between;gap:12px}}.badge{{font-size:12px;padding:3px 10px;border-radius:6px;background:#443c21;color:#ffe2a1}}.badge.error{{background:#4d2933;color:#ffc1ce}}.code{{font:12px ui-monospace,monospace}}.time{{font:14px ui-monospace,monospace;color:var(--green);margin:10px 0 14px}}.frames{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px}}figure{{margin:8px 0 16px}}img{{width:100%;aspect-ratio:16/9;object-fit:contain;background:#090b0f;border-radius:8px}}figcaption{{font-size:11px}}.review{{display:flex;gap:8px;align-items:center;font-size:13px;border-top:1px solid #34404b;padding-top:14px}}small{{font-size:11px}}aside,details{{background:#18232c;padding:16px 20px;border-radius:12px;margin:20px 0}}summary{{cursor:pointer}}footer{{color:var(--muted);font-size:12px;margin-top:32px}}.empty{{padding:40px;border:1px dashed #536171;border-radius:16px}}@media(max-width:600px){{main{{padding:26px 16px}}.finding{{padding:18px}}.stat{{padding:12px}}.stat strong{{font-size:26px}}.review{{flex-wrap:wrap}}.frames{{gap:5px}}}}@media print{{:root{{color-scheme:light}}body{{background:white;color:black}}.finding,.stat,aside,details{{background:white;border-color:#bbb;break-inside:avoid}}.toolbar,.review{{display:none}}.time,.muted,.code,small,figcaption,footer{{color:#333}}}}
.review-row{{border-top:1px solid #34404b;padding-top:14px;display:grid;gap:12px}}.review-row label{{display:grid;gap:6px}}select,textarea{{font:inherit;background:#101419;color:white;border:1px solid #607181;border-radius:5px;padding:8px;max-width:100%;width:100%}}select:focus-visible,textarea:focus-visible{{outline:3px solid #86bcff}}
</style></head><body><main><header><div class="brand">AHILL LAB / CUTGUARD 0.1</div><h1>확인할 구간을,<br>명확하게.</h1><p class="filename">{e(source_name)}</p><p class="muted">{e(media_line)}</p></header>
<section class="stats" aria-label="검사 요약"><div class="stat"><strong>{len(findings):02}</strong><span>전체 발견 항목</span></div><div class="stat"><strong>{counts['error']:02}</strong><span>형식·범위 오류</span></div><div class="stat"><strong>{counts['review']:02}</strong><span>편집자 검토 후보</span></div></section>
<p class="muted">원본은 변경하지 않았습니다. 후보는 편집 실수의 확정 판정이 아닙니다. 의도된 암전·스틸컷·빠른 컷·자막 중첩은 정상일 수 있습니다.</p>{notes}
<details><summary>검사 기준과 한계 보기</summary><p>검은 화면 ≥ {config['black_min']}초 · 정지 ≥ {config['freeze_min']}초 · 짧은 컷 ≤ {config['short_cut_max']}초 · 장면 변화 임계값 {config['scene_threshold']}</p><p>읽기 속도 &gt; {config['cps_max']}자/초 · 한 줄 &gt; {config['line_max']}자. 가독성 값은 사용자 설정이며 공식 플랫폼 기준이 아닙니다.</p><p>영상은 폭 320px로 축소해 검사합니다. 타임코드는 영상 시작 기준 초 단위이며 프레임 번호·방송용 드롭프레임 타임코드가 아닙니다. 이미지 시각은 추출 요청 시각입니다.</p><p>음성 싱크·화면에 구워진 자막·얼굴 일관성·자막 안전영역은 이 버전에서 검사하지 않습니다. 검사 항목이 없어도 무결함을 보장하지 않습니다.</p></details>
<aside><strong>검토 결과 보관</strong><p>판정 후 JSON 파일을 내보내세요. 같은 보고서에서 다시 불러올 수 있습니다. 자동 저장되지는 않습니다.</p><button id="export-review">검토 파일 내보내기</button> <label>불러오기 <input id="import-review" type="file" accept=".json,application/json"></label><p id="review-message" aria-live="polite"></p></aside><h2>검토 목록</h2><nav class="toolbar" aria-label="항목 필터"><button data-filter="all" aria-pressed="true">전체</button><button data-filter="error" aria-pressed="false">오류</button><button data-filter="review" aria-pressed="false">검토 후보</button><span id="visible-count" class="muted" aria-live="polite">{len(findings)}개 표시</span></nav>
<section id="findings">{''.join(cards) if cards else '<p class="empty">설정된 검사 기준에서 발견된 항목이 없습니다.</p>'}</section>
<footer>CutGuard {e(report['version'])} · 로컬 검사 · {e(report['created_at'])}<br>이 보고서에는 원본에서 추출한 이미지와 파일명이 포함될 수 있습니다.</footer></main>
<script>document.querySelectorAll('[data-filter]').forEach(button=>button.addEventListener('click',()=>{{let count=0;document.querySelectorAll('[data-filter]').forEach(b=>b.setAttribute('aria-pressed',String(b===button)));document.querySelectorAll('.finding').forEach(card=>{{card.hidden=button.dataset.filter!=='all'&&card.dataset.kind!==button.dataset.filter;if(!card.hidden)count++;}});document.getElementById('visible-count').textContent=count+'개 표시';}}));</script><script id="review-data" type="application/json">{review_data}</script><script>{SCRIPT}</script></body></html>'''
