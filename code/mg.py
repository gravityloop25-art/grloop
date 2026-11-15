import sys, math, random
import numpy as np
from PIL import Image, ImageDraw
from common import *
CMD=sys.argv[1]; SEED=int(sys.argv[2]); ATT=float(sys.argv[3]); GROW=float(sys.argv[4]); TARGET=int(sys.argv[5]); NB0=int(sys.argv[6])
PV={int(x) for x in sys.argv[7:]}
random.seed(SEED); rng=np.random.default_rng(SEED)
CX,CY,R=540.0,1000.0,470.0; BR=9.0; SUB=3; SP=7.0
BC=[(60,220,255),(255,60,220),(255,160,60),(160,100,255),(120,255,160)]
sky=Sky(171)
aa=rng.uniform(0,2*np.pi,NB0); rr=rng.uniform(150,440,NB0)
P=np.stack([CX+rr*np.cos(aa),CY+rr*np.sin(aa)],1); b=rng.uniform(0,2*np.pi,NB0); V=SP*np.stack([np.cos(b),np.sin(b)],1)
CI=np.arange(NB0)%5; caught=0; power=1.0; events=[]; MR=34.0
def step(fr):
    global P,V,CI,caught,power,MR
    nc=0; ng=0
    for sub in range(SUB):
        P+=V/SUB
        rel=P-[CX,CY]; d=np.hypot(rel[:,0],rel[:,1])+1e-9; nrm=rel/d[:,None]
        out=d>R-BR
        if out.any():
            vn=(V*nrm).sum(1); g=out&(vn>0); V[g]-=2*vn[g,None]*nrm[g]; P[g]=np.array([CX,CY])+nrm[g]*(R-BR-1)
        # attraction ~ power
        acc=ATT*power/np.maximum(d,40)**1.0
        V-=nrm*acc[:,None]/SUB*0.35
        V*=0.9965
        sp=np.hypot(V[:,0],V[:,1]); big=sp>16; V[big]*=(16/sp[big])[:,None]
        near=d<MR+BR
        if near.any():
            caught_idx=np.where(near)[0]; nc+=len(caught_idx)
            keep=np.ones(len(P),bool); keep[caught_idx]=False; P,V,CI=P[keep],V[keep],CI[keep]
    if nc:
        caught+=nc; power+=nc*GROW; MR=34+caught*0.12
        events.append((fr,"click",random.choice([1,3,4,6]))); 
        if nc>=2: events.append((fr,"pop",min(8,caught*9//TARGET)))
def draw(fr,endfr):
    img=Image.new("RGB",(W,H)); d=ImageDraw.Draw(img)
    d.ellipse((CX-R-4,CY-R-4,CX+R+4,CY+R+4),outline=(255,235,250),width=5)
    gl=1+0.08*math.sin(fr*0.2)
    for k,(c,a) in enumerate(((90,40),(60,80),(30,140))):
        rad=(MR+c)*gl; d.ellipse((CX-rad,CY-rad,CX+rad,CY+rad),outline=(int(255*a/140),int(60*a/140),int(220*a/140)),width=3)
    d.ellipse((CX-MR,CY-MR,CX+MR,CY+MR),fill=(255,70,220),outline=(255,230,250),width=4)
    d.ellipse((CX-MR*.45,CY-MR*.45,CX+MR*.45,CY+MR*.45),fill=(255,230,250))
    for (x,y),c in zip(P,CI):
        col=BC[c%5]; d.ellipse((x-BR,y-BR,x+BR,y+BR),fill=col); d.ellipse((x-5,y-7,x,y-2),fill=tuple(min(255,k+110) for k in col))
    f=font(72); t1="Every ball it catches"; t2="makes it stronger"
    d.text((540-d.textlength(t1,font=f)/2,100),t1,font=f,fill=(255,240,252)); d.text((540-d.textlength(t2,font=f)/2,185),t2,font=f,fill=(255,240,252))
    f2=font(110); tx=f"{caught}"; d.text((540-d.textlength(tx,font=f2)/2,285),tx,font=f2,fill=(255,200,245))
    f3=font(36); tx=f"of {TARGET} caught   -   POWER x{power:.0f}"; d.text((540-d.textlength(tx,font=f3)/2,420),tx,font=f3,fill=(220,190,235))
    bw=760; by=CY+R+50
    d.rectangle((540-bw/2,by,540+bw/2,by+18),outline=(140,70,130),width=2); d.rectangle((540-bw/2,by,540-bw/2+bw*min(1,caught/TARGET),by+18),fill=(255,60,200))
    if endfr is not None and fr>=endfr:
        k=fr-endfr; f5=font(100); tx="ALL CAUGHT!"
        d.rectangle((0,CY-85,W,CY+85),fill=(0,0,0))
        if k%14<10 or k>40: d.text((540-d.textlength(tx,font=f5)/2,CY-60),tx,font=f5,fill=(255,250,210))
    return compose(sky.frame(fr),img,.7,.55,.3)
def run():
    wr=Writer() if CMD=="render" else None; fr=0; endfr=None; log={}
    while True:
        if endfr is None:
            step(fr)
            if caught>=TARGET: endfr=fr; events.append((fr,"fin",0))
        if fr%90==0: log[fr//30]=(caught,round(power))
        if wr: wr.write(draw(fr,endfr))
        elif CMD=="preview" and fr in PV: Image.fromarray(draw(fr,endfr)).save(f"p_{fr}.png")
        fr+=1
        if (endfr is not None and fr>endfr+105) or fr>=45*FPS: break
    if wr:
        wr.close(); make_audio(fr,events); mux("video_tmp.mp4","audio.wav","magnet.mp4")
    print(SEED,ATT,GROW,TARGET,"end",endfr and round(endfr/30,1),log)
run()
