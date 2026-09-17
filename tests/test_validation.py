import contextlib,io,json,tempfile,unittest,copy
from pathlib import Path
from cutguard.cli import main
from cutguard.validation import read_report
from cutguard.models import Config
from cutguard.doctor import diagnose
from unittest.mock import patch


class ValidationTests(unittest.TestCase):
    def valid(self):
        return {'schema_version':'1.0','config':Config().__dict__,'media':None,'subtitle':{'name':'a.srt'},
                'findings':[{'code':'srt_speed','start':1,'end':2,'cue':'1'}]}

    def test_reject_malformed_shapes_without_tracebacks(self):
        variants=[[],{}, {'schema_version':'9'}, self.valid(),self.valid(),self.valid()]
        variants[3]['findings'][0]['start']=float('nan')
        variants[4]['findings']='bad'
        variants[5]['config']['cps_max']=True
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/'report.json'
            for index,variant in enumerate(variants):
                p.write_text(json.dumps(variant))
                err=io.StringIO()
                with contextlib.redirect_stderr(err):
                    result=main(['review',str(p),'--out',str(Path(temp)/f'out{index}.json')])
                self.assertEqual(result,2)
                self.assertNotIn('Traceback',err.getvalue())
                self.assertFalse((Path(temp)/f'out{index}.json').exists())

    def test_utf8_bom(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/'r.json';p.write_text(json.dumps(self.valid()),encoding='utf-8-sig')
            self.assertEqual(read_report(p)['schema_version'],'1.0')

    def test_reversed_and_infinite_times(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/'r.json'
            for end in (0,float('inf')):
                r=self.valid();r['findings'][0]['end']=end;p.write_text(json.dumps(r))
                with self.assertRaises(ValueError):read_report(p)

    def test_missing_ffmpeg_diagnosis(self):
        with patch('cutguard.doctor.shutil.which',return_value=None):
            report=diagnose()
        self.assertTrue(report['subtitle_cli_ready'])
        self.assertFalse(report['video_cli_ready'])
