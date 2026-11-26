# 11_VIVERSE_WEB — VIVERSE rebuild (PAUSED 26 Nov 2026)

Paused on HOME LAND's instruction to continue in UEFN. Source for the new web build lives here so it can't be lost again.

State when paused:
- `tools/serve.mjs`, `tools/run_page.mjs` — local server + headless Chromium runner.
- `tools/fbx2glb.html` — converts the 47 UEFN level FBX meshes to GLB (worked: bounds/materials in `build_cache/level/report.json`).
  Coordinate map found: FBXLoader space (lx,ly,lz) cm -> UE (-lx, ly, lz); UE (x,y,z) cm -> three (x, z, y)/100; UE yaw θ -> three rotation.y = -θ.
- `tools/gen_textures.py` — tileable PBR texture generator (asphalt, concrete, pavers, sand, stucco, roof, wood, steel, wallpaint, grass, dirt, water normal). Has a shape bug in `grass()`/scalar-colour paths; fix before running.
- Not started: renderer, level assembly, skate physics, store, riders, HUD, zip.
