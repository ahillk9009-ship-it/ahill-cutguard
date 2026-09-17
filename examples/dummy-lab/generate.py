"""Generate original deterministic motion-graphics QC fixtures. No external footage."""
from pathlib import Path
import math, subprocess, json, argparse
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W,H,FPS,SECONDS=360,640,25,12
ROOT=Path(__file__).resolve().parent

def font(size, bold=False):
    name='DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf'
    try: return ImageFont.truetype(name,size)
    except OSError: return ImageFont.load_default(size=size)

FONTS={s:font(s,s in (32,48,19)) for s in (11,12,14,19,32,48)}
COLORS=[((12,27,40),(76,223,199)),((32,20,43),(243,137,177)),((31,30,14),(234,208,112))]

def frame(n):
    t=n/FPS; scene=n//100; bg,accent=COLORS[scene]
    y,x=np.mgrid[0:H,0:W]
    glow=np.clip(1-np.sqrt(((x-180)/300)**2+((y-270)/400)**2),0,1)
    arr=np.empty((H,W,3),dtype=np.uint8)
    for c in range(3): arr[:,:,c]=np.clip(bg[c]+glow*16,0,255)
    im=Image.fromarray(arr); d=ImageDraw.Draw(im)
    d.text((24,24),'AHILL LAB / CUTGUARD',font=FONTS[12],fill=accent)
    d.text((24,62),['FLOW','PULSE','ORBIT'][scene],font=FONTS[48],fill=(240,244,245))
    d.text((25,122),'SYNTHETIC MOTION STUDY',font=FONTS[11],fill=(175,187,197))
    # Visibly moving object: no static shots in the clean reference.
    cx=180+75*math.sin(t*1.6); cy=300+65*math.cos(t*1.1)
    d.rounded_rectangle((22,165,338,448),radius=22,outline=(70,80,88),width=1)
    for k in range(3):
        radius=35+k*22
        col=tuple(int(v*(1-k*.21)) for v in accent)
        d.ellipse((cx-radius,cy-radius,cx+radius,cy+radius),outline=col,width=3)
    d.ellipse((cx-8,cy-8,cx+8,cy+8),fill=accent)
    for k in range(8):
        px=40+k*40; height=12+18*(1+math.sin(t*3+k*.7))
        d.rounded_rectangle((px,429-height,px+6,429),radius=3,fill=accent)
    d.text((24,480),f'SCENE 0{scene+1}',font=FONTS[19],fill=accent)
    d.text((24,515),'Original procedural test footage',font=FONTS[14],fill=(206,214,220))
    d.line((24,566,336,566),fill=(75,84,90),width=2)
    d.line((24,566,24+312*t/SECONDS,566),fill=accent,width=3)
    d.text((24,590),f'{t:05.2f}s   /   12.00s',font=FONTS[14],fill=(220,226,230))
    d.text((24,616),'360 x 640   |   25 FPS   |   NO AUDIO',font=FONTS[11],fill=(150,166,178))
    return im

def write_variant(name, frames):
    path=ROOT/'media'/f'{name}.mp4'
    command=['ffmpeg','-nostdin','-hide_banner','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','pipe:0','-an','-c:v','libx264','-crf','18','-preset','fast','-pix_fmt','yuv420p','-movflags','+faststart',str(path)]
    proc=subprocess.Popen(command,stdin=subprocess.PIPE)
    try:
        for image in frames: proc.stdin.write(image.tobytes())
    finally: proc.stdin.close()
    if proc.wait(timeout=60): raise RuntimeError('FFmpeg encode failed')

def main():
    (ROOT/'media').mkdir(exist_ok=True)
    clean=[frame(n) for n in range(FPS*SECONDS)]
    dirty=[im.copy() for im in clean]
    for n in range(75,77): dirty[n]=Image.new('RGB',(W,H),'white')
    for n in range(150,156): dirty[n]=Image.new('RGB',(W,H),'black')
    # Repeat frame 200 through 235; freeze starts at 8.00, motion returns at 9.44.
    for n in range(200,236): dirty[n]=clean[200].copy()
    write_variant('01-clean',clean)
    write_variant('02-faulty',dirty)
    # Same visual signal but intentionally approved flash/blackout/hold.
    # Identical bytes ensure the comparison isolates editorial intent.
    import shutil
    shutil.copyfile(ROOT/'media/02-faulty.mp4',ROOT/'media/03-intentional.mp4')
    good='''1
00:00:00,300 --> 00:00:02,700
흐름을 따라 움직입니다.

2
00:00:03,000 --> 00:00:05,700
색과 리듬을 확인합니다.

3
00:00:06,000 --> 00:00:08,700
장면이 자연스럽게 이어집니다.

4
00:00:09,000 --> 00:00:11,700
마지막까지 확인합니다.
'''
    bad='''1
00:00:00,300 --> 00:00:02,700
흐름을 따라 움직입니다.

2
00:00:02,500 --> 00:00:02,900
이 자막은 너무 빠르게 지나가서 읽기가 어렵습니다.

3
00:00:06,000 --> 00:00:08,700
장면이 자연스럽게 이어집니다.

4
00:00:11,000 --> 00:00:13,000
영상이 끝난 뒤에도 남는 자막
'''
    for name,text in [('01-clean',good),('02-faulty',bad),('03-intentional',good)]:
        (ROOT/'media'/f'{name}.srt').write_text(text,encoding='utf-8')
    truth={'description':'Hand-authored synthetic ground truth; not real-world accuracy evidence.',
           'fps':FPS,'duration':SECONDS,'tolerance_seconds':0.08,
           'cases':{'01-clean':{'defects':[]},'02-faulty':{'defects':[
            {'code':'short_cut','start':3.0,'end':3.08},
            {'code':'black','start':6.0,'end':6.24},
            {'code':'freeze','start':8.0,'end':9.44},
            {'code':'srt_overlap','cue':'2'}, {'code':'srt_speed','cue':'2'},
            {'code':'srt_line_length','cue':'2'}, {'code':'srt_out_of_bounds','cue':'4'}]},
           '03-intentional':{'defects':[],'approved_effects':['3.00–3.08 flash','6.00–6.24 blackout','8.00–9.44 hold'],
           'note':'Video bytes equal faulty case; editorial intent differs, subtitles are clean. Heuristic candidates must not be presented as confirmed defects.'}}}
    (ROOT/'ground-truth.json').write_text(json.dumps(truth,ensure_ascii=False,indent=2),encoding='utf-8')
    clean[40].save(ROOT/'poster.png')
    print('Generated 3 videos, 3 SRTs and ground truth.',flush=True)

if __name__=='__main__': main()
