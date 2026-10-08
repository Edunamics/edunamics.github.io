"""檢查圖面標註：找出 SVG 文字與看得見的線段、其他文字重疊，或超出圖框被裁切的地方。

本站原則：圖內標註不可與線段重疊。新增或修改圖面後執行：
  python3 -m http.server 8765 &        （在網站根目錄）
  python3 tools/check-labels.py http://localhost:8765/ *.html
每頁回傳空清單即通過；桌機 1280 與手機 390 兩種寬度都會檢查。
無法避開格線的圖表標註，可加 paint-order:stroke 的底色光暈遮住格線，檢查時視為通過。
需要：pip install playwright && playwright install chromium
"""
import sys, json, asyncio
from playwright.async_api import async_playwright

JS = r"""
() => {
  document.documentElement.classList.remove('tabbed');
  document.querySelectorAll('main>section').forEach(s => s.hidden = false);
  document.querySelectorAll('details').forEach(d => d.open = true);
  const st = document.createElement('style'); st.textContent = 'text,tspan{pointer-events:none!important} svg *{pointer-events:visiblePainted!important} svg{pointer-events:auto!important}'; document.head.appendChild(st);
  const out = [];
  const svgs = [...document.querySelectorAll('svg')];

  const visAt = (g, x, y) => {
    for (const el of document.elementsFromPoint(x, y)) {
      if (el === g || g.contains(el)) return true;
      if (!(el instanceof SVGGraphicsElement) || el.tagName === 'svg' || el.tagName === 'g' || el.closest('text')) continue;
      const cs = getComputedStyle(el);
      let op = parseFloat(cs.opacity); for (let a = el.parentElement; a && a.tagName !== 'svg'; a = a.parentElement) op *= parseFloat(getComputedStyle(a).opacity);
      const fillOpaque = cs.fill !== 'none' && parseFloat(cs.fillOpacity) * op > 0.9;
      if (fillOpaque) return false;
    }
    return false;
  };
  const skipAnc = el => el.closest('defs,marker,clipPath,pattern,mask,symbol,text');
  svgs.forEach((svg, si) => {
    if (svg.parentElement && svg.parentElement.closest('svg')) return;
    const texts = [...svg.querySelectorAll('text')].filter(t => t.getClientRects().length && t.textContent.trim());
    if (!texts.length) return;
    svg.scrollIntoView({block:'start',behavior:'instant'}); const r0 = svg.getBoundingClientRect();
    if (r0.width < 2) return;
    const fig = svg.closest('figure,.ex,.map,.proc-card,article,section');
    let cap = svg.getAttribute('aria-label') || '';
    if (!cap && fig) { const fc = fig.querySelector('figcaption,b,h4,.tag'); if (fc) cap = fc.textContent.trim().slice(0, 40); }
    const sec = svg.closest('main>section');
    const geos = [...svg.querySelectorAll('line,path,polyline,polygon,rect,circle,ellipse')].filter(g => !skipAnc(g) && g.getClientRects().length);
    const items = [];
    geos.forEach(g => {
      const cs = getComputedStyle(g);
      if (cs.visibility === 'hidden' || parseFloat(cs.opacity) === 0) return;
      const stroked = cs.stroke && cs.stroke !== 'none' && parseFloat(cs.strokeWidth) > 0 && parseFloat(cs.strokeOpacity) > 0;
      const filled = cs.fill && cs.fill !== 'none' && parseFloat(cs.fillOpacity) > 0;
      let small = false;
      try { const b = g.getBBox(); small = b.width * b.height < 500; } catch (e) {}
      if (!stroked && !(filled && small)) return;
      let len = 0; try { len = g.getTotalLength(); } catch (e) { return; }
      if (!len) return;
      const ctm = g.getScreenCTM(); if (!ctm) return;
      const n = Math.min(1500, Math.max(8, Math.ceil(len / 1.2)));
      const pts = [];
      for (let i = 0; i <= n; i++) { const p = g.getPointAtLength(len * i / n); const q = p.matrixTransform(ctm); if (visAt(g, q.x, q.y)) pts.push([q.x, q.y]); }
      items.push({ g, pts });
    });
    const trs = texts.map(t => { const r = t.getBoundingClientRect(); const ih = r.height * 0.12; return { t, x1: r.left - 2, x2: r.right + 2, y1: r.top + ih - 1, y2: r.bottom - ih + 1 }; });
    trs.forEach((tr, ti) => {
      const hits = new Set();
      const tcs = getComputedStyle(tr.t);
      const halo = /^stroke/.test(tcs.paintOrder) && parseFloat(tcs.strokeWidth) >= 3;  // 有底色光暈的標註會遮住下方格線
      items.forEach(({ g, pts }) => {
        if (halo || tr.t.contains(g)) return;
        let c = 0;
        for (const [x, y] of pts) if (x > tr.x1 && x < tr.x2 && y > tr.y1 && y < tr.y2) c++;
        if (c) hits.add(`${g.tagName}.${g.getAttribute('class') || ''}${g.id ? '#' + g.id : ''}[${c}]`);
      });
      trs.forEach((o, oi) => {
        if (oi <= ti) return;
        const ox = Math.min(tr.x2, o.x2) - Math.max(tr.x1, o.x1), oy = Math.min(tr.y2, o.y2) - Math.max(tr.y1, o.y1);
        if (ox > 3 && oy > 3) hits.add('TEXT:' + o.t.textContent.trim().slice(0, 20));
      });
      { const r = tr.t.getBoundingClientRect(); if (r.left < r0.left - 0.5 || r.right > r0.right + 0.5 || r.top + r.height * .15 < r0.top - 0.5 || r.bottom - r.height * .15 > r0.bottom + 0.5) hits.add('CLIP'); }
      if (hits.size) out.push({ svg: si, sec: sec ? sec.id : '', cap, text: tr.t.textContent.trim().slice(0, 30), hits: [...hits].slice(0, 6) });
    });
  });
  return out;
}
"""


async def main():
    base = sys.argv[1]
    widths = [1280, 390]
    res = {}
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for page in sys.argv[2:]:
            for w in widths:
                pg = await b.new_page(viewport={'width': w, 'height': 900})
                await pg.goto(base + page)
                await pg.wait_for_timeout(400)
                r = await pg.evaluate(JS)
                for x in r:
                    x['w'] = w
                res.setdefault(page, []).extend(r)
                await pg.close()
        await b.close()
    print(json.dumps(res, ensure_ascii=False, indent=0))

asyncio.run(main())
