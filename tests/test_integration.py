import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from cutguard.engine import scan
from cutguard.models import Config
from cutguard.cli import main
from scripts.make_demo import create_demo


@unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'), 'FFmpeg required')
class VideoIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.temp.name)
        create_demo(cls.root / 'fixture')
        cls.video = cls.root / 'fixture' / 'demo.mp4'
        cls.srt = cls.root / 'fixture' / 'demo.srt'
        cls.before = hashlib.sha256(cls.video.read_bytes()).hexdigest()
        cls.report = scan(cls.video, cls.srt, cls.root / 'report', Config(thumbnails=3))

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_expected_visual_events_with_time_tolerance(self):
        expected = json.loads((self.root / 'fixture' / 'expected.json').read_text())
        for event in expected['visual_events']:
            candidates = [f for f in self.report['findings'] if f['code'] == event['code']]
            self.assertTrue(any(abs(f['start'] - event['start']) <= .08 and abs(f['end'] - event['end']) <= .08 for f in candidates), (event, candidates))

    def test_evidence_and_source_integrity(self):
        self.assertEqual(hashlib.sha256(self.video.read_bytes()).hexdigest(), self.before)
        visual = [f for f in self.report['findings'] if f['code'] in ('black', 'freeze', 'short_cut')]
        self.assertTrue(all(len(f['evidence']) == 3 for f in visual[:3]))
        self.assertTrue(all(frame['image'].startswith('data:image/jpeg;base64,/9j/') for f in visual[:3] for frame in f['evidence']))

    def test_srt_errors_and_ci_exit(self):
        codes = {f['code'] for f in self.report['findings']}
        self.assertTrue({'srt_overlap', 'srt_speed', 'srt_out_of_bounds', 'srt_line_length'} <= codes)
        result = main(['scan', '--srt', str(self.srt), '--duration', '7', '--out', str(self.root / 'ci'), '--fail-on', 'error'])
        self.assertEqual(result, 1)

    def test_moving_video_has_no_visual_findings(self):
        video = self.root / 'moving.mp4'
        subprocess.run(['ffmpeg', '-v', 'error', '-f', 'lavfi', '-i', 'testsrc2=size=320x180:rate=25:duration=2', '-c:v', 'mpeg4', str(video)], check=True, timeout=60)
        report = scan(video, output=self.root / 'clean', config=Config(thumbnails=0))
        self.assertEqual(report['findings'], [])

    def test_corrupt_video_is_error_not_clean_report(self):
        video = self.root / 'bad.mp4'
        video.write_bytes(b'not a video')
        result = main(['scan', str(video), '--out', str(self.root / 'bad-report')])
        self.assertEqual(result, 2)
        self.assertFalse((self.root / 'bad-report').exists())


if __name__ == '__main__':
    unittest.main()
