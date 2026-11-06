// The frame every chino drawing shares, so a change to the top bar, the tabs or
// the rail is made once. Load it at the end of a drawing's page, after icons.js:
//
//   <div class="computer" data-view="movies">…</div>
//       the top bar, with "movies" current. data-query="sin" shows typed text in
//       the search field; data-count="0" hides the bell's count.
//   <div class="phone" data-view="movies">…</div>
//       the top bar and the five tabs. data-tabs="web" for the web on a phone
//       (zap in place of downloads), data-tabs="none" for no tabs.
//       data-bar="back" data-title="settings" for a back arrow and a title;
//       data-bar="none" for no top bar (the player, zap).
//   <div class="tv" data-view="movies">…</div>
//       the rail, with that view current (the bell with its count, as on the
//       other sizes), and the safe area's outline.
//       data-rail="none" (with class "full") for a screen without the rail.
//   data-view="none" marks no view as current.
//
// data-co-parts="logo:1:top,views:2:top,bell:3:top" on a frame numbers the parts
// frame.js draws itself: logo, views, search, bell, avatar, tabs, back, rail,
// settings, current (the current view) (name:number:side).
//
// data-co="2" on any element inside a frame numbers that part of the drawing; the
// text under the figure says what each number is. The number sits in the margin
// left of the screen, level with the element, with a line to it;
// data-co-side="right" puts it in the right margin. Two numbers on one side at
// the same height push each other down, so number things at different heights,
// or put one on the right.
(function () {
  const icon = (name, cls = '') => `<i data-i="${name}" class="${cls}"></i>`;
  const logo = '<span class="logo"><svg viewBox="0 0 14 18"><path d="M2 2 L11 9 L2 16" fill="none" stroke="#58A6FF" stroke-width="3"/></svg>chino</span>';
  const views = ['home', 'movies', 'shows', 'watchlist', 'zap'];
  const bell = (count) => `<span class="icon-b bell">${icon('bell')}${count === '0' ? '' : `<span class="count">${count || 2}</span>`}</span>`;
  const make = (html) => { const t = document.createElement('template'); t.innerHTML = html.trim(); return t.content.firstChild; };
  const lift = () => {};

  for (const f of document.querySelectorAll('.computer')) {
    const view = f.dataset.view || 'home';
    if (f.dataset.bar !== 'none') {
      const q = f.dataset.query;
      const field = q ? `<span class="field filled">${icon('search', 's16')}${q}<span class="caret" style="margin-left:1px"></span></span>`
                      : `<span class="field">${icon('search', 's16')}Search movies, shows and people</span>`;
      f.prepend(make(`<header class="tb">${logo}<nav class="views">${views.map((v) => `<span class="${v === view ? 'on' : ''}">${v}</span>`).join('')}</nav>
        <div class="end">${field}${bell(f.dataset.count)}<span class="av">au</span></div></header>`));
    }
    lift(f);
  }

  for (const f of document.querySelectorAll('.phone')) {
    const view = f.dataset.view || 'home';
    const scroll = document.createElement('div');
    scroll.className = 'scroll';
    while (f.firstChild) scroll.appendChild(f.firstChild);
    f.appendChild(scroll);
    if (f.dataset.bar === 'back') {
      f.prepend(make(`<header class="tb back"><span class="icon-b">${icon('arrow-left')}</span><span class="title">${f.dataset.title || ''}</span></header>`));
    } else if (f.dataset.bar !== 'none') {
      f.prepend(make(`<header class="tb">${logo}<span class="icon-b search">${icon('search')}</span>${bell(f.dataset.count)}<span class="av">au</span></header>`));
    }
    if (f.dataset.tabs !== 'none') {
      const tabs = f.dataset.tabs === 'web'
        ? [['home', 'house'], ['movies', 'film'], ['shows', 'tv'], ['watchlist', 'bookmark'], ['zap', 'zap']]
        : [['home', 'house'], ['movies', 'film'], ['shows', 'tv'], ['watchlist', 'bookmark'], ['downloads', 'download']];
      f.appendChild(make(`<nav class="tabs">${tabs.map(([v, i]) => `<span class="${v === view ? 'on' : ''}">${icon(i)}${v}</span>`).join('')}</nav>`));
    }
    lift(f);
  }

  for (const f of document.querySelectorAll('.tv')) {
    const view = f.dataset.view || 'home';
    if (f.dataset.rail !== 'none') {
      const count = f.dataset.count === '0' ? '' : `<span class="count">${f.dataset.count || 2}</span>`;
      const it = (v, i) => `<span class="it it-${v}${v === view ? ' cur' : ''}">${icon(i)}${v === 'notifications' ? count : ''}</span>`;
      f.appendChild(make(`<nav class="rail"><span class="av">au</span>${it('search', 'search')}${it('home', 'house')}${it('movies', 'film')}${it('shows', 'tv')}
        ${it('watchlist', 'bookmark')}${it('zap', 'zap')}<span class="gap"></span>${it('notifications', 'bell')}${it('settings', 'settings')}</nav>`));
    }
    f.appendChild(make('<div class="safe"></div>'));
    lift(f);
  }

  for (const el of document.querySelectorAll('i[data-i]')) {
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('viewBox', '0 0 24 24');
    svg.setAttribute('class', 'i ' + el.className);
    if (el.getAttribute('style')) svg.setAttribute('style', el.getAttribute('style'));
    svg.innerHTML = (window.ICONS || {})[el.dataset.i] || '';
    if (!window.ICONS?.[el.dataset.i]) console.error(`no icon "${el.dataset.i}" in icons.js`);
    el.replaceWith(svg);
  }

  
  const parts = { logo: '.tb .logo', views: '.tb .views', search: '.tb .field, .tb .search, .rail .it-search',
                  bell: '.tb .bell, .rail .it-notifications', avatar: '.tb .av, .rail .av', tabs: '.tabs',
                  back: '.tb.back .icon-b', rail: '.rail', settings: '.rail .it-settings',
                  current: '.tb .views .on, .tabs .on, .rail .it.cur' };
  for (const f of document.querySelectorAll('[data-co-parts]')) {
    for (const entry of f.dataset.coParts.split(',')) {
      const [name, n, side] = entry.trim().split(':');
      const el = parts[name] && f.querySelector(parts[name]);
      if (!el) { console.error(`data-co-parts: no "${name}" in this frame`); continue; }
      el.dataset.co = n;
      if (side) el.dataset.coSide = side;
    }
  }

  // the numbers, once the fonts have set the text where it stays: in the margin
  // beside the screen, level with what they mark, with a line to it
  const place = () => {
    const used = new Map();
    for (const el of document.querySelectorAll('[data-co]')) {
      const frame = el.closest('.computer, .phone, .tv'), shot = el.closest('.shot');
      if (!frame || !shot) continue;
      shot.style.position = 'relative';
      const s = shot.getBoundingClientRect(), f = frame.getBoundingClientRect(), r = el.getBoundingClientRect();
      const side = ['right', 'top', 'bottom'].includes(el.dataset.coSide) ? el.dataset.coSide : 'left';
      const ys = used.get(frame) || { left: [], right: [], top: [], bottom: [] };
      used.set(frame, ys);
      if (side === 'top' || side === 'bottom') {
        // above or below the screen, over the middle of the part, with a line down or up to it
        let x = Math.round(r.left - s.left + Math.min(r.width, 60) / 2 - 11);
        while (ys[side].some((u) => Math.abs(u - x) < 26)) x += 26;
        ys[side].push(x);
        const y = Math.round(side === 'top' ? f.top - s.top - 26 : f.bottom - s.top + 4);
        const from = side === 'top' ? y + 22 : Math.round(Math.min(r.bottom, f.bottom - 16) - s.top + 2);
        const to = side === 'top' ? Math.round(Math.max(r.top, f.top + 16) - s.top - 2) : y;
        if (to - from > 2) shot.appendChild(make(`<i class="co-line ${side}" style="left:${x + 10}px;top:${from}px;height:${to - from}px"></i>`));
        shot.appendChild(make(`<b class="co" style="left:${x}px;top:${y}px">${el.dataset.co}</b>`));
        continue;
      }
      let y = Math.round(r.top - s.top + Math.min(r.height, 44) / 2 - 11);
      while (ys[side].some((u) => Math.abs(u - y) < 24)) y += 24;
      ys[side].push(y);
      const x = Math.round(side === 'left' ? f.left - s.left - 26 : f.right - s.left + 4);
      // a part cut off by the screen's edge is met where it is still in view
      const from = side === 'left' ? x + 22 : Math.round(Math.min(r.right, f.right - 16) - s.left + 2);
      const to = side === 'left' ? Math.round(Math.max(r.left, f.left + 16) - s.left - 2) : x;
      if (to - from > 2) shot.appendChild(make(`<i class="co-line ${side}" style="left:${from}px;top:${y + 11}px;width:${to - from}px"></i>`));
      shot.appendChild(make(`<b class="co" style="left:${x}px;top:${y}px">${el.dataset.co}</b>`));
    }
  };
  document.fonts.ready.then(place);
})();
