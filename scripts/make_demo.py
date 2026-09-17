"""Generate a reproducible 7-second fixture; no third-party footage."""
from pathlib import Path
import subprocess
import sys


def create_demo(folder):
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    sources = ['testsrc2=size=640x360:rate=25:duration=2',
               'color=white:size=640x360:rate=25:duration=0.08',
               'testsrc2=size=640x360:rate=25:duration=2',
               'color=black:size=640x360:rate=25:duration=0.32',
               'color=blue:size=640x360:rate=25:duration=1.6',
               'testsrc2=size=640x360:rate=25:duration=1']
    command = ['ffmpeg', '-nostdin', '-hide_banner', '-v', 'error', '-y']
    for source in sources:
        command += ['-f', 'lavfi', '-i', source]
    command += ['-filter_complex', ''.join(f'[{i}:v]' for i in range(6)) + 'concat=n=6:v=1:a=0[v]',
                '-map', '[v]', '-c:v', 'mpeg4', '-q:v', '2', '-pix_fmt', 'yuv420p', str(folder / 'demo.mp4')]
    subprocess.run(command, check=True, timeout=60)
    (folder / 'demo.srt').write_text('''1
00:00:00,300 --> 00:00:01,500
오늘은 컷가드를 테스트합니다.

2
00:00:01,200 --> 00:00:01,600
이 자막은 너무 빠르게 지나가는 예시입니다.

3
00:00:03,000 --> 00:00:04,000
한 줄에 너무 많은 글자를 넣었을 때 검토가 필요한 자막 예시

4
00:00:06,500 --> 00:00:08,000
영상 종료를 넘는 자막
''', encoding='utf-8')
    (folder / 'expected.json').write_text('''{
  "duration": 7.0,
  "visual_events": [
    {"code": "short_cut", "start": 2.0, "end": 2.08},
    {"code": "black", "start": 4.08, "end": 4.4},
    {"code": "freeze", "start": 4.4, "end": 6.0}
  ],
  "tolerance_seconds": 0.08,
  "note": "Synthetic fixture only, not a real-world accuracy benchmark."
}
''', encoding='utf-8')
    return folder


if __name__ == '__main__':
    create_demo(sys.argv[1] if len(sys.argv) > 1 else 'demo')
