#!/usr/bin/env python3
"""Render the evidence-bounded 30-second Action Gate v0.4.2 demo."""
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import subprocess, os, wave, math

OUT = "/home/ubuntu/action_gate_demo"
W, H, FPS, DURATION = 1920, 1080, 30, 30
TOTAL = FPS * DURATION
FONT = "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf"
BOLD = "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf"
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
C = {
    "white": (241,246,252), "muted": (165,181,200), "dim": (109,129,151),
    "bg": (8,14,24), "panel": (15,25,38), "panel2": (19,32,47),
    "line": (47,66,87), "blue": (105,177,255), "cyan": (104,211,225),
    "green": (115,211,164), "red": (238,123,126), "amber": (235,190,116),
}
SCENES=[(0,5),(5,11),(11,18),(18,24),(24,28),(28,30)]

def F(size, bold=False, mono=False):
    return ImageFont.truetype(MONO if mono else (BOLD if bold else FONT), size)

def rounded(d, box, radius=22, fill=None, outline=None, width=2):
    d.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)

def text(d, xy, value, size=28, color=None, bold=False, anchor="mm", mono=False, spacing=6):
    d.multiline_text(xy, value, font=F(size,bold,mono), fill=color or C["white"], anchor=anchor,
                     align="center", spacing=spacing)

def ease(x):
    x=max(0.0,min(1.0,x)); return x*x*(3-2*x)

def slide(p, dist=24): return int(dist*(1-ease(p)))

def make_bg():
    yy=np.linspace(0,1,H)[:,None,None]
    top=np.array([7,13,22],dtype=np.float32)[None,None,:]
    bottom=np.array([13,25,40],dtype=np.float32)[None,None,:]
    arr=np.broadcast_to(top*(1-yy)+bottom*yy,(H,W,3)).copy().astype(np.uint8)
    im=Image.fromarray(arr,"RGB")
    d=ImageDraw.Draw(im,"RGBA")
    # Restrained blueprint grid and soft structural edge accents.
    for x in range(0,W,96): d.line((x,0,x,H),fill=(86,132,169,13),width=1)
    for y in range(0,H,96): d.line((0,y,W,y),fill=(86,132,169,13),width=1)
    d.ellipse((1470,-590,2240,180),fill=(41,103,145,20))
    d.ellipse((-500,740,250,1490),fill=(54,74,130,18))
    return im
BG=make_bg()

def frame_header(d,t):
    rounded(d,(90,44,475,98),27,(18,34,51),outline=(50,80,107),width=1)
    text(d,(282,71),"ACTION GATE  /  v0.4.2",19,C["cyan"],bold=True)
    rounded(d,(1155,44,1830,98),27,(22,32,44),outline=(76,91,105),width=1)
    text(d,(1492,71),"ILLUSTRATIVE SIMULATION  ·  LOCAL TEST RESULTS",17,C["amber"],bold=True)
    d.line((90,126,1830,126),fill=(57,78,98,170),width=1)
    d.line((90,1031,1830,1031),fill=(57,78,98,130),width=1)
    text(d,(960,1056),"TEST FIXTURES  ·  NO CUSTOMER SYSTEM  ·  NOT LIVE PRODUCTION DATA",16,C["muted"],bold=True)
    # Timeline rail.
    d.rounded_rectangle((90,1018,1830,1025),radius=3,fill=(47,64,82,150))
    d.rounded_rectangle((90,1018,90+int(1740*t/DURATION),1025),radius=3,fill=(*C["cyan"],220))

def scene_at(t):
    for i,(a,b) in enumerate(SCENES):
        if a<=t<b or (i==len(SCENES)-1 and t<=b): return i
    return len(SCENES)-1

def draw_scene(i,t):
    a,b=SCENES[i]; local=t-a; p=ease(local/min(.75,b-a))
    im=BG.copy(); d=ImageDraw.Draw(im,"RGBA"); frame_header(d,t)
    if i==0:
        text(d,(960,292+slide(p,40)),"AI AGENTS CAN ACT.",76,C["white"],bold=True)
        text(d,(960,402+slide(p,40)),"SHOULD THEY?",92,C["blue"],bold=True)
        d.line((430,535,1490,535),fill=(72,113,150,160),width=3)
        # Moving request pulse stops at the gate boundary.
        px=460+int(min(1,(local/3.4))*740)
        d.ellipse((px-11,524,px+11,546),fill=(*C["cyan"],245))
        rounded(d,(340,620,1580,822),24,(15,27,42),outline=(57,84,110),width=2)
        text(d,(420,670),"LOCAL HTTP TEST FIXTURE",18,C["amber"],bold=True,anchor="lm")
        text(d,(420,735),"DELETE FILE",26,C["white"],bold=True,anchor="lm",mono=True)
        text(d,(420,783),"/production/data.db",23,C["muted"],anchor="lm",mono=True)
        rounded(d,(1270,702,1515,777),17,(23,40,57),outline=(70,112,146),width=1)
        text(d,(1392,739),"REQUEST",19,C["cyan"],bold=True)
    elif i==1:
        text(d,(960,210+slide(p)),"CONTEXT. POLICY. DECISION.",55,C["white"],bold=True)
        # Fields match the HTTP test fixture and the actual v0.4.2 decision policy.
        rounded(d,(168,310,835,798),28,(15,27,42),outline=(60,88,116),width=2)
        text(d,(225,362),"TEST REQUEST",18,C["blue"],bold=True,anchor="lm")
        fields=[("TENANT","integration-tenant"),("ACTOR","actor-1"),("ACTION","delete_file"),("TARGET","/production/data.db")]
        for j,(k,v) in enumerate(fields):
            y=443+j*80
            text(d,(232,y),k,17,C["dim"],bold=True,anchor="lm",mono=True)
            text(d,(472,y),v,22,C["white"],anchor="lm",mono=True)
            if j<3: d.line((224,y+32,780,y+32),fill=(41,58,76,180),width=1)
        # Gate and policy label; no invented risk score or fabricated event ID.
        rounded(d,(1005,333,1735,520),26,(18,32,48),outline=(77,154,192),width=2)
        text(d,(1370,390),"ACTION GATE",33,C["cyan"],bold=True)
        text(d,(1370,448),"production_destructive_action",19,C["muted"],mono=True)
        rounded(d,(1136,616,1600,716),22,(23,34,49),outline=(87,104,121),width=1)
        text(d,(1368,666),"POLICY CHECK",20,C["muted"],bold=True)
        d.line((835,540,1005,430),fill=(104,211,225,190),width=3)
        d.line((1370,520,1370,616),fill=(104,211,225,145),width=3)
        for j in range(4):
            x=880+j*39; y=510-j*25
            d.ellipse((x-5,y-5,x+5,y+5),fill=(*C["cyan"],210))
    elif i==2:
        text(d,(960,206+slide(p)),"DECIDE BEFORE EXECUTION.",56,C["white"],bold=True)
        cards=[
            (150,336,925,800,"DENY",C["red"],"delete_file  ·  /production/data.db","No tool side effect in this test"),
            (995,336,1770,800,"ALLOW",C["green"],"read_public_file  ·  /public/info.txt","Executes only with bound decision ID"),
        ]
        for x1,y1,x2,y2,label,col,action,detail in cards:
            rounded(d,(x1,y1,x2,y2),28,(15,27,42),outline=(*col,170),width=2)
            rounded(d,(x1+42,y1+42,x1+258,y1+106),20,(*col,25),outline=(*col,130),width=1)
            text(d,(x1+150,y1+74),label,27,col,bold=True,mono=True)
            text(d,(x1+58,y1+192),action,23,C["white"],anchor="lm",mono=True)
            d.line((x1+58,y1+232,x2-58,y1+232),fill=(53,71,89,190),width=1)
            text(d,(x1+58,y1+291),detail,20,C["muted"],anchor="lm")
            # Visual path follows actual asserted outcome (stop / execute after binding).
            sy=y1+360; d.line((x1+58,sy,x2-80,sy),fill=(*col,155),width=3)
            if label=="DENY":
                d.line((x2-108,sy-18,x2-72,sy+18),fill=(*col,245),width=5)
                d.line((x2-72,sy-18,x2-108,sy+18),fill=(*col,245),width=5)
                text(d,(x1+70,sy+48),"TOOL NOT INVOKED",16,col,bold=True,anchor="lm")
            else:
                d.ellipse((x2-96,sy-9,x2-78,sy+9),fill=(*col,245))
                text(d,(x1+70,sy+48),"GATE-BOUND TEST TOOL",16,col,bold=True,anchor="lm")
    elif i==3:
        text(d,(960,207+slide(p)),"A DECISION MUST CHANGE WHAT HAPPENS.",48,C["white"],bold=True)
        rounded(d,(250,335,1670,828),28,(14,26,41),outline=(55,79,103),width=2)
        # Clear two-path execution diagram based on the passing HTTP integration test.
        text(d,(385,414),"HTTP ENFORCEMENT TEST",19,C["blue"],bold=True,anchor="lm")
        d.line((390,515,1530,515),fill=(65,92,119,190),width=4)
        nodes=[(440,"REQUEST",C["white"]),(865,"ACTION GATE",C["cyan"]),(1390,"TEST TOOL",C["muted"])]
        for x,label,col in nodes:
            d.ellipse((x-24,491,x+24,539),fill=(*col,45),outline=(*col,220),width=3)
            text(d,(x,584),label,18,col,bold=True)
        # DENY branch ends at the boundary.
        d.line((865,540,865,665),fill=(*C["red"],200),width=3)
        rounded(d,(520,670,870,760),20,(45,27,37),outline=(*C["red"],180),width=1)
        text(d,(695,715),"DENY  →  BLOCKED",22,C["red"],bold=True,mono=True)
        # ALLOW branch proceeds only after a decision ID is bound.
        d.line((910,515,1390,515),fill=(*C["green"],205),width=4)
        rounded(d,(1045,650,1530,764),20,(21,40,42),outline=(*C["green"],155),width=1)
        text(d,(1287,684),"ALLOW + BOUND DECISION",19,C["green"],bold=True)
        text(d,(1287,727),"tool_executed = true",21,C["white"],mono=True)
        text(d,(960,802),"The tool in this run was the repository's integration-test tool server.",17,C["muted"])
    elif i==4:
        text(d,(960,202+slide(p)),"DECISIONS. EVIDENCE. REVIEW.",50,C["white"],bold=True)
        # Evidence states shown are assertions from the actual local integration runs.
        cards=[
            (160,340,690,650,"EXECUTED",C["green"],"Evidence state recorded"),
            (710,340,1240,650,"REPLAY REJECTED",C["amber"],"One-time nonce · fail closed"),
            (1260,340,1760,650,"80 REPO TESTS PASS",C["blue"],"Fresh isolated test directory"),
        ]
        for x1,y1,x2,y2,title,col,sub in cards:
            rounded(d,(x1,y1,x2,y2),25,(15,27,42),outline=(*col,145),width=2)
            text(d,((x1+x2)//2,y1+105),title,24,col,bold=True,mono=True)
            text(d,((x1+x2)//2,y1+186),sub,17,C["muted"])
        rounded(d,(385,734,1535,828),22,(15,31,43),outline=(54,89,116),width=1)
        text(d,(960,780),"HTTP INTEGRATION  PASS     ·     MCP INTEGRATION  PASS",22,C["cyan"],bold=True)
    elif i==5:
        rounded(d,(235,200,1685,854),34,(13,25,40),outline=(77,137,166),width=2)
        rounded(d,(760,244,1160,299),27,(17,41,52),outline=(65,131,144),width=1)
        text(d,(960,271),"LOCAL TESTS · v0.4.2",19,C["cyan"],bold=True)
        text(d,(960,392),"ACTION GATE",69,C["white"],bold=True)
        text(d,(960,482),"GOVERN THE ACTION. NOT JUST THE INTENT.",30,C["cyan"],bold=True)
        text(d,(960,568),"HTTP + MCP INTEGRATION PASS  ·  80 REPO TESTS PASS",20,C["green"],bold=True)
        text(d,(960,651),"6a8aa17a28ba50c73de1ba714f25bfc04e3268c9",22,C["muted"],mono=True)
        text(d,(960,724),"NOT A CUSTOMER DEPLOYMENT  ·  NO PRODUCTION SYSTEM USED",17,C["amber"],bold=True)
        text(d,(960,791),"github.com/hamidhayatijozani/HamidCognition-Unified",18,C["muted"],mono=True)
    return im

def render_video():
    out=os.path.join(OUT,"action-gate-demo-30s.mp4")
    cmd=["ffmpeg","-y","-loglevel","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-an","-c:v","libx264","-preset","medium","-crf","19","-pix_fmt","yuv420p","-movflags","+faststart",out]
    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    for n in range(TOTAL):
        t=n/FPS; i=scene_at(t); img=draw_scene(i,t)
        # Brief 0.25s dissolve at information-state boundaries.
        start,end=SCENES[i]
        if i>0 and t-start<0.25:
            prev=draw_scene(i-1,t)
            img=Image.blend(prev,img,ease((t-start)/0.25))
        proc.stdin.write(img.tobytes())
        if n%150==0: print(f"Rendered {n}/{TOTAL} frames",flush=True)
    proc.stdin.close()
    if proc.wait()!=0: raise RuntimeError("ffmpeg video encoding failed")
    return out

def render_audio(video_path):
    sr=48000; n=sr*DURATION; t=np.arange(n,dtype=np.float64)/sr
    # Original, subdued, instrumental electronic underscore; no vocals or sourced material.
    chords=[(146.83,174.61,220.00),(116.54,146.83,174.61),(130.81,164.81,196.00),(98.00,130.81,164.81)]
    audio=np.zeros(n,dtype=np.float64)
    for k,fs in enumerate(chords):
        a=k*7.5; b=min(DURATION,a+8.3); ix=(t>=a)&(t<b); lt=t[ix]-a; dur=b-a
        env=np.minimum(1,np.maximum(0,lt/1.0))*np.minimum(1,np.maximum(0,(dur-lt)/1.4))
        pad=np.zeros(ix.sum())
        for j,f in enumerate(fs): pad+=.48*np.sin(2*np.pi*f*lt+j*.13)+.1*np.sin(2*np.pi*f*2.002*lt+j*.2)
        audio[ix]+=.055*env*pad
    for beat in np.arange(0,DURATION,1.25):
        p0=int(beat*sr); q=np.arange(min(int(.25*sr),n-p0))/sr
        audio[p0:p0+len(q)]+=.025*np.sin(2*np.pi*(72-16*q)*q)*np.exp(-q*15)
    for at in [5,11,18,24,28]:
        p0=int(at*sr); q=np.arange(int(.11*sr))/sr
        audio[p0:p0+len(q)]+=.042*(np.sin(2*np.pi*900*q)+.4*np.sin(2*np.pi*1400*q))*np.exp(-q*34)
    fade=np.ones(n); fade[:sr//2]=np.linspace(0,1,sr//2); fade[-int(1.2*sr):]=np.linspace(1,0,int(1.2*sr))
    audio=np.tanh(audio*fade*1.7)*.8
    stereo=np.column_stack([audio,np.roll(audio,int(.004*sr))])
    pcm=(np.clip(stereo,-1,1)*32767).astype("<i2")
    wav_path=os.path.join(OUT,"action-gate-demo-underscore.wav")
    with wave.open(wav_path,"wb") as wf:
        wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(sr); wf.writeframes(pcm.tobytes())
    tmp=os.path.join(OUT,"action-gate-demo-with-audio.mp4")
    subprocess.run(["ffmpeg","-y","-loglevel","error","-i",video_path,"-i",wav_path,"-c:v","copy","-c:a","aac","-b:a","192k","-shortest","-movflags","+faststart",tmp],check=True)
    os.replace(tmp,video_path)

def main():
    video=render_video(); render_audio(video)
    draw_scene(5,29.0).save(os.path.join(OUT,"action-gate-demo-poster.jpg"),quality=93,optimize=True)
    print(f"VIDEO={video}")
    print("POSTER="+os.path.join(OUT,"action-gate-demo-poster.jpg"))

if __name__=="__main__": main()
