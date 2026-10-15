#!/usr/bin/env python3
"""Build font-independent SVG formulas for Manufacturing and Statics."""
from pathlib import Path
import importlib.util, json
from lxml import html,etree
ROOT=Path(__file__).resolve().parents[1]
def module(name,file):
 spec=importlib.util.spec_from_file_location(name,Path(__file__).with_name(file));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
u=module('course_formula_utils','course-formula-utils.py');data=module('course_formula_data','course-formula-data.py')
sources=json.loads(Path(__file__).with_name('course-formula-source.json').read_text())
out=ROOT/'assets/course-formulas';out.mkdir(exist_ok=True);index=[]
for name,source in sources.items():
 doc=html.fromstring(source);blocks=doc.xpath('//*[contains(concat(" ",normalize-space(@class)," ")," formula ")]')
 assert len(blocks)==len(data.FORMULAS[name]),name
 for i,(block,rows) in enumerate(zip(blocks,data.FORMULAS[name]),1):
  labels=block.xpath('./*[@class="lab" or @class="desc"]');label=labels[0].text_content().strip() if labels else ''
  filename=Path(name).stem+f'-eq{i:02}.svg';b,w,h=u.display_svg(rows);(out/filename).write_bytes(b)
  original=' '.join(block.text_content().split());block.clear();block.set('class','formula formula-image')
  if label:etree.SubElement(block,'div',{'class':'lab'}).text=label
  a=etree.SubElement(block,'a',{'class':'formula-image-link','href':'assets/course-formulas/'+filename,'target':'_blank','rel':'noopener','aria-label':'放大公式：'+(label or original)})
  etree.SubElement(a,'img',{'class':'math-display','src':'assets/course-formulas/'+filename,'alt':original,'width':str(round(w)),'height':str(round(h)),'style':f'width:{w:.2f}px','decoding':'async'})
  index.append({'page':name,'index':i,'file':filename,'original':original,'rows':rows})
 main=doc.xpath('//main')[0]
 selected=main.xpath('.//p|.//li|.//td|.//th|.//figcaption|.//summary|.//small|.//*[contains(concat(" ",normalize-space(@class)," ")," callout ")]|.//h3|.//h4|.//*[@class="m" or @class="eq" or @class="callout" or @class="note" or @class="ans"]')
 selected_set=set(selected)
 for e in selected:
  if any(a in selected_set for a in e.iterancestors()):continue
  if e.xpath('ancestor::*[contains(concat(" ",normalize-space(@class)," ")," formula ")]'):continue
  u.rewrite(e)
 head=doc.find('head');head.append(etree.Element('link',rel='stylesheet',href='assets/course-formulas.css'))
 (ROOT/name).write_text('<!doctype html>\n'+html.tostring(doc,encoding='unicode')+'\n')
 print(name,len(blocks),'display',len(doc.xpath('//img[@class="math-inline"]')),'inline')
(out/'index.json').write_text(json.dumps(index,ensure_ascii=False,indent=2)+'\n')
if u.errors:
 (ROOT.parent/'output/course-formula-errors.json').write_text(json.dumps(u.errors,ensure_ascii=False,indent=2));print(json.dumps(u.errors,ensure_ascii=False,indent=2));raise SystemExit(str(len(u.errors))+' errors')
print('All formulas rendered:',len(index))
