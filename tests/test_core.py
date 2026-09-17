import math
from pathlib import Path
import tempfile
import unittest
from cutguard.models import Config, Cue, timestamp
from cutguard.subtitles import parse_srt, check_cues, inspect_srt
from cutguard.video import parse_log
from cutguard.engine import scan
from cutguard.cli import main


class SubtitleTests(unittest.TestCase):
    def test_bom_crlf_and_comma(self):
        cues, errors = parse_srt('\ufeff1\r\n00:00:01,000 --> 00:00:02,500\r\n안녕하세요\r\n')
        self.assertEqual(errors, [])
        self.assertEqual(cues[0].end, 2.5)

    def test_malformed_is_not_silently_skipped(self):
        cues, errors = parse_srt('1\n00:70:00,000 --> 00:00:02,000\n잘못된 시간')
        self.assertEqual(cues, [])
        self.assertEqual(errors[0].code, 'srt_parse')

    def test_empty_file(self):
        self.assertEqual(parse_srt('  ')[1][0].code, 'srt_empty')

    def test_nested_overlap_and_touching(self):
        cues = [Cue('1', 0, 10, 'a'), Cue('2', 1, 2, 'b'), Cue('3', 3, 4, 'c'), Cue('4', 10, 11, 'd')]
        overlaps = [f for f in check_cues(cues, 12) if f.code == 'srt_overlap']
        self.assertEqual([f.cue for f in overlaps], ['2', '3'])

    def test_invalid_duration_and_bounds(self):
        codes = {f.code for f in check_cues([Cue('1', 8, 7, 'a'), Cue('2', 9, 12, 'b')], 10)}
        self.assertIn('srt_duration', codes)
        self.assertIn('srt_out_of_bounds', codes)

    def test_korean_speed_excludes_tags_and_spaces(self):
        self.assertNotIn('srt_speed', {f.code for f in check_cues([Cue('1', 0, 1, '<i>가 나</i>')], 2, Config(cps_max=2))})
        self.assertIn('srt_speed', {f.code for f in check_cues([Cue('1', 0, .5, '<i>가 나</i>')], 2, Config(cps_max=2))})

    def test_duplicate_and_order(self):
        cues, errors = parse_srt('1\n00:00:02,000 --> 00:00:03,000\na\n\n1\n00:00:01,000 --> 00:00:02,000\nb')
        self.assertEqual(errors[0].code, 'srt_duplicate')
        self.assertIn('srt_order', {f.code for f in check_cues(cues, 4)})

    def test_cp949(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'korean.srt'
            path.write_bytes('1\n00:00:00,000 --> 00:00:01,000\n안녕'.encode('cp949'))
            self.assertEqual(inspect_srt(path, 2, Config())[0][0].text, '안녕')


class CoreTests(unittest.TestCase):
    def test_invalid_config(self):
        for kwargs in [{'freeze_min': -1}, {'scene_threshold': 1}, {'cps_max': math.nan}, {'timeout': math.inf}, {'thumbnails': -1}]:
            with self.assertRaises(ValueError):
                Config(**kwargs)

    def test_eof_freeze_and_scene_boundaries(self):
        issues = parse_log(['freeze_start: 2', 'showinfo pts_time:1', 'showinfo pts_time:1.08', 'showinfo pts_time:4'], 5, Config())
        self.assertEqual([(f.start, f.end) for f in issues if f.code == 'freeze'], [(2, 5)])
        self.assertEqual(len([f for f in issues if f.code == 'short_cut']), 1)

    def test_timestamp_carry(self):
        self.assertEqual(timestamp(59.9999), '00:01:00.000')

    def test_missing_input_exit(self):
        self.assertEqual(main(['scan']), 2)

    def test_srt_only_report_and_overwrite_protection(self):
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / 'captions.srt'
            original = '1\n00:00:00,000 --> 00:00:02,000\n안녕'
            source.write_text(original, encoding='utf-8')
            out = Path(temp) / 'result'
            report = scan(srt=source, output=out)
            self.assertEqual(len(report['warnings']), 1)
            self.assertTrue((out / 'report.html').is_file())
            self.assertTrue((out / 'markers.csv').is_file())
            with self.assertRaises(ValueError):
                scan(srt=source, output=out)
            self.assertEqual(source.read_text(encoding='utf-8'), original)

    def test_html_escape(self):
        from cutguard.report import render
        report = {'findings': [], 'media': None, 'subtitle': {'name': '<img src=x onerror=alert(1)>'},
                  'warnings': ['<script>alert(1)</script>'], 'config': Config().__dict__, 'version': 'test', 'created_at': 'now'}
        body = render(report)
        self.assertNotIn('<img src=x', body)
        self.assertIn('&lt;script&gt;', body)


if __name__ == '__main__':
    unittest.main()
