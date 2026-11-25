# Cabarete Curb Grind — Tripo v4: HAI foliage (19 Nov 2026)

Own tropical foliage generated in Tripo Studio so the island no longer depends on Fortnite gallery meshes that UEFN's
reference validator rejects (every Asteria/Helios tropical set, and even a freshly placed `SM_PalmTree_*`, is a
"Disallowed reference" — see `UEFN_INSTALL_STATUS.md`, Tier B part 4).

Pipeline per asset (Claude-in-Chrome on Tripo Studio, ~5 min each): **Image → Generate Image for 3D** (Nano Banana 2,
free) → **Multiview Image** (free) → the multi-view card's **Multi-View to 3D** → **HD Model, H3.1, 8K texture OFF**
(55 credits, 4K PBR) → **Export GLB 4k** to `C:\Users\211in\Downloads`. Credits 23 995 → 23 775.

| Asset | Tripo id | Faces (HD) | Prompt gist | Where it is used |
|---|---|---|---|---|
| `CCG_Palm_A` | 8a2074d6 | 352 292 | tall straight Caribbean coconut palm, ring bark, coconuts | all 35 `L_Palm*` actors (2 of 3 picks) |
| `CCG_Palm_B` | f1dfac4e | 346 032 | shorter leaning coconut palm with hanging dead fronds | `L_Palm*` (1 of 3 picks) |
| `CCG_SeaGrape` | 3c4d7d7c | 344 524 | sea grape (*Coccoloba uvifera*) coastal shrub, round leathery leaves, red veins | 181 `FT_SeaGrape_*` |
| `CCG_Bougainvillea` | 315376fb | 319 090 | 2 m magenta bougainvillea bush | 194 `FT_Bougainvillea_*` |

Files (all on the F drive, `03_MODELS_3D\tripo_pipeline\foliage\`): the 4K masters `CCG_<Name>.glb` (18–23 MB,
basecolor / normal / rm 4096², origin at the trunk or stem base, ~1 m tall normalised), `check_foliage.png` (Blender
Eevee check render of the four masters), `web\CCG_<Name>_web.glb` (gltf-transform: `simplify --ratio 0.06 --error 0.05`
→ ~21 k triangles, 1024² WebP textures, 1.0–1.4 MB each — the plain `optimize --simplify-ratio` path leaves foliage
untouched because the default error bound rejects every collapse) and `web\check_foliage_web.png`.

UEFN: imported with `uefn_tripo_import.py` (`CCG_SRC` = the foliage folder, Nanite on; `uefn_tripo_tex.py` fixes the
normal / rm compression) under `/CCG/Tripo/CCG_<Name>/`. `uefn_gfx_f.py` then swaps every `L_Palm*` to `CCG_Palm_A/B`
(6.5–13 m, random yaw, ±2° lean — no more gallery-palm publish risk) and places 375 shrubs: 1–2 per palm on the sand
side, along the four park perimeters (every 14 m) and bougainvillea against ~40 % of the building backs. Ground =
complex-collision trace that must land on `L_Ground`. Validate Project: clean. Only warning: the bougainvillea LOD0 is
53 k vertices against UEFN's 30 k recommendation (Nanite fallback) — accepted for now; the web GLB is the 21 k version.

Not done: VIVERSE / Horizon / UE5 placement of these meshes (the web source is still missing — see the install log);
grass-level understory is still the 24 legal gallery meshes from Tier B part 4.
