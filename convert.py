import json, sys, re, collections
from datetime import datetime

src, out = sys.argv[1], sys.argv[2]
data = json.load(open(src))

def iso(s):
    try: return datetime.strptime(s, "%a %b %d %H:%M:%S %z %Y").strftime("%Y-%m-%d")
    except Exception: return ""

recs, no_text, with_links = [], 0, 0
for t in data:
    text = re.sub(r"https://t\.co/\w+", "", t.get("text", "")).strip()
    text = re.sub(r"\s+\n", "\n", text)
    links = [l for l in t.get("links", []) if "t.co" not in l]
    if len(text) < 25: no_text += 1
    if links: with_links += 1
    recs.append({
        "id": t["id"], "date": iso(t.get("created_at", "")),
        "handle": t.get("handle", ""), "name": t.get("name", ""),
        "text": text, "links": links,
        "has_media": bool(t.get("media")),
        "likes": t.get("likes"), "url": t.get("url"),
        "quoted": (t.get("quoted") or {}).get("text", "") if t.get("quoted") else "",
    })

recs.sort(key=lambda r: r["date"], reverse=True)
with open(out, "w") as f:
    for r in recs:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")

authors = collections.Counter(r["handle"] for r in recs)
dates = [r["date"] for r in recs if r["date"]]
print(f"total        {len(recs)}")
print(f"date range   {min(dates)} -> {max(dates)}")
print(f"thin text    {no_text}  ({100*no_text//len(recs)}%)")
print(f"has links    {with_links}  ({100*with_links//len(recs)}%)")
print(f"has media    {sum(1 for r in recs if r['has_media'])}")
print("top authors  " + ", ".join(f"@{a}({n})" for a, n in authors.most_common(8)))
