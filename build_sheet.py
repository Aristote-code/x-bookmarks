#!/usr/bin/env python3
"""Generate contact-sheet.html — a visual grid of every saved post, for eyeballing
the image-only ones that keyword search can't reach."""
import json, os, html

HERE = os.path.dirname(os.path.abspath(__file__))
items = []
for src, fn in (("x", "bookmarks.jsonl"), ("threads", "threads.jsonl")):
    p = os.path.join(HERE, fn)
    if not os.path.exists(p):
        continue
    for l in open(p):
        r = json.loads(l)
        m = r.get("media") or []
        items.append({
            "h": r["handle"], "d": r["date"], "s": r.get("source", src),
            "t": " ".join(r["text"].split())[:200],
            "u": r["url"],
            "i": m[0]["url"] if m else "",
            "v": 1 if any(x.get("type") in ("video", "animated_gif") for x in m) else 0,
        })
items.sort(key=lambda x: x["d"], reverse=True)
data = json.dumps(items, ensure_ascii=False, separators=(",", ":"))

tpl = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Saved Posts</title>
<style>
:root{--bg:#fff;--fg:#14161a;--muted:#6b7280;--line:#e5e7eb;--card:#fff;--accent:#2563eb}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#0d0f12;--fg:#e8eaed;--muted:#9aa2ad;--line:#242a31;--card:#14171b;--accent:#6ea8fe}}
:root[data-theme="dark"]{--bg:#0d0f12;--fg:#e8eaed;--muted:#9aa2ad;--line:#242a31;--card:#14171b;--accent:#6ea8fe}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.5 ui-sans-serif,-apple-system,"Segoe UI",sans-serif}
header{position:sticky;top:0;z-index:5;background:var(--bg);border-bottom:1px solid var(--line);padding:14px 16px}
.bar{display:flex;gap:10px;flex-wrap:wrap;align-items:center;max-width:1600px;margin:0 auto}
input[type=search]{flex:1;min-width:220px;padding:9px 12px;border:1px solid var(--line);border-radius:9px;background:var(--card);color:var(--fg);font-size:15px}
select,label.tog{padding:8px 11px;border:1px solid var(--line);border-radius:9px;background:var(--card);color:var(--fg);font-size:14px;cursor:pointer}
label.tog{display:flex;align-items:center;gap:7px;user-select:none}
#count{color:var(--muted);font-size:14px;white-space:nowrap}
main{max-width:1600px;margin:0 auto;padding:16px;display:grid;gap:14px;grid-template-columns:repeat(auto-fill,minmax(230px,1fr))}
a.card{display:flex;flex-direction:column;background:var(--card);border:1px solid var(--line);border-radius:12px;overflow:hidden;text-decoration:none;color:inherit}
a.card:hover{border-color:var(--accent)}
.thumb{width:100%;aspect-ratio:1/1;object-fit:cover;display:block;background:var(--line)}
.noimg{width:100%;aspect-ratio:1/1;display:flex;align-items:center;justify-content:center;color:var(--muted);font-size:13px;background:var(--line)}
.meta{padding:9px 11px 11px;font-size:13px}
.who{display:flex;justify-content:space-between;gap:8px;color:var(--muted);font-size:12px;margin-bottom:5px}
.txt{display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}
.tag{position:absolute;top:0;left:0;margin:7px;padding:1px 6px;border-radius:5px;background:rgba(0,0,0,.65);color:#fff;font-size:11px}
.wrap{position:relative}
#more{display:block;margin:22px auto 40px;padding:11px 22px;border:1px solid var(--line);border-radius:9px;background:var(--card);color:var(--fg);font-size:15px;cursor:pointer}
@media (max-width:640px){main{grid-template-columns:repeat(auto-fill,minmax(150px,1fr));padding:12px 16px}}
</style></head><body>
<header><div class="bar">
<input type="search" id="q" placeholder="filter by text or @handle…" autocomplete="off">
<select id="src"><option value="">both sources</option><option value="x">X only</option><option value="threads">Threads only</option></select>
<select id="yr"><option value="">any year</option></select>
<label class="tog"><input type="checkbox" id="img" checked> with image</label>
<span id="count"></span>
</div></header>
<main id="grid"></main>
<button id="more" hidden>Show more</button>
<script>
const DATA = __DATA__;
const grid=document.getElementById('grid'),q=document.getElementById('q'),src=document.getElementById('src'),
      yr=document.getElementById('yr'),img=document.getElementById('img'),count=document.getElementById('count'),
      more=document.getElementById('more');
[...new Set(DATA.map(d=>d.d.slice(0,4)))].sort().reverse().forEach(y=>{
  const o=document.createElement('option');o.value=y;o.textContent=y;yr.appendChild(o);});
let shown=0,cur=[];
const PAGE=120;
function filt(){
  const t=q.value.trim().toLowerCase(), s=src.value, y=yr.value, i=img.checked;
  return DATA.filter(d=>{
    if(s&&d.s!==s)return false;
    if(y&&!d.d.startsWith(y))return false;
    if(i&&!d.i)return false;
    if(t&&!(d.t.toLowerCase().includes(t)||d.h.toLowerCase().includes(t)))return false;
    return true;});
}
function esc(s){const e=document.createElement('div');e.textContent=s;return e.innerHTML;}
function render(reset){
  if(reset){cur=filt();shown=0;grid.innerHTML='';}
  const slice=cur.slice(shown,shown+PAGE);
  grid.insertAdjacentHTML('beforeend', slice.map(d=>`<a class="card" href="${d.u}" target="_blank" rel="noopener">
<div class="wrap">${d.i?`<img class="thumb" loading="lazy" src="${d.i}" alt="">`:`<div class="noimg">no image</div>`}${d.v?'<span class="tag">video</span>':''}</div>
<div class="meta"><div class="who"><span>@${esc(d.h)}</span><span>${d.d}</span></div>
<div class="txt">${esc(d.t)||'<i>no caption</i>'}</div></div></a>`).join(''));
  shown+=slice.length;
  count.textContent=`${cur.length} post${cur.length===1?'':'s'}`;
  more.hidden=shown>=cur.length;
}
[q,src,yr,img].forEach(el=>el.addEventListener('input',()=>render(true)));
more.addEventListener('click',()=>render(false));
render(true);
</script></body></html>"""

open(os.path.join(HERE, "contact-sheet.html"), "w").write(tpl.replace("__DATA__", data))
print(f"contact-sheet.html — {len(items)} posts, {sum(1 for i in items if i['i'])} with thumbnails")
