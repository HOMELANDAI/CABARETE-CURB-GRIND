# Riders v2 — Tripo Smart Mesh + PBR (14 Nov 2026)

Kefla, Koda and Crash were regenerated as **real Tripo Studio models** instead of the v1 vertex-colour scans:

| | v1 (Oct) | v2 (this package) |
|---|---|---|
| Source | 1.9 M-tri Tripo scan, vertex colour only | Tripo **Smart Mesh P2.0**, multi-view to 3D from T-pose refs, **quad topology** (27.6k / 29.6k / 28.4k quads) |
| Colour | Cycles bake of vertex colour → 4K sheet | Tripo **PBR texture pass**, **8K albedo** (`tex/T_<Name>_albedo_8k.jpg`) → 4K albedo |
| Normal | baked from the scan | detail normal derived from the 8K albedo (`strength 0.6`); Tripo's preview FBX ships the colour map only |
| AO / roughness | baked / luminance | AO baked in Blender from the quad mesh; roughness fur 0.78–0.92, cloth 0.80, nose + eyes 0.35 |
| Mesh | 40k tris decimated | ≈ 56k tris quads, **no decimation** (Horizon copy `SK_<Name>_Horizon.fbx` collapsed to 19.5k tris) |
| Rig | Rigify biped, 33 DEF bones, 6 `CCG_*` clips | **identical** (same `rig_rider.py` fit, re-run as `tripo_pipeline/rig_tripo.py`) — every loader keeps working |

Before / after render: `../reference/riders_v1_vs_v2_tripo.jpg` (top v1, bottom v2). Known differences: Koda's PBR pass came out
with light-grey pants and no blue hand wraps (the design has black pants + blue wraps) — a 30-credit re-texture in Tripo Studio
with the Koda reference image fixes it if wanted. The v1 rigs are kept in `v1_vertexcolour_bake/`.

## Files
- `SK_<Name>.fbx` — rig + mesh + 6 clips (UE5 / UEFN); `SK_<Name>.glb` — same, textures embedded (34 MB, 4K); `SK_<Name>_Horizon.fbx` — ≤ 20k tris
- `SK_<Name>_master.blend` — Blender 5 master (metarig, Rigify control rig, NLA clips, packed textures) — open this to re-pose, add clips, repaint weights
- `tex/` — albedo 8K + 4K, normal 4K, ao 2K, orm 2K, mra 2K
- `tripo_pipeline/` — `rig_tripo.py` (import → cleanup → orient → 1.1 m → AO bake → Rigify → clips), `post_tex_tripo.py` (texture sets per engine),
  `export_tripo.py` (material, FBX/GLB, Horizon decimate, check render), `webglb.sh` (1K web GLB), `pack_tripo.sh` (place into every build)

## Reproduce / do the women
In Tripo Studio: Image tool → T-pose reference (front) → **Multiview Image** → **Multi-View to 3D** with **Smart Mesh**, polycount 25 000
(the field resets to 5 000 every time), 4 generations → pick one → **Texture** (PBR on, 30 credits). Download the `tripo_texture_*.fbx`
(the studio's `model_url`; the CDN needs a browser User-Agent + `Referer: https://studio.tripo3d.ai/`), then:
```
python rig_tripo.py <Name> <tripo_texture.fbx> <outdir>
python -I post_tex_tripo.py <Name> <outdir>
python export_tripo.py <Name> <outdir>
./webglb.sh <Name> && ./pack_tripo.sh
```
