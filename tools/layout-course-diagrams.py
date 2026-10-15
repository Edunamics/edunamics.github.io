#!/usr/bin/env python3
"""Separate diagram labels from drawing edges and outline glyphs.
Geometry is retained. Labels are moved to the nearest clear position, or into
an added margin when the diagram is crowded. No glyph depends on browser fonts.
Requires fonttools, numpy, svgpathtools and lxml.
"""
from pathlib import Path
from io import StringIO
import json,math,re
import numpy as np
from lxml import html,etree
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen
from svgpathtools import parse_path
from svgpathtools.parser import parse_transform
ROOT=Path(__file__).resolve().parents[1]
FONT=TTFont('/System/Library/Fonts/Supplemental/Arial Unicode.ttf');GLYPHS=FONT.getGlyphSet();CMAP=FONT.getBestCmap();U=FONT['head'].unitsPerEm
CACHE={};REPORT=[]
def num(x,default=0):
 try:return float(re.search(r'[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?',str(x))[0])
 except:return default

def style(e):
 return dict(p.split(':',1) for p in e.get('style','').split(';') if ':' in p)
def fontsize(e,inherited=14,statics=False):
 size=e.get('font-size') or style(e).get('font-size')
 if size:return num(size,inherited)*(inherited if str(size).endswith('em') else 1)
 cls=e.get('class','').split()
 if 'sub' in cls:return inherited*.72
 if statics:
  for c,sz in [('tb',15),('tf',14),('tr',14),('td',13),('ta',13),('tc',13),('tn',12),('tax',14),('teq',30)]:
   if c in cls:return sz
 return inherited

def matrix(e,root):
 chain=[]
 while e is not root:
  chain.append(e);e=e.getparent()
  if e is None:break
 m=np.eye(3)
 for e in reversed(chain):m=m@parse_transform(e.get('transform',''))
 return m

def points_transform(ps,m):
 if not len(ps):return np.empty((0,2))
 a=np.array(ps);return (m@np.column_stack((a,np.ones(len(a)))).T).T[:,:2]

def geometry(svg):
 points=[]
 for e in svg.iterdescendants():
  if not isinstance(e.tag,str) or any(a.tag in ('defs','marker','pattern','clippath','text') for a in e.iterancestors() if a is not svg):continue
  tag=e.tag.lower();ps=[]
  if tag=='line':ps=[complex(num(e.get('x1')),num(e.get('y1'))),complex(num(e.get('x2')),num(e.get('y2')))]
  elif tag in ('polyline','polygon'):
   a=list(map(float,re.findall(r'[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?',e.get('points',''))));ps=[complex(*a[i:i+2]) for i in range(0,len(a)-1,2)]
   if tag=='polygon' and ps:ps.append(ps[0])
  elif tag=='rect':
   x,y,w,h=[num(e.get(k)) for k in ['x','y','width','height']];ps=[complex(x,y),complex(x+w,y),complex(x+w,y+h),complex(x,y+h),complex(x,y)]
  elif tag in ('circle','ellipse'):
   x,y=num(e.get('cx')),num(e.get('cy'));rx=num(e.get('rx') or e.get('r'));ry=num(e.get('ry') or e.get('r'));ps=[complex(x+rx*math.cos(t),y+ry*math.sin(t)) for t in np.linspace(0,2*math.pi,65)]
  elif tag=='path':
   try:
    p=parse_path(e.get('d',''));vals=[]
    for seg in p:
     vals += [seg.point(t) for t in np.linspace(0,1,max(2,min(1200,int(seg.length()/2)+2)))]
    a=points_transform([(p.real,p.imag) for p in vals],matrix(e,svg));points.extend(a);continue
   except Exception:continue
  if len(ps)>1:
   vals=[]
   for a,b in zip(ps,ps[1:]):vals.extend(a+(b-a)*t for t in np.linspace(0,1,max(2,min(1000,int(abs(a-b)/2)+2))))
   points.extend(points_transform([(p.real,p.imag) for p in vals],matrix(e,svg)))
 return np.array(points) if points else np.empty((0,2))

def glyph(char):
 if char in CACHE:return CACHE[char]
 name=CMAP.get(ord(char))
 if not name:raise ValueError('Missing diagram glyph '+repr(char))
 g=GLYPHS[name];pen=SVGPathPen(GLYPHS);g.draw(pen);bp=BoundsPen(GLYPHS);g.draw(bp)
 CACHE[char]=(pen.getCommands(),g.width,bp.bounds);return CACHE[char]

def label(e,svg,statics,prefix,defs):
 size=14 if statics else 14
 # Parent groups may set inherited font size.
 for a in reversed(list(e.iterancestors())):
  if a is svg:continue
  size=fontsize(a,size,False)
 size=fontsize(e,size,statics)
 x,y=num(e.get('x')),num(e.get('y'));start=x;paths=[];bounds=[];used=[]
 def run(text,node,sz):
  nonlocal x,y
  if not text:return
  if node is not e:
   if node.get('x') is not None:x=num(node.get('x'))
   if node.get('y') is not None:y=num(node.get('y'))
   x+=num(node.get('dx'));y+=num(node.get('dy'))
   shift=node.get('baseline-shift','')
   if shift=='sub':y+=size*.25
   elif shift=='super':y-=size*.4
  for c in text:
   d,advance,bbox=glyph(c);scale=sz/U;gid=prefix+'-'+str(ord(c))
   if d and gid not in used:
    used.append(gid)
    if gid not in defs:defs[gid]=d
   if d:paths.append((gid,x,y,scale,node.get('fill') if node is not e else None))
   if bbox:
    a,b,cx,dy=bbox;bounds.append((x+a*scale,y-dy*scale,x+cx*scale,y-b*scale))
   x+=advance*scale
 run(e.text,e,size)
 for c in e:
  run(c.text,c,fontsize(c,size,statics));run(c.tail,e,size)
 anchor=e.get('text-anchor','start');offset=(x-start)*({'middle':.5,'end':1}.get(anchor,0))
 group=etree.Element('g');group.set('class','diagram-label');group.set('aria-label',''.join(e.itertext()));group.set('role','img')
 color=e.get('fill') or style(e).get('fill')
 if not color:
  cls=e.get('class','').split();color='var(--force)' if 'tf' in cls else 'var(--res)' if 'tr' in cls else 'var(--muted)' if any(c in cls for c in ['td','ta','tc','tn','tax']) else 'var(--accent)' if 'teq' in cls else 'var(--ink)'
 group.set('fill',color);group.set('stroke','none')
 if e.get('transform'):group.set('transform',e.get('transform'))
 for gid,x,y,sc,fill in paths:
  use=etree.SubElement(group,'use',{'href':'#'+gid,'transform':f'translate({x-offset:.4f} {y:.4f}) scale({sc:.7f} {-sc:.7f})'})
  if fill:use.set('fill',fill)
 if not bounds:return group,np.array([0,0,0,0]),np.eye(3)
 a=min(b[0] for b in bounds)-offset;b=min(b[1] for b in bounds);c=max(b[2] for b in bounds)-offset;d=max(b[3] for b in bounds)
 m=matrix(e,svg);corners=points_transform([(a,b),(c,b),(c,d),(a,d)],m)
 bbox=np.array([corners[:,0].min(),corners[:,1].min(),corners[:,0].max(),corners[:,1].max()])
 return group,bbox,matrix(e.getparent(),svg) if e.getparent() is not svg else np.eye(3)

def intersect(a,b,pad=3):return a[0]<b[2]+pad and a[2]>b[0]-pad and a[1]<b[3]+pad and a[3]>b[1]-pad

def conflicts(box,pts,boxes,index):
 p=2.8
 hits=int(np.count_nonzero((pts[:,0]>box[0]-p)&(pts[:,0]<box[2]+p)&(pts[:,1]>box[1]-p)&(pts[:,1]<box[3]+p))) if len(pts) else 0
 text=sum(1 for j,b in enumerate(boxes) if j!=index and intersect(box,b,3))
 return hits+text*100

def process(svg,name,ordinal):
 labels=svg.xpath('.//text');wview=list(map(float,(svg.get('viewbox') or svg.get('viewBox') or '0 0 640 360').split()));vx,vy,w,h=wview;pts=geometry(svg);defs={};items=[]
 prefix='lbl-'+Path(name).stem+'-'+str(ordinal)
 for e in labels:
  g,b,m=label(e,svg,name.startswith('statics'),prefix,defs);items.append([e,g,b,m])
 boxes=[item[2].copy() for item in items];before=sum(conflicts(b,pts,boxes,i)>0 for i,b in enumerate(boxes));moved=[];gutter=h+vy+12
 # Place long labels first; a short label has more choices near its attachment.
 order=sorted(range(len(items)),key=lambda i:-(boxes[i][2]-boxes[i][0]))
 for i in order:
  b=boxes[i]
  if conflicts(b,pts,boxes,i)==0:continue
  found=None
  for radius in [4,8,12,18,24,32,44,60,80]:
   opts=[]
   for angle in np.linspace(0,2*math.pi,24,endpoint=False):
    dx,dy=radius*math.cos(angle),radius*math.sin(angle);nb=b+np.array([dx,dy,dx,dy])
    if nb[0]<vx+3 or nb[2]>vx+w-3 or nb[1]<vy+3 or nb[3]>vy+h-3:continue
    if conflicts(nb,pts,boxes,i)==0:opts.append((abs(dx)*.1+abs(dy)*.05,dx,dy,nb))
   if opts:found=min(opts,key=lambda x:x[0]);break
  if found is None:
   # Dedicated lower margin guarantees clear labels without shrinking the drawing.
   dx=vx+10-b[0];dy=gutter-b[1];nb=b+np.array([dx,dy,dx,dy]);gutter=nb[3]+10;found=(0,dx,dy,nb)
  _,dx,dy,nb=found;boxes[i]=nb;moved.append({'text':''.join(items[i][0].itertext()),'dx':round(dx,2),'dy':round(dy,2)})
  if items[i][1].get('fill') in ('var(--paper)','#fff','#ffffff','white'):items[i][1].set('fill','var(--ink)')
  delta=np.linalg.inv(items[i][3])@np.array([dx,dy,0]);g=items[i][1];g.set('transform',f'translate({delta[0]:.4f} {delta[1]:.4f}) '+g.get('transform',''))
  # Longer relocations retain their original attachment through a thin leader.
  if math.hypot(dx,dy)>28:
   old=(b[:2]+b[2:])/2;new=np.array([min(max(old[0],nb[0]),nb[2]),min(max(old[1],nb[1]),nb[3])]);lead=etree.Element('path',{'d':f'M{old[0]:.2f} {old[1]:.2f}L{new[0]:.2f} {new[1]:.2f}','fill':'none','stroke':'var(--muted)','stroke-width':'.65','stroke-dasharray':'2 3','opacity':'.7','class':'label-leader'})
   svg.append(lead)
 for e,g,b,m in items:e.getparent().replace(e,g)
 container=etree.Element('defs')
 for gid,d in defs.items():etree.SubElement(container,'path',{'id':gid,'d':d})
 svg.insert(0,container)
 minx=min([vx]+[b[0]-8 for b in boxes]);miny=min([vy]+[b[1]-8 for b in boxes]);maxx=max([vx+w]+[b[2]+8 for b in boxes]);maxy=max([vy+h]+[b[3]+8 for b in boxes]);svg.attrib.pop('viewbox',None);svg.set('viewBox',f'{minx:.2f} {miny:.2f} {maxx-minx:.2f} {maxy-miny:.2f}')
 after=sum(conflicts(b,pts,boxes,i)>0 for i,b in enumerate(boxes))
 REPORT.append({'page':name,'diagram':ordinal,'label':svg.get('aria-label',''),'labels':len(labels),'clashes_before':before,'clashes_after':after,'moved':moved,'size':[round(maxx-minx),round(maxy-miny)],'label_bounds':[{'text':''.join(item[0].itertext()),'box':[round(float(v),3) for v in box]} for item,box in zip(items,boxes)]})

for p in sorted([*ROOT.glob('ch[0-9]*.html'),*ROOT.glob('statics-ch*.html')]):
 doc=html.fromstring(p.read_text());svgs=doc.xpath('//svg[.//text]')
 for i,svg in enumerate(svgs,1):process(svg,p.name,i)
 p.write_text('<!doctype html>\n'+html.tostring(doc,encoding='unicode')+'\n')
 print(p.name,'diagrams',len(svgs),flush=True)
(ROOT.parent/'output/course-diagram-layout-report.json').write_text(json.dumps(REPORT,ensure_ascii=False,indent=2)+'\n')
print('Diagrams',len(REPORT),'labels',sum(x['labels'] for x in REPORT),'moved',sum(len(x['moved']) for x in REPORT),'remaining',sum(x['clashes_after'] for x in REPORT))
