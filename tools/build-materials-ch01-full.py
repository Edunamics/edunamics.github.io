#!/usr/bin/env python3
"""Reflow the complete first Materials chapter into accessible web content.
Run with the same Python dependencies as build-materials-course.py.
Source page references are editorial traceability, never public PDF links.
"""
from pathlib import Path
from io import BytesIO
import importlib.util, html, json, math, re
import matplotlib
matplotlib.use('Agg')
matplotlib.rcParams.update({'svg.fonttype':'path','svg.hashsalt':'materials-full-ch01'})
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Circle, Rectangle, Arc, Polygon
from matplotlib.font_manager import FontProperties
ROOT=Path(__file__).resolve().parents[1]
def module(name,file):
 s=importlib.util.spec_from_file_location(name,Path(__file__).with_name(file));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
m=module('materials_base','build-materials-course.py');d=module('materials_ch01_data','materials-ch01-full-data.py')
P='#4b2a9a';INK='#1e1830';LOAD='#c2410c';SOFT='#eee8f8';MUTED='#625a76'
fp=FontProperties(fname='/System/Library/Fonts/Supplemental/Arial Unicode.ttf',size=10)
figures={};equations=[]
def eq(tex,lab=''):
 equations.append(tex);return m.formula(tex,lab)
def p(text):return '<p>'+html.escape(text)+'</p>'
def h(text):return '<h3>'+html.escape(text)+'</h3>'
def ul(items):return '<ul>'+''.join('<li>'+html.escape(x)+'</li>' for x in items)+'</ul>'
def table(head,rows):return '<div class="table-scroll"><table><thead><tr>'+''.join('<th scope="col">'+html.escape(x)+'</th>' for x in head)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+html.escape(x)+'</td>' for x in row)+'</tr>' for row in rows)+'</tbody></table></div>'
def note(s):return '<p class="callout warn">'+html.escape(s)+'</p>'
def canvas(title):
 f,a=plt.subplots(figsize=(9.6,4.4));f.subplots_adjust(.02,.025,.98,.98);a.set(xlim=(-.4,10.5),ylim=(-.2,4.7),aspect='equal');a.axis('off');label(a,5,4.4,title,size=12,color=P);return f,a
def label(a,x,y,s,color=INK,size=10,ha='center'):
 a.text(x,y,s,fontproperties=fp,fontsize=size,color=color,ha=ha,va='center')
def line(a,x,y,color=P,lw=2,**kw):a.plot(x,y,color=color,lw=lw,**kw)
def arrow(a,start,end,color=LOAD):a.add_patch(FancyArrowPatch(start,end,arrowstyle='-|>',mutation_scale=12,color=color,lw=1.7))
def moment(a,x,y,text,ccw=True):
 a.add_patch(Arc((x,y),.65,.85,theta1=40,theta2=310,color=LOAD,lw=1.7));ang=math.radians(310 if ccw else 40);end=(x+.325*math.cos(ang),y+.425*math.sin(ang));arrow(a,(end[0]-.1,end[1]-.05) if ccw else (end[0]-.07,end[1]+.1),end);label(a,x+.65,y,text,color=LOAD,size=9)
def support(a,x,y,kind='pin',name=''):
 if kind=='fixed':
  line(a,[x,x],[y-.55,y+.55],lw=4)
  for yy in [y-.5+i*.18 for i in range(7)]:line(a,[x-.2,x],[yy-.15,yy],color=MUTED,lw=.8)
 else:
  a.add_patch(Polygon([(x,y),(x-.19,y-.32),(x+.19,y-.32)],fc=SOFT,ec=P,lw=1.3))
  if kind=='roller':
   for xx in [x-.11,x+.11]:a.add_patch(Circle((xx,y-.39),.055,fc='white',ec=P))
  line(a,[x-.32,x+.32],[y-.5,y-.5],color=MUTED,lw=.9)
 if name:label(a,x,y-.72,name,size=10,color=P)
def dim(a,x1,x2,text,y=.45):
 a.annotate('',(x1,y),(x2,y),arrowprops={'arrowstyle':'<->','color':MUTED,'lw':.7});label(a,(x1+x2)/2,y-.2,text,size=9)
def finish(key,f,a,caption):
 b=BytesIO();f.savefig(b,format='svg',facecolor='white',metadata={'Date':None});plt.close(f);raw=b.getvalue();figures[key]={'svg':raw,'caption':caption};return figure_html(key)
def figure_html(key):
 v=figures[key];return '<figure class="lecture-figure"><button class="figure-zoom" data-zoom aria-label="放大：'+html.escape(v['caption'],quote=True)+'"><img src="'+m.encoded(v['svg'])+'" width="922" height="422" alt="'+html.escape(v['caption'],quote=True)+'" loading="lazy" decoding="async"></button><figcaption>重繪圖｜'+html.escape(v['caption'])+'。點圖可放大。</figcaption></figure>'
def beam(key,title,L,supports,points=(),loads=(),marks=(),dims=(),couples=()):
 f,a=canvas(title);x=lambda s:.7+8.4*s/L;y=2
 line(a,[x(0),x(L)],[y,y],lw=6)
 for at,kind,name in supports:support(a,x(at),y,kind,name)
 for j,(at,text) in enumerate(points):
  top=3.8 if j%2==0 else 3.35;arrow(a,(x(at),top-.18),(x(at),y+.03));label(a,x(at),top,text,color=LOAD,size=9)
 for j,(start,end,wa,wb,text) in enumerate(loads):
  high=max(wa,wb) or 1;bottom=2.18
  xx=[start+(end-start)*i/9 for i in range(10)]
  heights=[.85*(wa+(wb-wa)*((i/9)**3 if key=='p11' else i/9))/high for i in range(10)]
  for z,ht in zip(xx,heights):
   if ht>.04:arrow(a,(x(z),bottom+ht),(x(z),bottom))
  line(a,[x(z) for z in xx],[bottom+ht for ht in heights],color=LOAD,lw=1)
  label(a,(x(start)+x(end))/2,3.25,text,color=LOAD,size=9)
 for at,text in marks:
  line(a,[x(at),x(at)],[1.8,2.35],color=MUTED,lw=1,ls='--');label(a,x(at),1.55,text,size=9)
 for start,end,text in dims:dim(a,x(start),x(end),text)
 for at,text in couples:moment(a,x(at),2.4,text)
 return finish(key,f,a,title+'；尺寸與標籤置於構件外側')
def axial(key,number=False):
 f,a=canvas('分段桿：外力與截面位置');xs=[1.4,3.8,6.2,8.6];ys=[.65,.48,.33]
 for i in range(3):a.add_patch(Rectangle((xs[i],2-ys[i]/2),xs[i+1]-xs[i],ys[i],fc=SOFT,ec=P,lw=2));label(a,(xs[i]+xs[i+1])/2,1.35,('3 m' if number else f'L{i+1} / A{i+1}'))
 forces=['4000 N ←','9000 N →','2000 N →','7000 N ←'] if number else ['固定端','3P →','2P →','P ←']
 for i,(x,t) in enumerate(zip(xs,forces)):
  label(a,x,3.2 if i%2==0 else 3.65,t,color=LOAD);label(a,x,1.6,('ABCD' if number else 'abcd')[i],color=P)
  if i==0 and not number:support(a,x,2,'fixed')
  else:
   right=(number and i in [1,2]) or (not number and i in [1,2])
   arrow(a,(x,2),(x+(.85 if right else -.85),2))
 return finish(key,f,a,'三段桿的負載、分段長度與截面；箭號旁文字給出軸向力方向')
def curved(key,mode):
 title={'quarter':'四分之一圓弧桿','half':'半圓桿兩端向外受力','arch':'半圓簡支梁跨中集中力'}[mode];f,a=canvas(title);cx,cy,r=5,1.25,2.25
 if mode=='quarter':
  ts=[math.pi/2+i*math.pi/200 for i in range(101)];line(a,[cx+r*math.cos(t) for t in ts],[cy+r*math.sin(t) for t in ts],lw=6);support(a,cx-r,cy,'fixed','固定端');arrow(a,(cx,3.45),(cx,2.7));label(a,cx+.5,3.7,'P ↓',color=LOAD);theta=math.pi*.78;pt=(cx+r*math.cos(theta),cy+r*math.sin(theta));line(a,[cx,pt[0]],[cy,pt[1]],lw=1,ls='--');line(a,[cx-r,cx],[cy,cy],color=MUTED,lw=1,ls='--');label(a,4.0,1.6,'θ');label(a,4.6,2.4,'R');label(a,*[pt[0]-.3,pt[1]+.3],'截面')
 else:
  ts=[i*math.pi/160 for i in range(161)];line(a,[cx+r*math.cos(t) for t in ts],[cy+r*math.sin(t) for t in ts],lw=6)
  line(a,[cx-r,cx+r],[cy,cy],color=MUTED,lw=.8,ls='--')
  if mode=='arch':support(a,cx-r,cy,'roller','A');support(a,cx+r,cy,'pin','C');arrow(a,(cx,4.05),(cx,3.5));label(a,cx+.4,3.95,'P ↓',color=LOAD);label(a,cx+.25,3.25,'B');theta=math.pi*.72;label(a,4.2,1.6,'θ：由左端起算',size=9)
  else:
   arrow(a,(cx-r,cy),(cx-r-1.3,cy));arrow(a,(cx+r,cy),(cx+r+1.3,cy));force='P=1000 N' if key=='e10' else '2P';label(a,1.5,1.65,force,color=LOAD);label(a,8.5,1.65,force,color=LOAD);theta=math.pi/4;label(a,5.85,1.6,'θ',size=10)
  pt=(cx+r*math.cos(theta),cy+r*math.sin(theta));line(a,[cx,pt[0]],[cy,pt[1]],lw=1,ls='--');label(a,(cx+pt[0])/2-.2,(cy+pt[1])/2+.2,'R' if mode=='arch' else 'r');a.add_patch(Circle(pt,.08,fc='white',ec=LOAD));label(a,pt[0]+(-.5 if mode=='arch' else .5),pt[1]+.35,'截面')
 label(a,cx,cy-.25,'O',color=MUTED)
 return finish(key,f,a,title+'；角度基準依題目文字定義')
def special(key):
 if key=='e3':return axial(key)
 if key=='e4':return axial(key,True)
 if key in ['e9','e10','p10','p12']:return curved(key,'quarter' if key=='e9' else 'arch' if key=='p12' else 'half')
 f,a=canvas({'e2':'偏心負載與等效力偶','e5':'四皮帶輪的扭矩平衡','e8':'軸力在斜接面的分解','e11':'繩索與滑輪構架','p7':'導向繩索與豎臂','p8':'上下梁的接觸作用力'}[key])
 if key=='e2':
  line(a,[1,9],[1.8,1.8],lw=6);support(a,1,1.8,'pin','A');support(a,9,1.8,'roller','B');line(a,[6.333,6.333,7.667],[1.8,3.13,3.13],lw=6);arrow(a,(7.667,3.9),(7.667,3.2));label(a,8.5,3.8,'P = 500 kN',color=LOAD);dim(a,1,6.333,'200 mm');dim(a,6.333,9,'100 mm');dim(a,6.333,7.667,'50 mm',3.6);label(a,5.5,2.6,'50 mm');label(a,6.0,1.4,'C')
 elif key=='e5':
  line(a,[5,5],[.8,3.9],lw=5)
  for i,(name,t) in enumerate(zip('ABCD',['+30','−65','+20','+15'])):
   y=3.6-i*.85;a.add_patch(Rectangle((4.2,y-.12),1.6,.24,fc=SOFT,ec=P));label(a,3,y,name);label(a,7,y,t+' kip·in',color=LOAD)
  line(a,[3.6,6.2],[2.32,2.32],color=MUTED,lw=1,ls='--');label(a,2.2,2.32,'BC 截面')
 elif key=='e8':
  a.add_patch(Rectangle((2,1.5),6,1,fc=SOFT,ec=P,lw=2));line(a,[4.7,5.28],[1.5,2.5],color=LOAD,lw=3);arrow(a,(2,2),(.7,2));arrow(a,(8,2),(9.3,2));label(a,1.1,2.5,'8 kN',color=LOAD);label(a,8.9,2.5,'8 kN',color=LOAD);label(a,4.5,1.1,'接面與軸夾 60°');label(a,5.8,3.4,'法向 N；切向 V');line(a,[5,6],[2,1.42],color=MUTED,lw=1,ls='--');label(a,7.1,.6,'截面：25 mm × 30 mm')
 elif key=='e11':
  X=lambda v:1+5*v;y=1.5;line(a,[X(0),X(1.5)],[y,y],lw=6);line(a,[X(.5),X(.5)],[y,y+2],lw=6);support(a,X(0),y,'pin','A');support(a,X(.5),y+2,'pin','C');a.add_patch(Circle((X(1.5),y),.75,fc=SOFT,ec=P));line(a,[X(.5),X(1.5)],[y+.75,y+.75],color=LOAD,lw=1.3);line(a,[X(1.5)+.75,X(1.5)+.75],[y,y-.75],color=LOAD,lw=1.3);arrow(a,(X(1.5)+.75,y-.75),(X(1.5)+.75,.2));label(a,9.7,.55,'W=1.6 kN',color=LOAD,size=9);label(a,X(.5)-.4,y+.7,'E');label(a,X(.5)-.3,y-.25,'D');label(a,X(.9),y-.25,'G');label(a,X(1.5),y,'B');dim(a,X(0),X(.5),'0.5 m',.4);dim(a,X(.5),X(1.5),'1.0 m',.4);label(a,1.6,3.25,'DC=0.4 m',size=9);label(a,6,3.7,'r=0.15 m；DE=0.15 m',size=9)
 elif key=='p7':
  xx=lambda v:1+v*1.25;y=1.55;line(a,[xx(0),xx(6)],[y,y],lw=6);line(a,[xx(4),xx(4)],[y,y+1.875],lw=6);support(a,xx(0),y,'pin','A');support(a,xx(6),y,'roller','D');line(a,[xx(2),xx(4)],[y,y+1.875],color=LOAD,lw=1.3);arrow(a,(xx(2),y),(xx(2),.65));label(a,xx(2)+.65,.65,'6 kN',color=LOAD);label(a,xx(2),1.9,'B');label(a,xx(4)+.25,y-.25,'C');label(a,xx(4),3.7,'E');label(a,7.3,2.75,'1.5 m');dim(a,xx(0),xx(2),'2 m',.15);dim(a,xx(2),xx(4),'2 m',.15);dim(a,xx(4),xx(6),'2 m',.15)
 elif key=='p8':
  line(a,[1,8.2],[2.7,2.7],lw=6);line(a,[1.8,9.8],[1.5,1.5],lw=6);support(a,1,2.7,'pin','A');support(a,1.8,1.5,'roller','C');support(a,9.8,1.5,'pin','D');a.add_patch(Circle((5,2.1),.6,fc='white',ec=P));label(a,5.9,2.1,'B');arrow(a,(2.6,3.8),(2.6,2.8));arrow(a,(8.2,3.8),(8.2,2.8));label(a,2.6,4,'500 N',color=LOAD);label(a,8.2,4,'1000 N',color=LOAD);label(a,4.6,3.25,'上梁：2 m + 3 m + 4 m',size=9);dim(a,1.8,5,'4 m',.3);dim(a,5,9.8,'6 m',.3)
 return finish(key,f,a,{'e2':'500 kN 向下負載作用於 C 右方50 mm 的剛臂','e5':'以 A、C、D 扭矩為正，BC 段作截面平衡','e8':'60°斜焊接面；分力投影到接面法向及切向','e11':'ADB 與 DC 在 D 鉸接；滑輪半徑造成繩端 E 的高度','p7':'BE 纜索水平2 m、垂直1.5 m，B 點接續向下吊重','p8':'上梁的 B 向上接觸力，對下梁必須反向'}[key])
def problem_figure(key):
 if key in ['e2','e3','e4','e5','e8','e9','e10','e11','p7','p8','p10','p12']:return special(key)
 configs={
 'e1':(12,[(0,'pin','A'),(12,'roller','B')],[(11,'30 N')],[(0,9,0,20,'0 → 20 N/m')],[],[(0,9,'9 m'),(9,11,'2 m'),(11,12,'1 m')],[]),
 'e6':(9,[(0,'pin','A'),(6,'roller','B')],[],[(0,3,8,8,'8 kN/m'),(7.5,9,6,6,'6 kN/m')],[(4.5,'切面 x=4.5 m')],[(0,3,'3 m'),(3,6,'3 m'),(6,7.5,'1.5 m'),(7.5,9,'1.5 m')],[]),
 'e7':(6,[(6,'fixed','B 固定端')],[],[(0,6,0,1,'0 → q₀')],[(0,'A 自由端'),(2.5,'x')],[(0,6,'L')],[]),
 'p1':(2.4,[(0,'pin','A'),(1.8,'roller','B')],[(2.4,'500 N')],[(0,1.2,0,900,'0 → 900 N/m')],[],[(0,1.2,'1.2 m'),(1.2,1.8,'0.6 m'),(1.8,2.4,'0.6 m')],[]),
 'p2':(1.8,[(.4,'roller','A：x=d'),(1.8,'pin','B')],[(0,'100 N'),(.9,'200 N'),(1.8,'300 N')],[],[],[(0,.9,'900 mm'),(.9,1.8,'900 mm')],[]),
 'p3':(4,[(0,'fixed','A')],[(1,'4 kN')],[(2,4,1.5,1.5,'1.5 kN/m')],[(.5,'D')],[(0,1,'1 m'),(1,2,'1 m'),(2,4,'2 m')],[]),
 'p4':(.54,[(.12,'pin','C'),(.42,'roller','E')],[(0,'500 N'),(.54,'500 N')],[],[(.32,'D')],[(0,.12,'120 mm'),(.12,.32,'200 mm'),(.32,.42,'100 mm'),(.42,.54,'120 mm')],[(.32,'60 N·m ↺')]),
 'p5':(10,[(0,'pin','A'),(8,'roller','B')],[(3,'28 kN')],[(0,10,6,6,'6 kN/m（全長）')],[(5,'D')],[(0,3,'3 m'),(3,5,'2 m'),(5,8,'3 m'),(8,10,'2 m')],[]),
 'p6':(6,[(0,'pin','A'),(6,'roller','B')],[],[(0,6,0,240,'w(x)=40x；末端240 N/m')],[],[(0,6,'6 m')],[]),
 'p9':(10,[(0,'pin','左支承'),(10,'roller','右支承')],[],[(0,4,2,2,'2 kN/m'),(4,10,2,0,'線性降至0')],[(2,'A'),(4,'B'),(7,'C')],[(0,2,'2 m'),(2,4,'2 m'),(4,7,'3 m'),(7,10,'3 m')],[]),
 'p11':(8,[(0,'fixed','A')],[],[(0,8,1000,2024,'w=1000+2x³ N/m（曲線示意）')],[(8,'B')],[(0,8,'8 m')],[])}
 c=configs[key];return beam(key,next(x['title'] for x in d.CASES if x['id']==key),*c)

def concept(key):
 f,a=canvas({'force':'力的分解、力矩與力偶','supports':'支承替換成反力','cuts':'截面內力：平面與空間','loads':'負載圖的面積與形心'}[key])
 if key=='force':
  arrow(a,(1,1),(3,3),P);arrow(a,(1,1),(3,1),P);arrow(a,(3,1),(3,3),P);label(a,2,3.35,'F');label(a,2,.65,'Fx');label(a,3.4,2,'Fy');label(a,1.7,1.35,'θ')
  line(a,[5,8],[1.5,1.5],lw=4);a.add_patch(Circle((5,1.5),.08,fc=P));arrow(a,(8,3),(8,1.5));label(a,8.5,2.7,'F');label(a,6.4,1.1,'d：垂直力臂');label(a,6.5,.6,'M=Fd');arrow(a,(5,3.4),(6,3.4));arrow(a,(6,4),(5,4));label(a,7.2,3.8,'力偶：合力0，矩≠0',size=9)
 elif key=='supports':
  for x,k,t in [(1.4,'roller','滾支承'),(5,'pin','鉸支承'),(8.7,'fixed','固定端')]:
   line(a,[x,x+1],[2,2],lw=5);support(a,x,2,k);arrow(a,(x,1),(x,1.8),P);label(a,x,3.5,t);label(a,x+.4,.5,'Ry',color=P)
   if k!='roller':arrow(a,(x-.9,2),(x-.1,2),P);label(a,x-.8,2.4,'Rx',color=P)
   if k=='fixed':moment(a,x+.6,2.8,'M')
 elif key=='cuts':
  a.add_patch(Rectangle((.8,1.4),3.2,1,fc=SOFT,ec=P));line(a,[4,4],[1.1,2.7],color=MUTED,ls='--');arrow(a,(4,1.9),(5.1,1.9),P);label(a,5.3,1.9,'N');arrow(a,(4.15,1.9),(4.15,.8),P);label(a,4.7,.9,'V');moment(a,4.5,2.8,'M');label(a,2.1,3.4,'2D：N、V、M')
  a.add_patch(Circle((7.5,2),.7,fc=SOFT,ec=P));arrow(a,(7.5,2),(9.1,2),P);arrow(a,(7.5,2),(7.5,3.2),P);arrow(a,(7.5,2),(6.4,1.0),P);label(a,9.1,2.4,'N / T');label(a,7.8,3.4,'Vy / My');label(a,6.8,.65,'Vz / Mz');label(a,8,3.9,'3D：3力＋3矩')
 elif key=='loads':
  a.add_patch(Rectangle((.8,1.5),3,1.3,fc=SOFT,ec=P));arrow(a,(2.3,1.3),(2.3,.5));label(a,2.3,3.2,'均布 w；長 L');label(a,2.3,.2,'R=wL，位於 L/2')
  a.add_patch(Polygon([(5.5,1.5),(9,1.5),(9,2.8)],fc=SOFT,ec=P));arrow(a,(7.833,1.3),(7.833,.5));label(a,7.25,3.2,'由0增至 w₀；長 L');label(a,7.4,.2,'R=w₀L/2，距小端2L/3')
 return finish(key,f,a,{'force':'平面分力、垂直力臂與純力偶的差異','supports':'理想平面滾支承1個反力、鉸支承2個分量、固定端另有反力矩','cuts':'左段右切面：軸力向外、剪力向下、正彎矩使梁下凹；空間截面有6個分量','loads':'分布負載合力等於面積，作用於負載圖形心'}[key])

def sections():
 s=[]
 s.append(h('一、力學的定義')+p('力學研究物體受力後的運動，以及內部受力與變形。工程力學常包含靜力學、動力學與材料力學；分析同一構件時，通常先以剛體模型求外力平衡，再以可變形體模型求應力與位移。')+h('二、力學的種類')+table(['分類','研究對象與分支'],[['固體力學／剛體','靜力學；動力學再分運動學與動力學（含力與運動關係）'],['固體力學／可變形體','材料力學、彈性力學、塑性力學'],['流體力學','液體及氣體的靜止、流動與受力']])+h('三、機械力學研究的範圍')+table(['科目','模型與主要問題'],[['靜力學','以剛體近似討論力與力矩平衡，求支承反力及構件內力。'],['動力學','運動學描述位置、速度與加速度；動力學連結受力、質量及運動。'],['材料力學','把構件視為可變形體，研究應力、應變、變形、強度與穩定。']])+note('靜力平衡不代表材料沒有變形。受拉桿可以兩端外力平衡，同時伸長並具有內部應力。'))
 s.append(h('一、力的分類與特性')+p('力是使物體改變運動狀態、或具有改變運動與形狀傾向的作用。力有大小、方向、作用點三要素；在剛體平衡中還必須追蹤作用線。')+table(['分類','意義與例子'],[['外力／內力','外力由所選系統之外作用；內力是系統內部各部分的相互作用。切開系統後，原來的內力成為局部自由體的外力。'],['接觸力','須經接觸傳遞，例如法向壓力、摩擦力、繩索張力。'],['超距力','可不直接接觸而作用，例如重力、電力、磁力。'],['集中力／分布力','集中力是理想化於一點的作用；分布力可沿長度、面積或體積分布。']])+h('力的外效應、內效應與可傳性')+p('外效應是物體整體平移或轉動狀態的改變；內效應是內部應力與變形。剛體上的力可沿同一作用線移動而不改變其外效應，稱力的可傳性。這不保證局部應力及變形不變。功描述力沿位移的作用；不能把力與功視為相同物理量。')+eq(r'W=\int\mathbf F\cdot d\mathbf r','功的 SI 單位為 J=N·m；與力矩同量綱，但物理意義不同')+h('二、單位與數值大小')+table(['量','常用符號','SI 單位'],[['質量','m','kg'],['長度','L','m'],['時間','t','s'],['力','F','N'],['力矩','M','N·m'],['線負載','w','N/m']])+eq(r'1\ \mathrm N=1\ \mathrm{kg\cdot m/s^2},\quad 1\ \mathrm N=10^5\ \mathrm{dyn}','牛頓定義與達因換算')+eq(r'1\ \mathrm{kgf}=9.80665\ \mathrm N,\quad 1\ \mathrm{gf}=980.665\ \mathrm{dyn}','標準重力換算；原稿9.8與980為近似值')+table(['字首','符號','倍率'],[['giga','G','10⁹'],['mega','M','10⁶'],['kilo','k','10³'],['milli','m','10⁻³'],['micro','μ','10⁻⁶'],['nano','n','10⁻⁹']])+h('三、分解、合成、力矩與力偶')+p('平面力沿兩個互相垂直座標分解；若 θ 從正 x 軸逆時針量起，分量符號由角度決定。非正交分解時，分力大小可能大於合力；正交分量的絕對值則不超過原力大小。')+eq(r'\mathbf F=F_x\mathbf i+F_y\mathbf j,\quad F_x=F\cos\theta,\quad F_y=F\sin\theta','正交分量')+eq(r'R_x=\sum F_x,\quad R_y=\sum F_y,\quad R=\sqrt{R_x^2+R_y^2}','合力方向用 atan2(Ry,Rx) 辨識象限')+concept('force')+p('力矩代表力對指定點或軸的旋轉效應。平面問題取逆時針為正，力臂必須是矩心到作用線的垂直距離。作用線通過矩心時，對該點的力矩為零。空間中對指定軸的矩，必須投影到該軸；作用線與軸相交或平行時，軸矩為零。')+eq(r'\mathbf M_O=\mathbf r\times\mathbf F,\quad M_O=xF_y-yF_x,\quad |M_O|=Fd','點矩與平面分量式')+p('力偶由大小相等、方向相反、作用線平行但不同線的兩力組成。合力為零而合矩不為零；力偶矩與矩心無關，可視為自由向量，方向由右手定則決定。同平行面、同大小與同轉向的力偶外效應相等。')+eq(r'\mathbf R=0,\quad |\mathbf C|=Fd','d 為兩平行作用線的垂直距離')+h('四、常見負載形式與等效合力')+concept('loads')+eq(r'R=\int_a^b w(x)\,dx,\quad \bar x=\frac{\int_a^b xw(x)\,dx}{R}','R≠0 時可用一個等效合力取代分布負載的外效應')+eq(r'W_{\mathrm{uniform}}=wL,\quad W_{\mathrm{triangle}}=\frac12w_0L','均布與三角形分布')+p('集中力用力與力臂求矩；集中力偶直接加入力矩方程。梯形負載可拆成矩形加三角形，或直接積分。將等效合力再移到另一點，必須補回力偶，不能只移動箭頭。')+h('五、常用三角函數')+eq(r'\sin(\pi/2+\theta)=\cos\theta,\quad\sin(\pi/2-\theta)=\cos\theta','互餘角')+eq(r'\cos(\pi-\theta)=-\cos\theta,\quad\tan(\pi/2-\theta)=\cot\theta','角度轉換；原稿最後一式排版有誤，這裡列正確恆等式')+eq(r'\sin(\alpha\pm\beta)=\sin\alpha\cos\beta\pm\cos\alpha\sin\beta','正弦和差角')+eq(r'\cos(\alpha\pm\beta)=\cos\alpha\cos\beta\mp\sin\alpha\sin\beta','餘弦和差角')+eq(r'\tan(\alpha\pm\beta)=\frac{\tan\alpha\pm\tan\beta}{1\mp\tan\alpha\tan\beta}','正切和差角；分母不可為零')+eq(r'\sin2\theta=2\sin\theta\cos\theta','二倍角')+eq(r'\cos2\theta=\cos^2\theta-\sin^2\theta=1-2\sin^2\theta=2\cos^2\theta-1','二倍角')+eq(r'\tan2\theta=\frac{2\tan\theta}{1-\tan^2\theta}','定義域內適用')+eq(r'\frac a{\sin A}=\frac b{\sin B}=\frac c{\sin C}=2R_c','正弦定理；Rc 為三角形外接圓半徑')+eq(r'a^2=b^2+c^2-2bc\cos A','餘弦定理；其餘兩式循環置換 a,b,c 與 A,B,C')+h('六、范力濃定理與移力')+p('一個力對 O 的矩，等於其分力對 O 的矩和。對同一矩心計算，可先分解再取矩，也可先求合力再取矩。')+eq(r'\mathbf r\times(\mathbf F_1+\mathbf F_2)=\mathbf r\times\mathbf F_1+\mathbf r\times\mathbf F_2','Varignon 定理')+p('把作用於 A 的力 F 平行移到 O，需另加 rOA×F 的力偶。兩者共同構成力—力偶等效系統。')+eq(r'\mathbf R=\sum_i\mathbf F_i,\quad\mathbf M_O=\sum_i\mathbf r_i\times\mathbf F_i+\sum_j\mathbf C_j','一般力系移到 O 的等效結果'))
 s.append(h('一、自由體圖的定義')+p('將全部或部分物體與周圍分離，以力或力矩取代被移除的接觸與約束，即為自由體圖。研究整體時，內部作用與反作用互相抵銷；研究單一構件或截段時，切面作用必須畫出。')+h('二、畫圖步驟')+ul(['選定系統邊界，畫出簡化外形與座標。','把已知力、分布負載、自重及外加力偶畫全。','移除支承並畫出它能提供的反力與反力矩。','標上力臂、幾何尺寸及未知量；未知方向可先假設。','求得負值表示實際方向與假設相反；同一作用與反作用不能同時畫在同一物體上。'])+h('三、接觸與支承反力')+concept('supports')+table(['約束','自由體圖上的作用','適用條件'],[['光滑平面、曲面或點接觸','一個垂直於接觸切面的法向反力','無摩擦；可分離的接觸不能提供拉力。'],['繩索','沿繩方向、拉離物體的張力','柔軟輕繩只能拉不能推。'],['理想滑輪','沿各繩段方向的張力','同一條輕繩與無摩擦、可忽略慣性的滑輪，兩側張力相同。'],['滾支承','一個垂直於支承面的反力','沿支承面可自由移動。'],['平面鉸支承','水平、垂直兩個反力分量','限制兩個平移，不限制平面轉動。'],['平面固定端','兩個反力分量加一個反力矩','限制兩個平移及一個轉動。'],['光滑滑塊','導軌法向力；鉸接點另有兩個分量','依選取滑塊或桿件自由體，作用方向互為相反。'],['二力構件','兩端大小相等、反向、共線的力','僅兩處端力、無其他外力與力偶，且處於平衡；兩端受力不自動保證是二力構件。']])+h('四、常見結構的自由體圖')+table(['結構','整體自由體','分離構件時'],[['簡支梁','鉸支承兩反力、滾支承一反力，外加全部荷載','求梁內力時，在指定位置切開。'],['懸臂梁','固定端兩反力及一反力矩','可優先取自由端一側，減少未知數。'],['理想桁架','整體外反力及節點荷載','每桿視為二力構件，節點圖上的桿力沿桿軸。']])+note('如果重量不可忽略、桿中另受外力或力偶，就不能再直接把該桿當成二力構件。'))
 s.append(h('一、力系種類')+table(['類別','作用線的幾何關係'],[['共線力系','各力在同一直線上。'],['平面共點力系','各力在同一平面，作用線交於同一點。'],['平面平行力系','共面，作用線互相平行。'],['平面一般力系','共面，既非全平行也非全共點。'],['空間共點力系','作用線交於一點，但不全在同一平面。'],['空間平行力系','作用線平行，但不全共面。'],['空間一般力系','既非全共點也非全平行，且不全共面。']])+h('二、平面共點力系與三力平衡')+p('共點力對交點的矩恆為零，因此平衡只需兩個獨立分量方程。二力平衡要求兩力等大、反向、共線；三個非平行力使剛體平衡時，其作用線必須共點，且向量首尾相接形成封閉三角形。若三力互相平行，則另以平行力系的力矩條件處理。')+eq(r'\sum F_x=0,\quad\sum F_y=0','平面共點力系的兩個獨立方程')+eq(r'\frac{F_1}{\sin\theta_1}=\frac{F_2}{\sin\theta_2}=\frac{F_3}{\sin\theta_3}','拉密定理；θi 為另外兩力之間的夾角')+p('三角形法可用正弦、餘弦定理求力。30°–60°–90°封閉力三角形的三邊長比為1：√3：2，對應力的比例依圖中邊的標號決定；不能脫離邊與角對應直接背 F₁、F₂、F₃ 的順序。')+h('三、剛體力系的合成與平衡')+p('質點平衡只要求合力零；剛體平衡同時要求合力與合矩零。力多邊形封閉僅代表合力零，對一般剛體尚須檢查合矩。舊式圖解法中，一般平行或非共點力系還需索多邊形封閉。')+eq(r'\sum F_x=0,\quad\sum F_y=0,\quad\sum M_O=0','平面剛體的三個獨立平衡方程')+table(['力系','獨立平衡方程數','選式方法'],[['平面共點力系','2','兩個力分量為零。'],['平面平行力系','2','沿力方向的合力與一個力矩為零。'],['平面一般力系','3','兩個力分量與一個力矩為零。'],['空間共點力系','3','x、y、z 三個力分量為零。'],['空間一般力系','6','三個力分量與三個力矩分量為零。']])+eq(r'\sum F_x=\sum F_y=\sum F_z=0','空間力平衡')+eq(r'\sum M_x=\sum M_y=\sum M_z=0','空間矩平衡')+ul(['選未知反力交點為矩心，常能直接消去多個未知量。','均布、三角形與曲線負載先化為合力和作用位置。','未知反力數超過可用獨立平衡式時，需再加入材料關係及變形相容，這是靜不定問題。','未知數與方程式同數不保證結構穩定，仍須檢查支承排列是否能限制剛體運動。']))
 s.append(h('一、截面法與平面內力')+p('假想把構件在所求位置切開，取任一側作自由體圖。原材料內部相互作用轉成切面的合力及合矩。先求整體反力，再求局部平衡；如果自由端一側較簡單，可直接從該側開始。')+concept('cuts')+table(['分量','方向與作用','本頁一般梁題慣例'],[['軸力 N','沿構件軸線，垂直於截面','拉伸為正、壓縮為負。'],['剪力 V','位於截面內，橫向於桿軸','左段右切面向下為正；另一側切面反向。'],['彎矩 M','使梁彎曲的截面力矩','使梁下凹為正；左段右切面正矩為逆時針。']])+eq(r'\sum F_{\parallel}=0,\quad\sum F_{\perp}=0,\quad\sum M_{\mathrm{cut}}=0','依序求 N、V、M')+p('內力只靠截面平衡求得；應力還需要面積及截面形狀。一般平面梁的三項為軸力、剪力、彎矩，不應把彎矩統稱為扭矩。曲桿必須沿局部切線與法線分解，並清楚定義角度與切面箭號。')+h('二、空間截面內力')+p('若取桿軸為 x 軸，空間切面有一個軸力 N、兩個剪力 Vy與Vz、一個沿桿軸的扭矩 T，以及繞另外兩軸的彎矩 My與Mz，共六個分量。扭矩繞桿軸使構件扭轉；彎矩繞橫向軸使構件彎曲。兩側切面的力與矩互為作用、反作用。')+eq(r'\mathbf R=N\mathbf i+V_y\mathbf j+V_z\mathbf k','切面合力')+eq(r'\mathbf M=T\mathbf i+M_y\mathbf j+M_z\mathbf k','切面合矩')+h('三、截面位置與正負號檢查')+ul(['在集中力、集中力偶、分布負載改變或接點位置分段。','集中橫向力造成剪力跳躍；集中力偶造成彎矩跳躍。','取另一側自由體應得到相同的內力狀態，但切面箭號相反。','原稿有些題目以剪力向上為正；本頁在題目中另行註明，並提供與一般梁號誌的換算。','力矩單位為 N·m 或 kN·m，不能只寫力的單位。']))
 return s

def build():
 old=(ROOT/'materials-ch01.html').read_text();titles=['力學的分類','力的重要性質','自由體圖','平面力系之合成及平衡','內力分析'];entries=[(f'sec{i}',f'1-{i}',t) for i,t in enumerate(titles,1)]+[('ex','範例','11道完整範例'),('practice','演練','12道實戰演練')]
 tabs=''.join(f'<a class="tab" id="tab-{id}" href="#{id}" role="tab" aria-controls="{id}" aria-selected="{"true" if j==0 else "false"}"><span class="ic">{m.icon(j)}</span><span class="tx"><span class="no">{no}</span><span class="nm">{title}</span></span></a>' for j,(id,no,title) in enumerate(entries))
 body=[];ranges=['1','2–9','10–13','14–16','17–18']
 for i,content in enumerate(sections(),1):body.append(f'<section id="sec{i}" aria-labelledby="h-sec{i}"><h2 id="h-sec{i}"><span class="no">1-{i}</span>{titles[i-1]}</h2><p class="source-ref">依原稿第 {ranges[i-1]} 頁重編</p>{content}</section>')
 for group,title in [('ex','完整範例'),('practice','實戰演練')]:
  articles=[]
  for c in [c for c in d.CASES if c['group']==group]:
   lab=('範例' if group=='ex' else '演練')+str(c['no']);drawing=problem_figure(c['id']);calcs=''.join(eq(*e) for e in c['eq']);steps='<ol>'+''.join('<li>'+html.escape(t)+'</li>' for t in c['steps'])+'</ol>';warning=note(c['note']) if c.get('note') else ''
   articles.append(f'<article class="example full-example" id="{c["id"]}"><h3>{lab}｜{html.escape(c["title"])}</h3><p class="source-ref">原稿第 {c["page"]} 頁 · 題目與計算重新編排</p>{p(c["q"])}{drawing}{warning}<details class="worked-solution"><summary><span class="qn">解</span><span>展開完整推導與答案</span></summary><div class="solution">{steps}{calcs}<p class="answer">{html.escape(c["answer"])}</p></div></details></article>')
  body.append(f'<section id="{group}" aria-labelledby="h-{group}"><h2 id="h-{group}"><span class="no">{"EX" if group=="ex" else "TRY"}</span>{title}</h2><p>依原講義順序保留全部題目，圖面重繪，計算重新核對。先看題目自行分析，再展開推導；題圖與原解析不同之處另加註記。</p><nav class="problem-index" aria-label="{title}索引">'+''.join(f'<a href="#{c["id"]}">{c["no"]}</a>' for c in d.CASES if c['group']==group)+'</nav>'+''.join(articles)+'</section>')
 header='<header class="hero"><div><div class="crumb"><a href="mechanics-of-materials.html">材料力學</a> / CH 01</div><h1>力的基本觀念<small>Fundamentals of Force</small></h1><p class="lede">由力的性質、自由體圖與平衡方程，進入截面內力分析。完整重編第一章五節、11 道範例與12 道實戰演練；公式圖檔與重繪圖直接隨文閱讀。</p><div class="meta"><span>5 節完整講解</span><span>11 道範例</span><span>12 道實戰演練</span><span>依原稿43頁重編</span></div></div><div class="hero-art" aria-hidden="true">'+m.icon(1)+'</div></header>'
 head=old[:old.index('<body>')];head=head.replace('assets/materials-course.css?v=purple-20261015','assets/materials-course.css?v=full-ch01-20261015')
 nav='<nav class="chapter-nav" aria-label="章節導覽"><a href="mechanics-of-materials.html#ch-h">材料力學章節總覽</a><a href="materials-ch02.html">下一章 →</a></nav>'
 result=head+'<body>'+header+'<div class="wrap"><nav class="tabs" role="tablist" aria-label="本章各節" aria-orientation="vertical"><p class="tabs-label">SECTIONS</p>'+tabs+'</nav><main>'+''.join(body)+nav+'</main></div><dialog id="figure-dialog" aria-label="放大圖面"><button class="zoom-close" autofocus>關閉 ×</button><img alt=""><p></p></dialog><script src="assets/chapter.js"></script><script src="assets/materials-course.js?v=no-pdf-20261015"></script></body></html>'
 (ROOT/'materials-ch01.html').write_text(result)
 qa=ROOT.parent/'output/materials-ch01-full';qa.mkdir(parents=True,exist_ok=True)
 for key,v in figures.items():(qa/(key+'.svg')).write_bytes(v['svg'])
 report={'sections':5,'examples':11,'practice':12,'source_pages':43,'figures':len(figures),'formula_placements':len(equations),'unique_formulas':len(set(equations)),'coverage':[{'id':c['id'],'source_page':c['page'],'title':c['title']} for c in d.CASES]}
 (qa/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False))
if __name__=='__main__':build()
