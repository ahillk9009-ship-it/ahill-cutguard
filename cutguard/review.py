"""Portable review decisions bound to one exact report; no implicit persistence."""
import hashlib
import json
from pathlib import Path

STATES = ('pending', 'approved', 'needs_fix')


def report_id(report):
    return hashlib.sha256(json.dumps(report, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode()).hexdigest()


def blank_review(report):
    return {'schema_version': '1.0', 'report_id': report_id(report), 'decisions': {
        str(i): {'status': 'pending', 'note': ''} for i in range(len(report['findings']))}}


def validate_review(report, review):
    expected = blank_review(report)
    if not isinstance(review, dict) or review.get('schema_version') != '1.0' or review.get('report_id') != expected['report_id']:
        raise ValueError('검토 파일이 이 보고서와 일치하지 않습니다.')
    decisions = review.get('decisions')
    if not isinstance(decisions, dict) or set(decisions) != set(expected['decisions']):
        raise ValueError('검토 항목 목록이 일치하지 않습니다.')
    for value in decisions.values():
        if not isinstance(value, dict) or value.get('status') not in STATES or not isinstance(value.get('note'), str) or len(value['note']) > 2000:
            raise ValueError('유효하지 않은 검토 상태 또는 메모입니다.')
    return review


def save_new(path, value):
    path = Path(path)
    with path.open('x', encoding='utf-8') as f:
        json.dump(value, f, ensure_ascii=False, indent=2)


def review_command(args):
    from .validation import read_report
    report = read_report(args.report)
    review = validate_review(report, json.loads(args.load.read_text(encoding='utf-8'))) if args.load else blank_review(report)
    if args.finding is not None:
        key = str(args.finding)
        if key not in review['decisions']:
            raise ValueError('검토 항목 번호가 없습니다. 첫 항목은 0입니다.')
        review['decisions'][key] = {'status': args.status, 'note': args.note}
    validate_review(report, review)
    save_new(args.out, review)
