import sys, math, random
import numpy as np
from PIL import Image, ImageDraw
from common import *
CMD=sys.argv[1]; SEED=int(sys.argv[2]); GAP1=float(sys.argv[3]); GAP2=float(sys.argv[4]); TARGET=int(sys.argv[5]); NB0=int(sys.argv[6])
PV={int(x) for x in sys.argv[7:]}
rng=np.random.default_rng(SEED); random.seed(SEED)
CX,CY,R2=540.0,1060.0,450.0; R1=215.0
BR=9.0; SPEED=8.5; SUB=4; CAP=600; GHOST=8; TLIM=30.0; W1=0.016; W2=-0.011
BC=[(60,220,255),(255,60,220),(255,160,60),(160,100,255),(120,255,160)]
sky=Sky(124)
aa=rng.uniform(0,2*np.pi,NB0); rr=rng.uniform(0,150,NB0)
P=np.stack([CX+rr*np.cos(aa),CY+rr*np.sin(aa)],1); bb=rng.uniform(0,2*np.pi,NB0)
V=SPEED*np.stack([np.cos(bb),np.sin(bb)],1); GH=np.zeros(NB0); CI=np.arange(NB0)%5; Z=np.zeros(NB0,int)
EP=np.zeros((0,2)); EV=np.zeros((0,2)); EC=np.zeros(0,int); EA=np.zeros(0)
esc=0; events=[]; G1=math.radians(GAP1); G2=math.radians(GAP2)
def th1(t): return -math.pi/2+W1*t
def th2(t): return math.pi/2+W2*t
def rot(v,a):
    c,s=math.cos(a),math.sin(a); return np.stack([v[:,0]*c-v[:,1]*s,v[:,0]*s+v[:,1]*c],1)
def adf(ang,th): return np.abs((ang-th+math.pi)%(2*math.pi)-math.pi)
def step(fr):
    global P,V,GH,CI,Z,EP,EV,EC,EA,esc
    nb=0; ne=0
    for sub in range(SUB):
        P+=V/SUB; t=fr+(sub+1)/SUB; a1=th1(t); a2=th2(t)
        rel=P-[CX,CY]; d=np.hypot(rel[:,0],rel[:,1])+1e-9; ang=np.arctan2(rel[:,1],rel[:,0]); nrm=rel/d[:,None]
        g1=adf(ang,a1)<G1/2; g2=adf(ang,a2)<G2/2
        # inner: zone0 hits ring1 from inside
        h0=(Z==0)&(d>R1-BR)
        pas=h0&g1&(d>R1-BR+3); Z[pas]=1
        hit=h0&~g1
        # zone1 hits ring1 from outside
        h1=(Z==1)&(d<R1+BR)
        pas=h1&g1&(d<R1+BR-3); Z[pas]=0
        hit2=h1&~g1
        # zone1 hits ring2
        h2=(Z==1)&(d>R2-BR)
        go=h2&g2&(d>R2-BR+3)
        hit3=h2&~g2
        clone=np.zeros(len(P),bool)
        for m,sgn,rad in ((hit,1,R1-BR-1),(hit2,-1,R1+BR+1),(hit3,1,R2-BR-1)):
            idx=np.where(m)[0]
            if len(idx):
                vn=(V[idx]*nrm[idx]).sum(1)*sgn; gd=vn>0; ii=idx[gd]
                if len(ii):
                    V[ii]-=2*(vn[gd]*sgn)[:,None]*nrm[ii]; P[ii]=np.array([CX,CY])+nrm[ii]*rad
                    if m is not hit2: clone[ii]=True
        cand=np.where(clone&(GH<=0))[0]; cand=cand[:max(0,CAP-len(P))]
        if len(go.nonzero()[0]):
            gi=go.nonzero()[0]
            EP=np.vstack([EP,P[gi]]); EV=np.vstack([EV,V[gi]*1.1]); EC=np.concatenate([EC,CI[gi]]); EA=np.concatenate([EA,np.zeros(len(gi))])
            esc+=len(gi); ne+=len(gi); keep=np.ones(len(P),bool); keep[gi]=False
            cand=np.array([np.sum(keep[:c]) for c in cand if keep[c]],int) if len(cand) else cand
            P,V,GH,CI,Z=P[keep],V[keep],GH[keep],CI[keep],Z[keep]
        if len(cand):
            nv=rot(V[cand],-0.42); V[cand]=rot(V[cand],0.42); CI[cand]+=1; GH[cand]=GHOST
            P=np.vstack([P,P[cand]+rng.normal(0,1.2,(len(cand),2))]); V=np.vstack([V,nv]); GH=np.concatenate([GH,np.full(len(cand),GHOST)])
            CI=np.concatenate([CI,CI[cand]]); Z=np.concatenate([Z,Z[cand]]); nb+=len(cand)
    GH-=1
    if len(EP):
        EP+=EV; EA+=1; on=EA<22; EP,EV,EC,EA=EP[on],EV[on],EC[on],EA[on]
    if nb: events.append((fr,"click",random.choice([1,3,4,6])))
    if ne: events.append((fr,"pop",min(8,esc*9//TARGET)))
def draw(fr,endfr,win):
    img=Image.new("RGB",(W,H)); d=ImageDraw.Draw(img); ringc=(255,235,250)
    for R,G,th,col in ((R2,GAP2,th2(fr),ringc),(R1,GAP1,th1(fr),(200,235,255))):
        g=math.degrees(th); d.arc((CX-R,CY-R,CX+R,CY+R),g+G/2,g+360-G/2,fill=col,width=6)
        for sgn in(-1,1):
            a=th+sgn*math.radians(G)/2; d.ellipse((CX+R*math.cos(a)-9,CY+R*math.sin(a)-9,CX+R*math.cos(a)+9,CY+R*math.sin(a)+9),fill=(255,170,70))
    for (x,y),c,ag in zip(EP,EC,EA):
        k2=(1-ag/22)*.85; col=BC[c%5]; d.ellipse((x-BR,y-BR,x+BR,y+BR),fill=tuple(int(v*k2) for v in col))
    for (x,y),c in zip(P,CI):
        col=BC[c%5]; d.ellipse((x-BR,y-BR,x+BR,y+BR),fill=col); d.ellipse((x-5,y-7,x,y-2),fill=tuple(min(255,v+110) for v in col))
    f=font(70); t1="Can they escape"; t2="both rings in 30s?"
    d.text((540-d.textlength(t1,font=f)/2,95),t1,font=f,fill=(255,240,252)); d.text((540-d.textlength(t2,font=f)/2,178),t2,font=f,fill=(255,240,252))
    left=max(0.0,TLIM-fr/FPS); k=left/TLIM; tc=lerp((255,60,60),(120,255,170),k) if k>.3 else (255,60,60)
    if left<5 and (fr//8)%2: tc=(255,255,255)
    f2=font(120); tx=f"{left:.1f}s"; d.text((540-d.textlength(tx,font=f2)/2,275),tx,font=f2,fill=tc)
    f3=font(66); tx=f"ESCAPED {esc} / {TARGET}"; d.text((540-d.textlength(tx,font=f3)/2,CY+R2+45),tx,font=f3,fill=(255,200,245))
    bw=760; by=CY+R2+140
    d.rectangle((540-bw/2,by,540+bw/2,by+18),outline=(140,70,130),width=2)
    d.rectangle((540-bw/2,by,540-bw/2+bw*min(1,esc/TARGET),by+18),fill=(255,60,200))
    f4=font(34); tx=f"{len(P)} balls inside  -  every hit splits a ball"; d.text((540-d.textlength(tx,font=f4)/2,by+40),tx,font=f4,fill=(210,190,225))
    if endfr is not None and fr>=endfr:
        q=fr-endfr; f6=font(100); tx=("JUST IN TIME!" if left<3 else "ESCAPED!") if win else "TIME'S UP!"
        d.rectangle((0,CY-85,W,CY+85),fill=(0,0,0))
        if q%14<10 or q>40: d.text((540-d.textlength(tx,font=f6)/2,CY-60),tx,font=f6,fill=(255,250,210) if win else (255,90,90))
    return compose(sky.frame(fr),img,.7,.55,.3)
def run():
    wr=Writer() if CMD=="render" else None; fr=0; endfr=None; win=None; log={}
    while True:
        if endfr is None: step(fr)
        elif len(EP): EP[:]+=EV; EA[:]+=1
        if endfr is None:
            if esc>=TARGET: endfr=fr; win=True; events.append((fr,"fin",0))
            elif fr/FPS>=TLIM: endfr=fr; win=False
        if fr%90==0: log[fr//30]=(len(P),esc)
        if wr: wr.write(draw(fr,endfr,win))
        elif CMD=="preview" and fr in PV: Image.fromarray(draw(fr,endfr,win)).save(f"p_{fr}.png")
        fr+=1
        if (endfr is not None and fr>endfr+105) or fr>=40*FPS: break
    if wr:
        wr.close(); make_audio(fr,events); mux("video_tmp.mp4","audio.wav","doppel_ring.mp4")
    print(SEED,GAP1,GAP2,TARGET,"end",endfr and round(endfr/30,1),win,log)
run()
