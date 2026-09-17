"""Real-browser release gate. Requires QA-only Playwright + Chromium installation.
Run on a workstation/CI that permits testing its own local files.
"""
from pathlib import Path
import json
import sys
import tempfile
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from cutguard.engine import scan
from cutguard.review import validate_review


def main():
    from playwright.sync_api import sync_playwright
    with tempfile.TemporaryDirectory() as temp:
        root=Path(temp)
        srt=root/'한국어 자막.srt'
        srt.write_text('1\n00:00:00,000 --> 00:00:00,100\n빠르게 지나가는 자막입니다.\n',encoding='utf-8')
        report=scan(srt=srt, output=root/'report', duration=1)
        with sync_playwright() as pw:
            browser=pw.chromium.launch()
            page=browser.new_page(viewport={'width':1280,'height':900},accept_downloads=True)
            errors=[];page.on('pageerror',lambda error:errors.append(str(error)))
            page.goto((root/'report/report.html').as_uri())
            assert page.locator('.finding').count()==len(report['findings'])
            page.get_by_role('button',name='오류',exact=True).click()
            assert page.locator('.finding:visible').count()==0
            page.get_by_role('button',name='전체',exact=True).click()
            page.get_by_label('항목 0 판정',exact=True).select_option('approved')
            page.get_by_label('항목 0 메모',exact=True).fill('의도된 자막 속도')
            with page.expect_download() as event:
                page.get_by_role('button',name='검토 파일 내보내기',exact=True).click()
            path=root/'review.json';event.value.save_as(path)
            saved=json.loads(path.read_text(encoding='utf-8'))
            validate_review(report,saved)
            assert saved['decisions']['0']=={'status':'approved','note':'의도된 자막 속도'}
            page.reload()
            assert page.get_by_label('항목 0 판정',exact=True).input_value()=='pending'
            page.locator('#import-review').set_input_files(path)
            page.wait_for_function("document.querySelector('select').value === 'approved'")
            assert page.get_by_label('항목 0 메모',exact=True).input_value()=='의도된 자막 속도'
            saved['report_id']='wrong';wrong=root/'wrong.json';wrong.write_text(json.dumps(saved),encoding='utf-8')
            page.locator('#import-review').set_input_files(wrong)
            page.get_by_text('이 보고서의 검토 파일이 아닙니다.',exact=True).wait_for()
            assert page.get_by_label('항목 0 판정',exact=True).input_value()=='approved'
            page.set_viewport_size({'width':390,'height':844})
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), 'Horizontal overflow'
            assert not errors,errors
            browser.close()
    print('PASS: browser filters, download, persisted decisions, reload/import, mismatch rejection, narrow viewport, JS errors')

if __name__=='__main__': main()
