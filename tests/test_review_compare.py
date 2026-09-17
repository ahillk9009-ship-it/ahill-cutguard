import copy, unittest, tempfile, json
from pathlib import Path
from cutguard.review import blank_review, validate_review, save_new
from cutguard.compare import compare_reports
from cutguard.models import Config
from cutguard.cli import main


def report():
    return {'schema_version':'1.0','config':Config().__dict__,'media':{'name':'demo.mp4'},'subtitle':None,'findings':[
        {'code':'black','start':1.0,'end':1.3,'cue':None},
        {'code':'freeze','start':3.0,'end':5.0,'cue':None}]}


class ReviewCompareTests(unittest.TestCase):
    def test_roundtrip(self):
        r=report();v=blank_review(r);v['decisions']['0']={'status':'approved','note':'의도된 암전'}
        self.assertEqual(validate_review(r,json.loads(json.dumps(v))),v)

    def test_wrong_report_rejected(self):
        r=report();v=blank_review(r);r['media']['name']='different.mp4'
        with self.assertRaises(ValueError): validate_review(r,v)

    def test_bad_states_and_missing_entries(self):
        for mode in ('status','missing','note'):
            r=report();v=blank_review(r)
            if mode=='status': v['decisions']['0']['status']='fixed'
            elif mode=='missing': del v['decisions']['0']
            else: v['decisions']['0']['note']='x'*2001
            with self.assertRaises(ValueError):validate_review(r,v)

    def test_preserves_existing_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'review.json';save_new(p,{'a':1})
            with self.assertRaises(FileExistsError):save_new(p,{'a':2})
            self.assertEqual(json.loads(p.read_text()),{'a':1})

    def test_new_remaining_and_disappeared(self):
        a=report();b=copy.deepcopy(a);b['findings'][0]['start']+=.04
        b['findings'][1]={'code':'short_cut','start':6,'end':6.08,'cue':None}
        c=compare_reports(a,b)
        self.assertEqual([len(c[k]) for k in ('remaining','no_longer_detected','newly_detected')],[1,1,1])

    def test_one_to_one(self):
        a=report();a['findings']=[a['findings'][0]]*2;b=report();b['findings']=b['findings'][:1]
        self.assertEqual(len(compare_reports(a,b)['remaining']),1)

    def test_settings_and_scope_mismatch(self):
        for mode in ('config','scope'):
            a=report();b=copy.deepcopy(a)
            if mode=='config':b['config']['cps_max']=99
            else:b['subtitle']={'name':'a.srt'}
            with self.assertRaises(ValueError):compare_reports(a,b)

    def test_cli_review(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'r.json';p.write_text(json.dumps(report()));out=Path(tmp)/'v.json'
            self.assertEqual(main(['review',str(p),'--finding','0','--status','approved','--note','title card','--out',str(out)]),0)
            self.assertEqual(json.loads(out.read_text())['decisions']['0']['status'],'approved')

    def test_invalid_tolerance(self):
        with self.assertRaises(ValueError): compare_reports(report(),report(),float('nan'))
