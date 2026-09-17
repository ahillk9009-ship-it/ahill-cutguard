# 배포 검증 실행

## 이 환경에서 실행한 검증

`python qa/local_gate.py`: 테스트 실패·오류·생략 또는 FFmpeg 미설치가 있으면 실패합니다. `qa-results/local-gate.json`에 실제 결과를 남깁니다. 로컬 테스트 통과만으로 Windows/브라우저 검증이 통과 처리되지는 않습니다.

## 실제 Windows와 브라우저가 있는 환경에서

별도 QA 가상환경에서 실행하세요. Playwright는 검사 도구 본체의 의존성이 아니라 검증용입니다.

```powershell
py -3 -m venv .qa-venv
.qa-venv\Scripts\python -m pip install . playwright
.qa-venv\Scripts\python -m playwright install chromium
.qa-venv\Scripts\python qa\browser_smoke.py
.qa-venv\Scripts\python qa\gui_smoke.py
```

브라우저 테스트는 실제 Chromium에서 필터·검토 파일 다운로드·새로고침 후 불러오기·다른 보고서 거부·좁은 화면 너비를 확인합니다. Tk 테스트는 실제 창과 이벤트 루프에서 SRT 검사 완료까지 확인하되 OS 파일 선택창과 외부 브라우저 열기는 모의 처리합니다. 실제 파일 선택과 기본 브라우저 열기는 수동 확인도 필요합니다.

`release-check.yml`은 GitHub의 Windows/Linux 브라우저, Windows Tk, 배포 패키지 메타데이터 검사 작업을 정의합니다. 소스 커밋 `4c05c3f`에서 네 작업 모두 통과했으며 [실행 근거와 한계](../docs/RELEASE_VERIFICATION_KO.md)를 기록했습니다. 이후 커밋은 해당 SHA의 결과를 별도로 확인합니다. 이 작업은 업로드·릴리스 발행을 하지 않습니다. 후속 실제 사용에서 실행·파일 선택·검사 완료와 Edge 창 생성을 확인했지만, 보고서 화면과 네이티브 검토 파일 저장·불러오기는 미검증입니다. 안정판 배포로 간주하지 마세요.
