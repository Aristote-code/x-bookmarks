#!/usr/bin/env python3
"""Rebuild inspo.md as a full inspiration index.

Hand-curated finance groups are preserved by reading them back out of the existing
file; everything else is bucketed by surface keywords, one post per bucket.
"""
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
MD = os.path.join(HERE, "inspo.md")

rows = {}
for src, fn in (("x", "bookmarks.jsonl"), ("threads", "threads.jsonl")):
    for l in open(os.path.join(HERE, fn)):
        r = json.loads(l); r.setdefault("source", src); rows[r["url"]] = r

# The hand-curated finance groups. Only these are preserved from the existing file —
# without the whitelist every auto-bucketed URL would read back as "curated" on a
# second run and the buckets below would never apply again.
FINANCE_GROUPS = [
    "Wallet & payments", "Cards", "Transactions, invoices & billing",
    "Budget, savings & trackers", "Trading, stocks & crypto",
    "Motion details worth stealing", "Widgets",
    "Direction & craft (not screens — how finance should feel)",
    "Adjacent — pricing pages & business dashboards",
]
curated, order = {}, []
if os.path.exists(MD):
    cur = None
    for line in open(MD):
        h = re.match(r"^## (.+?)\s*$", line)
        if h:
            cur = h.group(1) if h.group(1) in FINANCE_GROUPS else None
            if cur and cur not in order: order.append(cur)
        u = re.search(r"(https?://\S+)\s*$", line)
        if u and cur: curated[u.group(1)] = cur

# surface buckets, most specific first — each post lands in exactly one
BUCKETS = [
 ("Onboarding",                      r"\bonboard(ing)?\b|\bwelcome screen\b|\bsign ?up\b|\bsign ?in\b|\blog ?in\b|\bfirst run\b|\bwalkthrough\b"),
 ("Paywall & pricing",               r"\bpaywall\b|\bpricing\b|\bsubscription\b|\bupgrade screen\b|\bplan(s)? (page|screen)\b"),
 ("App Store & launch",              r"\bapp ?store\b|\bplay ?store\b|\bscreen ?shots?\b|\baso\b|\blaunch video\b"),
 ("Dashboards & analytics",          r"\bdashboard\b|\banalytics\b|\bmetrics\b|\boverview\b|\bkpi\b|\breport(s|ing)?\b|\binsight(s)?\b"),
 ("Charts & data viz",               r"\bchart(s)?\b|\bgraph(s)?\b|\bdata ?vi[sz]\b|\bvisuali[sz]ation\b|\bstat(s)?\b"),
 ("E-commerce & checkout",           r"\bcheckout\b|\bcart\b|\be-?commerce\b|\bshop(ping)?\b|\bproduct page\b|\border(s|ing)?\b|\bstorefront\b"),
 ("Chat & messaging",                r"\bchat\b|\bmessag(e|es|ing)\b|\binbox\b|\bconversation\b|\bcomment(s)?\b|\bdm(s)?\b"),
 ("Calendar, tasks & scheduling",    r"\bcalendar\b|\bschedul(e|ing)\b|\bbooking\b|\breminder(s)?\b|\bto-?do\b|\btask(s)?\b|\bagenda\b|\bplanner\b"),
 ("Maps & location",                 r"\bmap(s)?\b|\blocation\b|\bnavigation app\b|\bgps\b|\bdelivery track"),
 ("Media players & audio",           r"\bplayer\b|\bmusic\b|\baudio\b|\bpodcast\b|\bvideo (app|player)\b|\bspotify\b|\bplaylist\b"),
 ("Camera, photo & gallery",         r"\bcamera\b|\bphoto(s)?\b|\bgaller(y|ies)\b|\balbum(s)?\b|\bfilter app\b"),
 ("Health, fitness & wellbeing",     r"\bfitness\b|\bhealth\b|\bworkout\b|\bsteps? app\b|\bsleep\b|\bmeditat(e|ion)\b|\bwellbeing\b|\bmedal(s)?\b"),
 ("Travel & transport",              r"\btravel\b|\bflight(s)?\b|\bhotel(s)?\b|\btrip(s)?\b|\bride\b|\bev\b|\bcharging\b|\btransport\b"),
 ("Games & playful",                 r"\bgame(s)?\b|\bplayful\b|\bpuzzle\b|\barcade\b|\bleaderboard\b|\bgamif(y|ication|ied)\b|\bstreak(s)?\b|\bbadge(s)?\b|\breward(s)?\b"),
 ("Navigation, tabs & menus",        r"\bnav(bar|igation)?\b|\btab ?bar\b|\bsidebar\b|\bmenu\b|\bdrawer\b|\bbottom sheet\b|\bheader\b|\bfooter\b"),
 ("Lists, feeds & tables",           r"\bfeed\b|\blist\b|\btable\b|\bgrid\b|\bcollection\b|\bcard stack\b|\bcarousel\b"),
 ("Forms, inputs & search",          r"\bform(s)?\b|\binput(s)?\b|\btext ?field\b|\bsearch\b|\bfilter(s|ing)?\b|\bkeyboard\b|\bpicker\b|\bslider\b|\btoggle\b|\bdropdown\b"),
 ("Modals, sheets & notifications",  r"\bmodal\b|\bpopover\b|\btooltip\b|\btoast\b|\bnotification(s)?\b|\balert\b|\bdialog\b|\bsheet\b"),
 ("Buttons & controls",              r"\bbutton(s)?\b|\bcta\b|\bswitch\b|\bstepper\b|\bcontrol(s)?\b|\bfab\b"),
 ("Empty, loading & success states", r"\bempty state(s)?\b|\bloading\b|\bloader\b|\bskeleton\b|\bsuccess\b|\berror\b|\bsplash\b|\bprogress\b|\bconfetti\b"),
 ("Profile & settings",              r"\bprofile\b|\bsettings\b|\baccount\b|\bavatar(s)?\b|\bpreferences\b"),
 ("Motion & micro-interactions",     r"\banimat(e|ed|ion|ions)\b|\bmicro[- ]?interaction\b|\btransition(s)?\b|\beasing\b|\bkeyframe(s)?\b|\bmotion\b|\brive\b|\blottie\b|\bspring\b|\bhaptic|\bgesture(s)?\b|\bscroll\b|\bhover\b|\bparallax\b"),
 ("3D, shaders & visual effects",    r"\bshader(s)?\b|\b3d\b|\bthree\.?js\b|\bwebgl\b|\bblender\b|\bglass\b|\bblur\b|\bglow\b|\bparticle(s)?\b|\bgradient(s)?\b|\bnoise\b|\bliquid\b"),
 ("Icons & illustration",            r"\bicon(s|set)?\b|\billustrat(e|ion|ions)\b|\bmascot\b|\bcharacter\b|\bsvg\b|\bdrawing\b|\bart(work)?\b"),
 ("Typography",                      r"\btypograph(y|ic)\b|\btypeface\b|\bfont(s)?\b|\bkerning\b|\btype scale\b|\btext style(s)?\b"),
 ("Design systems & tokens",         r"\bdesign system(s)?\b|\btoken(s)?\b|\bcomponent(s)?\b|\bui kit\b|\bstyle guide\b|\bvariant(s)?\b|\blibrar(y|ies)\b"),
 ("Landing & marketing pages",       r"\blanding page\b|\bhero\b|\bwebsite\b|\bmarketing\b|\bbento\b|\bportfolio\b|\bweb ?site\b"),
 ("Tools, AI & workflow",            r"\bclaude\b|\bopus\b|\bgpt\b|\bgemini\b|\bprompt(s|ing)?\b|\bskill\b|\bmcp\b|\bplugin\b|\bworkflow\b|\bcursor\b|\bfigma\b|\bai\b"),
 ("General app screens",             r"\bscreen(s)?\b|\bpage(s)?\b|\bflow\b|\bui\b|\bux\b|\bapp\b|\bconcept\b|\bredesign\b|\bmobile\b|\binterface\b|\bprototype\b|\bdesign\b"),
]

def bucket(r):
    hay = " ".join([r["text"], r.get("name", "")]).lower()
    if not r["text"].strip():
        return "Image-only — no caption to search"
    for name, pat in BUCKETS:
        if re.search(pat, hay):
            return name
    return "Everything else"

groups = {}
for url, r in rows.items():
    g = curated.get(url) or bucket(r)
    groups.setdefault(g, []).append(r)

# curated finance groups keep their original order and sit first
rest = [g for g in groups if g not in order]
pinned = [g for g in order if g in groups]
tail = ["Everything else", "Image-only — no caption to search"]
rest = [g for g in rest if g not in tail]
rest.sort(key=lambda g: -len(groups[g]))
ordered = list(dict.fromkeys(pinned + rest + [g for g in tail if g in groups]))

out = ["# UI inspiration — every saved post\n",
       f"All {len(rows)} saves from X bookmarks + Threads, grouped by what the design is.",
       "Captions are short because most of these are images or video — open the link to see it.",
       "The curated finance groups come first; everything after is bucketed by keyword, so",
       "expect some drift. For the image-only ones, open `contact-sheet.html` and scan by eye.\n",
       "## Contents\n"]
for g in ordered:
    anchor = re.sub(r"[^a-z0-9]+", "-", g.lower()).strip("-")
    out.append(f"- [{g}](#{anchor}) — {len(groups[g])}")

for g in ordered:
    out.append(f"\n## {g}\n")
    for r in sorted(groups[g], key=lambda r: r["date"], reverse=True):
        t = " ".join(r["text"].split())[:110] or "_no caption_"
        out.append(f"- **@{r['handle']}** · {r['date']} · `{r['source']}` — {t}  \n  {r['url']}")

open(MD, "w").write("\n".join(out) + "\n")
print(f"{len(rows)} posts across {len(ordered)} groups")
for g in ordered:
    print(f"  {len(groups[g]):>4}  {g}")
