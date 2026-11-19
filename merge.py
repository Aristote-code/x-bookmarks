#!/usr/bin/env python3
"""Merge a refresh capture into the existing jsonl files. Idempotent — matches on id."""
import json, os, re, sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))

def load(fn):
    p = os.path.join(HERE, fn)
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else []

def write(fn, recs):
    recs.sort(key=lambda r: r["date"], reverse=True)
    with open(os.path.join(HERE, fn), "w") as f:
        for r in recs:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

def xdate(s):
    try: return datetime.strptime(s, "%a %b %d %H:%M:%S %z %Y").strftime("%Y-%m-%d")
    except Exception: return ""

def from_hook(t):
    text = re.sub(r"https://t\.co/\w+", "", t.get("text", "")).strip()
    return {"id": t["id"], "date": xdate(t.get("created_at", "")), "handle": t.get("handle", ""),
            "name": t.get("name", ""), "text": text,
            "links": [l for l in (t.get("links") or []) if "t.co" not in l],
            "has_media": bool(t.get("media")), "likes": t.get("likes"), "url": t.get("url"),
            "quoted": (t.get("quoted") or {}).get("text", "") if t.get("quoted") else "", "source": "x"}

def from_dom(d):
    return {"id": d["id"], "date": (d.get("datetime") or "")[:10], "handle": d.get("handle", ""),
            "name": "", "text": (d.get("text") or "").strip(), "links": d.get("links") or [],
            "has_media": bool(d.get("hasMedia")), "likes": None, "url": d.get("url"),
            "quoted": "", "source": "x"}

DATEISH = re.compile(r"^(\d{1,2}/\d{1,2}/\d{2,4}|\d+[smhdw]|now|Just now)$", re.I)
COUNTY = re.compile(r"^[\d.,]+[KM]?$")

def from_threads(p):
    lines = [l.strip() for l in (p.get("block") or "").split("\n")]
    if lines and lines[0] == p["handle"]: lines = lines[1:]
    if lines and DATEISH.match(lines[0] or ""): lines = lines[1:]
    while lines and (COUNTY.match(lines[-1] or "") or not lines[-1]): lines.pop()
    return {"id": p["code"], "date": (p.get("datetime") or "")[:10], "handle": p["handle"], "name": "",
            "text": "\n".join(l for l in lines if l).strip(), "links": p.get("links") or [],
            "has_media": False, "likes": None, "url": p["url"], "quoted": "", "source": "threads"}

def merge(existing_fn, incoming, label):
    cur = load(existing_fn)
    have = {r["id"]: r for r in cur}
    added = []
    for rec in incoming:
        if not rec["id"] or rec["id"] in have:
            continue
        have[rec["id"]] = rec
        added.append(rec)
    write(existing_fn, list(have.values()))
    print(f"{label}: {len(cur)} -> {len(have)}  (+{len(added)})")
    for r in sorted(added, key=lambda r: r["date"], reverse=True):
        t = r["text"].replace("\n", " ")[:90] or "(no text — media post)"
        print(f"   {r['date']}  @{r['handle']}  {t}")
    return added

x = json.load(open(os.path.join(HERE, "x-refresh.json")))
# hook records are richer than DOM ones, so they go in first and win on id collisions
merge("bookmarks.jsonl", [from_hook(t) for t in x["hook"]] + [from_dom(d) for d in x["dom"]], "X bookmarks")
print()
th = json.load(open(os.path.join(HERE, "threads-refresh.json")))
merge("threads.jsonl", [from_threads(p) for p in th], "Threads saves")
