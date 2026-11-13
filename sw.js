// Funciona sin internet una vez instalado. VERSION cambia sola en cada actualización del catálogo.
const VERSION = 'hk-cdd3c7e4a6';
const FILES = ["./", "index.html", "data.js", "manifest.webmanifest", "img/excell-white.png", "img/giti.png", "img/gt-oil.png", "img/gt-radial.svg", "img/hk-logo.png", "img/hk-white.png", "img/mighty.png", "img/tecfil-white.png", "img/yhaguy-logo.png", "icons/apple-touch-icon.png", "icons/favicon-32.png", "icons/icon-192.png", "icons/icon-512.png", "icons/icon-maskable-512.png"];
self.addEventListener('install', e => { e.waitUntil(caches.open(VERSION).then(c => c.addAll(FILES)).then(() => self.skipWaiting())); });
self.addEventListener('activate', e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== VERSION).map(k => caches.delete(k)))).then(() => self.clients.claim())); });
self.addEventListener('fetch', e => {
  const r = e.request; if (r.method !== 'GET') return;
  const u = new URL(r.url);
  if (u.origin === location.origin) {
    // Primero la red (para tener siempre la última versión); sin internet, la copia guardada.
    // index, datos y scripts: siempre preguntar al servidor si hay versión nueva (no usar la caché de 10 min del navegador)
    const fresh = r.mode === 'navigate' || /\.(html|js|webmanifest)$|\/$/.test(u.pathname);
    e.respondWith(fetch(fresh ? new Request(r, { cache: 'no-cache' }) : r).then(res => { const cp = res.clone(); caches.open(VERSION).then(c => c.put(r, cp)); return res; })
      .catch(() => caches.match(r, { ignoreSearch: true }).then(m => m || caches.match('index.html'))));
  } else if (/fonts\.(googleapis|gstatic)\.com$/.test(u.hostname)) {
    e.respondWith(caches.match(r).then(m => m || fetch(r).then(res => { const cp = res.clone(); caches.open(VERSION).then(c => c.put(r, cp)); return res; })));
  }
});
