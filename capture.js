// Paste into the Chrome console on x.com/i/history BEFORE the Bookmarks timeline loads
// (reload the page right after pasting if it already rendered).
// Auto-scrolls to the end, then downloads x-bookmarks-raw.json.
(() => {
  if (window.__bm) return 'already running';
  window.__bm = { raw: [] };
  const of = window.fetch;
  window.fetch = async function (...a) {
    const res = await of.apply(this, a);
    try {
      const u = typeof a[0] === 'string' ? a[0] : (a[0] && a[0].url) || '';
      if (/Bookmarks/i.test(u)) res.clone().json().then(j => window.__bm.raw.push(j)).catch(() => {});
    } catch (e) {}
    return res;
  };

  const pick = r => (r && r.__typename === 'TweetWithVisibilityResults') ? r.tweet : r;
  window.__extract = () => {
    const out = new Map();
    for (const j of window.__bm.raw)
      for (const i of (j?.data?.bookmark_timeline_v2?.timeline?.instructions || []))
        for (const e of (i.entries || [])) {
          const r = pick(e?.content?.itemContent?.tweet_results?.result);
          if (!r) continue;
          const id = r.rest_id || r.legacy?.id_str;
          if (!id || out.has(id)) continue;
          const u = r.core?.user_results?.result || {}, ul = u.legacy || {}, lg = r.legacy || {};
          const handle = u.core?.screen_name || ul.screen_name || '';
          const note = r.note_tweet?.note_tweet_results?.result;
          const q = pick(r.quoted_status_result?.result);
          out.set(id, {
            id, url: `https://x.com/${handle || 'i'}/status/${id}`,
            handle, name: u.core?.name || ul.name || '',
            created_at: lg.created_at || '',
            text: note?.text || lg.full_text || '',
            links: (note?.entity_set?.urls || lg.entities?.urls || []).map(x => x.expanded_url).filter(Boolean),
            media: (lg.extended_entities?.media || lg.entities?.media || []).map(m => ({ type: m.type, url: m.media_url_https })),
            replies: lg.reply_count ?? null, reposts: lg.retweet_count ?? null, likes: lg.favorite_count ?? null,
            quoted: q ? { handle: q.core?.user_results?.result?.core?.screen_name || '', text: q.note_tweet?.note_tweet_results?.result?.text || q.legacy?.full_text || '' } : null
          });
        }
    return [...out.values()];
  };

  let last = 0, stagnant = 0;
  const iv = setInterval(() => {
    window.scrollTo(0, document.documentElement.scrollHeight);
    const n = window.__extract().length;
    if (n === last) stagnant++; else { stagnant = 0; last = n; console.log('captured', n); }
    if (stagnant > 30) {
      clearInterval(iv);
      const blob = new Blob([JSON.stringify(window.__extract())], { type: 'application/json' });
      const a = document.createElement('a');
      a.href = URL.createObjectURL(blob); a.download = 'x-bookmarks-raw.json';
      document.body.appendChild(a); a.click(); a.remove();
      console.log('done —', last, 'bookmarks downloaded');
    }
  }, 1200);
  return 'capturing…';
})();
