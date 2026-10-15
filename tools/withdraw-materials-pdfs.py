"""Remove published Materials PDFs and reader links; retain working sources outside site."""
from pathlib import Path
from lxml import html as LH
ROOT=Path(__file__).resolve().parents[1]
def withdraw():
 for path in sorted(ROOT.glob('materials-ch*.html')):
  doc=LH.fromstring(path.read_text());chapter=int(path.stem[-2:])
  for e in doc.xpath('//*[@id="source" or @id="tab-source"]'):e.getparent().remove(e)
  for e in doc.xpath('//p[contains(@class,"source-ref")]'):
   links=e.xpath('.//a[contains(@href,".pdf")]')
   if links:e.getparent().remove(e)
  for e in doc.xpath('//p[contains(@class,"source-ref")]'):
   if '完整原講義' in e.text_content():e.text='以下為依本章觀念編寫並重新計算的教學例題。';[e.remove(c) for c in list(e)]
  for e in doc.xpath('//header//*[@class="meta"]/span'):
   if '完整原講義' in e.text_content():e.text='網頁講義';[e.remove(c) for c in list(e)]
  for e in doc.xpath('//script[contains(@src,"materials-course.js")]'):e.set('src','assets/materials-course.js?v=no-pdf-20261015')
  for e in doc.xpath('//link[contains(@href,"materials-course.css")]'):e.set('href','assets/materials-course.css?v=full-ch01-20261015')
  path.write_text('<!doctype html>\n'+LH.tostring(doc,encoding='unicode')+'\n')
 overview=ROOT/'mechanics-of-materials.html';doc=LH.fromstring(overview.read_text())
 for e in doc.xpath('//*[@class="meta"]/span'):
  if '原講義' in e.text_content():e.text='網頁講義'
 first=doc.xpath('//a[@href="materials-ch01.html"]')[0];meta=first.xpath('.//*[@class="meta"]')[0];meta.clear();meta.set('class','meta')
 for text in ['5 節完整講解','11 道完整範例','12 道實戰演練']:LH.etree.SubElement(meta,'span').text=text
 first.xpath('.//p')[0].text='完整重編五節原講義：力的分類與性質、自由體圖、力系平衡及內力分析，含全部 11 道範例、12 道實戰演練、重繪圖與公式圖檔。'
 lede=doc.xpath('//*[@class="lede"]')[0];lede.text='靜力學算出外力與反力，材料力學接著問：構件裡面受多大的力、會變形多少、會不會壞。由應力與應變，逐步分析軸向、扭轉、彎曲及組合負載，最後進入能量法、塑性與柱的挫曲。第一章已完整重編為網頁講義，包含全部範例與實戰演練；其餘各章提供重點講解與教學例題。'
 facts=doc.xpath('//*[@class="facts"]/div');facts[2].find('b').text='39';facts[2].find('span').text='道範例，另有12題演練'
 for e in doc.xpath('//link[contains(@href,"materials-course.css")]'):e.set('href','assets/materials-course.css?v=full-ch01-20261015')
 overview.write_text('<!doctype html>\n'+LH.tostring(doc,encoding='unicode')+'\n')
 published=ROOT/'assets/materials'
 for path in published.glob('*.pdf'):path.unlink()
 if published.exists() and not any(published.iterdir()):published.rmdir()
 print('Materials: no PDF downloads/readers or published PDF copies remain.')
if __name__=='__main__':withdraw()
