// Offline-Cache. VERSION bei jedem Update erhöhen, damit alle Geräte die neue Fassung laden.
const VERSION = "draft-coach-2026-11-19";
const CORE = [
  "./",
  "index.html",
  "data/stats.js",
  "manifest.webmanifest",
  "icons/icon-192.png",
  "icons/icon-512.png",
  "icons/apple-touch-icon.png",
  "maps/belle-s-rock.webp",
  "maps/bridge-too-far.webp",
  "maps/center-stage.webp",
  "maps/double-swoosh.webp",
  "maps/dry-season.webp",
  "maps/dueling-beetles.webp",
  "maps/flaring-phoenix.webp",
  "maps/gem-fort.webp",
  "maps/hard-rock-mine.webp",
  "maps/hideout.webp",
  "maps/hot-potato.webp",
  "maps/kaboom-canyon.webp",
  "maps/layer-cake.webp",
  "maps/new-horizons.webp",
  "maps/open-business.webp",
  "maps/out-in-the-open.webp",
  "maps/parallel-plays.webp",
  "maps/pinball-dreams.webp",
  "maps/ring-of-fire.webp",
  "maps/safe-zone.webp",
  "maps/shooting-star.webp",
  "maps/sneaky-fields.webp",
  "maps/triple-dribble.webp",
  "maps/undermine.webp"
];
self.addEventListener("install", e => {
  e.waitUntil(caches.open(VERSION).then(c => c.addAll(CORE)).then(() => self.skipWaiting()));
});
self.addEventListener("activate", e => {
  e.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k => k !== VERSION).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener("fetch", e => {
  const req = e.request;
  if (req.method !== "GET") return;
  // Seite selbst: erst Netz (für Updates), sonst Cache
  if (req.mode === "navigate") {
    e.respondWith(fetch(req).then(r => { const c = r.clone(); caches.open(VERSION).then(x => x.put("index.html", c)); return r; })
      .catch(() => caches.match("index.html")));
    return;
  }
  // Alles andere (Bilder, Icons, Schriften): erst Cache, sonst Netz und merken
  e.respondWith(caches.match(req).then(hit => hit || fetch(req).then(r => {
    if (r.ok || r.type === "opaque") { const c = r.clone(); caches.open(VERSION).then(x => x.put(req, c)); }
    return r;
  })));
});
