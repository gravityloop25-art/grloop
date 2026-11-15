import sys, math, random, wave
import numpy as np
from PIL import Image, ImageDraw
from common import *
CMD=sys.argv[1]; SEED=int(sys.argv[2]); GAPD=float(sys.argv[3]); SP=float(sys.argv[4]); WR=float(sys.argv[5])
PV={int(x) for x in sys.argv[6:]}
rng=random.Random(SEED)
CX,CY,R=540.0,1000.0,450.0; BR=24.0; SUB=8
sky=Sky(181)
MEL=[64,67,69,67,64,62,60,62, 64,67,69,72,71,69,67,64, 62,65,67,65,62,60,59,60, 62,65,67,69,72,71,69,67]
BASS=[45,45,38,43]
HUES=[(255,60,220),(255,150,60),(60,220,255),(150,100,255),(120,255,160)]
def gapc(t): return -math.pi/2+WR*t
def adf(a,b): return abs((a-b+math.pi)%(2*math.pi)-math.pi)
def sim(maxfr=60*FPS):
    x,y=CX-80.0,CY+60.0; a=rng.uniform(0,2*math.pi); vx,vy=SP*math.cos(a),SP*math.sin(a)
    bounces=[]; traj=[]; esc=None; fr=0
    while fr<maxfr:
        for s in range(SUB):
            t=fr+(s+1)/SUB; x+=vx/SUB; y+=vy/SUB
            d=math.hypot(x-CX,y-CY)
            if esc is None and d>R-BR:
                ang=math.atan2(y-CY,x-CX)
                if adf(ang,gapc(t))<math.radians(GAPD)/2 and len(bounces)>=3: esc=fr; 
                else:
                    nx,ny=(x-CX)/d,(y-CY)/d; vn=vx*nx+vy*ny
                    if vn>0:
                        vx-=2*vn*nx; vy-=2*vn*ny; r=rng.uniform(-0.12,0.12); c,s_=math.cos(r),math.sin(r); vx,vy=vx*c-vy*s_,vx*s_+vy*c
                        x=CX+nx*(R-BR-1); y=CY+ny*(R-BR-1); bounces.append((fr,ang))
        traj.append((x,y))
        fr+=1
        if esc is not None and fr>esc+110: break
    return bounces,traj,esc
def tone_note(m,dur=1.6,amp=0.5):
    f=440*2**((m-69)/12); n=int(SR*dur); t=np.arange(n)/SR
    env=np.exp(-t*4.2)*(1-np.exp(-t*400))
    w=np.sin(2*np.pi*f*t)+0.35*np.sin(2*np.pi*2*f*t)*np.exp(-t*6)+0.15*np.sin(2*np.pi*3*f*t)*np.exp(-t*9)
    return amp*env*w
def build_audio(nfr,bounces,esc):
    n=int(nfr/FPS*SR)+SR; out=np.zeros(n)
    def add(sig,start):
        i=int(start/FPS*SR); e=min(n,i+len(sig)); out[i:e]+=sig[:e-i]
    for k,(fr,_) in enumerate(bounces):
        add(tone_note(MEL[k%32]),fr)
        add(tone_note(MEL[k%32]-12,1.0,0.12),fr)
        if k%4==0: add(tone_note(BASS[(k//4)%4]+12,1.4,0.35),fr)
    if esc is not None:
        for j,m in enumerate([69,72,76,81]): add(tone_note(m,2.4,0.4),esc+j*4)
        add(tone_note(45,2.6,0.4),esc)
    out/=max(1e-9,np.abs(out).max())*1.15
    pcm=(out*32000).astype(np.int16)
    with wave.open("audio.wav","wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
def draw(fr,bounces,traj,esc):
    img=Image.new("RGB",(W,H)); d=ImageDraw.Draw(img)
    nb=sum(1 for b in bounces if b[0]<=fr); last=[b for b in bounces if b[0]<=fr]
    # ring with gap
    g=math.degrees(gapc(fr)); gw=GAPD
    flash=0.0; col=(255,235,250)
    if last:
        age=fr-last[-1][0]; flash=max(0,1-age/14)
    ringc=tuple(int(c*(0.75+0.25*flash)) for c in col)
    d.arc((CX-R,CY-R,CX+R,CY+R),g+gw/2,g+360-gw/2,fill=ringc,width=6)
    for sgn in(-1,1):
        a=math.radians(g)+sgn*math.radians(gw)/2; d.ellipse((CX+R*math.cos(a)-9,CY+R*math.sin(a)-9,CX+R*math.cos(a)+9,CY+R*math.sin(a)+9),fill=(255,170,70))
    # ripples
    for k,(bf,ang) in enumerate(bounces):
        age=fr-bf
        if 0<=age<22:
            c=HUES[k%5]; rad=14+age*5; px=CX+(R)*math.cos(ang); py=CY+(R)*math.sin(ang); f=1-age/22
            d.ellipse((px-rad,py-rad,px+rad,py+rad),outline=tuple(int(v*f) for v in c),width=4)
    # trail
    c=HUES[(nb-1)%5] if nb>0 else HUES[0]
    for j in range(24,0,-1):
        if fr-j>=0:
            x,y=traj[fr-j]; f=(1-j/24)*0.5; r=BR*(1-j/40); d.ellipse((x-r,y-r,x+r,y+r),fill=tuple(int(v*f) for v in c))
    x,y=traj[fr]; d.ellipse((x-BR,y-BR,x+BR,y+BR),fill=c); d.ellipse((x-9,y-12,x-1,y-4),fill=tuple(min(255,v+120) for v in c))
    f1=font(72); t1="Every bounce plays"; t2="the next note"
    d.text((540-d.textlength(t1,font=f1)/2,95),t1,font=f1,fill=(255,240,252)); d.text((540-d.textlength(t2,font=f1)/2,178),t2,font=f1,fill=(255,240,252))
    f2=font(36); t3="no bounce = no music"; d.text((540-d.textlength(t3,font=f2)/2,282),t3,font=f2,fill=(210,190,225))
    f3=font(130); tx=str(nb); d.text((540-d.textlength(tx,font=f3)/2,CY+R+30),tx,font=f3,fill=c)
    f4=font(34); tx="NOTES PLAYED"; d.text((540-d.textlength(tx,font=f4)/2,CY+R+185),tx,font=f4,fill=(220,190,235))
    # note dots
    for k in range(32):
        xx=540-31*13+k*26+0; on=k<nb%32 or (nb>=32 and nb%32==0 and nb>0) or (nb>=32)
        d.ellipse((xx-6,300+0-6+0,xx+6,300+6),fill=(255,255,255)) if False else None
    if esc is not None and fr>=esc:
        k=fr-esc; f5=font(100); tx="ESCAPED!"; d.rectangle((0,CY-85,W,CY+85),fill=(0,0,0))
        if k%14<10 or k>40: d.text((540-d.textlength(tx,font=f5)/2,CY-60),tx,font=f5,fill=(255,250,210))
    return compose(sky.frame(fr),img,.7,.55,.3)
def main():
    bounces,traj,esc=sim()
    nfr=len(traj)
    print(SEED,GAPD,SP,WR,"bounces",len(bounces),"esc",esc and round(esc/30,1))
    if CMD=="sim": return
    if CMD=="preview":
        for f in PV: Image.fromarray(draw(f,bounces,traj,esc)).save(f"p_{f}.png")
        return
    wr=Writer()
    for fr in range(nfr): wr.write(draw(fr,bounces,traj,esc))
    wr.close(); build_audio(nfr,bounces,esc); mux("video_tmp.mp4","audio.wav","klang_ausbruch.mp4")
main()
