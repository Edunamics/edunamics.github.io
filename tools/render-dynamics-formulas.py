#!/usr/bin/env python3
"""Render Dynamics equations as font-independent SVG images.
Requires matplotlib and lxml. Run from any directory; only Dynamics chapters change.
Display equations use reviewed TeX; inline equations retain their original notation.
"""
from pathlib import Path
from io import BytesIO
import base64, hashlib, importlib.util, json, re
import matplotlib
matplotlib.use('Agg')
matplotlib.rcParams.update({'svg.fonttype':'path','svg.hashsalt':'dynamics-formulas','mathtext.fontset':'stix','savefig.transparent':True})
from matplotlib.figure import Figure
from matplotlib.textpath import TextPath
from matplotlib.font_manager import FontProperties
from matplotlib.mathtext import math_to_image
from lxml import html, etree
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('formula_data',Path(__file__).with_name('dynamics-formula-data.py'))
data=importlib.util.module_from_spec(spec);spec.loader.exec_module(data)
NS='http://www.w3.org/2000/svg'
OUT=ROOT/'assets/dynamics-formulas';OUT.mkdir(exist_ok=True)
# SVG path outlines, including Chinese notes, remove the browser-font dependency.
CJK=FontProperties(fname='/System/Library/Fonts/Supplemental/Arial Unicode.ttf',size=10)
CACHE={}; manifest=[];errors=[]
SOURCES=json.loads(Path(__file__).with_name('dynamics-formula-source.json').read_text())
def math_svg(tex,size=15):
 key=(tex,size)
 if key in CACHE:return CACHE[key]
 out=BytesIO();math_to_image('$'+tex+'$',out,prop=FontProperties(size=size),format='svg',color='#152231')
 svg=etree.fromstring(out.getvalue());
 for stamp in svg.xpath('//*[local-name()="date"]'):stamp.getparent().remove(stamp)
 w,h=map(float,svg.get('viewBox').split()[2:]);b=etree.tostring(svg)
 CACHE[key]=(b,w*4/3,h*4/3);return CACHE[key]
def display_svg(rows):
 fig=Figure(figsize=(8,2),dpi=96); y=0; maxw=0; texts=[]
 for tex,note in rows:
  b,w,h=math_svg(tex,17); maxw=max(maxw,w,TextPath((0,0),note,prop=CJK).get_extents().width*4/3 if note else 0)
  # Font sizes and physical spacing use points, preserving fractions and descenders.
  y+=max(h*0.75,24)+8
  texts.append((tex,note,y))
  if note:y+=19
 height=y+12;width=max(maxw*0.75+16,120)
 fig.set_size_inches(width/72,height/72)
 for tex,note,yy in texts:
  fig.text(8/width,1-yy/height,'$'+tex+'$',fontsize=17,color='#152231',va='baseline')
  if note:fig.text(8/width,1-(yy+16)/height,note,fontproperties=CJK,color='#566677',va='baseline')
 out=BytesIO();fig.savefig(out,format='svg',transparent=True,metadata={'Date':None})
 svg=etree.fromstring(out.getvalue());svg.set('role','img');assert not svg.xpath('//*[local-name()="text"]')
 return etree.tostring(svg,xml_declaration=True,encoding='utf-8'),width*4/3,height*4/3
GREEK={'α':'alpha','β':'beta','γ':'gamma','θ':'theta','ω':'omega','μ':'mu','η':'eta','τ':'tau','φ':'varphi','Σ':'sum','Δ':'Delta','π':'pi','ρ':'rho','λ':'lambda','ϕ':'phi','ε':'epsilon','σ':'sigma','Ω':'Omega'}
SUB=dict(zip('₀₁₂₃₄₅₆₇₈₉','0123456789'));SUP=dict(zip('⁰¹²³⁴⁵⁶⁷⁸⁹','0123456789'))
def to_tex(s):
 s=re.sub(r'\\mathit\{v\}₀\\mathit\{([xy])\}',lambda m:r'\mathit{v}_{0'+m[1]+'}',s)
 # Keep the source's meaning; only normalize its typography.
 for char,cmd in GREEK.items():s=s.replace(char,'\\'+cmd+' ')
 s=re.sub('([₀₁₂₃₄₅₆₇₈₉]+)',lambda m:'_{'+''.join(SUB[c] for c in m[0])+'}',s)
 s=re.sub('([⁰¹²³⁴⁵⁶⁷⁸⁹]+)',lambda m:'^{'+''.join(SUP[c] for c in m[0])+'}',s)
 for a,b in [('½',r'\frac{1}{2}'),('−','-'),('×',r'\times '),('·',r'\cdot '),('⋅',r'\cdot '),('≈',r'\approx '),('≤',r'\leq '),('≥',r'\geq '),('⟹',r'\Longrightarrow '),('→',r'\rightarrow '),('∫',r'\int '),('%',r'\%')]:s=s.replace(a,b)
 s=re.sub(r'([A-Za-z]|\\(?:theta|omega|alpha) )\u0307',r'\\dot{\1}',s)
 s=re.sub(r'([A-Za-z]|\\(?:theta|omega|alpha) )\u0308',r'\\ddot{\1}',s)
 s=s.replace('ṙ',r'\dot{r}')
 while '√' in s:
  j=s.index('√')
  if j+1<len(s) and s[j+1]=='(':
   depth=1;k=j+2
   while k<len(s) and depth:
    if s[k]=='(':depth+=1
    elif s[k]==')':depth-=1
    k+=1
   if depth:raise ValueError('Unclosed square root: '+s)
   s=s[:j]+r'\sqrt{'+s[j+2:k-1]+'}'+s[k:]
  else:
   m=re.match(r'√([0-9]+)',s[j:])
   if not m:raise ValueError('Unsupported root: '+s)
   s=s[:j]+r'\sqrt{'+m[1]+'}'+s[j+len(m[0]):]
 s=re.sub(r'\b(sin|cos|tan)\b',r'\\\1 ',s)
 return s.strip()
MATH=re.compile(r'[A-Za-z0-9α-ωΑ-Ωϕϕ₀-₉⁰¹²³⁴⁵⁶⁷⁸⁹ṙ\u0307\u0308=+−\-×·⋅/()\[\]{}_^\\.,\s√∫≈≤≥<>|%\u00bd⟹→π]+')
def image(tex,alt):
 b,w,h=math_svg(tex)
 alt=re.sub(r'\\(?:mathit|mathrm)\{([^{}]*)\}',r'\1',alt)
 e=etree.Element('img',{'class':'math-inline','src':'data:image/svg+xml;base64,'+base64.b64encode(b).decode(),'alt':alt,'width':f'{w:.2f}','height':f'{h:.2f}','style':f'width:{w:.2f}px','decoding':'async'})
 return e

def convert_text(s):
 result=[];end=0
 for m in MATH.finditer(s):
  raw=m[0];core=raw.strip()
  # An English heading or an ordinary number is prose, not an equation.
  active=bool(re.search(r'[=α-ωΑ-Ω₀-₉⁰¹²³⁴⁵⁶⁷⁸⁹ṙ_^\\√∫≈≤≥½⟹→]',core))
  if not core or not active:continue
  if m.start()>end:result.append(s[end:m.start()])
  lead=raw[:len(raw)-len(raw.lstrip())];trail=raw[len(raw.rstrip()):]
  result.append(lead)
  try:
   tex=to_tex(core);b,w,h=math_svg(tex)
   # Break calculations between equalities so phone text stays readable.
   chunks=re.split(r'(?<==)\s*',core) if w>300 else [core]
   for chunk in chunks:
    if chunk.strip():result.extend([image(to_tex(chunk.strip()),chunk.strip()),' '])
  except Exception as err:
   errors.append({'source':core,'error':str(err)});result.append(core)
  result.append(trail);end=m.end()
 result.append(s[end:]);return result

def rich_math(e):
 if e.tag in ('sub','sup'):
  t=''.join(e.itertext());t={'合':r'\mathrm{total}','總':r'\mathrm{total}','非保守':r'\mathrm{nc}'}.get(t,t);return ('_' if e.tag=='sub' else '^')+'{'+t+'}'
 if e.tag=='i':return r'\mathit{'+(e.text or '')+''.join(rich_math(c)+(c.tail or '') for c in e)+'}'
 raise ValueError(e.tag)
def rewrite(e):
 # Preserve emphasis, links, and labels; merge adjacent math markup into one expression.
 original=list(e);pieces=[];buf=e.text or '';e.text=None
 def flush():
  nonlocal buf
  pieces.extend(convert_text(buf));buf=''
 for child in original:
  tail=child.tail or '';child.tail=None
  if child.tag in ('i','sub','sup'):
   buf+=rich_math(child);e.remove(child)
  else:
   flush();e.remove(child)
   if child.tag not in ('br','img','svg'):rewrite(child)
   pieces.append(child)
  buf+=tail
 flush()
 for piece in pieces:
  if isinstance(piece,str):
   if len(e):e[-1].tail=(e[-1].tail or '')+piece
   else:e.text=(e.text or '')+piece
  else:e.append(piece)

for ch in range(1,8):
 p=ROOT/f'dynamics-ch{ch:02}.html'
 # Read the checked-in text version; generated images can be rebuilt without duplication.
 source=SOURCES[p.name]
 source=source.replace('<sub>0&gt; 0（向下），加速度 <i>a</i> = <i>g</i>，物體一直向下加速。</sub>', '<sub>0</sub> &gt; 0（向下），加速度 <i>a</i> = <i>g</i>，物體一直向下加速。')
 doc=html.fromstring(source);blocks=doc.xpath('//div[@class="formula"]');assert len(blocks)==len(data.FORMULAS[ch])
 figures_before=doc.xpath('//figure[contains(@class,"lecture-figure")]//img/@src')
 for i,(block,rows) in enumerate(zip(blocks,data.FORMULAS[ch]),1):
  label=block.xpath('./*[@class="lab" or @class="desc"]');labeltext=label[0].text_content().strip() if label else ''
  alt='；'.join(tex+(('（'+note+'）') if note else '') for tex,note in rows)
  filename=f'ch{ch:02}-eq{i:02}.svg';b,w,h=display_svg(rows);(OUT/filename).write_bytes(b)
  for child in list(block):block.remove(child)
  block.text=None
  if labeltext:
   lab=etree.SubElement(block,'div',{'class':'lab'});lab.text=labeltext
  a=etree.SubElement(block,'a',{'class':'formula-image-link','href':'assets/dynamics-formulas/'+filename,'target':'_blank','rel':'noopener','aria-label':'放大公式：'+(labeltext or f'{ch}-{i}')})
  etree.SubElement(a,'img',{'class':'math-display','src':'assets/dynamics-formulas/'+filename,'alt':alt,'width':f'{w:.2f}','height':f'{h:.2f}','style':f'width:{w:.2f}px','decoding':'async'})
  manifest.append({'chapter':ch,'index':i,'label':labeltext,'file':filename,'equations':[{'tex':t,'note':n} for t,n in rows]})
 # Inline variables, explanations, and worked solutions use self-contained SVG images.
 main=doc.xpath('//main')[0]
 for e in list(main.xpath('.//p[not(ancestor::figure)]|.//li|.//div[@class="q"]|.//div[@class="m"]|.//div[@class="callout"]|.//*[@class="note"]')):
  if not e.xpath('ancestor::*[@class="formula"]') and not e.xpath('ancestor::li|ancestor::*[@class="q"]'):rewrite(e)
 assert doc.xpath('//figure[contains(@class,"lecture-figure")]//img/@src')==figures_before
 p.write_text('<!doctype html>\n'+html.tostring(doc,encoding='unicode')+'\n')
 print(p.name,'display:',len(blocks),'inline:',len(doc.xpath('//img[@class="math-inline"]')))
(OUT/'index.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
if errors:
 print(json.dumps(errors,ensure_ascii=False,indent=2));raise SystemExit('Inline render errors: '+str(len(errors)))
print('Rendered',len(manifest),'display formula images;',len(CACHE),'unique math expressions')
