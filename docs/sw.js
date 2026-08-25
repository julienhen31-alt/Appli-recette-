const CACHE='frigo-recettes-v20';
const ASSETS=['./','./index.html','./app.html','./manifest.webmanifest','./icon-192.png','./icon-512.png'];
self.addEventListener('install',e=>{
  e.waitUntil(caches.open(CACHE).then(c=>Promise.all(ASSETS.map(u=>fetch(u,{cache:'reload'}).then(r=>c.put(u,r)).catch(()=>{})))).then(()=>self.skipWaiting()));
});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(k=>Promise.all(k.filter(x=>x!==CACHE).map(x=>caches.delete(x)))).then(()=>self.clients.claim()));});
self.addEventListener('fetch',e=>{
  if(e.request.method!=='GET') return;
  if(e.request.url.includes('api.github.com')) return;
  const isHTML = e.request.mode==='navigate' || e.request.destination==='document' || e.request.url.endsWith('.html') || e.request.url.endsWith('/');
  if(isHTML){
    e.respondWith(fetch(e.request,{cache:'no-store'}).then(res=>{
      const copy=res.clone();
      caches.open(CACHE).then(c=>c.put(e.request,copy)).catch(()=>{});
      return res;
    }).catch(()=>caches.match(e.request).then(hit=>hit||caches.match('./index.html'))));
    return;
  }
  e.respondWith(caches.match(e.request).then(hit=>hit||fetch(e.request).then(res=>{
    const copy=res.clone();
    caches.open(CACHE).then(c=>c.put(e.request,copy)).catch(()=>{});
    return res;
  }).catch(()=>caches.match('./index.html'))));
});
