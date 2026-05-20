// sw.js — Service Worker لـ Bashar Pro ERP
const CACHE_NAME = 'bashar-erp-v1';
const ASSETS = [
  '/bashar-erp/',
  '/bashar-erp/index.html',
  'https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@300;400;500;600;700&display=swap',
  'https://cdn.jsdelivr.net/npm/chart.js',
  'https://cdn.jsdelivr.net/npm/xlsx@0.18.5/dist/xlsx.full.min.js',
];

// تثبيت — تخزين الأصول
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      return cache.addAll(ASSETS).catch(err => {
        console.log('Cache addAll error (non-fatal):', err);
      });
    })
  );
  self.skipWaiting();
});

// تفعيل — حذف الكاشات القديمة
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
    )
  );
  self.clients.claim();
});

// طلبات الشبكة — network first, cache fallback
self.addEventListener('fetch', event => {
  // تجاهل طلبات Supabase (لا تُخزَّن)
  if (event.request.url.includes('supabase.co')) return;

  event.respondWith(
    fetch(event.request)
      .then(response => {
        // خزِّن نسخة حديثة
        if (response.ok && event.request.method === 'GET') {
          const clone = response.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone));
        }
        return response;
      })
      .catch(() => {
        // إذا انقطع الإنترنت — استخدم الكاش
        return caches.match(event.request).then(cached => {
          if (cached) return cached;
          // صفحة offline احتياطية
          if (event.request.destination === 'document') {
            return caches.match('/bashar-erp/index.html');
          }
        });
      })
  );
});

// مزامنة في الخلفية عند عودة الإنترنت
self.addEventListener('sync', event => {
  if (event.tag === 'cloud-sync') {
    event.waitUntil(
      self.clients.matchAll().then(clients => {
        clients.forEach(client => client.postMessage({ type: 'SYNC_NOW' }));
      })
    );
  }
});
