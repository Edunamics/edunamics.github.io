"""重新產生網站用的王漢宗特黑體子集字型。

用法：python3 tools/build-font.py <wt014.ttf 路徑>
掃描網站根目錄所有 .html 用到的字元，輸出 fonts/HanWangHeiHeavy-subset.woff2。
新增或修改頁面文字後要重跑，否則新字會改用備用字型顯示。
需要：pip install fonttools brotli
"""
import glob, os, sys
from fontTools import subset
from fontTools.ttLib import TTFont

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = sys.argv[1]
chars = set()
for f in glob.glob(os.path.join(root, '*.html')):
    chars |= set(open(f, encoding='utf8').read())
chars |= {chr(c) for c in range(0x20, 0x7f)}
cmap = TTFont(src).getBestCmap()
keep = sorted(c for c in chars if ord(c) in cmap)
missing = sorted(c for c in chars if ord(c) > 0x2e80 and ord(c) not in cmap)
opts = subset.Options()
opts.flavor = 'woff2'
opts.layout_features = ['*']
opts.name_IDs = ['*']
font = subset.load_font(src, opts)
s = subset.Subsetter(opts)
s.populate(unicodes=[ord(c) for c in keep])
s.subset(font)
out = os.path.join(root, 'fonts', 'HanWangHeiHeavy-subset.woff2')
subset.save_font(font, out, opts)
print(f'{len(keep)} glyphs -> {out} ({os.path.getsize(out)//1024} KB)')
if missing:
    print('字型裡沒有的字（會以備用字型顯示）：', ''.join(missing))
