"""Read-only installation diagnosis; does not install or alter the system."""
import platform
import shutil
import subprocess
import sys
import json


def diagnose():
    checks={'python':{'version':platform.python_version(),'ok':sys.version_info >= (3,10)},
            'platform':platform.platform()}
    for tool in ('ffmpeg','ffprobe'):
        executable=shutil.which(tool)
        value={'ok':False,'version':None}
        if executable:
            try:
                r=subprocess.run([executable,'-version'],capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=10)
                value={'ok':r.returncode==0,'version':r.stdout.splitlines()[0] if r.stdout else None}
            except (OSError,subprocess.TimeoutExpired):pass
        checks[tool]=value
    try:
        import tkinter
        checks['tkinter']={'importable':True,'version':tkinter.TkVersion,
                           'notice':'모듈 확인만 수행했습니다. GUI 화면 동작은 별도 확인해야 합니다.'}
    except ImportError:
        checks['tkinter']={'importable':False}
    checks['subtitle_cli_ready']=checks['python']['ok']
    checks['video_cli_ready']=checks['python']['ok'] and all(checks[t]['ok'] for t in ('ffmpeg','ffprobe'))
    return checks


def doctor_command(args):
    result=diagnose()
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 0 if result['video_cli_ready'] else 1
