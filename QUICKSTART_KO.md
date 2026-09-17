# CutGuard v0.2.2 빠른 시작

영상에서 확인할 구간과 자막 오류를 찾는 로컬 실행 도구입니다. 첫 버전은 규칙 기반 검사이며 API 비용이 들지 않습니다.

## 바로 결과 보기

압축을 풀고 `examples/faulty-v020/report.html`을 브라우저에서 여세요. 합성 영상의 실제 검사 결과입니다. 이전·구간·이후 이미지를 비교하고 오류/검토 후보 필터를 사용할 수 있습니다.

## 내 영상 검사 — Windows

1. Python 3.10 이상을 설치합니다. Tcl/Tk와 PATH 옵션을 포함하세요.
2. FFmpeg를 설치하고 `ffmpeg`와 `ffprobe`가 PATH에서 실행되게 설정하세요. https://ffmpeg.org/download.html
3. 명령 프롬프트에서 `python --version`, `ffmpeg -version`, `ffprobe -version`을 확인하세요.
4. 압축을 푼 폴더의 `START_WINDOWS.bat`을 더블클릭하세요.
5. 영상 및 SRT(선택)를 지정하고 **검사 시작**을 누르세요.
6. 보고서를 저장할 상위 폴더를 선택하면 결과 폴더를 새로 만들고 브라우저를 엽니다.

Windows 실행과 GUI의 실제 클릭 동작은 이번 Linux 환경에서 검증하지 못했습니다. 문제가 생기면 아래 CLI로 같은 엔진을 실행할 수 있습니다.

## 명령어로 실행

압축을 푼 폴더에서:

```bash
python -m cutguard scan "내영상.mp4" --srt "자막.srt" --out "검사결과-01"
```

자막만 검사할 수도 있습니다. 이때 FFmpeg는 필요 없습니다.

```bash
python -m cutguard scan --srt "자막.srt" --duration 30 --out "자막검사-01"
```

`--duration`은 영상 길이(초)입니다. 생략하면 영상 길이 초과 검사는 생략됩니다. 출력 폴더가 이미 있다면 새 이름을 사용하세요.

## 결과 해석

- **오류**: 잘못된 시간 형식·역전된 표시 시간·영상 길이 초과 등.
- **검토 후보**: 검은 화면·정지 구간·짧은 컷·자막 겹침·빠른 읽기 속도 등. 의도된 연출이면 정상입니다.
- **검토 판정과 메모**: 정상 연출/수정 필요를 선택한 뒤 검토 JSON 파일을 내보내세요. 같은 보고서에 다시 불러올 수 있습니다. 자동 저장은 아닙니다.
- **CSV**: 편집 시 참고할 초 단위 목록입니다. Premiere/Resolve 자동 마커 가져오기 기능은 아닙니다.

영상은 그대로 유지됩니다. 결과 HTML에는 영상에서 추출한 이미지가 포함되므로 공유 전 내용을 확인하세요.

## 기본 기준 변경

```bash
python -m cutguard scan "내영상.mp4" --freeze-min 2 --short-cut-max 0.1 --thumbnails 6 --out "검사결과-02"
```

정지 검토 2초, 짧은 컷 0.1초 이하, 근거 이미지 생성은 첫 6개 영상 후보에 적용됩니다. 후보 목록은 모두 남습니다.

## 아직 지원하지 않는 검사

얼굴 일관성, 음성과 자막의 실제 싱크, 화면에 구워진 자막 OCR, 자막 안전영역, 잔상 분석과 자동 수정은 후속 개발 항목입니다. Python과 FFmpeg는 별도 설치가 필요하며 설치형 EXE는 아닙니다.

## 검토 파일과 수정 전후 비교

```bash
python -m cutguard review examples/faulty-v020/report.json --finding 3 --status needs_fix --note "2프레임 컷 확인" --out 내검토.json
python -m cutguard compare examples/faulty-v020/report.json examples/clean-v020/report.json --out 비교결과.json
```

항목 번호는 0부터 시작합니다. 미검출은 수정 완료의 보장이 아닙니다. 시간축이 이동하면 신규/미검출로 나뉠 수 있습니다. 실제 브라우저의 검토 파일 다운로드·불러오기와 Windows GUI는 아직 검증하지 못했으며 CLI 저장·불러오기는 검증했습니다.

## 실행 전 확인

`CHECK_WINDOWS.bat`을 실행하거나 `python -m cutguard doctor`를 입력하세요. `video_cli_ready: true`면 Python·FFmpeg 실행 전제조건을 확인한 것입니다. GUI 동작 확인과 같지는 않습니다.
