// Service worker disabled to resolve cache/CSP conflicts.
self.addEventListener('install', e => self.skipWaiting());
self.addEventListener('activate', e => self.clients.claim());
self.addEventListener('fetch', e => {
  // Always fetch from network
  return; 
});
