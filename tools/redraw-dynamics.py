"""Build original, editable SVG teaching diagrams for the dynamics chapters.

Reference metadata lives in assets/dynamics/sources.json. No raster source is
embedded; coordinates and labels below encode the physical relationships.
Run: python3 tools/redraw-dynamics.py
"""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / 'assets/dynamics'

STYLE = '''
svg{--fg:#152231;--sub:#566677;--line:#b2c4bd;--paper:#fff;--soft:#e1f0e8;--motion:#0f6b3a;--velocity:#2563a6;--force:#c2410c;color:var(--fg);background:var(--paper)}
@media(prefers-color-scheme:dark){svg{--fg:#e5edf6;--sub:#adbecb;--line:#526d60;--paper:#13211a;--soft:#1a3426;--motion:#5fc696;--velocity:#80b8f2;--force:#ff9a73}}
text{font-family:"PingFang TC","Microsoft JhengHei",sans-serif;font-size:22px;fill:var(--fg)}
.small{font-size:18px;fill:var(--sub)}.eq{font-size:24px;fill:var(--motion)}
.geo{stroke:var(--fg);stroke-width:2;fill:none}.guide{stroke:var(--line);stroke-width:1.5;stroke-dasharray:6 5;fill:none}
.body{fill:var(--soft);stroke:var(--motion);stroke-width:2}.ghost{fill:none;stroke:var(--line);stroke-width:2;stroke-dasharray:6 5}
.force{stroke:var(--force);fill:none;stroke-width:3}.velocity{stroke:var(--velocity);fill:none;stroke-width:3}.motion{stroke:var(--motion);fill:none;stroke-width:3}
.force-label{fill:var(--force)}.velocity-label{fill:var(--velocity)}.motion-label{fill:var(--motion)}
.dot{fill:var(--fg)}.area{fill:var(--soft);stroke:none}.panel{fill:none;stroke:var(--line);stroke-width:1.3}
'''

class Figure:
    def __init__(self, key, w=640, h=400):
        self.key, self.w, self.h, self.parts = key, w, h, []
    def add(self,s):self.parts.append(s);return self
    def text(self,x,y,s,cls='',anchor='start',size=None):
        return self.add(f'<text x="{x}" y="{y}" class="{cls}" text-anchor="{anchor}"'+(f' style="font-size:{size}px"' if size else '')+f'>{html.escape(s)}</text>')
    def line(self,x1,y1,x2,y2,cls='geo'):
        return self.add(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" class="{cls}"/>')
    def arrow(self,x1,y1,x2,y2,cls='motion',both=False):
        return self.add(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" class="{cls}" marker-end="url(#{self.key}-{cls})"'+(f' marker-start="url(#{self.key}-{cls}-start)"' if both else '')+'/>')
    def path(self,d,cls='geo',arrow=False):
        return self.add(f'<path d="{d}" class="{cls}"'+(f' marker-end="url(#{self.key}-{cls})"' if arrow else '')+'/>')
    def circle(self,x,y,r,cls='body'):
        return self.add(f'<circle cx="{x}" cy="{y}" r="{r}" class="{cls}"/>')
    def rect(self,x,y,w,h,cls='body',rx=3):
        return self.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" class="{cls}"/>')
    def ellipse(self,x,y,rx,ry,cls='body'):
        return self.add(f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" class="{cls}"/>')
    def ground(self,x,y,w):
        self.line(x,y,x+w,y)
        for a in range(int(x),int(x+w),14):self.line(a,y,a-8,y+10,'guide')
        return self
    def eq(self,s,y=None):return self.text(self.w/2,y or self.h-25,s,'eq','middle')
    def label(self,s):return self.text(32,34,s,'small')
    def block(self,x,y,label='m',w=70,h=54):
        self.rect(x,y,w,h);self.text(x+w/2,y+h/2+7,label,anchor='middle');return self
    def point(self,x,y,label=None,dx=10,dy=-12):
        self.circle(x,y,4,'dot')
        if label:self.text(x+dx,y+dy,label)
        return self
    def axes(self,x,y,w,h,xlabel='x',ylabel='y'):
        self.arrow(x,y,x+w,y,'geo');self.arrow(x,y,x,y-h,'geo');self.text(x+w+8,y+7,xlabel);self.text(x-10,y-h-12,ylabel);return self
    def spring(self,x,y,length=170,amp=12):
        seg=length/12;d=f'M {x} {y} L {x+seg} {y}'
        for i in range(2,12):d+=f' L {x+i*seg} {y+amp*(1 if i%2==0 else -1)}'
        d+=f' L {x+length} {y}'
        return self.path(d)
    def disk(self,x=300,y=195,r=90):
        self.circle(x,y,r);self.point(x,y,'G',dx=-25,dy=25);return self
    def rotate(self,x,y,r=45,cls='motion',clockwise=True,label='ω'):
        if clockwise:d=f'M {x-r*.75} {y-r*.66} A {r} {r} 0 0 1 {x+r*.95} {y-r*.3}'
        else:d=f'M {x+r*.75} {y-r*.66} A {r} {r} 0 0 0 {x-r*.95} {y-r*.3}'
        self.path(d,cls,True);self.text(x,y-r-14,label,cls+'-label','middle');return self
    def body(self,x,y,angle=0):
        # An elliptical rigid body with material points A and B.
        self.add(f'<g transform="translate({x} {y}) rotate({angle})">')
        self.ellipse(0,0,68,95);self.add('</g>');return self
    def xml(self,title,desc):
        defs=''
        for cls,var in [('geo','fg'),('motion','motion'),('velocity','velocity'),('force','force')]:
            for start in [False,True]:
                k=f'{self.key}-{cls}'+('-start' if start else '')
                defs+=f'<marker id="{k}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto'+('-start-reverse' if start else '')+'" markerUnits="userSpaceOnUse"><path d="M 0 0 L 10 5 L 0 10 Z" fill="var(--'+var+')"/></marker>'
        return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" width="{self.w}" height="{self.h}" role="img" aria-labelledby="{self.key}-title {self.key}-desc"><title id="{self.key}-title">{html.escape(title)}</title><desc id="{self.key}-desc">{html.escape(desc)}</desc><defs>{defs}</defs><style>{STYLE}</style>'+''.join(self.parts)+'</svg>\n'

figs={}
def new(ch,n,h=400,w=640):
    key=f'ch{ch:02}-fig{n:02}';f=Figure(key,w,h);figs[key]=f;return f

# 1. Rectilinear kinematics.
f=new(1,1)
f.path('M 75 290 C 120 60 245 285 330 150 S 495 200 552 72','velocity',True)
for x,y,l in [(75,290,'A'),(168,177,'B'),(332,149,'C'),(552,72,'D')]:f.point(x,y,l)
f.arrow(75,290,552,72,'force');f.text(340,105,'位移 Δr','force-label');f.text(100,120,'實際路徑','velocity-label');f.eq('位移：起點到終點的向量')
f=new(1,2,h=260);f.arrow(55,160,590,160,'geo');f.text(600,166,'x');f.point(90,160,'O',dy=36);f.point(235,160,'x(t)',dx=-28,dy=36);f.point(485,160,'x(t + Δt)',dx=-62,dy=36);f.arrow(235,92,485,92,'motion');f.line(235,82,235,165,'guide');f.line(485,82,485,165,'guide');f.text(350,72,'Δx','motion-label','middle');f.eq('Δx = x(t + Δt) − x(t)')

def graph(f,x,y,kind,row,mode):
    ox,oy=x+28,y+130;f.axes(ox,oy,125,90,'t',kind);f.text(x+85,y+20,mode,'small','middle')
    if kind=='x':
        if mode=='等加速度':f.path(f'M {ox} {oy} Q {ox+100} {oy-3} {ox+120} {oy-85}','motion');f.line(ox+53,oy-12,ox+110,oy-67,'velocity')
        else:f.line(ox,oy-(15 if row==0 else 85),ox+120,oy-(85 if row==0 else 15),'motion')
    if kind=='v':
        if mode=='等加速度':f.path(f'M {ox} {oy} L {ox} {oy-15} L {ox+120} {oy-85} L {ox+120} {oy} Z','area');f.line(ox,oy-15,ox+120,oy-85,'velocity')
        else:
            offset=50 if row==0 else -36;f.rect(ox,oy-offset if offset>0 else oy,120,abs(offset),'area');f.line(ox,oy-offset,ox+120,oy-offset,'velocity')
    if kind=='a':f.line(ox,oy-(55 if mode=='等加速度' else 0),ox+120,oy-(55 if mode=='等加速度' else 0),'force')
    captions={'x':'斜率 = v','v':'面積 = Δx','a':'a = 0' if mode!='等加速度' else 'a 為常數'}
    f.text(x+85,y+(195 if kind=='v' and row==1 and mode!='等加速度' else 175),captions[kind],'small','middle')
f=new(1,3,h=485)
for row in range(2):
    for j,k in enumerate(['x','v','a']):graph(f,20+j*205,30+row*205,k,row,'v > 0' if row==0 else 'v < 0')
f.eq('等速度：x 隨時間線性變化，a = 0')
f=new(1,4,h=265)
for j,k in enumerate(['x','v','a']):graph(f,20+j*205,12,k,0,'等加速度')
f.eq('x = x₀ + v₀t + ½at²',250)
f=new(1,5);f.path('M 70 285 L 485 92 L 485 285 Z');f.add('<g transform="translate(263 195) rotate(-25)">');f.block(-36,-54,'m');f.add('</g>');f.arrow(263,171,263,295,'force');f.arrow(263,171,194,203,'motion');f.arrow(263,171,332,263,'velocity');f.line(194,203,263,295,'guide');f.line(332,263,263,295,'guide');f.text(277,298,'g','force-label');f.text(90,210,'g sin θ','motion-label');f.text(339,241,'g cos θ','velocity-label');f.path('M 122 285 A 52 52 0 0 0 117 263');f.text(132,272,'θ');f.eq('沿斜面：a = g sin θ')

# 2. Curvilinear motion.
f=new(2,1);f.circle(295,190,126);f.line(295,190,421,190);f.arrow(295,190,376,94,'geo');f.point(295,190,'O',dx=-24,dy=26);f.point(421,190,'A');f.point(376,94,'B');f.path('M 346 190 A 51 51 0 0 0 328 151','motion',True);f.text(354,171,'θ','motion-label');f.text(317,135,'r');f.path('M 436 190 A 141 141 0 0 0 386 82','velocity',True);f.text(431,104,'s','velocity-label');f.rotate(295,190,74,clockwise=False);f.eq('s = rθ　　v = rω')
f=new(2,2,h=450);f.axes(90,85,440,0,'x','');f.arrow(90,85,90,325,'geo');f.text(70,347,'y');f.text(55,78,'O');f.path('M 90 85 Q 350 85 460 320','guide');f.arrow(90,85,220,85,'velocity');f.text(163,64,'v₀','velocity-label');f.point(353,204,'P',dx=-28,dy=25);f.line(353,85,353,204,'guide');f.line(90,204,353,204,'guide');f.arrow(353,204,465,204,'velocity');f.arrow(353,204,353,280,'motion');f.arrow(353,204,465,280,'force');f.text(473,204,'vₓ','velocity-label');f.text(323,285,'vᵧ','motion-label');f.text(474,293,'v','force-label');f.arrow(530,115,530,205,'force');f.text(548,163,'g','force-label');f.text(202,182,'x');f.text(62,151,'y');f.eq('x = v₀t　　y = ½gt²（向下為正）')
f=new(2,3,h=430);f.axes(75,310,490,255);f.path('M 75 310 Q 315 -95 555 310','motion');f.point(75,310,'O',dx=-26,dy=22);f.arrow(75,310,170,169,'velocity');f.arrow(75,310,170,310,'geo');f.line(170,310,170,169,'guide');f.text(150,167,'v₀','velocity-label');f.text(118,343,'v₀ cos θ','small');f.text(179,253,'v₀ sin θ','small');f.path('M 122 310 A 47 47 0 0 0 101 271');f.text(132,288,'θ');f.point(315,108);f.arrow(315,108,412,108,'velocity');f.text(319,86,'vᵧ = 0','small');f.line(315,108,315,310,'guide');f.text(327,235,'H','motion-label');f.arrow(75,368,555,368,'geo',True);f.text(315,357,'R',anchor='middle');f.arrow(528,105,528,184,'force');f.text(545,151,'g','force-label');f.eq('R = v₀² sin(2θ) / g（落點與起點同高）',416)
f=new(2,4);f.circle(285,205,108,'geo');f.point(285,205,'O',dx=-25,dy=27);f.point(370,138,'P');f.arrow(370,138,435,221,'velocity');f.arrow(370,138,288,203,'motion');f.arrow(370,138,353,285,'force');f.line(288,203,353,285,'guide');f.line(435,221,353,285,'guide');f.text(445,213,'aₜ','velocity-label');f.text(290,167,'aₙ','motion-label');f.text(368,281,'a','force-label');f.text(60,77,'aₜ：改變速率','velocity-label');f.text(60,108,'aₙ：改變方向','motion-label');f.eq('aₙ = v²/r　　aₜ = rα　　a² = aₙ² + aₜ²')
f=new(2,5,h=430);f.path('M 55 315 L 300 125 L 575 315 Z');f.circle(300,126,27);f.circle(300,126,5,'dot');f.add('<g transform="translate(185 214) rotate(-38)">');f.block(-35,-45,'A');f.add('</g>');f.add('<g transform="translate(428 212) rotate(35)">');f.block(-35,-45,'B');f.add('</g>');f.path('M 171 180 L 278 105 A 28 28 0 0 1 322 106 L 451 181','motion');f.arrow(251,109,137,198,'geo');f.text(163,125,'sA');f.arrow(352,105,473,190,'geo');f.text(434,134,'sB');f.text(254,70,'固定滑輪','small');f.eq('sA + sB = 常數 → vA + vB = 0')
f=new(2,6,h=480);f.ground(140,65,300);f.line(270,65,270,85);f.circle(360,115,30);f.circle(300,245,30);f.path('M 270 65 L 270 245 A 30 30 0 0 0 330 245 L 330 115 A 30 30 0 0 1 390 115 L 390 360','motion');f.line(300,275,300,317);f.block(270,317,'A',60,65);f.block(360,360,'B',60,65);f.line(120,65,120,317,'guide');f.arrow(120,65,120,317,'geo',True);f.text(72,220,'sA');f.arrow(495,65,495,360,'geo',True);f.text(508,244,'sB');f.text(225,300,'動滑輪','small');f.eq('2sA + sB = 常數 → 2vA + vB = 0',464)

# 3. Newton's second law.
f=new(3,1,h=410);f.label('受力圖');f.axes(125,232,120,120);f.arrow(125,232,180,142,'force');f.arrow(125,232,57,167,'force');f.arrow(125,232,137,310,'force');f.point(125,232,'P');f.text(185,142,'F₁','force-label');f.text(35,154,'F₂','force-label');f.text(145,315,'F₃','force-label');f.text(305,224,'=','eq','middle',36);f.text(400,34,'運動圖','small');f.axes(430,232,125,120);f.point(430,232,'P');f.arrow(430,232,429,155,'motion');f.text(451,155,'ma','motion-label');f.eq('ΣFₓ = maₓ　　ΣFᵧ = maᵧ')
f=new(3,2);f.path('M 55 244 Q 176 36 280 240','guide');f.point(181,133,'P',dx=-28,dy=0);f.arrow(181,133,262,170,'velocity');f.arrow(181,133,142,225,'motion');f.text(262,154,'t','velocity-label');f.text(122,244,'n','motion-label');f.text(306,196,'=','eq','middle',36);f.point(445,180,'P');f.arrow(445,180,529,219,'force');f.arrow(445,180,406,272,'motion');f.text(531,210,'maₜ','force-label');f.text(354,295,'maₙ','motion-label');f.eq('ΣFₜ = m dv/dt　　ΣFₙ = mv²/ρ')
f=new(3,3);f.label('升降機整體：張力 T 與重量 mg');f.block(155,153,'m',95,95);f.arrow(202,153,202,64,'force');f.text(218,74,'T','force-label');f.arrow(202,248,202,326,'force');f.text(215,326,'mg','force-label');f.text(321,209,'=','eq','middle',36);f.block(411,153,'m',95,95);f.arrow(458,153,458,64,'motion');f.text(478,90,'ma','motion-label');f.eq('向上為正：T − mg = ma')
f=new(3,4,h=470);f.ground(55,158,348);f.block(175,104,'A',85,54);f.text(177,86,'30 kg','small');f.circle(403,150,20);f.circle(448,261,25);f.path('M 260 130 L 403 130 A 20 20 0 0 1 423 150 L 423 261 A 25 25 0 0 0 473 261 L 473 157','geo');f.line(463,157,484,157);f.line(448,286,448,306);f.block(411,306,'B',75,62);f.text(490,342,'50 kg','small');f.arrow(270,101,335,101,'force');f.text(303,82,'T','force-label');f.arrow(399,260,399,203,'force');f.arrow(499,260,499,203,'force');f.text(355,196,'T','force-label');f.text(505,198,'T','force-label');f.arrow(448,369,448,411,'force');f.text(460,408,'mBg','force-label');f.eq('mAaA = T　　mBg − 2T = mBaB',454)
f=new(3,5,h=470);f.point(279,65,'O',dx=-24,dy=-16);f.line(279,65,279,325,'guide');f.line(279,65,427,325);f.ellipse(279,325,148,44,'guide');f.point(427,325,'P',dy=-12);f.line(279,325,427,325,'guide');f.text(337,348,'r');f.text(365,193,'L');f.path('M 279 126 A 61 61 0 0 1 311 117');f.text(292,150,'θ');f.arrow(427,325,365,215,'force');f.text(368,247,'T','force-label');f.arrow(427,325,427,403,'force');f.text(444,395,'mg','force-label');f.arrow(427,325,332,325,'motion');f.text(339,301,'mv²/r','motion-label');f.eq('r = L sin θ　　T cos θ = mg',454)
f=new(3,6);f.point(364,285);f.arrow(224,126,224,285,'force');f.arrow(364,285,224,285,'motion');f.arrow(364,285,224,126,'velocity');f.line(364,126,364,285,'guide');f.text(178,224,'mg','force-label');f.text(263,320,'T sin θ','motion-label');f.text(278,176,'T','velocity-label');f.path('M 364 233 A 52 52 0 0 0 330 245');f.text(325,237,'θ');f.eq('T sin θ = mv²/r　　T cos θ = mg')

# 4. Work and energy.
f=new(4,1,h=300);f.ground(85,200,475);f.block(165,145);f.rect(440,145,70,54,'ghost');f.arrow(84,168,160,168,'force');f.text(87,145,'F','force-label');f.arrow(200,246,475,246,'motion');f.text(340,233,'s','motion-label','middle');f.eq('W = Fs',287)
f=new(4,2);f.ground(70,256,505);f.block(170,200);f.rect(454,200,70,54,'ghost');f.arrow(205,201,340,104,'force');f.arrow(205,201,340,201,'motion');f.arrow(340,201,340,104,'velocity');f.path('M 259 201 A 54 54 0 0 0 249 169');f.text(276,184,'θ');f.text(350,104,'F','force-label');f.text(275,229,'F cos θ','motion-label');f.text(355,169,'F sin θ','velocity-label');f.arrow(205,307,489,307,'geo');f.text(350,332,'s',anchor='middle');f.eq('W = Fs cos θ')
f=new(4,3);f.ground(65,256,510);f.block(139,201);f.rect(458,201,70,54,'ghost');f.arrow(72,229,132,229,'force');f.text(78,213,'F','force-label');f.arrow(174,201,174,113,'force');f.text(185,121,'N','force-label');f.arrow(174,255,174,323,'force');f.text(187,326,'mg','force-label');f.arrow(225,173,307,173,'velocity');f.text(245,151,'v₁','velocity-label');f.arrow(465,173,568,173,'velocity');f.text(502,151,'v₂','velocity-label');f.arrow(240,287,489,287,'motion');f.text(360,310,'s','motion-label');f.eq('W合 = ½mv₂² − ½mv₁²')
f=new(4,4);f.ground(118,302,390);f.circle(246,107,23);f.text(238,69,'m');f.arrow(246,135,246,222,'force');f.text(270,192,'mg','force-label');f.line(286,107,443,107,'guide');f.arrow(431,107,431,302,'geo',True);f.text(454,207,'h');f.text(126,334,'基準面：Ug = 0','small');f.eq('Ug = mgh')
f=new(4,5);f.line(112,124,112,272);f.spring(112,196,252,14);f.block(364,169,'m',64,55);f.line(290,112,290,289,'guide');f.text(290,91,'原長位置','small','middle');f.arrow(290,286,397,286,'geo',True);f.text(343,312,'x',anchor='middle');f.arrow(397,125,310,125,'force');f.text(435,132,'F = −kx','force-label');f.eq('Us = ½kx²')

# 5. Momentum and impact.
def collisions(f,oblique=False):
    for j,offset in enumerate([0,310]):
        f.text(offset+165,44,'碰撞前' if j==0 else '碰撞後',anchor='middle')
        f.circle(offset+100,190,40);f.circle(offset+205,190,40);f.text(offset+100,197,'A',anchor='middle');f.text(offset+205,197,'B',anchor='middle')
        f.arrow(offset+40,190,offset+277,190,'geo');f.text(offset+282,197,'n');f.arrow(offset+153,268,offset+153,107,'geo');f.text(offset+145,94,'t')
        if not oblique:
            f.arrow(offset+100,134,offset+(58 if j else 172),134,'velocity');f.arrow(offset+205,250,offset+(277 if j else 163),250,'motion');f.text(offset+96,114,'vA′' if j else 'vA','velocity-label');f.text(offset+205,283,'vB′' if j else 'vB','motion-label')
        else:
            ax=offset+100+(-40 if j else 60);bx=offset+205+(60 if j else -40)
            f.arrow(offset+100,190,ax,105,'velocity');f.arrow(offset+205,190,bx,109,'motion');f.line(ax,105,offset+100,105,'guide');f.line(offset+100,105,offset+100,190,'guide');f.line(bx,109,offset+205,109,'guide');f.line(bx,109,bx,190,'guide');f.text(offset+65,78,'vA′' if j else 'vA','velocity-label');f.text(offset+216,78,'vB′' if j else 'vB','motion-label')
f=new(5,1,h=360);collisions(f);f.eq('mAvA + mBvB = mAvA′ + mBvB′',337)
f=new(5,2,h=390);collisions(f,True);f.text(320,322,'切向分量保持不變','small','middle');f.eq('e = (vB,n′ − vA,n′) / (vA,n − vB,n)')
f=new(5,3);f.axes(210,270,325,192);f.arrow(210,270,87,335,'geo');f.text(75,356,'z');f.point(210,270,'O',dx=8,dy=28);f.arrow(210,270,399,146,'motion');f.point(399,146,'P');f.arrow(399,146,448,58,'velocity');f.arrow(210,270,115,320,'force');f.text(311,221,'r','motion-label');f.text(459,65,'mv','velocity-label');f.text(75,302,'HO','force-label');f.eq('HO = r × mv（垂直於 r 與 v 的平面）')

# 6. Rigid-body kinematics.
f=new(6,1,h=440);f.axes(88,337,440,260);f.body(367,179,23);f.point(356,238,'A',dx=-26,dy=15);f.point(374,128,'B');f.arrow(88,337,356,238,'velocity');f.arrow(88,337,374,128,'motion');f.arrow(356,238,374,128,'force');f.text(179,308,'rA','velocity-label');f.text(168,230,'rB','motion-label');f.text(396,203,'rB/A','force-label');f.text(46,363,'O');f.text(40,32,'固定座標','small');f.text(458,114,'平移座標','small');f.eq('rB = rA + rB/A　　平移時：vA = vB',419)
f=new(6,2);f.disk(192,215,80);f.rotate(192,215,110,label='ω');f.disk(462,215,80);f.rotate(462,215,110,label='α');f.text(192,335,'角速度','velocity-label','middle');f.text(462,335,'角加速度','force-label','middle');f.eq('ω = dθ/dt　　α = dω/dt')
f=new(6,3,h=430);f.disk(191,228,84);f.point(268,196,'P');f.arrow(191,228,268,196,'geo');f.text(219,244,'r');f.arrow(268,196,236,119,'velocity');f.text(211,106,'v','velocity-label');f.text(184,56,'速度','small','middle');f.disk(461,228,84);f.point(538,196,'P');f.arrow(538,196,461,228,'motion');f.arrow(538,196,506,119,'force');f.text(519,106,'aₜ','force-label');f.text(476,267,'aₙ','motion-label');f.text(461,56,'加速度','small','middle');f.eq('v = ω × r　　a = α × r − ω²r',406)
f=new(6,4,h=450)
for x in [110,328,536]:
    f.body(x,197,25);f.point(x-37,238,'A',dx=-24,dy=24);f.point(x+34,175,'B',dx=8,dy=17)
f.text(215,207,'=','eq','middle',36);f.text(434,207,'+','eq','middle',36);f.arrow(73,238,111,200,'velocity');f.arrow(144,175,212,171,'velocity');f.arrow(291,238,329,200,'velocity');f.arrow(362,174,400,136,'velocity');f.arrow(570,175,600,209,'force');f.text(538,312,'vB/A','force-label');f.rotate(499,238,105);f.text(108,350,'一般平面運動','small','middle');f.text(327,350,'隨 A 平移','small','middle');f.text(534,350,'繞 A 旋轉','small','middle');f.eq('vB = vA + ω × rB/A',427)
f=new(6,5,h=430);f.body(169,203,20);f.body(469,203,20);f.point(149,250,'A');f.point(213,175,'B');f.point(445,260,'A');f.point(513,175,'B');f.text(324,205,'+','eq','middle',36);f.arrow(149,250,91,307,'velocity');f.arrow(213,175,155,232,'velocity');f.text(66,344,'aA','velocity-label');f.arrow(513,175,445,260,'motion');f.arrow(513,175,598,243,'force');f.text(435,293,'aₙ','motion-label');f.text(563,270,'aₜ','force-label');f.text(169,63,'平移加速度','small','middle');f.text(470,63,'相對加速度','small','middle');f.eq('aB = aA + α × rB/A − ω²rB/A',408)
f=new(6,6,h=440);f.path('M 202 316 L 378 203 L 402 230 L 225 346 Z','body');f.point(213,331,'A',dy=27);f.point(387,218,'B',dy=25);f.point(213,87,'C',dx=-24);f.arrow(213,331,342,331,'velocity');f.text(356,340,'vA','velocity-label');f.arrow(387,218,454,129,'velocity');f.text(466,126,'vB','velocity-label');f.line(213,87,213,331,'guide');f.line(213,87,387,218,'guide');f.text(224,235,'rA');f.text(290,139,'rB');f.path('M 213 132 A 45 45 0 0 0 258 87','motion',True);f.text(274,111,'ω','motion-label');f.eq('vA/rA = vB/rB = ω　　vC = 0',419)
f=new(6,7,h=470);f.axes(90,365,420,278);f.arrow(90,365,53,400,'geo');f.text(40,420,'z');f.circle(364,224,114);f.point(364,224,"O′",dx=-30,dy=27);f.rect(294,205,133,30,'ghost');f.block(353,205,'P',35,30);f.arrow(90,365,364,224,'geo');f.arrow(364,224,526,224,'velocity');f.text(535,232,'x′','velocity-label');f.arrow(364,224,364,78,'velocity');f.text(374,78,'y′','velocity-label');f.rotate(364,224,145,label='ω');f.arrow(392,185,460,185,'force');f.text(452,162,'v相對','force-label');f.text(105,102,'固定座標 O','small');f.text(252,382,'旋轉座標 O′','small');f.eq('a柯氏 = 2ω × v相對',451)
f=new(6,8,h=440);f.axes(100,336,435,270);f.path('M 100 336 L 380 160 L 397 187 L 117 363 Z','body');f.add('<g transform="translate(328 192) rotate(-32)">');f.block(-33,-27,'P',66,55);f.add('</g>');f.arrow(100,336,328,192,'motion');f.arrow(328,192,442,120,'velocity');f.arrow(328,192,256,78,'force');f.text(201,290,'r','motion-label');f.text(449,111,'eᵣ','velocity-label');f.text(207,87,'eθ','force-label');f.path('M 158 336 A 58 58 0 0 0 144 297');f.text(162,315,'θ');f.eq('v = ṙ eᵣ + rθ̇ eθ',420)

# 7. Rigid-body kinetics and moments of inertia.
f=new(7,1);f.path('M 222 101 Q 273 66 323 106 Q 371 167 348 265 Q 327 305 270 302 Q 210 290 213 231 Z','body');f.arrow(281,325,281,53,'geo');f.text(294,49,'z');f.ellipse(281,231,69,21,'guide');f.point(338,226,'dm',dx=22,dy=7);f.arrow(281,231,338,226,'motion');f.text(308,209,'r','motion-label');f.eq('I = ∫r² dm')
f=new(7,2);f.rect(104,177,430,20);f.arrow(319,287,319,84,'geo');f.text(335,87,'z');f.text(319,163,'G',anchor='middle');f.arrow(104,257,534,257,'geo',True);f.text(320,283,'L',anchor='middle');f.text(320,118,'均質細桿','small','middle');f.eq('IG = mL²/12　　I端點 = mL²/3')
f=new(7,3,h=880)
def inertia_row(f,y,label,formula,kind):
    f.rect(25,y,590,185,'panel',8);f.text(47,y+33,label);cx,cy=175,y+102
    if kind=='plate':f.rect(cx-68,cy-40,136,80);f.line(cx-68,cy+53,cx+68,cy+53,'guide');f.text(cx,cy+75,'a',anchor='middle');f.text(cx-86,cy+8,'b');f.arrow(cx,cy,cx+92,cy,'geo');f.text(cx+100,cy+7,'x');f.arrow(cx,cy,cx,cy-68,'geo');f.text(cx+12,cy-67,'y');f.circle(cx,cy,8,'geo');f.circle(cx,cy,2,'dot');f.text(cx-25,cy-13,'z')
    elif kind=='disk':f.ellipse(cx,cy,62,39);f.arrow(cx,cy,cx+57,cy,'geo');f.text(cx+25,cy-13,'R');f.arrow(cx,cy,cx,cy-68,'geo');f.text(cx+12,cy-65,'z')
    elif kind=='cylinder':
        cy+=15
        f.rect(cx-50,cy-36,100,72);f.ellipse(cx,cy+36,50,17);f.ellipse(cx,cy-36,50,17);f.arrow(cx,cy-36,cx+48,cy-36,'geo');f.text(cx+15,cy-46,'R');f.arrow(cx,cy+36,cx,cy-69,'geo');f.text(cx+60,cy-65,'z')
    else:f.circle(cx,cy,53);f.circle(cx,cy,43,'geo');f.arrow(cx,cy,cx+51,cy,'geo');f.text(cx+24,cy-11,'R');f.arrow(cx,cy,cx,cy-69,'geo');f.text(cx+11,cy-65,'z')
    for k,eq in enumerate(formula):f.text(323,y+81+k*34,eq,'eq',size=22)
inertia_row(f,16,'矩形薄板',['Ix = mb²/12','Iy = ma²/12','Iz = m(a² + b²)/12'],'plate')
inertia_row(f,218,'均質薄圓板',['Iz = ½mR²'],'disk')
inertia_row(f,420,'均質實心圓柱',['Iz = ½mR²'],'cylinder')
inertia_row(f,622,'薄圓環',['Iz = mR²'],'ring');f.text(320,850,'軸線通過質心；z 垂直於板面／沿圓柱軸','small','middle')
f=new(7,4,h=355);f.circle(189,169,75);f.ellipse(189,169,75,23,'guide');f.arrow(189,254,189,60,'geo');f.text(204,60,'z');f.arrow(189,169,252,137,'motion');f.text(221,133,'R','motion-label');f.text(343,129,'實心球：I = ⅖mR²','eq');f.text(343,184,'薄球殼：I = ⅔mR²','eq');f.eq('Ix = Iy = Iz（均質球體）',328)
f=new(7,5);f.circle(313,185,92);f.circle(313,185,48,'geo');f.point(313,185,'G',dx=13,dy=27);f.arrow(130,185,512,185,'geo');f.text(72,191,'A');f.text(527,192,'A′');f.arrow(130,93,512,93,'velocity');f.text(72,99,'B','velocity-label');f.text(527,100,'B′','velocity-label');f.arrow(164,185,164,93,'motion',True);f.text(183,146,'d','motion-label');f.arrow(313,185,357,160,'geo');f.text(344,184,'a₁','small');f.arrow(313,185,394,225,'geo');f.text(364,241,'a₂','small');f.eq('IB = IG + md²（兩軸平行）')
f=new(7,6,h=425);f.body(169,224,23);f.arrow(104,188,143,219,'force');f.text(60,172,'F₁','force-label');f.arrow(153,304,153,255,'force');f.text(118,328,'F₂','force-label');f.arrow(197,233,245,233,'force');f.text(250,224,'F₃','force-label');f.text(325,239,'=','eq','middle',36);f.body(477,224,23);f.point(169,224,'G',dx=-15,dy=10);f.point(469,237,'G',dx=-25,dy=22);f.arrow(469,237,568,217,'motion');f.text(536,198,'maG','motion-label');f.rotate(477,224,120,cls='force',label='IGα');f.text(170,51,'自由體圖','small','middle');f.text(481,51,'運動圖','small','middle');f.eq('ΣF = maG　　ΣMG = IGα',405)
f=new(7,7,h=450);f.body(349,199,35);f.point(210,309,'O',dx=-27);f.point(365,204,'G');f.line(210,309,365,204,'guide');f.arrow(365,204,210,309,'motion');f.arrow(365,204,421,287,'velocity');f.text(265,252,'maₙ','motion-label');f.text(438,277,'maₜ','velocity-label');f.arrow(365,204,365,107,'force');f.text(384,111,'F','force-label');f.rotate(210,309,65,label='α');f.text(164,234,'rG','small');f.eq('aₙ = ω²rG　　aₜ = αrG',421)
f=new(7,8,h=455);f.disk(306,244,103);f.ground(102,347,425);f.arrow(306,244,306,318,'force');f.text(345,324,'mg','force-label');f.arrow(306,347,306,284,'force');f.text(320,286,'N','force-label');f.arrow(306,347,214,347,'force');f.text(201,326,'f','force-label');f.arrow(409,244,512,244,'force');f.text(526,250,'P','force-label');f.arrow(306,80,431,80,'motion');f.text(445,88,'aG','motion-label');f.rotate(306,244,133,label='');f.text(168,141,'α','motion-label');f.text(56,52,'示例：水平推力作用於質心','small');f.eq('vG = ωR　　aG = αR（無滑動）',433)
f=new(7,9);f.ellipse(303,235,105,35);f.rect(198,188,210,47);f.ellipse(303,188,105,35);f.arrow(303,270,303,62,'geo');f.text(319,62,'z');f.point(384,207,'mi',dx=12,dy=23);f.line(303,188,384,207,'guide');f.text(347,183,'ri','small');f.arrow(384,207,426,123,'velocity');f.text(439,126,'vi','velocity-label');f.rotate(303,322,35,label='ω');f.eq('T = ½Iω²')
f=new(7,10);f.disk(367,224,91);f.point(191,105,'O',dx=-24,dy=-15);f.line(191,105,367,224,'guide');f.text(257,156,'d');f.arrow(367,224,427,135,'velocity');f.text(440,131,'vG','velocity-label');f.rotate(367,224,125);f.eq('T = ½mvG² + ½IGω²')

def main():
    items=json.loads((ART/'sources.json').read_text())
    assert len(figs)==len(items)==43
    for item in items:
        old=item['file'];key=Path(old).stem;f=figs[key]
        for private_key in ['reference_file', 'box', 'source_url']:
            item.pop(private_key, None)
        item['file']=f'assets/dynamics/{key}.svg'
        item['width'],item['height']=f.w,f.h
        item['redrawn']=True
        desc=item['title']+'。依講義概念重新繪製；幾何形狀為示意，不代表實際比例。'
        (ROOT/item['file']).write_text(f.xml(item['title'],desc))
    for chapter in range(1,8):
        path=ROOT/f'dynamics-ch{chapter:02}.html';s=path.read_text()
        for item in [x for x in items if x['chapter']==chapter]:
            key=Path(item['file']).stem
            pattern=r'<figure class="lecture-figure">[\s\S]*?'+re.escape(key)+r'\.(?:webp|svg)[\s\S]*?</figure>'
            # Match the individual figure, never across preceding figures.
            pattern=r'<figure class="lecture-figure">(?:(?!</figure>)[\s\S])*?'+re.escape(key)+r'\.(?:webp|svg)(?:(?!</figure>)[\s\S])*?</figure>'
            title=html.escape(item['title']);src=item['file']
            replacement=f'''<figure class="lecture-figure">
          <a href="{src}" target="_blank" rel="noopener" aria-label="放大圖面：{title}"><img src="{src}" alt="{title}" width="{item['width']}" height="{item['height']}" loading="lazy" decoding="async"></a>
          <figcaption>{title}｜依程東版講義 {chapter}-{item['page']} 重繪 · <a href="{src}" target="_blank" rel="noopener">放大圖面</a></figcaption>
        </figure>'''
            s,n=re.subn(pattern,lambda m:replacement,s)
            assert n==1,(chapter,key,n)
        path.write_text(s)
    (ART/'sources.json').write_text(json.dumps(items,ensure_ascii=False,indent=2)+'\n')
    print('Redrew 43 SVG diagrams and updated all seven chapters.')

if __name__=='__main__':main()
