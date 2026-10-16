#!/usr/bin/env python3
"""Build Statics CH3–6 from editable notes and preserve the complete source PDFs.
Uses the Materials builder's outlined math renderer and shared chapter UI.
PYTHONPATH=/private/tmp/dynamics-math-render:/private/tmp/materials-pdf python3 tools/build-statics-completion.py
"""
from pathlib import Path
from io import BytesIO
import importlib.util,html,json,re,shutil
ROOT=Path(__file__).resolve().parents[1]
def module(name,file):
 s=importlib.util.spec_from_file_location(name,Path(__file__).with_name(file));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
m=module('course_page_helpers','build-materials-course.py');data=module('statics_notes','statics-completion-data.py')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle,Circle,Polygon,Arc,FancyArrowPatch
from lxml import etree,html as LH
import numpy as np,pymupdf
BLUE='#0e4a8a';INK='#152231';FORCE='#c2410c';MUTED='#566677';FILL='#e2ebf6'
assets=ROOT/'assets/statics-figures';assets.mkdir(exist_ok=True)
pdfs=ROOT/'assets/statics-lectures';pdfs.mkdir(exist_ok=True)
figures={};manifest=[]
ICONS={
 'truss':'<path d="M3 19 12 4l9 15H3Zm0 0h18M7.5 11.5l4.5 7.5 4.5-7.5"/>',
 'joint':'<circle cx="12" cy="12" r="2"/><path d="m3 5 7.5 5.5M14 12h7M12 14v7M3 12h7"/>',
 'frame':'<path d="M4 20V8h15V3M2 20h5M16 3h6M12 3v7m-2-2 2 2 2-2"/>',
 'friction':'<path d="M3 19h18M2 12h5m-2-2 2 2-2 2m12-2h5m-2-2 2 2-2 2"/><rect x="8" y="7" width="8" height="10"/>',
 'angle':'<path d="M4 20V4m0 16h16M4 20 20 7M4 14a6 6 0 0 1 4 1"/>',
 'centroid':'<rect x="5" y="5" width="14" height="14"/><path d="M12 2v20M2 12h20"/>',
 'composite':'<path d="M4 4h16v16H4z"/><circle cx="15" cy="9" r="3"/>',
 'axes':'<path d="M3 20h18M12 3v19"/><rect x="6" y="7" width="12" height="10"/>',
 'section':'<path d="M4 4h16v4h-6v12h-4V8H4zM3 13h18"/>',
 'virtual':'<path d="M2 12h20m-10 0-3 7h6l-3-7ZM5 3v6m-2-2 2 2 2-2M19 3v6m-2-2 2 2 2-2"/>',
 'potential':'<path d="M3 3v18h18M5 7q7 20 15 0"/>',
 'example':'<path d="M9 18h6m-5 3h4M8 14a6 6 0 1 1 8 0l-1 3H9l-1-3Z"/>',
 'quiz':'<circle cx="12" cy="12" r="9"/><path d="M9 8a3 3 0 0 1 6 0c0 2-3 2-3 5m0 3v1"/>',
 'source':'<path d="M5 3h10l4 4v14H5V3Zm10 0v5h4M8 12h8m-8 4h8"/>'}
SECTION_ICONS={3:['truss','joint','frame'],4:['friction','friction','angle'],5:['centroid','composite','axes','section'],6:['virtual','potential']}
def icon(key):return '<svg viewBox="0 0 24 24" aria-hidden="true">'+ICONS[key]+'</svg>'
def picture(key):
 if key in figures:return figures[key]
 fig,ax=plt.subplots(figsize=(8.4,3.7));fig.subplots_adjust(.025,.04,.975,.96)
 ax.set(xlim=(0,10),ylim=(0,4));ax.set_aspect('equal');ax.axis('off')
 def line(xs,ys,**kw):ax.plot(xs,ys,color=kw.pop('color',INK),lw=kw.pop('lw',2),**kw)
 def arrow(a,b,color=FORCE):ax.add_patch(FancyArrowPatch(a,b,arrowstyle='-|>',mutation_scale=15,color=color,lw=2))
 def label(x,y,text,color=INK):ax.text(x,y,text,fontproperties=m.fp,color=color,ha='center',va='center')
 def rect(x,y,w,h,fill=FILL):ax.add_patch(Rectangle((x,y),w,h,fc=fill,ec=BLUE,lw=2))
 def point(x,y):ax.add_patch(Circle((x,y),.055,fc='white',ec=BLUE,lw=1.5))
 def pin(x,y):ax.add_patch(Polygon([(x,y),(x-.2,y-.35),(x+.2,y-.35)],fc=FILL,ec=INK,lw=1.3))
 def roller(x,y):
  pin(x,y)
  for xx in [x-.1,x+.1]:ax.add_patch(Circle((xx,y-.42),.06,fc='white',ec=INK,lw=1))
  ground(x-.3,x+.3,y-.5)
 def ground(x1,x2,y):line([x1,x2],[y,y],color=MUTED,lw=1)
 def member(a,b,color=BLUE):line([a[0],b[0]],[a[1],b[1]],color=color,lw=3);point(*a);point(*b)
 def spring(a,b,y):
  x=np.linspace(a,b,10);ys=[y if i in [0,9] else y+(.12 if i%2 else -.12) for i in range(10)];line(x,ys,color=BLUE)
 titles={
 'truss':('簡單桁架與節點負載','桿件在端點鉸接；外力施加於節點'),
 'twoforce':('二力構件：拉力與壓力','左：兩端拉離構件；右：兩端推向構件'),
 'joint':('節點法的桿力假設','先將所有未知桿力假設拉離節點，負值再改判為壓力'),
 'zero':('零力構件的兩個基本規則','無節點外力時：左圖兩桿皆零；右圖不共線第三桿為零'),
 'section':('截面法與力矩中心','選擇截線及矩心，消去不需要的未知桿力'),
 'frame':('構架的整體與構件自由體圖','二力連桿沿軸傳力；承載橫桿則承受多個外力'),
 'lever':('機具的力臂與力放大','關鍵是作用線至轉銷的垂直距離'),
 'triangle-example':('三角桁架｜教學例3-1','跨度6 m、高4 m；斜桿長5 m；頂點向下10 kN'),
 'section-example':('截開底弦與斜桿｜教學例3-3','底部跨度8 m、高3 m；中點向下12 kN；虛線為截線'),
 'frame-example':('二力連桿與承載橫桿｜教學例3-4','橫桿3 m，6 kN負載距左端1 m，右端連桿鉛直'),
 'friction-curve':('靜摩擦的調整與動摩擦','上升段：靜止時隨所需力調整；極限後改採動摩擦'),
 'friction-block':('水平物塊的自由體圖','橘色向右：拉力；藍色向左：摩擦；正向力垂直接觸面'),
 'tipping':('滑動與傾倒的兩種門檻','水平力增加時，地面總反力的作用點會向底邊移動'),
 'ladder':('光滑牆面與粗糙地面','牆只提供法向力；梯腳同時有法向力與摩擦力'),
 'ladder-example':('梯子平衡｜教學例4-3','梯腳距牆3 m、梯頂高4 m、梯重200 N作用於中點'),
 'incline':('斜面物塊與摩擦方向','重力向下；法向力垂直斜面；摩擦依滑動趨勢決定'),
 'friction-angle':('摩擦角與接觸總反力','總反力位於法向與切向反力合成的方向'),
 'hanging':('水平物塊連到懸掛重物','輕繩與光滑固定滑輪使繩張力相同'),
 'centroid':('對稱性與面積形心','兩條對稱軸交點即形心；密度不均時質心可能不同'),
 'composite':('挖孔面積的形心','孔洞的面積與一次矩都要扣除'),
 'semicircle':('半圓弧線與半圓薄板','同半徑下，線長加權的形心比面積加權更高'),
 'l-section':('L形面積的拆分','底板與左直板不重疊；圓點標記為教學例的形心'),
 'inertia':('平行軸定理的軸距','虛線為形心軸；另一條平行軸距離為d'),
 't-section':('T形截面的共同形心軸','上翼板100×20 mm，腹板20×80 mm；總高100 mm'),
 'hollow':('同心中空圓截面','內圓與外圓形心相同，孔洞慣性矩直接扣除'),
 'section-modulus':('最外緣距離與截面係數','不對稱截面須分別使用上、下緣距離'),
 'virtual-rod':('光滑牆角桿的虛位移','下端朝牆水平力與桿重作虛功；光滑法向反力不作虛功'),
 'pulley':('單動滑輪的力與位移','兩段繩支承負載；自由端拉出長度是負載上升量的兩倍'),
 'potential':('位能與穩定性','左：最小值穩定；中：最大值不穩定；右：常數位能中性'),
 'rod-spring':('桿與彈簧的平衡位能','教學例：30°為局部最大值；90°為可行範圍的穩定位置')}
 title,caption=titles[key];label(5,3.75,title,BLUE)
 if key in ('truss','triangle-example'):
  A=(3.2,.7);B=(6.8,.7);C=(5,3.1)
  for a,b in [(A,B),(A,C),(B,C)]:member(a,b)
  pin(*A);roller(*B);arrow((5,3.55),(5,3.1));label(2.8,.5,'A');label(7.2,.5,'B');label(5,2.7,'C');label(6.3,3.35,'10 kN' if key.endswith('example') else 'P',FORCE)
 elif key=='twoforce':
  rect(1.5,1.7,2.2,.5);arrow((1.4,1.95),(.5,1.95));arrow((3.8,1.95),(4.7,1.95));rect(6.2,1.7,2.2,.5);arrow((5.2,1.95),(6.1,1.95));arrow((9.5,1.95),(8.5,1.95));label(2.6,1.1,'拉');label(7.3,1.1,'壓')
 elif key=='joint':
  point(5,1.4)
  for xy in [(2,1.4),(7.5,1.4),(3.5,3.05)]:arrow((5,1.4),xy,BLUE)
  arrow((5,1.2),(5,.5));label(1.5,1.4,'N1');label(8,1.4,'N2');label(3,3.2,'N3');label(5.6,.5,'P')
 elif key=='zero':
  for a,b in [((1,1),(2.5,2.6)),((2.5,2.6),(4,1))]:member(a,b)
  point(2.5,2.6);label(2.5,.55,'兩桿皆零')
  member((5.5,1.5),(9,1.5));member((7.2,1.5),(7.2,2.9),FORCE);label(7.2,.55,'第三桿為零')
 elif key in ('section','section-example'):
  A=(2.4,.8);B=(5,.8);C=(7.6,.8);D=(5,2.75)
  for a,b in [(A,B),(B,C),(A,D),(D,C),(B,D)]:member(a,b)
  pin(*A);roller(*C);line([3.7,3.7],[.4,3.2],color=FORCE,ls='--');arrow((5,.7),(5,.05));label(2,.4,'A');label(8,.4,'C');label(5,3.1,'D');label(6,.35,'12 kN' if key.endswith('example') else 'P',FORCE)
 elif key in ('frame','frame-example'):
  A=(1.5,1.2);B=(8,1.2);C=(8,3.1);member(A,B);member(B,C);pin(*A);point(*C);ground(7.5,8.5,3.2);arrow((3.65,2.7),(3.65,1.3));label(1.1,.6,'A');label(8.5,1.2,'B');label(8.5,3.1,'C');label(3.65,3,'6 kN' if key.endswith('example') else 'P',FORCE)
 elif key=='lever':
  line([1,8.5],[1.4,1.4],color=BLUE,lw=4);pin(6.6,1.4);arrow((1.6,2.9),(1.6,1.5));arrow((8.1,2.9),(8.1,1.5));label(1.1,2.9,'P');label(8.65,2.9,'F');label(4.5,.6,'轉銷')
 elif key=='friction-curve':
  arrow((1,.8),(9,.8),MUTED);arrow((1,.8),(1,3.3),MUTED);line([1,5],[.8,3],color=BLUE);line([5,5,8.5],[3,2.2,2.2],color=FORCE);label(.5,3.35,'摩擦力');label(8.6,.35,'外力');label(4.5,3.35,'靜摩擦上限')
 elif key=='friction-block':
  rect(3.3,1.25,3,1.3);ground(1,9,1.2);arrow((6.5,1.9),(8.3,1.9));arrow((3.1,1.35),(1.5,1.35),BLUE);arrow((4.8,2.7),(4.8,3.3),BLUE);arrow((4.8,1.1),(4.8,.45));label(8.6,1.9,'P');label(1.3,1.8,'F');label(5.4,3.1,'N');label(5.4,.45,'W')
 elif key=='tipping':
  rect(3.5,.85,2,2.2);ground(1,8.8,.8);arrow((1.7,2.7),(3.3,2.7));arrow((4.5,1.9),(4.5,1.1));arrow((5.4,.2),(5.4,.8),BLUE);point(5.5,.85);label(1.4,2.7,'P');label(4.9,1.75,'W');label(6.9,.7,'臨界底邊')
 elif key in ('ladder','ladder-example','virtual-rod'):
  xb=5.9 if key=='virtual-rod' else 5.3;xg=(3.5+xb)/2;line([3.5,3.5],[.7,3.4],color=MUTED);ground(2.8,8,.7);line([3.5,xb],[3.1,.7],color=BLUE,lw=4);arrow((3.7,3.1),(4.7,3.1),BLUE);arrow((xg,1.9),(xg,1.05));arrow((xb,.75),(xb,1.65),BLUE);arrow((xb-.2,.7),(xb-1.3,.7),FORCE);label(3,3.1,'B');label(xb+.5,.65,'A');label(xg-.6,1.3,'W');label(xb-1.3,.3,'P' if key=='virtual-rod' else '摩擦')
 elif key=='incline':
  line([1,9],[.8,3],color=MUTED);p=np.array([[3.8,1.57],[5.7,2.09],[5.42,3.05],[3.52,2.53]]);ax.add_patch(Polygon(p,fc=FILL,ec=BLUE,lw=2));arrow((4.7,2.3),(4.7,1));arrow((4.5,2.5),(4.2,3.45),BLUE);arrow((5.9,2.3),(7.2,2.66));label(5.25,.95,'W');label(3.65,3.3,'N');label(7.7,2.8,'P')
 elif key=='friction-angle':
  arrow((3,1),(3,3.2),BLUE);arrow((3,1),(7,1),BLUE);arrow((3,1),(7,3.2));ax.add_patch(Arc((3,1),1.6,1.6,theta1=29,theta2=90,ec=MUTED));label(2.5,3.2,'N');label(7.3,.7,'F');label(7.4,3.3,'R');label(3.9,2.1,'φ')
 elif key=='hanging':
  rect(1.8,2.1,2.3,.8);line([1,6.6],[2.1,2.1],color=MUTED);line([6.6,6.6],[2.1,.6],color=MUTED);ax.add_patch(Circle((6.7,2.5),.35,fc='white',ec=BLUE,lw=2));line([4.1,6.7],[2.85,2.85],color=BLUE);line([7.05,7.05],[2.5,1.35],color=BLUE);rect(6.65,.65,.8,.7);label(3,.9,'A：60 kg');label(8.3,.9,'B：m')
 elif key in ('centroid','composite','inertia'):
  rect(3,1,4,2);line([2,8],[2,2],color=MUTED,ls='--');line([5,5],[.55,3.35],color=MUTED,ls='--');point(5,2)
  if key=='composite':ax.add_patch(Circle((5.8,2),.55,fc='white',ec=BLUE,lw=2));label(8,2,'孔洞')
  elif key=='inertia':line([2,8],[.65,.65],color=FORCE);arrow((8,.7),(8,2),MUTED);label(8.5,1.3,'d')
  else:label(5,.3,'形心')
 elif key=='semicircle':
  t=np.linspace(0,np.pi,120)
  for xx,filled in [(2.5,False),(7.5,True)]:
   if filled:ax.add_patch(Polygon(list(zip(xx+1.4*np.cos(t),1+1.4*np.sin(t))),fc=FILL,ec=BLUE,lw=2))
   else:line(xx+1.4*np.cos(t),1+1.4*np.sin(t),color=BLUE,lw=3)
   ground(xx-1.6,xx+1.6,1);point(xx,1+1.4*(4/(3*np.pi) if filled else 2/np.pi))
  label(2.5,.5,'圓弧線');label(7.5,.5,'半圓面積')
 elif key=='l-section':
  s=.024;x0=3.5;y0=.7;ax.add_patch(Polygon([(x0,y0),(x0+80*s,y0),(x0+80*s,y0+20*s),(x0+20*s,y0+20*s),(x0+20*s,y0+100*s),(x0,y0+100*s)],fc=FILL,ec=BLUE,lw=2));line([x0,x0+80*s],[y0+20*s,y0+20*s],color=MUTED,ls='--');point(x0+25*s,y0+35*s);label(6.8,1,'底板');label(2.6,2.5,'直板');label(6.8,2.5,'形心在缺口內')
 elif key in ('t-section','section-modulus'):
  # Exact proportions: flange 100x20, web 20x80, overall height 100.
  scale=.023;x0=3.8;y0=.8;yb=y0+67.7777778*scale
  ax.add_patch(Polygon([(x0,y0+80*scale),(x0+40*scale,y0+80*scale),(x0+40*scale,y0),(x0+60*scale,y0),(x0+60*scale,y0+80*scale),(x0+100*scale,y0+80*scale),(x0+100*scale,y0+100*scale),(x0,y0+100*scale)],fc=FILL,ec=BLUE,lw=2));line([2.7,7.2],[yb,yb],color=FORCE,ls='--');label(8.2,yb,'形心軸')
  if key=='section-modulus':line([7,7],[y0,y0+2.3],color=MUTED,lw=1);label(7.7,2.9,'上緣');label(7.7,1.1,'下緣')
 elif key=='hollow':
  ax.add_patch(Circle((5,2),1.2,fc=FILL,ec=BLUE,lw=2));ax.add_patch(Circle((5,2),.6,fc='white',ec=BLUE,lw=2));line([3.2,6.8],[2,2],color=MUTED,ls='--');line([5,5],[.45,3.5],color=MUTED,ls='--');label(7.7,2.9,'外圓');label(7.7,1.2,'內孔')
 elif key=='pulley':
  ground(2.5,7.7,3.3);ax.add_patch(Circle((5,1.6),.55,fc=FILL,ec=BLUE,lw=2));ax.add_patch(Circle((5.93,2.9),.38,fc='white',ec=BLUE,lw=2));line([4.45,4.45],[1.6,3.3],color=BLUE);line([5.55,5.55],[1.6,2.9],color=BLUE);line([6.31,6.31],[2.9,1.3],color=BLUE);arrow((6.31,1.1),(6.31,.35));arrow((5,1),(5,.25));label(6.9,.55,'P');label(5.6,.4,'W');label(2.1,2,'兩段支承繩')
 elif key=='potential':
  q=np.linspace(-1,1,80)
  for i in range(3):
   xx=1.8+3.2*i;ys=1.3+.8*q*q if i==0 else 2.2-.8*q*q if i==1 else np.ones_like(q)*1.6
   line(xx+q,ys,color=BLUE);point(xx,1.3 if i==0 else 2.2 if i==1 else 1.6)
   label(xx,.6,['穩定','不穩定','中性'][i])
 elif key=='rod-spring':
  t=np.linspace(0,np.pi/2,200);v=200*np.cos(t)**2+200*np.sin(t);line(1.2+7.5*t/(np.pi/2),.9+(v-200)/25,color=BLUE);arrow((1,.7),(9.2,.7),MUTED);arrow((1,.7),(1,3.35),MUTED);point(3.7,2.9);label(3.7,3.35,'30°：極大');label(8.3,1.5,'90°：極小');label(9.2,.3,'θ');label(.65,3.35,'V')
 out=BytesIO();fig.savefig(out,format='svg',facecolor='white',metadata={'Date':None});plt.close(fig);svg=etree.fromstring(out.getvalue());assert not svg.xpath('//*[local-name()="text"]');dest=assets/(key+'.svg');dest.write_bytes(etree.tostring(svg));figures[key]={'src':str(dest.relative_to(ROOT)),'title':title,'caption':caption};return figures[key]

def drawing(key):
 f=picture(key);return f'<figure class="lecture-figure"><button class="figure-zoom" data-zoom aria-label="放大：{html.escape(f["title"])}"><img src="{f["src"]}" alt="{html.escape(f["caption"])}" width="806" height="355" decoding="async"></button><figcaption>重繪示意圖｜{html.escape(f["caption"])}。點圖可放大。</figcaption></figure>'
def equations(rows):return ''.join(m.formula(*row) for row in rows)
def navigation(n):
 prev=f'<a href="statics-ch{n-1:02}.html">← 上一章</a>' if n>1 else '<span></span>';nxt=f'<a href="statics-ch{n+1:02}.html">下一章 →</a>' if n<6 else '<span></span>'
 return f'<nav class="chapter-nav" aria-label="章節導覽">{prev}<a href="statics.html#ch-h">靜力學章節總覽</a>{nxt}</nav>'
def source(n):
 working=ROOT.parent/f'sources/statics/original-ch{n:02}.pdf';return working if working.exists() else pdfs/f'statics-ch{n:02}.pdf'

for c in data.CHAPTERS:
 n=c['n'];pdf=pdfs/f'statics-ch{n:02}.pdf'
 if source(n).resolve()!=pdf.resolve():shutil.copyfile(source(n),pdf)
 d=pymupdf.open(pdf);starts=[]
 for i in range(1,len(c['sections'])+1):
  pat=re.compile(rf'(?m)^\s*{n}\s*[-－]\s*{i}(?:[.．\s]|$)');page=next((j+1 for j,p in enumerate(d) if pat.search(p.get_text())),None);assert page,(n,i);starts.append(page)
 pdf_url=str(pdf.relative_to(ROOT));entries=[(f'sec{i}',f'{n}-{i}',s['title']) for i,s in enumerate(c['sections'],1)]+[('ex','範例','教學例題'),('quiz','自測','觀念自測'),('source','原文','完整原講義')]
 tab_icons=SECTION_ICONS[n]+['example','quiz','source']
 tabs=''.join(f'<a class="tab" id="tab-{id}" href="#{id}" role="tab" aria-controls="{id}" aria-selected="{"true" if j==0 else "false"}"><span class="ic">{icon(tab_icons[j])}</span><span class="tx"><span class="no">{no}</span><span class="nm">{html.escape(title)}</span></span></a>' for j,(id,no,title) in enumerate(entries));sections=[]
 for i,s in enumerate(c['sections'],1):
  paragraphs=''.join('<p>'+html.escape(p)+'</p>' for p in s['text']);figs=''.join(drawing(k) for k in s['figures']);points=''.join('<li>'+html.escape(p)+'</li>' for p in s['points']);note=f'<p class="callout warn">{html.escape(s["note"])}</p>' if s['note'] else ''
  sections.append(f'<section id="sec{i}" aria-labelledby="h-sec{i}"><h2 id="h-sec{i}"><span class="no">{n}-{i}</span>{html.escape(s["title"])}</h2><p class="source-ref"><a href="{pdf_url}#page={starts[i-1]}" target="_blank" rel="noopener">對照原講義第 {starts[i-1]} 頁 ↗</a></p>{paragraphs}{figs}{equations(s["eqs"])}<h3>解題順序與檢查</h3><ul>{points}</ul>{note}</section>')
 ex=[]
 for i,e in enumerate(c['examples'],1):
  steps=''.join('<li>'+html.escape(p)+'</li>' for p in e['steps']);pic=drawing(e['figure']) if e['figure'] else ''
  ex.append(f'<article class="example"><h3>例 {n}-{i}　{e["title"]}</h3><p>{html.escape(e["q"])}</p>{pic}<details class="worked-solution"><summary><span class="qn">解</span><span>展開完整計算</span></summary><div class="solution"><ol>{steps}</ol>{equations(e["eqs"])}<p class="answer">{html.escape(e["answer"])}</p></div></details></article>')
 sections.append('<section id="ex" aria-labelledby="h-ex"><h2 id="h-ex"><span class="no">EX</span>教學例題</h2><p class="source-ref">以下依本章觀念編寫並重新計算，用於練習分析步驟。原講義的全部例題、國考題與解析另保留於「完整原講義」。</p>'+''.join(ex)+'</section>')
 qs=[]
 for i,q in enumerate(c['quiz'],1):
  # Questions retain all choices outside disclosure, so the correct option is not exposed before opening.
  question_options=''.join(f'<li><span class="ol">({chr(65+j)})</span>{html.escape(text)}</li>' for j,text in enumerate(q['options']))
  qs.append(f'<article class="example"><h3>第 {i} 題</h3><p>{html.escape(q["q"])}</p><ul class="opts">{question_options}</ul><details><summary><span class="qn">答</span><span>查看答案與觀念</span></summary><div class="ans"><b>答案：({chr(65+q["answer"])})</b><p>{html.escape(q["why"])}</p></div></details></article>')
 sections.append('<section id="quiz" aria-labelledby="h-quiz"><h2 id="h-quiz"><span class="no">Q</span>觀念自測</h2><p class="source-ref">本頁自編觀念題。先作答，再展開答案；原講義考題另見完整PDF。</p>'+''.join(qs)+'</section>')
 sections.append(f'<section id="source" aria-labelledby="h-source"><h2 id="h-source"><span class="no">PDF</span>完整原講義</h2><p>本章完整原講義共 {len(d)} 頁，保留全部原題、圖面、解析與推導，搭配網頁重點講解、公式圖檔及重繪示意圖閱讀。</p><p><a class="source-open" href="{pdf_url}" target="_blank" rel="noopener">另開完整原講義 ↗</a><a class="source-open" href="{pdf_url}" download>下載本章 PDF ↓</a></p><div class="pdf-reader" data-pdf="{pdf_url}"><p>切換至此節後載入原講義。手機若未顯示預覽，請使用上方「另開完整原講義」。</p></div></section>')
 page=f'''<!doctype html>
<html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><title>靜力學 第{n}章 {c['title']}｜知識動力場</title><meta name="description" content="{html.escape(c['lede'],quote=True)}"><link rel="stylesheet" href="assets/chapter.css"><link rel="stylesheet" href="assets/dynamics-chapter.css"><link rel="stylesheet" href="assets/materials-course.css"><link rel="stylesheet" href="assets/statics-chapter.css"></head><body><header class="hero"><div><div class="crumb"><a href="statics.html">靜力學</a> / CH {n:02}</div><h1>{c['title']}<small>{c['en']}</small></h1><p class="lede">{c['lede']}</p><div class="meta"><span>{len(c['sections'])} 節</span><span>{len(c['examples'])} 道教學例題</span><span>{len(c['quiz'])} 題觀念自測</span><span>完整原講義 {len(d)} 頁</span></div></div><div class="hero-art" aria-hidden="true">{icon(SECTION_ICONS[n][0])}</div></header><div class="wrap"><nav class="tabs" role="tablist" aria-label="本章各節" aria-orientation="vertical"><p class="tabs-label">SECTIONS</p>{tabs}</nav><main>{''.join(sections)}{navigation(n)}</main></div><dialog id="figure-dialog" aria-label="放大圖面"><button class="zoom-close" autofocus>關閉 ×</button><img alt=""><p></p></dialog><script src="assets/chapter.js"></script><script src="assets/materials-course.js"></script></body></html>'''
 (ROOT/f'statics-ch{n:02}.html').write_text(page)
 manifest.append({'chapter':n,'file':f'statics-ch{n:02}.html','title':c['title'],'sections':len(c['sections']),'examples':len(c['examples']),'quiz':len(c['quiz']),'source_pages':len(d),'section_start_pages':starts,'formulas':sum(len(s['eqs']) for s in c['sections'])+sum(len(e['eqs']) for e in c['examples']),'figure_placements':sum(len(s['figures']) for s in c['sections'])+sum(bool(e['figure']) for e in c['examples'])})
 print(n,c['title'],len(c['sections']),'sections',len(d),'source pages')

# Reuse the existing Statics palette; the layout remains the shared chapter layout.
old=(ROOT/'statics-ch02.html').read_text();style=old.split('<style>',1)[1].split('</style>',1)[0];palette=style.split('*{box-sizing:border-box}',1)[0]
navcss='.chapter-nav{display:flex;flex-wrap:wrap;justify-content:space-between;align-items:center;gap:12px;border-top:1px solid var(--line);padding-top:20px;margin-top:20px;font-size:14px}.chapter-nav a{color:var(--accent);text-decoration:none}.chapter-nav a:hover{text-decoration:underline}.chapter-nav a:focus-visible{outline:2px solid var(--accent);outline-offset:4px}'
(ROOT/'assets/statics-chapter.css').write_text('/* Statics palette, shared by all six chapters. */\n'+palette+'\n'+navcss+'\n.zoom-close{border-color:#0e4a8a;color:#0e4a8a}\n')
for n in [1,2]:
 p=ROOT/f'statics-ch{n:02}.html';s=p.read_text()
 if 'assets/statics-chapter.css' not in s:s=s.replace('</head>','<link rel="stylesheet" href="assets/statics-chapter.css"></head>',1)
 if 'aria-label="章節導覽"' not in s:s=s.replace('</main>',navigation(n)+'\n</main>',1)
 p.write_text(s)

p=ROOT/'statics.html';doc=LH.fromstring(p.read_text());cards=doc.xpath('//*[contains(concat(" ",normalize-space(@class)," ")," ch ")]');assert len(cards) in [5,6]
for c,info,card in zip(data.CHAPTERS[:3],manifest[:3],cards[2:5]):
 card.tag='a';card.set('class','ch');card.set('href',info['file']);h=card.find('h3');h.clear();h.text=c['title'];meta=card.xpath('.//*[@class="meta"]')[0];meta.clear();meta.set('class','meta')
 for text in [f'{info["sections"]} 節',f'{info["examples"]} 道教學例題',f'{info["quiz"]} 題自測',f'原講義 {info["source_pages"]} 頁']:etree.SubElement(meta,'span').text=text
if len(cards)==5:
 c=data.CHAPTERS[-1];info=manifest[-1];family=etree.Element('div',{'class':'family'});etree.SubElement(family,'div',{'class':'fam-label'}).text='虛功與穩定　VIRTUAL WORK & STABILITY';wrap=etree.SubElement(family,'div',{'class':'cards'});card=etree.SubElement(wrap,'a',{'class':'ch','href':info['file']});num=etree.SubElement(card,'div',{'class':'num'});num.text='06';etree.SubElement(num,'small').text='CH';etree.SubElement(card,'h3').text=c['title'];etree.SubElement(card,'p').text='符合約束的虛位移、總虛功為零、重力與彈簧位能、平衡駐值及穩定性判斷。';meta=etree.SubElement(card,'div',{'class':'meta'})
 for text in ['2 節','4 道教學例題','4 題自測','原講義 8 頁']:etree.SubElement(meta,'span').text=text
 doc.xpath('//*[@id="ch-h"]/ancestor::section')[0].append(family)
facts=doc.xpath('//*[@class="facts"]/div');facts[0].find('b').text='6';facts[1].find('b').text='6';facts[2].find('b').text='43'
lede=doc.xpath('//*[@class="lede"]')[0];lede.text='物體不動，不代表沒有受力，而是所有的力剛好互相抵銷。本科目共六章：先描述力與平衡，再分析桁架、構架及摩擦，接著計算形心與慣性矩，最後以虛功與最小位能討論平衡及穩定。各章提供網頁講解與例題；第三至六章並附完整原講義，公式以圖檔呈現，圖面重新繪製。'
for b in doc.xpath('//b'):
 if b.text=='1 : 5 章':b.text='1 : 6 章'
for e in doc.xpath('//*[not(*)]'):
 if e.text=='1 : 5 章':e.text='1 : 6 章'
map_svg=doc.xpath('//*[@aria-labelledby="map-h"]//svg')[0]
map_svg.set('viewbox','0 0 960 364');map_svg.set('aria-label','解題地圖：第一章力的工具，第二章平衡，第三章結構與第四章摩擦求反力及內力；第五章斷面性質銜接材料力學，第六章虛功與最小位能提供平衡及穩定的另一種分析方法')
map_svg.xpath('./rect')[0].set('height','344')
for t in map_svg.xpath('./text'):
 if t.text=='斷面':t.set('y','246')
 elif t.text=='CH 5 質心、形心及慣性矩':t.set('y','246')
 elif t.text=='重心、慣性矩、截面係數':t.set('x','98');t.set('y','265');t.set('font-size','11')
if not map_svg.xpath('./g[@id="statics-virtual-map"]'):
 g=etree.SubElement(map_svg,'g',id='statics-virtual-map');etree.SubElement(g,'rect',x='30',y='298',width='456',height='50',fill='var(--accent-soft)',stroke='var(--accent)')
 etree.SubElement(g,'text',x='46',y='328',fill='var(--ink)',**{'font-size':'14'}).text='CH 6 虛功與最小位能原理'
 etree.SubElement(g,'path',d='M486 323L564 323',stroke='var(--accent)',fill='none',**{'stroke-width':'2','marker-end':'url(#ar)'})
 etree.SubElement(g,'text',x='580',y='328',fill='var(--muted)',**{'font-size':'13'}).text='另一種方法：由位移與位能判斷平衡、穩定'
head=doc.find('head')
if not head.xpath('./link[@href="assets/materials-course.css"]'):etree.SubElement(head,'link',rel='stylesheet',href='assets/materials-course.css')
p.write_text('<!doctype html>\n'+LH.tostring(doc,encoding='unicode')+'\n')
report={'chapters':manifest,'figures':list(figures.values()),'totals':{'new_chapters':4,'sections':sum(c['sections'] for c in manifest),'teaching_examples':sum(c['examples'] for c in manifest),'quiz':sum(c['quiz'] for c in manifest),'source_pages':sum(c['source_pages'] for c in manifest),'formulas':sum(c['formulas'] for c in manifest),'unique_figures':len(figures),'figure_placements':sum(c['figure_placements'] for c in manifest)}}
(ROOT.parent/'output').mkdir(exist_ok=True);(ROOT.parent/'output/statics-completion-manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(report['totals'])
m.mod('statics_fixed_headers','add-fixed-headers.py').apply()
