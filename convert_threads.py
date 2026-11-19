#!/usr/bin/env python3
"""Convert the Threads saved-posts capture into threads.jsonl."""
import json, sys, re, os, collections

src = sys.argv[1] if len(sys.argv) > 1 else "threads-raw.json"
out = sys.argv[2] if len(sys.argv) > 2 else "threads.jsonl"
data = json.load(open(src))

DATEISH = re.compile(r"^(\d{1,2}/\d{1,2}/\d{2,4}|\d+[smhdw]|now|Just now)$", re.I)
COUNTY = re.compile(r"^[\d.,]+[KM]?$")

recs, thin = [], 0
for p in data:
    lines = [l.strip() for l in (p.get("block") or "").split("\n")]
    if lines and lines[0] == p["handle"]:
        lines = lines[1:]
    if lines and DATEISH.match(lines[0] or ""):
        lines = lines[1:]
    while lines and (COUNTY.match(lines[-1] or "") or not lines[-1]):
        lines.pop()
    text = "\n".join(l for l in lines if l).strip()
    if len(text) < 25:
        thin += 1
    recs.append({
        "id": p["code"],
        "date": (p.get("datetime") or "")[:10],
        "handle": p["handle"], "name": "",
        "text": text,
        "links": p.get("links") or [],
        "has_media": False,
        "likes": None,
        "url": p["url"],
        "quoted": "",
        "source": "threads",
    })

recs.sort(key=lambda r: r["date"], reverse=True)
with open(out, "w") as f:
    for r in recs:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")

dates = [r["date"] for r in recs if r["date"]]
authors = collections.Counter(r["handle"] for r in recs)
print(f"total       {len(recs)}")
print(f"date range  {min(dates)} -> {max(dates)}" if dates else "no dates")
print(f"no datetime {sum(1 for r in recs if not r['date'])}")
print(f"thin text   {thin} ({100*thin//len(recs)}%)")
print(f"with links  {sum(1 for r in recs if r['links'])}")
print("top authors " + ", ".join(f"@{a}({n})" for a, n in authors.most_common(6)))
