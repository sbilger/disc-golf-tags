/* Discinsanity — service worker: offline app shell.
   Network-first (fresh deploys always win) with cache fallback, so the whole
   suite keeps working on the course with no signal. */
const CACHE = 'discinsanity-v3';
const SHELL = [
  'hub.html', 'index.html', 'doubles.html', 'events.html', 'leaderboards.html', 'account.html',
  'account.js', 'suite.js', 'courses.js', 'manifest.webmanifest',
  'assets/discinsanity-logo.png', 'assets/favicon.png', 'assets/icon-192.png',
  'assets/icon-512.png', 'assets/apple-touch-icon.png'
];
self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL)).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys()
    .then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});
self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  e.respondWith(
    fetch(e.request).then(r => {
      if (r.ok && new URL(e.request.url).origin === location.origin) {
        const copy = r.clone();
        caches.open(CACHE).then(c => c.put(e.request, copy));
      }
      return r;
    }).catch(() =>
      caches.match(e.request, { ignoreSearch: true }).then(m => m || new Response('', { status: 504 }))
    )
  );
});
