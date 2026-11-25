import { NodeIO } from '@gltf-transform/core';
import { transformMesh, getBounds } from '@gltf-transform/functions';
import { ALL_EXTENSIONS } from '@gltf-transform/extensions';
import { mat4 } from 'gl-matrix';
const io = new NodeIO().registerExtensions(ALL_EXTENSIONS);
for (const [src,dst] of process.argv.slice(2).map(s=>s.split('=')) ) {
  const doc = await io.read(src);
  const scene = doc.getRoot().getDefaultScene() || doc.getRoot().listScenes()[0];
  const b0 = getBounds(scene);
  const ymax = b0.max[1];
  // rotate 180 about X (y->-y, z->-z) then translate +ymax so min y = 0
  const m = mat4.create(); mat4.fromXRotation(m, Math.PI); const t = mat4.create(); mat4.fromTranslation(t,[0,ymax,0]); mat4.multiply(m,t,m);
  for (const mesh of doc.getRoot().listMeshes()) transformMesh(mesh, m);
  const b1 = getBounds(scene);
  await io.write(dst, doc);
  console.log(src, 'before', b0.min.map(v=>v.toFixed(3)), b0.max.map(v=>v.toFixed(3)), 'after', b1.min.map(v=>v.toFixed(3)), b1.max.map(v=>v.toFixed(3)));
}
