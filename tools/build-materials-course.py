#!/usr/bin/env python3
"""Build the 15 chapter course, outlined formula images and redrawn SVG figures.
PYTHONPATH=/private/tmp/dynamics-math-render:/private/tmp/materials-pdf python3 tools/build-materials-course.py
Prefer working source PDFs in ../sources/materials; published copies are a fallback.
"""
from pathlib import Path
from io import BytesIO
import base64,hashlib,html,importlib.util,json,re,shutil
import matplotlib
matplotlib.use('Agg')
matplotlib.rcParams.update({'svg.fonttype':'path','svg.hashsalt':'materials-course','mathtext.fontset':'stix','savefig.transparent':True})
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle,Circle,Ellipse,Polygon,Arc,FancyArrowPatch
from matplotlib.font_manager import FontProperties,fontManager
from lxml import etree
import pymupdf
ROOT=Path(__file__).resolve().parents[1]
def mod(name,file):
 s=importlib.util.spec_from_file_location(name,Path(__file__).with_name(file));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
data=mod('materials_data','materials-course-data.py');u=mod('materials_math','course-formula-utils.py')
def source_path(n):
 working=ROOT.parent/f'sources/materials/ch{n:02}.pdf'
 return working if working.exists() else ROOT/f'assets/materials/materials-ch{n:02}.pdf'
FONT='/System/Library/Fonts/Supplemental/Arial Unicode.ttf'
fontManager.addfont(FONT);fp=FontProperties(fname=FONT,size=12)
GREEN='#0f6b3a';INK='#152231';FORCE='#c2410c';MUTED='#566677';FILL='#e1f0e8'
FIGURES={};EQUATIONS={};manifest=[]
def encoded(b):return 'data:image/svg+xml;base64,'+base64.b64encode(b).decode()
def normalize(tex):
 tex=tex.replace('\\bigl','\\left').replace('\\bigr','\\right')
 tex=re.sub(r'\\(mathbf|mathcal|boldsymbol|mathrm|mathit)\s*(\\[A-Za-z]+|[A-Za-z])',lambda m:'\\'+m[1]+'{'+m[2]+'}',tex)
 def atom(s,j):
  while j<len(s) and s[j].isspace():j+=1
  start=j
  if s[j]=='{':
   level=1;j+=1
   while level:
    if s[j]=='{':level+=1
    elif s[j]=='}':level-=1
    j+=1
   return s[start:j],j
  if s[j]=='\\':
   j+=1
   while j<len(s) and s[j].isalpha():j+=1
  else:j+=1
  return '{'+s[start:j]+'}',j
 pos=0
 while True:
  k=tex.find('\\frac',pos)
  if k<0:break
  a,j=atom(tex,k+5);b,j=atom(tex,j);replace='\\frac'+a+b;tex=tex[:k]+replace+tex[j:];pos=k+len(replace)
 return tex
def formula(tex,note=''):
 tex=normalize(tex)
 b,w,h=u.math_svg(tex,17);key=hashlib.sha256(tex.encode()).hexdigest()[:12];EQUATIONS[key]={'tex':tex,'svg':b.decode()}
 return f'<div class="formula"><button class="formula-zoom" data-zoom aria-label="放大公式：{html.escape(note or tex,quote=True)}"><img class="math-display" src="{encoded(b)}" alt="{html.escape(tex,quote=True)}" width="{w:.2f}" height="{h:.2f}" style="width:{w:.2f}px" decoding="async"></button><small>{html.escape(note)}</small></div>'

def figure(key):
 if key in FIGURES:return FIGURES[key]
 fig,ax=plt.subplots(figsize=(8.4,3.7));fig.subplots_adjust(0.025,0.04,0.975,0.96)
 ax.set(xlim=(0,10),ylim=(0,4));ax.set_aspect('equal');ax.axis('off')
 def line(x,y,**kw):ax.plot(x,y,color=kw.pop('color',INK),lw=kw.pop('lw',2),**kw)
 def arrow(a,b,color=FORCE,**kw):ax.add_patch(FancyArrowPatch(a,b,arrowstyle='-|>',mutation_scale=15,color=color,lw=2,**kw))
 def label(x,y,s,color=INK):ax.text(x,y,s,fontproperties=fp,color=color,ha='center',va='center')
 def rect(x,y,w,h,fill=FILL):ax.add_patch(Rectangle((x,y),w,h,facecolor=fill,edgecolor=GREEN,lw=2))
 def circle(x,y,r):ax.add_patch(Circle((x,y),r,facecolor='white',edgecolor=GREEN,lw=2))
 def pin(x,y):ax.add_patch(Polygon([(x,y),(x-.25,y-.45),(x+.25,y-.45)],facecolor=FILL,edgecolor=INK,lw=1.5));line([x-.4,x+.4],[y-.5,y-.5],lw=1)
 def fixed(x,y1,y2):
  line([x,x],[y1,y2],lw=3)
  for yy in [y1+i*.2 for i in range(round((y2-y1)/.2)+1)]:line([x-.2,x],[yy-.15,yy],color=MUTED,lw=1)
 def axis():arrow((1,.8),(9.2,.8),MUTED);arrow((1,.8),(1,3.3),MUTED)
 def beam(y=2):rect(1.5,y-.1,7,.2)
 import numpy as np
 x=np.linspace(0,1,120)
 titles={
 'models':('外力平衡 → 內力 → 應力與變形','先決定分析對象，再選材料與幾何模型'),
 'force':('力的分解與力矩','橘色：作用力；綠色虛線：水平與鉛直分量'),
 'supports':('平面支承模型','鉸支承：兩反力；滾支承：法向反力；固定端：另有力矩'),
 'distributed':('分布負載與等效合力','矩形負載圖面積等於合力，作用於跨中'),
 'cut':('截面法求內力','切開後的一側：軸力、剪力與彎矩維持平衡'),
 'stress':('同一截面的正向與剪應力','正向應力垂直於面；剪應力沿著面'),
 'mohr':('莫爾應力圓','橫軸：正向應力；縱軸：剪應力；圓心水平位置為平均應力'),
 'traction':('斜截面上的應力向量','橘色：總應力向量；綠色：法向與切向分量'),
 'strain':('伸長與剪切變形','左：軸向伸長；右：直角改變；虛線表示原形'),
 'rosette':('0°／45°／90°應變花','各方向量到的是沿應變規軸線的正向應變'),
 'curve':('拉伸試驗的應力應變關係','線彈性 → 降伏與塑性 → 應變硬化 → 頸縮'),
 'plastic':('彈性完全塑性與卸載','實線：加載；虛線：彈性卸載；零應力處留下永久應變'),
 'pressure':('封閉薄壁圓筒的兩個膜應力','上、下方向：環向；左、右方向：軸向'),
 'axial':('軸向負載與分段伸長','各段內力、面積、長度及材料剛度須分別計算'),
 'thermal':('自由膨脹與受限膨脹','上：升溫可自由伸長；下：固定端反力造成壓縮'),
 'energy':('線彈性構件的應變能','負載與位移圖下的三角形面積即儲存能量'),
 'williot':('桿系小位移的投影','節點位移投影到各桿方向，得到該桿伸長量'),
 'centroid':('對稱面積的形心','兩條對稱軸的交點即面積形心'),
 'composite':('組合面積與孔洞','外部面積加總；孔洞的面積與一次矩需扣除'),
 'inertia':('平行軸定理','形心軸移到平行軸後，慣性矩增加面積乘距離平方'),
 'principal':('形心主軸與截面方向','主軸互相垂直，對主軸的面積慣性積為零'),
 'torsion':('圓軸扭轉與外緣變形','旋轉前後截面間的相對轉角沿長度累積'),
 'power':('旋轉軸的扭矩與功率','切向力造成扭矩；扭矩乘角速度得到功率'),
 'closed':('閉口與開口薄壁截面','左：連續剪力流；右：切開後抗扭剛度顯著下降'),
 'shear':('均布負載下的剪力與彎矩','上：剪力為直線；下：正彎矩為拋物線；兩端彎矩為零'),
 'bending':('正彎矩下的應力分布','上緣受壓、下緣受拉；中性軸上正向應力為零'),
 'compositebeam':('完全結合複合樑','界面應變連續；楊氏模數不同，正向應力不同'),
 'beamshear':('矩形樑的剪應力分布','自由表面為零，中性軸最大；曲線為拋物線'),
 'flow':('接合面剪力流','剪力流沿構件傳遞；每個接合件分攤一段長度'),
 'combined':('圓軸同時拉伸與扭轉','同一材料點的正向及剪應力必須一起分析'),
 'failure':('延性材料的等效應力比較','主應力空間內，Tresca與von Mises以不同準則判斷降伏'),
 'biaxial':('沿兩條主軸分解彎矩','截面兩個主軸方向的應力代數相加'),
 'deflection':('懸臂樑的撓曲線','虛線：未變形；實線：向下撓曲；固定端轉角為零'),
 'momentarea':('彎矩面積法的幾何量','陰影：彎矩除以剛度圖的面積；距離量至目標截面'),
 'redundant':('釋放冗力與變形相容','解除右支承後，以未知向上反力使右端位移回到零'),
 'castigliano':('虛設力求指定方向位移','先加入虛設力，對能量偏微分後再令虛設力為零'),
 'impact':('落下負載與彈性吸能','重物下降的位能轉為彈簧或構件的應變能'),
 'plastictorsion':('彈塑性圓軸的剪應力','中心彈性核心呈線性；外圈塑性區達剪降伏值'),
 'plasticbeam':('彎曲應力由彈性到全塑性','左：線性分布；右：拉壓區分別達降伏應力'),
 'stability':('平衡穩定性的三種情況','左：穩定；中：不穩定；右：中性平衡'),
 'buckling':('柱的端部約束與有效長度','左：鉸鉸；中：固定自由；右：固定固定')}
 title,caption=titles[key];label(5,3.75,title,GREEN)
 if key=='models':
  for i in range(3):rect(.8+i*3.2,1.5,2,1)
  arrow((2.9,2),(3.9,2),GREEN);arrow((6.1,2),(7.1,2),GREEN)
  for xx,s in [(1.8,'平衡'),(5,'內力'),(8.2,'變形')]:label(xx,1.05,s)
 elif key=='force':
  arrow((2,1),(8,3));line([2,8],[1,1],color=GREEN,ls='--');line([8,8],[1,3],color=GREEN,ls='--');circle(2,1,.07)
  label(5,3.15,'F',FORCE);label(5,.55,'Fx');label(8.6,2,'Fy');label(1.5,.55,'O')
 elif key=='supports':
  line([.8,3],[2.5,2.5]);pin(1.8,2.5);arrow((1.8,1),(1.8,1.8));arrow((.7,2.1),(1.4,2.1));
  line([4,6.2],[2.5,2.5]);pin(5,2.5);circle(4.88,1.9,.08);circle(5.12,1.9,.08);arrow((5,.9),(5,1.55))
  fixed(7.4,1.6,3);line([7.4,9.2],[2.5,2.5]);label(8.5,1.05,'力 + 力矩');label(1.8,.55,'鉸');label(5,.55,'滾')
 elif key=='distributed':
  rect(1,1.5,3,.2);pin(1.2,1.5);pin(3.8,1.5)
  for xx in np.linspace(1.2,3.8,7):arrow((xx,3),(xx,1.8))
  arrow((4.7,2.2),(5.5,2.2),GREEN);rect(6.2,1.5,2.8,.2);pin(6.4,1.5);pin(8.8,1.5);arrow((7.6,3),(7.6,1.8));label(2.5,.55,'分布負載');label(7.6,.55,'等效合力')
 elif key=='cut':
  rect(1.6,1.7,4.2,.6);fixed(1.6,1.2,2.8);line([5.8,5.8],[1.3,2.7],color=MUTED,ls='--');arrow((5.9,2),(7.4,2));arrow((6.2,1.5),(6.2,.8));ax.add_patch(Arc((6.4,2.7),1,1,theta1=0,theta2=150,color=FORCE,lw=2));arrow((6.0,3.0),(5.96,2.9));label(7.7,2,'N');label(6.2,.55,'V');label(7.3,3.15,'M')
 elif key=='stress':
  rect(3,1.2,3,1.7);arrow((6.1,2),(7.5,2));arrow((6.25,1.3),(6.25,2.8),GREEN);label(8.1,2,'正向');label(7.1,3.05,'剪切')
 elif key=='mohr':
  arrow((.8,1.9),(9,1.9),MUTED);arrow((2,.5),(2,3.25),MUTED);ax.add_patch(Circle((5.3,1.9),1.25,fill=False,edgecolor=GREEN,lw=2));line([5.3,6.3],[1.9,2.65],color=FORCE);circle(5.3,1.9,.04);label(8.7,1.45,'σ');label(1.6,3.25,'τ');label(5.3,1.5,'C');label(6.5,2.9,'R')
 elif key=='traction':
  line([2,6],[1,3],lw=3);circle(4,2,.05);arrow((4,2),(7,2.7));arrow((4,2),(4.8,0.6),GREEN);arrow((4,2),(6.2,3.1),GREEN);label(7.5,2.8,'t');label(5.2,.5,'法向');label(6.8,3.15,'切向')
 elif key=='strain':
  ax.add_patch(Rectangle((.8,1.3),2,1.2,fill=False,edgecolor=MUTED,ls='--'));rect(.8,1.3,2.8,1.2);arrow((3.7,1.9),(4.5,1.9));ax.add_patch(Rectangle((6,1.3),1.5,1.2,fill=False,edgecolor=MUTED,ls='--'));ax.add_patch(Polygon([(6,1.3),(7.5,1.3),(8,2.5),(6.5,2.5)],facecolor=FILL,edgecolor=GREEN,lw=2));label(2.1,.65,'長度改變');label(7,.65,'角度改變')
 elif key=='rosette':
  circle(4.5,1.6,.12)
  for a in [0,np.pi/4,np.pi/2]:
   arrow((4.5,1.6),(4.5+2.1*np.cos(a),1.6+1.5*np.sin(a)),GREEN)
  label(7.1,1.55,'0°');label(6.7,3.05,'45°');label(4.4,3.35,'90°')
 elif key in ('curve','plastic','energy'):
  axis();label(9.2,.4,'位移' if key=='energy' else '應變');label(.65,3.45,'力' if key=='energy' else '應力')
  if key=='curve':line([1,2.3,3.8,5.7,7,8],[.8,2.15,2.2,2.8,2.85,2.35],color=GREEN)
  if key=='plastic':line([1,3,7.7],[.8,2.7,2.7],color=GREEN);line([7.7,5.7],[2.7,.8],color=FORCE,ls='--');label(5.7,.35,'永久應變')
  if key=='energy':ax.add_patch(Polygon([(1,.8),(8,.8),(8,3)],facecolor=FILL,edgecolor=GREEN,lw=2));label(5.5,1.25,'U')
 elif key=='pressure':
  rect(2.6,1.2,4.8,1.6);ax.add_patch(Ellipse((2.6,2),.7,1.6,fc='white',ec=GREEN,lw=2));ax.add_patch(Arc((7.4,2),.7,1.6,theta1=270,theta2=90,color=GREEN,lw=2));arrow((4,2.8),(4,3.3));arrow((6,1.2),(6,.7));arrow((7.8,2),(9,2));arrow((2.1,2),(1,2));label(5,3.35,'環向');label(8.7,1.4,'軸向');label(5,1.9,'內壓 p')
 elif key=='axial':
  rect(2,1.5,3,1);rect(5,1.7,2.5,.6);arrow((1.8,2),(.7,2));arrow((7.7,2),(9,2));label(3.5,.9,'第一段');label(6.2,.9,'第二段')
 elif key=='thermal':
  fixed(1.5,2.4,3.1);rect(1.5,2.65,5,.3);line([7,7],[2.3,3.2],ls='--',color=FORCE);arrow((6.6,2.8),(7,2.8));fixed(1.5,1,1.7);rect(1.5,1.25,5,.3);fixed(6.5,1,1.7);arrow((.5,1.4),(1.2,1.4));arrow((7.5,1.4),(6.8,1.4));label(8.2,2.8,'自由');label(8.2,1.4,'受限')
 elif key=='williot':
  line([1.5,4.5,7.5],[2.8,1,2.8],lw=3,color=GREEN);pin(1.5,2.8);pin(7.5,2.8);arrow((4.5,1),(5.3,.55));line([1.5,5.3,7.5],[2.8,.55,2.8],ls='--',color=FORCE);label(4.5,1.5,'B');label(6.2,.55,'位移')
 elif key in ('centroid','composite','inertia','principal','biaxial'):
  rect(3,1,4,2);line([2,8],[2,2],ls='--',color=MUTED);line([5,5],[.6,3.4],ls='--',color=MUTED);circle(5,2,.045)
  if key=='composite':circle(5.9,2,.55);label(8.2,2,'孔洞')
  elif key=='inertia':line([2,8],[.65,.65],color=FORCE);arrow((8,0.7),(8,2),MUTED);label(8.45,1.35,'d');label(2,2.35,'形心軸')
  elif key=='principal':line([2.7,7.3],[.65,3.35],color=FORCE);line([4.1,5.9],[3.35,.65],color=FORCE)
  elif key=='biaxial':arrow((5,2),(8,2),FORCE);arrow((5,2),(5,3.2),GREEN);label(8.4,2,'Mz');label(5.6,3.2,'My')
  else:label(5,.55,'形心')
 elif key in ('torsion','power','combined'):
  rect(2,1.3,5.5,1.4);ax.add_patch(Ellipse((7.5,2),.9,1.4,fc=FILL,ec=GREEN,lw=2));fixed(2,1,3);line([2.2,7.4],[2.4,1.65],color=FORCE);ax.add_patch(Arc((8,2),1.7,1.9,theta1=200,theta2=470,color=FORCE,lw=2));arrow((8.3,2.8),(8.6,2.6));label(9,2.8,'T')
  if key=='combined':arrow((8.1,2),(9.3,2));label(9.25,1.45,'N')
  if key=='power':label(5,3.15,'角速度 ω')
 elif key=='closed':
  rect(1,1.1,2.6,1.9,fill='white');rect(1.15,1.25,2.3,1.6,fill='white');arrow((1.4,3.15),(3.2,3.15));arrow((3.8,2.9),(3.8,1.4));line([6.2,6.2,8.8,8.8],[2.7,1.1,1.1,3],color=GREEN,lw=5);line([6.2,7.5],[3,3],color=GREEN,lw=5);line([7.9,8.8],[3,3],color=GREEN,lw=5);label(2.3,.55,'閉口');label(7.5,.55,'開口')
 elif key=='shear':
  line([1,9],[2.65,2.65],color=MUTED,lw=1);line([1,5,9],[3.25,2.65,2.05],color=FORCE);line([1,9],[.65,.65],color=MUTED,lw=1);line(1+8*x,.65+4*x*(1-x),color=GREEN);label(.5,2.65,'V');label(.5,1,'M');label(5,.25,'跨中')
 elif key in ('bending','beamshear','compositebeam','plasticbeam'):
  rect(1.6,1,1.3,2);line([1,3.5],[2,2],color=MUTED,ls='--')
  if key=='compositebeam':rect(1.6,2.2,1.3,.8,fill='#efddca');line([5,6,6,7],[3,2.2,2.2,1],color=FORCE);line([5.8,5.8],[.8,3.2],color=MUTED,ls='--')
  elif key=='beamshear':y=np.linspace(1,3,100);line(5+1.5*(1-(y-2)**2),y,color=FORCE);line([5,5],[.8,3.2],color=MUTED,ls='--')
  else:
   line([5,7],[3,1],color=FORCE);line([6,6],[.8,3.2],color=MUTED,ls='--');arrow((6,3),(5.1,3));arrow((6,1),(7.2,1));
   if key=='plasticbeam':line([8.3,8.3,9.1,9.1],[3,2,2,1],color=GREEN)
  label(2.25,.55,'截面');label(6.3,.55,'應力分布')
 elif key=='flow':
  rect(1,2,8,.7);rect(1,1.3,8,.7)
  for xx in [2,4,6,8]:circle(xx,2,.08)
  for xx in [2,4,6,8]:arrow((xx-.3,3.2),(xx+.4,3.2))
  label(5,.65,'等間距接合件')
 elif key=='failure':
  arrow((2,2),(8.8,2),MUTED);arrow((5,.5),(5,3.4),MUTED);t=np.linspace(0,2*np.pi,180);line(5+1.5*(np.cos(t)+np.sin(t)/np.sqrt(3)),2+np.cos(t)-np.sin(t)/np.sqrt(3),color=GREEN);ax.add_patch(Polygon([(3.5,2),(3.5,1),(5,1),(6.5,2),(6.5,3),(5,3)],fill=False,edgecolor=FORCE,lw=2));label(8.8,1.55,'σ1');label(5.5,3.35,'σ2')
 elif key in ('deflection','redundant','castigliano'):
  fixed(1.5,.7,3);line([1.5,8.5],[2.7,2.7],ls='--',color=MUTED);line(1.5+7*x,2.7-1.5*x*x*(3-x)/2,color=GREEN);arrow((8.5,3.35),(8.5,1.45));label(9.1,3.15,'Q' if key=='castigliano' else 'P')
  if key=='redundant':pin(8.5,2.7);arrow((8.5,.55),(8.5,1.15),GREEN);label(7.3,.55,'冗力')
 elif key=='momentarea':
  line([1,9],[1,1],color=MUTED);ax.add_patch(Polygon([(1,1),(9,1),(9,3)],facecolor=FILL,edgecolor=GREEN,lw=2));line([6.33,6.33],[.6,2.4],ls='--',color=MUTED);arrow((6.4,.6),(9,.6),MUTED);label(3,2.5,'M / EI');label(9.2,.9,'B')
 elif key=='impact':
  rect(4.3,2.8,1.4,.6);arrow((5,2.6),(5,1.9));line([3.5,6.5],[1.7,1.7],lw=3);line([5,4.6,5.4,4.6,5.4,5],[1.7,1.5,1.25,1,.75,.5],color=GREEN);line([3.5,6.5],[.5,.5]);label(7,3,'重量 W');label(7,1.1,'等效剛度 k')
 elif key=='plastictorsion':
  circle(2.5,2,1.15);ax.add_patch(Circle((2.5,2),.65,fc=FILL,ec=GREEN,ls='--'));line([5.2,5.2],[1,3],color=MUTED);line([5.2,9],[1,1],color=MUTED);line([5.2,7,9],[1,2.7,2.7],color=FORCE);label(2.5,.4,'彈性核心與塑性外環');label(8,3.1,'剪降伏強度')
 elif key=='stability':
  q=np.linspace(-1,1,80)
  for k in range(3):
   xx=1.8+k*3.2; yy=1.3+q*q*.9 if k==0 else 2.2-q*q*.9 if k==1 else np.ones_like(q)*1.5
   line(xx+q,yy,color=GREEN);circle(xx,(1.3 if k==0 else 2.2 if k==1 else 1.5)+.17,.17)
  label(1.8,.65,'穩定');label(5,.65,'不穩定');label(8.2,.65,'中性')
 elif key=='buckling':
  for k in range(3):
   xx=1.8+k*3.2;shape=np.sin(np.pi*x) if k==0 else 1-np.cos(np.pi*x/2) if k==1 else (1-np.cos(2*np.pi*x))/2;line([xx,xx],[.9,3],color=MUTED,ls='--');line(xx+.35*shape,.9+2.1*x,color=GREEN);arrow((xx,3.5),(xx,3.05));
   if k==0:pin(xx,.9);pin(xx,3)
   else:line([xx-.5,xx+.5],[.8,.8],lw=3)
   if k==2:line([xx-.5,xx+.5],[3,3],lw=3)
   label(xx,.3,['K = 1','K = 2','K = 0.5'][k])
 out=BytesIO();fig.savefig(out,format='svg',facecolor='white',metadata={'Date':None});plt.close(fig)
 svg=etree.fromstring(out.getvalue());assert not svg.xpath('//*[local-name()="text"]')
 b=etree.tostring(svg);preview=ROOT.parent/'tmp/materials/redrawn';preview.mkdir(parents=True,exist_ok=True);(preview/(key+'.svg')).write_bytes(b);FIGURES[key]={'bytes':b,'caption':caption,'title':title};return FIGURES[key]

ICONS=[
 '<path d="M4 19V5m0 14h16M6 16L18 6m-6 0h6v6"/>',
 '<rect x="6" y="6" width="12" height="12"/><path d="M2 12h4m12 0h4M12 2v4m0 12v4"/>',
 '<path d="M4 19V5m0 14h16M6 16l5-6 5 1 4-7"/>',
 '<circle cx="12" cy="12" r="8"/><path d="M12 4v8l5 3"/>',
 '<path d="M4 8h16M4 16h16M7 8l-2 4 2 4m10-8 2 4-2 4"/>'
]
def icon(i):return '<svg viewBox="0 0 24 24" aria-hidden="true">'+ICONS[i%len(ICONS)]+'</svg>'
def source_pages(n,c):
 d=pymupdf.open(source_path(n));pages=[]
 for i,s in enumerate(c['sections'],1):
  pat=re.compile(rf'(?m)^\s*{n}\s*[-－]\s*{i}[.．\s]')
  found=next((j+1 for j,p in enumerate(d) if pat.search(p.get_text())),None)
  assert found,(n,i)
  pages.append(found)
 return len(d),pages

if __name__=='__main__':
 out=ROOT/'assets/materials';out.mkdir(parents=True,exist_ok=True)
 for n,c in enumerate(data.CHAPTERS,1):
  name=f'materials-ch{n:02}.html';pdf=f'assets/materials/materials-ch{n:02}.pdf';count,starts=source_pages(n,c)
  if source_path(n).resolve()!=(ROOT/pdf).resolve():shutil.copyfile(source_path(n),ROOT/pdf)
  entries=[(f'sec{i}',f'{n}-{i}',s['title']) for i,s in enumerate(c['sections'],1)]+[('ex','範例','教學例題'),('source','原文','完整原講義')]
  tabs=''.join(f'<a class="tab" id="tab-{id}" href="#{id}" role="tab" aria-controls="{id}" aria-selected="{"true" if j==0 else "false"}"><span class="ic">{icon(j)}</span><span class="tx"><span class="no">{no}</span><span class="nm">{html.escape(title)}</span></span></a>' for j,(id,no,title) in enumerate(entries))
  body=[]
  for i,s in enumerate(c['sections'],1):
   text=''.join('<p>'+html.escape(p)+'</p>' for p in s['text']);eqs=''.join(formula(*eq) for eq in s['eqs']);points=''.join('<li>'+html.escape(p)+'</li>' for p in s['points'])
   drawing=''
   if s['fig']:
    f=figure(s['fig']);drawing=f'<figure class="lecture-figure"><button class="figure-zoom" data-zoom aria-label="放大：{html.escape(f["title"])}"><img src="{encoded(f["bytes"])}" width="806" height="355" alt="{html.escape(f["caption"])}" decoding="async"></button><figcaption>重繪示意圖｜{html.escape(f["caption"])}。點圖可放大。</figcaption></figure>'
   note=f'<p class="callout warn">{html.escape(s["note"])}</p>' if s['note'] else ''
   body.append(f'<section id="sec{i}" aria-labelledby="h-sec{i}"><h2 id="h-sec{i}"><span class="no">{n}-{i}</span>{html.escape(s["title"])}</h2><p class="source-ref"><a href="{pdf}#page={starts[i-1]}" target="_blank" rel="noopener">對照原講義第 {starts[i-1]} 頁 ↗</a></p>{text}{drawing}{eqs}<h3>解題順序與檢查</h3><ul>{points}</ul>{note}</section>')
  examples=[]
  for i,e in enumerate(c['examples'],1):
   steps=''.join('<li>'+html.escape(s)+'</li>' for s in e['steps']);eqs=''.join(formula(*eq) for eq in e['eqs'])
   examples.append(f'<article class="example"><h3>例 {n}-{i}　{html.escape(e["title"])}</h3><p>{html.escape(e["q"])}</p><details class="worked-solution"><summary><span class="qn">解</span><span>展開完整計算</span></summary><div class="solution"><ol>{steps}</ol>{eqs}<p class="answer">{html.escape(e["answer"])}</p></div></details></article>')
  body.append('<section id="ex" aria-labelledby="h-ex"><h2 id="h-ex"><span class="no">EX</span>教學例題</h2><p class="source-ref">以下為依本章觀念編寫並重新計算的教學例題。原講義所有例題、考題與解析保留於「完整原講義」。</p>'+''.join(examples)+'</section>')
  body.append(f'<section id="source" aria-labelledby="h-source"><h2 id="h-source"><span class="no">PDF</span>完整原講義</h2><p>本章原講義共 {count} 頁，保留全部圖題、例題、考題與推導。網頁各節提供重點講解、公式圖檔及重繪示意圖，可搭配原文查閱。</p><p><a class="source-open" href="{pdf}" target="_blank" rel="noopener">另開完整原講義 ↗</a> <a class="source-open" href="{pdf}" download>下載本章 PDF ↓</a></p><div class="pdf-reader" data-pdf="{pdf}"><p>切換至此節後載入原講義。手機若未顯示預覽，請使用上方「另開完整原講義」。</p></div></section>')
  prev=f'<a href="materials-ch{n-1:02}.html">← 上一章</a>' if n>1 else '<span></span>'
  nxt=f'<a href="materials-ch{n+1:02}.html">下一章 →</a>' if n<15 else '<span></span>'
  nav=f'<nav class="chapter-nav" aria-label="章節導覽">{prev}<a href="mechanics-of-materials.html#ch-h">材料力學章節總覽</a>{nxt}</nav>'
  result=f'''<!doctype html>
<html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><title>材料力學 第{n}章 {c['title']}｜知識動力場</title><meta name="description" content="{html.escape(c['lede'],quote=True)}"><link rel="stylesheet" href="assets/chapter.css"><link rel="stylesheet" href="assets/dynamics-chapter.css"><link rel="stylesheet" href="assets/materials-course.css?v=purple-20261015"></head><body>
<header class="hero"><div><div class="crumb"><a href="mechanics-of-materials.html">材料力學</a> / CH {n:02}</div><h1>{c['title']}<small>{c['en']}</small></h1><p class="lede">{c['lede']}</p><div class="meta"><span>{len(c['sections'])} 節</span><span>{len(c['examples'])} 道教學例題</span><span>完整原講義 {count} 頁</span></div></div><div class="hero-art" aria-hidden="true">{icon(n)}</div></header>
<div class="wrap"><nav class="tabs" role="tablist" aria-label="本章各節" aria-orientation="vertical"><p class="tabs-label">SECTIONS</p>{tabs}</nav><main>{''.join(body)}{nav}</main></div><dialog id="figure-dialog" aria-label="放大示意圖"><button class="zoom-close" autofocus>關閉 ×</button><img alt=""><p></p></dialog><script src="assets/chapter.js"></script><script src="assets/materials-course.js"></script></body></html>'''
  (ROOT/name).write_text(result)
  manifest.append({'chapter':n,'file':name,'title':c['title'],'sections':len(c['sections']),'examples':len(c['examples']),'source_pages':count,'section_start_pages':starts,'formulas':sum(len(s['eqs']) for s in c['sections'])+sum(len(e['eqs']) for e in c['examples']),'figures':sum(bool(s['fig']) for s in c['sections'])})
  print(n,c['title'],len(c['sections']),'sections',count,'source pages')

 # Turn existing chapter cards into direct links, matching Dynamics.
 from lxml import html as LH
 page=ROOT/'mechanics-of-materials.html';doc=LH.fromstring(page.read_text());cards=doc.xpath('//*[contains(concat(" ",normalize-space(@class)," ")," ch ")]');assert len(cards)==15
 for n,(card,c,m) in enumerate(zip(cards,data.CHAPTERS,manifest),1):
  card.tag='a';card.set('class','ch');card.set('href',m['file'])
  for pill in card.xpath('.//*[contains(concat(" ",normalize-space(@class)," ")," pill ")]'):pill.getparent().remove(pill)
  h=card.find('h3');h.clear();h.text=c['title']
  meta=card.xpath('.//*[@class="meta"]')[0];meta.clear();meta.set('class','meta')
  for text in [f'{m["sections"]} 節',f'{m["examples"]} 道教學例題',f'原講義 {m["source_pages"]} 頁']:LH.etree.SubElement(meta,'span').text=text
 facts=doc.xpath('//*[@class="facts"]/div');facts[1].find('b').text=str(sum(m['sections'] for m in manifest));facts[2].find('b').text='30';facts[2].find('span').text='道教學例題'
 lede=doc.xpath('//*[@class="lede"]')[0];lede.text='靜力學算出外力與反力，材料力學接著問：構件裡面受多大的力、會變形多少、會不會壞。依完整十五章研所講義編排，從應力與應變，逐步分析軸向、扭轉、彎曲及組合負載，最後進入能量法、塑性與柱的挫曲。各章提供公式圖檔、重繪示意圖與教學例題，並保留完整原講義。'
 for e in doc.xpath('//p'):
  if e.text=='依主題分組，講義陸續上線':e.text='十五章完整上線，點選章節進入閱讀'
 head=doc.find('head')
 if not head.xpath('./link[@href="assets/materials-course.css?v=purple-20261015"]'):LH.etree.SubElement(head,'link',rel='stylesheet',href='assets/materials-course.css?v=purple-20261015')
 page.write_text('<!doctype html>\n'+LH.tostring(doc,encoding='unicode')+'\n')
 (ROOT.parent/'output').mkdir(parents=True,exist_ok=True)
 (ROOT.parent/'output/materials-course-manifest.json').write_text(json.dumps({'chapters':manifest,'totals':{'chapters':15,'sections':sum(m['sections'] for m in manifest),'examples':30,'source_pages':sum(m['source_pages'] for m in manifest),'formulas':sum(m['formulas'] for m in manifest),'figures':sum(m['figures'] for m in manifest)}},ensure_ascii=False,indent=2))
 print('Built',len(FIGURES),'unique figures;',len(EQUATIONS),'unique formula images')
