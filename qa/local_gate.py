"""Fail-closed local gate. No skipped tests may be counted as success."""
from pathlib import Path
import sys
import json
import platform
import io
import unittest
from datetime import datetime, timezone
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from cutguard import __version__
from cutguard.doctor import diagnose


def main():
    root=Path(__file__).resolve().parents[1]
    log=io.StringIO()
    suite=unittest.defaultTestLoader.discover(str(root/'tests'))
    result=unittest.TextTestRunner(stream=log,verbosity=2).run(suite)
    environment=diagnose()
    passed=result.wasSuccessful() and not result.skipped and environment['video_cli_ready']
    target=root/'qa-results';target.mkdir(exist_ok=True)
    (target/'local-tests.txt').write_text(log.getvalue(),encoding='utf-8')
    data={'version':__version__,'checked_at':datetime.now(timezone.utc).isoformat(),'platform':platform.platform(),
          'tests_run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'skipped':len(result.skipped),
          'local_gate':'passed' if passed else 'failed','environment':environment,
          'windows_gui':'not_executed_here','real_browser':'not_executed_here','github_actions':'not_executed_here',
          'stable_release_ready':False}
    (target/'local-gate.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(data,ensure_ascii=False,indent=2))
    return 0 if passed else 1

if __name__=='__main__':raise SystemExit(main())
