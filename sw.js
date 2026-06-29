/* Discinsanity — minimal service worker (network pass-through; enables install).
   TODO: add offline shell caching before launch. */
self.addEventListener('install', e => self.skipWaiting());
self.addEventListener('activate', e => self.clients.claim());
self.addEventListener('fetch', e => { e.respondWith(fetch(e.request).catch(() => new Response('', {status: 504}))); });
