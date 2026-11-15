import sys, math, random
import numpy as np
from PIL import Image, ImageDraw
from common import *
CMD=sys.argv[1]; SEED=int(sys.argv[2]); DOOR=float(sys.argv[3]); TARGET=int(sys.argv[4]); SP=float(sys.argv[5]); NPER=int(sys.argv[6])
PV={int(x) for x in sys.argv[7:]}
random.seed(SEED); rng=np.random.default_rng(SEED)
CX,CY,R=540.0,1000.0,470.0; BR=12.0; SUB=3; WROT=0.010
COLS=[(255,40,220),(255,150,60),(60,220,255),(150,90,255)]; NAMES=["PINK","ORANGE","CYAN","PURPLE"]
sky=Sky(161); DR=math.radians(DOOR)
N=4*NPER; aa=rng.uniform(0,2*np.pi,N); rr=rng.uniform(0,330,N)
P=np.stack([CX+rr*np.cos(aa),CY+rr*np.sin(aa)],1); b=rng.uniform(0,2*np.pi,N); V=SP*np.stack([np.cos(b),np.sin(b)],1)
C=np.arange(N)%4; esc=[0,0,0,0]; events=[]
EP=np.zeros((0,2)); EV=np.zeros((0,2)); EC=np.zeros(0,int); EA=np.zeros(0)
def dang(c,t): return -math.pi/2+c*math.pi/2+WROT*t
def step(fr):
    global P,V,C,EP,EV,EC,EA
    ne=0; nb=0
    for sub in range(SUB):
        P+=V/SUB; t=fr+(sub+1)/SUB
        rel=P-[CX,CY]; d=np.hypot(rel[:,0],rel[:,1])+1e-9; out=np.where(d>R-BR)[0]
        if len(out):
            ang=np.arctan2(rel[out,1],rel[out,0]); th=np.array([dang(c,t) for c in range(4)])
            df=np.abs((ang[:,None]-th[None,:]+math.pi)%(2*math.pi)-math.pi)
            own=df[np.arange(len(out)),C[out]]<DR/2
            go=out[own&(d[out]>R-BR+3)]
            if len(go):
                for c in C[go]: esc[c]+=1
                ne+=len(go); EP=np.vstack([EP,P[go]]); EV=np.vstack([EV,V[go]*1.2]); EC=np.concatenate([EC,C[go]]); EA=np.concatenate([EA,np.zeros(len(go))])
                keep=np.ones(len(P),bool); keep[go]=False; P,V,C=P[keep],V[keep],C[keep]
                rel=P-[CX,CY]; d=np.hypot(rel[:,0],rel[:,1])+1e-9; out=np.where(d>R-BR)[0]
            if len(out):
                nn=rel[out]/d[out,None]; vn=(V[out]*nn).sum(1); g=vn>0; ii=out[g]
                V[ii]-=2*vn[g,None]*nn[g]; P[ii]=np.array([CX,CY])+nn[g]*(R-BR-1); nb+=len(ii)
    if len(EP):
        EP+=EV; EA+=1; on=EA<22; EP,EV,EC,EA=EP[on],EV[on],EC[on],EA[on]
    if nb: events.append((fr,"click",random.choice([0,2,4,5,7])))
    if ne: events.append((fr,"pop",min(8,max(esc)*9//TARGET)))
def draw(fr,endfr,winner):
    img=Image.new("RGB",(W,H)); d=ImageDraw.Draw(img)
    for c in range(4):
        th=dang(c,fr); g=math.degrees(th); d.arc((CX-R,CY-R,CX+R,CY+R),g-DOOR/2,g+DOOR/2,fill=COLS[c],width=22)
    base=(255,235,250)
    for c in range(4):
        g0=math.degrees(dang(c,fr))+DOOR/2; g1=math.degrees(dang((c+1)%4,fr))-DOOR/2
        if c==3: g1=math.degrees(dang(0,fr))-DOOR/2+360
        d.arc((CX-R,CY-R,CX+R,CY+R),g0,g1,fill=base,width=6)
    for (x,y),c,ag in zip(EP,EC,EA):
        k2=(1-ag/22)*.9; col=COLS[c]; d.ellipse((x-BR,y-BR,x+BR,y+BR),fill=tuple(int(v*k2) for v in col))
    for (x,y),c in zip(P,C):
        col=COLS[c]; d.ellipse((x-BR,y-BR,x+BR,y+BR),fill=col); d.ellipse((x-5,y-7,x,y-2),fill=tuple(min(255,k+120) for k in col))
    f=font(72); t1="Which color escapes"; t2="first?"
    d.text((540-d.textlength(t1,font=f)/2,105),t1,font=f,fill=(255,240,252)); d.text((540-d.textlength(t2,font=f)/2,190),t2,font=f,fill=(255,240,252))
    f2=font(36); s=f"first to {TARGET} balls out wins"; d.text((540-d.textlength(s,font=f2)/2,295),s,font=f2,fill=(220,200,230))
    by=CY+R+70; bw=210; gx=30; f3=font(60); f4=font(24)
    for c in range(4):
        x=75+c*(bw+gx); p=min(1,esc[c]/TARGET)
        d.rectangle((x,by,x+bw,by+18),outline=tuple(int(k*.6) for k in COLS[c]),width=2); d.rectangle((x,by,x+bw*p,by+18),fill=COLS[c])
        tx=str(esc[c]); d.text((x+bw/2-d.textlength(tx,font=f3)/2,by+28),tx,font=f3,fill=COLS[c])
        d.text((x+bw/2-d.textlength(NAMES[c],font=f4)/2,by+98),NAMES[c],font=f4,fill=tuple(int(k*.8) for k in COLS[c]))
    if endfr is not None and fr>=endfr:
        k=fr-endfr; f5=font(100); tx=f"{NAMES[winner]} WINS!"
        d.rectangle((0,385,W,515),fill=(0,0,0))
        if k%14<10 or k>40: d.text((540-d.textlength(tx,font=f5)/2,395),tx,font=f5,fill=COLS[winner])
    return compose(sky.frame(fr),img,.6,.5,.3)
def run():
    wr=Writer() if CMD=="render" else None; fr=0; endfr=None; winner=None; log={}
    while True:
        if endfr is None:
            step(fr)
            if max(esc)>=TARGET: winner=int(np.argmax(esc)); endfr=fr; events.append((fr,"fin",0))
        elif len(EP): EP[:]+=EV; EA[:]+=1
        if fr%90==0: log[fr//30]=list(esc)
        if wr: wr.write(draw(fr,endfr,winner))
        elif CMD=="preview" and fr in PV: Image.fromarray(draw(fr,endfr,winner)).save(f"p_{fr}.png")
        fr+=1
        if (endfr is not None and fr>endfr+105) or fr>=40*FPS: break
    if wr:
        wr.close(); make_audio(fr,events); mux("video_tmp.mp4","audio.wav","farb_ausbruch.mp4")
    print(SEED,DOOR,TARGET,"end",endfr and round(endfr/30,1),winner,log)
run()
