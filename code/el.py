import sys, math, random, wave, colorsys, bisect
import numpy as np
from PIL import Image, ImageDraw
from common import *
CMD=sys.argv[1]; SEED=int(sys.argv[2]); S=float(sys.argv[3]); LIFE=float(sys.argv[4]); DECAY=float(sys.argv[5])
PV={int(x) for x in sys.argv[6:]}
rng=random.Random(SEED)
CX,CY=540.0,1110.0; A,B=380.0,690.0; C=math.sqrt(B*B-A*A)
FOC=[(0.0,-C),(0.0,C)]
sky=Sky(191)
WAVES=[(1.0,1),(3.0,4),(5.0,8),(7.0,16),(9.0,32),(11.5,64),(14.0,120),(17.0,200),(20.5,320)]
NSEG=14; END=int(31.5*FPS)
def hue_rgb(h,s=0.75,v=1.0):
    r,g,b=colorsys.hsv_to_rgb(h%1,s,v); return (int(r*255),int(g*255),int(b*255))
def hit(p,d):
    px,py=p; dx,dy=d; a=dx*dx/A**2+dy*dy/B**2; b=2*(px*dx/A**2+py*dy/B**2); c=px*px/A**2+py*py/B**2-1
    t=(-b+math.sqrt(b*b-4*a*c))/(2*a); return t
def make_path(f,th):
    p=FOC[f]; d=(math.cos(th),math.sin(th)); verts=[p]; cum=[0.0]; cross=[]; walls=[]
    for k in range(NSEG):
        t=hit(p,d); q=(p[0]+d[0]*t,p[1]+d[1]*t)
        if k>=1:
            fo=FOC[(f+k)%2]; s=(fo[0]-p[0])*d[0]+(fo[1]-p[1])*d[1]
            if 0<s<t: cross.append((cum[-1]+s,(f+k)%2))
        cum.append(cum[-1]+t); verts.append(q); walls.append(cum[-1])
        nx,ny=q[0]/A**2,q[1]/B**2; nn=math.hypot(nx,ny); nx/=nn; ny/=nn; dn=d[0]*nx+d[1]*ny
        d=(d[0]-2*dn*nx,d[1]-2*dn*ny); p=q
    return verts,cum,cross,walls
balls=[]
for wi,(t0,n) in enumerate(WAVES):
    f=wi%2; off=rng.uniform(0,6.28); spread=min(22,2+n//2)
    for i in range(n):
        th=off+2*math.pi*i/n; st=t0*FPS+i*spread/max(1,n)
        verts,cum,cross,walls=make_path(f,th)
        balls.append(dict(start=st,verts=verts,cum=cum,cross=cross,walls=walls,col=hue_rgb(((th-off)/(2*math.pi))),hue=((th-off)/(2*math.pi))%1,wave=wi))
balls.sort(key=lambda b:b["start"])
def pos(b,fr):
    d=(fr-b["start"])*S
    if d<0 or d>LIFE*FPS*S: return None
    cum=b["cum"]; k=min(bisect.bisect_right(cum,d)-1,len(cum)-2); u=(d-cum[k])/(cum[k+1]-cum[k]); p=b["verts"][k]; q=b["verts"][k+1]
    return (CX+p[0]+(q[0]-p[0])*u, CY+p[1]+(q[1]-p[1])*u)
# events
ripples={}; hits={}
for b in balls:
    for s,fo in b["cross"]:
        fr=int(b["start"]+s/S)
        if fr<END: ripples.setdefault((fr//3,fo),[]).append((fr,b["col"]))
    for s in b["walls"]:
        fr=int(b["start"]+s/S)
        if (fr-b["start"])<LIFE*FPS and fr<END: hits.setdefault(fr,[]).append(b["hue"])
rip_list=sorted((v[0][0],fo,v[0][1],len(v)) for (k,fo),v in ripples.items())
PENT=[0,2,4,7,9]
def note_for(h):
    i=int(h*15); return 57+12*(i//5)+PENT[i%5]
def tone_bell(m,dur=1.8,amp=0.2):
    f=440*2**((m-69)/12); n=int(SR*dur); t=np.arange(n)/SR; env=np.exp(-t*3.6)*(1-np.exp(-t*500))
    return amp*env*(np.sin(2*np.pi*f*t)+0.3*np.sin(2*np.pi*2.0*f*t)*np.exp(-t*5)+0.12*np.sin(2*np.pi*3.01*f*t)*np.exp(-t*8))
def build_audio():
    n=int(END/FPS*SR)+SR*2; out=np.zeros(n)
    def add(sig,fr):
        i=int(fr/FPS*SR); e=min(n,i+len(sig))
        if i<n: out[i:e]+=sig[:e-i]
    rr=random.Random(5); last=-9
    for fr in sorted(hits):
        if fr-last<2: continue
        last=fr; h=rr.choice(hits[fr]); add(tone_bell(note_for(h),1.4,0.16),fr)
    for wi,(t0,nn) in enumerate(WAVES):
        add(tone_bell([45,50,52,45,50,52,57,50,45][wi]+12*(wi>5),2.6,0.42),t0*FPS)
    lastr=-99
    for fr,fo,col,cnt in rip_list:
        if fr-lastr<14: continue
        lastr=fr; add(tone_bell(33+(fo*7),2.2,0.16+min(0.2,cnt*0.01)),fr)
    for j,m in enumerate([57,61,64,69,73,76]): add(tone_bell(m,3.2,0.3),int(29.0*FPS)+j*4)
    out/=np.abs(out).max()*1.12; pcm=(out*32000).astype(np.int16)
    with wave.open("audio.wav","wb") as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
LUT=np.array([int(v*DECAY) for v in range(256)],np.uint8)
trail=np.zeros((H,W,3),np.uint8); prevpos={}
def draw(fr):
    global trail
    img=Image.fromarray(LUT[trail]); d=ImageDraw.Draw(img); cur={}
    for b in balls:
        if b["start"]>fr: break
        p=pos(b,fr)
        if p is None: continue
        cur[id(b)]=p
        q=prevpos.get(id(b))
        if q is not None: d.line([q,p],fill=b["col"],width=3)
    prevpos.clear(); prevpos.update(cur)
    trail=np.asarray(img).copy()
    d.ellipse((CX-A-3,CY-B-3,CX+A+3,CY+B+3),outline=(255,240,252),width=6)
    for fo in FOC:
        d.ellipse((CX-9,CY+fo[1]-9,CX+9,CY+fo[1]+9),outline=(255,240,252),width=3)
    for rf,fo,col,cnt in rip_list:
        age=fr-rf
        if 0<=age<45:
            f=1-age/45; r0=10+age*4.2
            for j in range(3):
                r=r0-j*9
                if r>4: d.ellipse((CX-r,CY+FOC[fo][1]-r,CX+r,CY+FOC[fo][1]+r),outline=tuple(int(v*f*(1-j*0.25)) for v in col),width=3)
    for b in balls:
        if b["start"]>fr: break
        p=cur.get(id(b))
        if p: r=7; d.ellipse((p[0]-r,p[1]-r,p[0]+r,p[1]+r),fill=b["col"]); d.ellipse((p[0]-3,p[1]-4,p[0]+1,p[1]),fill=(255,255,255))
    cnt=sum(1 for b in balls if b["start"]<=fr)
    f1=font(70); t1="Every ball finds"; t2="the other point"
    d.text((540-d.textlength(t1,font=f1)/2,85),t1,font=f1,fill=(255,240,252)); d.text((540-d.textlength(t2,font=f1)/2,168),t2,font=f1,fill=(255,240,252))
    f2=font(100); tx=f"{cnt}"; d.text((540-d.textlength(tx,font=f2)/2,255),tx,font=f2,fill=(255,200,245))
    f3=font(30); tx="BALLS"; d.text((540+d.textlength(str(cnt),font=f2)/2+14,305),tx,font=f3,fill=(220,190,235))
    return compose(sky.frame(fr),img,.5,.4,.22)
def main():
    print("balls",len(balls),"wall hit frames",len(hits),"ripples",len(rip_list))
    if CMD=="sim": return
    if CMD=="preview":
        for f in sorted(PV):
            global trail,prevpos
            trail=np.zeros((H,W,3),np.uint8); prevpos={}
            for g in range(max(0,f-60),f+1): im=draw(g)
            Image.fromarray(im).save(f"p_{f}.png")
        return
    wr=Writer()
    for fr in range(END): wr.write(draw(fr))
    wr.close(); build_audio(); mux("video_tmp.mp4","audio.wav","ellipse_fokus.mp4")
main()
