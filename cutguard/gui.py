"""Small stdlib desktop launcher. Work happens off the Tk thread."""
from datetime import datetime
from pathlib import Path
import queue
import threading
import webbrowser
from .engine import scan


def launch():
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox
    try:
        root = tk.Tk()
    except tk.TclError as exc:
        raise ValueError('GUI를 시작할 수 없습니다. 데스크톱 화면/Tcl·Tk 설치를 확인하거나 scan 명령을 사용하세요.') from exc
    root.title('Ahill CutGuard · 영상 검수')
    root.geometry('720x400')
    root.minsize(580, 380)
    frame = ttk.Frame(root, padding=24)
    frame.pack(fill='both', expand=True)
    ttk.Label(frame, text='CutGuard', font=('', 24, 'bold')).grid(row=0, column=0, sticky='w')
    ttk.Label(frame, text='영상과 자막의 확인할 구간을 찾습니다. 원본은 변경하지 않습니다.').grid(row=1, column=0, columnspan=3, sticky='w', pady=(0, 22))
    video, srt, status = tk.StringVar(), tk.StringVar(), tk.StringVar(value='영상 또는 SRT 파일을 선택하세요.')
    def choose(target, types):
        path = filedialog.askopenfilename(filetypes=types)
        if path:
            target.set(path)
    for row, label, target, types in [(2, '영상 (선택)', video, [('Video', '*.mp4 *.mov *.mkv *.avi *.webm'), ('All', '*.*')]), (3, 'SRT (선택)', srt, [('Subtitles', '*.srt'), ('All', '*.*')])]:
        ttk.Label(frame, text=label).grid(row=row, column=0, sticky='w', pady=8)
        ttk.Entry(frame, textvariable=target).grid(row=row, column=1, sticky='ew', padx=12)
        ttk.Button(frame, text='찾기', command=lambda t=target, ft=types: choose(t, ft)).grid(row=row, column=2)
    frame.columnconfigure(1, weight=1)
    events = queue.Queue()
    busy = False
    def begin():
        nonlocal busy
        v, s = video.get().strip(), srt.get().strip()
        if not v and not s:
            messagebox.showinfo('파일 선택', '영상 또는 SRT 파일을 선택하세요.')
            return
        parent = filedialog.askdirectory(title='보고서를 저장할 상위 폴더 선택')
        if not parent:
            return
        out = Path(parent) / ('cutguard-' + datetime.now().strftime('%Y%m%d-%H%M%S-%f'))
        button.state(['disabled'])
        busy = True
        def work():
            try:
                scan(v or None, s or None, out, progress=lambda msg: events.put(('status', msg)))
                events.put(('done', out / 'report.html'))
            except Exception as exc:
                events.put(('error', str(exc)))
        threading.Thread(target=work, daemon=True).start()
    button = ttk.Button(frame, text='검사 시작', command=begin)
    button.grid(row=4, column=0, columnspan=3, sticky='ew', pady=24)
    ttk.Label(frame, textvariable=status, wraplength=640).grid(row=5, column=0, columnspan=3, sticky='w')
    ttk.Label(frame, text='영상 검사: FFmpeg 필요 · 얼굴/음성 싱크 검사는 후속 버전 예정', foreground='#666').grid(row=6, column=0, columnspan=3, sticky='w', pady=18)
    def poll():
        nonlocal busy
        try:
            while True:
                kind, value = events.get_nowait()
                if kind == 'status':
                    status.set(value)
                else:
                    busy = False
                    button.state(['!disabled'])
                    if kind == 'done':
                        status.set(f'완료: {value}')
                        webbrowser.open(value.resolve().as_uri())
                    else:
                        status.set('검사 실패')
                        messagebox.showerror('CutGuard', value)
        except queue.Empty:
            pass
        root.after(150, poll)
    def close():
        if busy:
            messagebox.showinfo('검사 진행 중', '검사가 완료된 후 창을 닫아 주세요.')
        else:
            root.destroy()
    root.protocol('WM_DELETE_WINDOW', close)
    poll()
    root.mainloop()
