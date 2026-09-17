# CutGuard 0.2.2 배포 검증 결과

## 판정 — 2026-09-17

소스 업로드 커밋 `4c05c3fde45c3a1378ad4bb7f71c6469bf44c430`의 GitHub Actions 자동 검증은 모두 통과했습니다. 아래 결과는 해당 커밋의 실행 로그에서 확인했습니다. 이후 커밋은 해당 SHA의 Actions 결과를 별도로 확인해야 합니다.

저장소는 **비공개**입니다. 공개 전환, 공개 릴리스와 PyPI 배포는 승인되지 않았으며 수행하지 않았습니다. 실제 PC의 OS 파일 선택·기본 브라우저 연결과 현업 정확도 검증이 남아 있으므로 안정판으로 소개하지 않습니다.

## 원격에서 직접 확인한 결과

| 검증 | 실행 환경·범위 | 결과·근거 |
|---|---|---|
| 핵심 테스트 | Ubuntu/Windows × Python 3.10/3.12, 조합별 28개 | 4개 작업 모두 성공: [tests](https://github.com/ahillk9009-ship-it/ahill-cutguard/actions/runs/35207563763) |
| 전체·영상 통합 테스트 | Ubuntu, Python 3.12, FFmpeg 설치 후 unittest 전체 실행 | 33개 통과, 실패·오류·생략 0: 같은 tests의 video 작업 |
| Windows GUI | 실제 Tk 창·컨트롤·이벤트 루프, 한국어 SRT의 작업 스레드 검사, 보고서 생성·열기 요청 | 성공: [windows-gui](https://github.com/ahillk9009-ship-it/ahill-cutguard/actions/runs/35207563764/job/105156958317) |
| Chromium | Ubuntu, 필터·판정/메모·실제 JSON 다운로드·새로고침 후 가져오기·다른 보고서 거부·390px 너비·JS 오류 확인 | 성공: [browser Ubuntu](https://github.com/ahillk9009-ship-it/ahill-cutguard/actions/runs/35207563764/job/105156958689) |
| Chromium | Windows, 위와 같은 브라우저 검증 | 성공: [browser Windows](https://github.com/ahillk9009-ship-it/ahill-cutguard/actions/runs/35207563764/job/105156958545) |
| 패키징 | Ubuntu, wheel·sdist 빌드와 두 파일의 twine check | 모두 성공: [package](https://github.com/ahillk9009-ship-it/ahill-cutguard/actions/runs/35207563764/job/105156958522) |

실패한 작업은 없으므로 소스 수정이나 기존 실행 재시도는 하지 않았습니다. Actions의 Node 런타임 폐기 예정 경고와 MANIFEST 제외 대상 부재 경고는 있었으나 작업은 성공했습니다.

## 검증의 한계

- GUI 검증은 `askdirectory`, 오류 메시지 상자와 `webbrowser.open`을 모킹합니다. 입력 SRT 경로는 자동 입력합니다. 실제 OS 파일 선택창, 기본 브라우저 실행, START_WINDOWS.bat 더블클릭과 사용자 PC 설치 상태는 확인하지 않았습니다.
- 브라우저 검증은 실제 headless Chromium과 파일 다운로드를 사용하지만, 가져오기는 Playwright의 `set_input_files`로 수행합니다. OS 파일 선택창을 직접 조작하지 않습니다. 390px에서 가로 넘침을 검사했으며 전체 화면의 수동 시각 검수나 다른 브라우저 지원을 증명하지 않습니다.
- GUI·브라우저 smoke 검증은 합성 SRT 기반입니다. Windows FFmpeg 영상 통합 검증이나 실제 편집 영상의 정확도·시간 절감 측정은 포함하지 않습니다.
- 원격 package 작업은 빌드와 메타데이터를 검사합니다. 소스 폴더 밖 독립 wheel 설치 검증까지 실행하는 작업은 아닙니다.
- 이전 Linux 작업에서 wheel RECORD 해시·크기 확인, 별도 가상환경 설치 후 소스 폴더 밖 CLI 실행과 오류 SRT 4개 탐지를 확인했다는 인계 기록이 있습니다. 이번 세션에서 그 이전 실행을 재현하거나 원본 로그를 재확인한 것은 아닙니다.

## 업로드와 병합 상태

- [Draft PR #1](https://github.com/ahillk9009-ship-it/ahill-cutguard/pull/1): `verify/v0.2.2` → `main`.
- 초기 커밋 `de54a92a0e7b7303ec08641574e4fbd0e9e737fd`를 보존한 소스 커밋에 원본 67개 경로가 있습니다.
- 준비된 원본 68개 중 `demo/demo.mp4`가 누락되었습니다. 예상 크기는 2,089,523바이트, Git blob SHA는 `2b035d0187f9da9fb222e3d36f9e8a04f3706a22`입니다. 해당 blob 조회도 404였습니다.
- 인계받은 `/workspace/scratch/cb031775f754/` 경로는 이번 Windows 환경에서 접근되지 않습니다. 사용자 제공 원본 영상을 기다립니다. 다른 영상으로 대체하거나 동일 영상이라고 가정해 재생성하지 않았습니다.
- 영상 업로드·크기/SHA/68개 경로 확인 후 최신 커밋의 tests·release-check를 확인하고, 기존 커밋을 보존하는 merge commit으로 main에 병합할 예정입니다. 현재는 업로드 완료 또는 main 병합 완료로 간주하지 않습니다.

## 공개 준비 판단

자동 검증 범위에서는 알파 검토를 진행할 근거가 확보되었습니다. 원본 업로드 완료, 실제 PC 수동 점검과 지원 범위 명시가 필요합니다. 공개 여부는 별도 승인 사항이며 현재는 비공개를 유지합니다.
