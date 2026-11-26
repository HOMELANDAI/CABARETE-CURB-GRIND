// Local static server for headless conversion + check renders (localhost only).
// GET serves files under the CCG repo; POST saves a body only under 11_VIVERSE_WEB/build_cache/ or shots/.
import http from 'node:http'; import fs from 'node:fs'; import path from 'node:path';
const root = path.resolve(process.argv[2] || '.'); const port = +(process.argv[3] || 8123);
const writable = ['11_VIVERSE_WEB/build_cache/', '11_VIVERSE_WEB/shots/'].map(p => path.join(root, p));
const types = {'.html':'text/html','.js':'text/javascript','.mjs':'text/javascript','.json':'application/json','.glb':'model/gltf-binary','.png':'image/png','.jpg':'image/jpeg','.webp':'image/webp'};
http.createServer((req, res) => {
  const p = path.normalize(path.join(root, decodeURIComponent(req.url.split('?')[0])));
  if (!p.startsWith(root)) { res.writeHead(403); res.end(); return; }
  if (req.method === 'POST') {
    if (!writable.some(w => p.startsWith(w))) { res.writeHead(403); res.end(); return; }
    const chunks = []; req.on('data', c => chunks.push(c));
    req.on('end', () => { fs.mkdirSync(path.dirname(p), { recursive: true }); fs.writeFileSync(p, Buffer.concat(chunks)); res.end('ok'); });
    return;
  }
  fs.readFile(p, (e, d) => {
    if (e) { res.writeHead(404); res.end(); return; }
    res.writeHead(200, { 'Content-Type': types[path.extname(p)] || 'application/octet-stream' }); res.end(d);
  });
}).listen(port, '127.0.0.1', () => console.log('serving', root, port));
