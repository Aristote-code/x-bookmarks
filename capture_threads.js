// Paste into the Chrome console on threads.com/saved.
// Walks the feed incrementally (it virtualizes hard — only ~7 posts exist in the DOM
// at a time), harvesting as it goes, then downloads threads-saved-raw.json.
(() => {
  if (window.__P) return 'already running';
  window.__P = new Map();
  const harvest = () => {
    for (const c of document.querySelectorAll('[data-pressable-container="true"]')) {
      const a = [...c.querySelectorAll('a[href*="/post/"]')].find(x => !/\/media$/.test(x.getAttribute('href') || ''));
      if (!a) continue;
      const m = (a.getAttribute('href') || '').match(/^\/@([\w.\-]+)\/post\/([\w-]+)/);
      if (!m) continue;
      const block = c.innerText || '', prev = window.__P.get(m[2]);
      if (prev && prev.block.length >= block.length) continue;
      const t = c.querySelector('time[datetime]');
      window.__P.set(m[2], {
        code: m[2], handle: m[1],
        url: `https://www.threads.com/@${m[1]}/post/${m[2]}`,
        datetime: t ? t.getAttribute('datetime') : '',
        block,
        links: [...new Set([...c.querySelectorAll('a[href^="http"]')].map(x => x.href).filter(h => !/threads\.(net|com)/i.test(h)))]
      });
    }
    return window.__P.size;
  };
  window.scrollTo(0, 0);
  let stagnant = 0, last = 0;
  const iv = setInterval(() => {
    window.scrollBy(0, 650);
    const n = harvest();
    const bottom = window.scrollY + window.innerHeight >= document.documentElement.scrollHeight - 200;
    if (n === last && bottom) stagnant++; else { if (n !== last) { stagnant = 0; console.log('captured', n); } last = n; }
    if (stagnant > 40) {
      clearInterval(iv);
      const blob = new Blob([JSON.stringify([...window.__P.values()])], { type: 'application/json' });
      const a = document.createElement('a');
      a.href = URL.createObjectURL(blob); a.download = 'threads-saved-raw.json';
      document.body.appendChild(a); a.click(); a.remove();
      console.log('done —', last, 'saved posts downloaded');
    }
  }, 450);
  return 'capturing…';
})();
