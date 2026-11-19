# Saved posts — local searchable copy

Two sources, one search. No API, no MCP server.

| Source | Count | Range | File |
|---|---|---|---|
| X bookmarks (@GAristote) | 1598 | 2020-11-21 → 2026-11-10 | `bookmarks.jsonl` |
| Threads saves | 250 | 2025-07-30 → 2026-11-09 | `threads.jsonl` |

First captured 2026-11-06, last refreshed 2026-11-10.
The `.jsonl` files are the source of truth — refreshes merge into them by id.

## Searching

```
python3 search.py rive animation            # all terms must match (AND), both sources
python3 search.py shader --since 2026-01-01
python3 search.py --source threads --limit 40
python3 search.py --author 60fps
python3 search.py figma --full
```

Searches text, handle, name, quoted text and links. Results interleave both sources,
newest first, each tagged `[x]` or `[threads]`. For anything the script can't express,
grep the JSONL directly — one record per line, same field names in both files:
`id, date, handle, name, text, links, has_media, likes, url, quoted, source`

## Browsing instead of searching

Keyword search only reads captions, and most saves are images or video with a few words
of caption — so a design saved with "v2 🚧" is invisible to it. Two things cover that gap:

- `inspo.md` — every save grouped into 40 surfaces (onboarding, motion, dashboards,
  wallet, widgets…) with a linked contents list. Rebuild with `python3 build_inspo.py`.
  The nine hand-curated finance groups at the top are preserved across rebuilds; the rest
  is bucketed by keyword, one bucket per post, so expect some drift.
- `contact-sheet.html` — open it in a browser for a visual grid of all 1848 posts with
  live filtering by text, source, year and has-image. Rebuild with `python3 build_sheet.py`.
  1503 of the X saves carry thumbnails; the 31 newest and all Threads saves don't.

## What's in the data

- **X**: 96% have media, 19% have under 25 characters of text. The value is often in the
  video, not the text — searching by `--author` or `--since` often beats keywords.
- **Threads**: much better text (5% thin), but `likes` is always null and `links` is empty —
  external URLs appear inline in the text instead (e.g. "affectui.com"), so searching a
  domain still works.

## Refreshing

Captures are merged, never overwritten, so nothing is lost if you later unsave something.

1. **X** — open `x.com/i/history` (tab "Bookmarks"), paste `capture.js`, let it scroll.
2. **Threads** — open `threads.com/saved`, paste `capture_threads.js`, let it walk.
3. Put both downloads in this folder as `x-refresh.json` / `threads-refresh.json`, then:
   `python3 merge.py` — it reports what's new and skips anything already stored.

### The page-one gotcha (X only)

X's app grabs a reference to `window.fetch` when it boots. If the hook is installed after
that, it still catches pagination (pages 2+) but **never sees page one** — which is exactly
where new bookmarks live. Re-patching `window.fetch` afterwards does nothing, because the app
is still calling the first wrapper it captured.

Two ways through it:
- Paste `capture.js` while the X splash screen is still up, before the timeline renders, or
- let the hook take pages 2+ and harvest the newest ~20 posts from the DOM
  (`article[data-testid="tweet"]`), which is what `merge.py`'s `from_dom` handles.

DOM-harvested records are thinner: no like counts, and links may be missing. The hook version
wins on an id collision, so a later full capture upgrades them automatically.
