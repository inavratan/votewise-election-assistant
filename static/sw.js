const CACHE_NAME = 'votewise-v1.0.9';
const STATIC_ASSETS = ['/', '/style.css', '/app.js', '/manifest.json'];

self.addEventListener('install', e => {
  self.skipWaiting();
  e.waitUntil(caches.open(CACHE_NAME).then(c => c.addAll(STATIC_ASSETS)));
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cache => {
          if (cache !== CACHE_NAME) {
            return caches.delete(cache);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', e => {
  if (e.request.url.includes('/api/')) { 
      e.respondWith(fetch(e.request)); 
      return; 
  }
  e.respondWith(caches.match(e.request).then(r => r || fetch(e.request)));
});
