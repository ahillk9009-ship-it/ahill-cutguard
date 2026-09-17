"""Real Tk event-loop test; mocks OS choosers/browser opening, not the scan engine."""
from pathlib import Path
import sys
import tempfile
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))


def main():
    import tkinter as tk
    from cutguard.gui import launch
    with tempfile.TemporaryDirectory() as temp:
        root=tk.Tk()  # Fails, rather than skips, when the display/Tk is unavailable.
        folder=Path(temp);srt=folder/'한국어 자막.srt'
        srt.write_text('1\n00:00:00,000 --> 00:00:01,000\n안녕하세요\n',encoding='utf-8')
        opened=[];errors=[];timed_out=[]
        def children(widget):
            for child in widget.winfo_children():
                yield child
                yield from children(child)
        def begin():
            widgets=list(children(root))
            entries=[w for w in widgets if w.winfo_class()=='TEntry']
            assert len(entries)==2
            entries[1].insert(0,str(srt))
            next(w for w in widgets if w.winfo_class()=='TButton' and w.cget('text')=='검사 시작').invoke()
        def poll():
            if opened or errors: root.destroy()
            else: root.after(100,poll)
        def deadline():
            timed_out.append(True);root.destroy()
        root.after(100,begin);root.after(200,poll);root.after(15000,deadline)
        root.report_callback_exception=lambda *args:(errors.append(str(args)),root.destroy())
        with patch('tkinter.Tk',return_value=root),patch('tkinter.filedialog.askdirectory',return_value=str(folder)),patch('tkinter.messagebox.showerror',side_effect=lambda *a:errors.append(a)),patch('cutguard.gui.webbrowser.open',side_effect=lambda uri:opened.append(uri)):
            launch()
        assert not timed_out,'GUI scan timed out'
        assert not errors,errors
        assert len(opened)==1 and opened[0].endswith('/report.html'),opened
        assert len(list(folder.glob('cutguard-*/report.json')))==1
    print('PASS: Tk window, controls, worker scan, completion, report-open request (OS chooser and browser mocked)')

if __name__=='__main__':main()
