# CutGuard 0.2.2 배포 검증 결과

## 판정 — 2026-09-17

소스 업로드 커밋 `4c05c3fde45c3a1378ad4bb7f71c6469bf44c430`의 GitHub Actions 자동 검증은 모두 통과했습니다. 아래 결과는 해당 커밋의 실행 로그에서 확인했습니다. 이후 커밋은 해당 SHA의 Actions 결과를 별도로 확인해야 합니다.

문서 갱신 커밋 `dd5146b0cd502aa568b5b45f1b63d5445af00a86`의 [tests](https://github.com/ahillk9009-ship-it/ahill-cutguard/actions/runs/35208423067)와 [release-check](https://github.com/ahillk9009-ship-it/ahill-cutguard/actions/runs/35208423057)도 같은 검증 범위에서 모두 통과했고 로그를 확인했습니다. 원본 데모 추가 이후 최신 커밋의 CI 링크·결과와 병합 상태는 [PR #1](https://github.com/ahillk9009-ship-it/ahill-cutguard/pull/1)에 기록합니다.

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

실패한 작업은 없으므로 검사 코드 수정이나 기존 실행 재시도는 하지 않았습니다. Actions의 Node 런타임 폐기 예정 경고와 MANIFEST 제외 대상 부재 경고는 있었으나 작업은 성공했습니다.

## 원본 데모 추가 시 로컬 검증

- Windows / Python 3.14.6 / FFmpeg 9.0에서 `python -m unittest discover -s tests -v`: 33개 통과, 실패·오류·생략 0. 영상 통합 테스트 5개를 포함합니다.
- 사용자가 첨부한 원본 `demo/demo.mp4`: 2,089,523바이트, Git blob SHA `2b035d0187f9da9fb222e3d36f9e8a04f3706a22` 일치.
- ffprobe: MPEG-4 영상, 640×360, 25fps, 7.000초. FFmpeg 전체 디코딩 오류 0.

## 검증의 한계

- GUI 검증은 `askdirectory`, 오류 메시지 상자와 `webbrowser.open`을 모킹합니다. 입력 SRT 경로는 자동 입력합니다. 실제 OS 파일 선택창, 기본 브라우저 실행, START_WINDOWS.bat 더블클릭과 사용자 PC 설치 상태는 확인하지 않았습니다.
- 브라우저 검증은 실제 headless Chromium과 파일 다운로드를 사용하지만, 가져오기는 Playwright의 `set_input_files`로 수행합니다. OS 파일 선택창을 직접 조작하지 않습니다. 390px에서 가로 넘침을 검사했으며 전체 화면의 수동 시각 검수나 다른 브라우저 지원을 증명하지 않습니다.
- GUI·브라우저 smoke 검증은 합성 SRT 기반입니다. Windows FFmpeg 영상 통합은 위 로컬 전체 테스트에서 확인했으며, GUI를 통한 영상 검사 전체 흐름이나 실제 편집 영상의 정확도·시간 절감 측정은 포함하지 않습니다.
- 원격 package 작업은 빌드와 메타데이터를 검사합니다. 소스 폴더 밖 독립 wheel 설치 검증까지 실행하는 작업은 아닙니다.
- 이전 Linux 작업에서 wheel RECORD 해시·크기 확인, 별도 가상환경 설치 후 소스 폴더 밖 CLI 실행과 오류 SRT 4개 탐지를 확인했다는 인계 기록이 있습니다. 이번 세션에서 그 이전 실행을 재현하거나 원본 로그를 재확인한 것은 아닙니다.

## 업로드와 병합 상태

- [PR #1](https://github.com/ahillk9009-ship-it/ahill-cutguard/pull/1): `verify/v0.2.2` → `main`.
- 초기 커밋 `de54a92a0e7b7303ec08641574e4fbd0e9e737fd`와 소스 업로드 커밋 `4c05c3f`의 67개 경로를 보존하고 원본 `demo/demo.mp4`를 추가해 전체 68개 경로를 구성했습니다. 검증 문서 내용은 실제 결과에 맞춰 갱신했습니다.
- 이전 실행 환경 경로에 접근할 수 없어 사용자가 원본 영상을 첨부했습니다. 파일 크기와 Git blob SHA를 확인했으며 다른 영상으로 대체하거나 재생성하지 않았습니다.
- main 통합 조건은 원격 68개 파일·영상 SHA/크기 일치와 최신 tests·release-check 성공입니다. 기존 커밋을 보존하는 merge commit을 사용하며 강제 push나 커밋 삭제는 하지 않습니다. 병합 및 병합 후 main CI의 실제 결과는 PR에 기록합니다.

## 공개 준비 판단

원본 파일 구성이 완성됐으며 자동 검증 범위에서는 알파 검토를 진행할 근거가 확보되었습니다. OS 파일 선택·기본 브라우저 열기 수동 점검과 실사용 평가가 남았습니다. 공개 여부는 별도 승인 사항이며 현재는 비공개를 유지합니다.
