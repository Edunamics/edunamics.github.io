"""Apply shared fixed navigation to the four subject overviews and all chapter pages.
Safe to rerun after rebuilding course pages. The entry page has no navigation row.
"""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CSS='assets/fixed-header.css?v=20261016'
JS='assets/fixed-header.js?v=20261016'
def apply():
 changed=[]
 for p in sorted(ROOT.glob('*.html')):
  s=p.read_text()
  if 'class="crumb"' not in s and 'class="top"' not in s:continue
  before=s
  if CSS not in s:s=s.replace('</head>',f'<link rel="stylesheet" href="{CSS}"></head>',1)
  # Chapter initialization must know the header height even on a direct #anchor visit.
  if 'src="assets/chapter.js' in s:
   s=s.replace(f'<script src="{JS}" defer></script>','')
   if f'<script src="{JS}"></script>' not in s:s=s.replace('<script src="assets/chapter.js',f'<script src="{JS}"></script><script src="assets/chapter.js',1)
  elif JS not in s:s=s.replace('</head>',f'<script src="{JS}" defer></script></head>',1)
  s=s.replace('src="assets/chapter.js"','src="assets/chapter.js?v=fixed-header-20261016"')
  if s!=before:p.write_text(s);changed.append(p.name)
 print('Fixed headers:',len(changed),'pages updated')
if __name__=='__main__':apply()
