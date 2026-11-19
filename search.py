#!/usr/bin/env python3
"""Search saved X bookmarks + Threads saves.
Usage: python3 search.py <terms...> [--author H] [--since YYYY-MM-DD] [--source x|threads] [--limit N] [--full]"""
import json, sys, os, argparse

HERE = os.path.dirname(os.path.abspath(__file__))
FILES = {"x": "bookmarks.jsonl", "threads": "threads.jsonl"}

p = argparse.ArgumentParser()
p.add_argument("terms", nargs="*")
p.add_argument("--author", default=None)
p.add_argument("--since", default=None)
p.add_argument("--source", default=None, choices=["x", "threads"])
p.add_argument("--limit", type=int, default=25)
p.add_argument("--full", action="store_true")
a = p.parse_args()

rows = []
for src, fn in FILES.items():
    path = os.path.join(HERE, fn)
    if not os.path.exists(path):
        continue
    for line in open(path):
        r = json.loads(line)
        r.setdefault("source", src)
        rows.append(r)

def hay(r):
    return " ".join([r["text"], r["handle"], r.get("name", ""), r.get("quoted", ""),
                     " ".join(r.get("links") or [])]).lower()

hits = rows
if a.source:
    hits = [r for r in hits if r["source"] == a.source]
if a.author:
    hits = [r for r in hits if a.author.lstrip("@").lower() in r["handle"].lower()]
if a.since:
    hits = [r for r in hits if r["date"] >= a.since]
for term in a.terms:
    t = term.lower()
    hits = [r for r in hits if t in hay(r)]

hits.sort(key=lambda r: r["date"], reverse=True)
by = {}
for r in hits:
    by[r["source"]] = by.get(r["source"], 0) + 1
tally = ", ".join(f"{v} {k}" for k, v in sorted(by.items())) or "none"
print(f"{len(hits)} match(es) ({tally})" + (f", showing {a.limit}" if len(hits) > a.limit else ""))

for r in hits[: a.limit]:
    txt = r["text"].replace("\n", " ")
    if not a.full and len(txt) > 220:
        txt = txt[:220] + "…"
    likes = f"  ♥{r['likes']}" if r.get("likes") is not None else ""
    print(f"\n[{r['source']}] {r['date']}  @{r['handle']}{likes}")
    print(f"  {txt or '(no text — media post)'}")
    for l in (r.get("links") or []):
        print(f"  link: {l}")
    print(f"  {r['url']}")
