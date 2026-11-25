# Cabarete Curb Grind

HomelandAI's skateboarding game set on the real Highway 5 strip of Cabarete, Dominican Republic — four skate parks, the Horseshoe, six signature rail structures, 102 grind rails, the HAI Skate Store stocked with HOME LAND's own deck and apparel designs, seven riders, trick scoring and a day-to-sunset cycle.

**Primary build:** Unreal Editor for Fortnite (UEFN) — installed, launching and pushing to a live session.
**Secondary build:** VIVERSE (Three.js, Vive Flow) — older, lighter; `09_DELIVERABLES/`.
Planned: Horizon Worlds, UE5.

Start with [`CLAUDE.md`](CLAUDE.md) (standing rules) and [`10_DOCS/CLAUDE_CODE_HANDOFF.md`](10_DOCS/CLAUDE_CODE_HANDOFF.md) (full brief), then [`10_DOCS/UEFN_INSTALL_STATUS.md`](10_DOCS/UEFN_INSTALL_STATUS.md) (the master status table).

## What is in this repo (the source tier)

| Folder | Contents |
|---|---|
| `00_INDEX/` | README + manifest of the full F-drive archive |
| `02_UEFN_WORKING_FILES/CCG_UEFN/` | The 9 Verse files (`verse2/`, `ccg_hud.verse`, `ccg_trick_input.verse`), `uefn/` build guides + manifest, `level/` — `gen_level.py` level generator, `placements.json`, `route_real.json`, `decals.json`, level FBX meshes, and every `uefn_*.py` editor automation script |
| `03_MODELS_3D/tripo_pipeline/` | Web-weight GLBs (`decks/web`, `foliage/web`, `tripo_web`, `tripo_horizon`), check renders, reference crops, Blender/gltf-transform pipeline scripts |
| `04_RIDERS_CCG_Riders/CCG_Riders/out_v2/` | The three dog riders' rig sources (small files only) |
| `05_IMAGES_AND_STILLS/` | Contact sheets and client captures |
| `06_SCRIPTS/` | Rider posing and the UEFN runner stub |
| `09_DELIVERABLES/` | VIVERSE zip (15 Nov 2026) |
| `10_DOCS/` | Status, Tripo pass docs, Claude Code handoff |

## What stays on the F drive (too large for GitHub)

`F:\HOMELANDAI\CURBSIDE GRIND (CCG)\` holds the full 7.4 GB archive. Not in the repo:

- `01_UEFN_PROJECT/` — snapshot of the UEFN project (4.1 GB; the live project is `C:\Users\211in\FortniteProjects\CabareteCurbGrind`)
- 4K Tripo masters and raw exports (`03_MODELS_3D/tripo_pipeline/decks/*.glb`, `decks/raw/`, `tripo_tex4k/`, `tripo_posed/`, foliage masters), ~2 GB
- `02_UEFN_WORKING_FILES/CCG_UEFN/uefn/assets/` (172 MB of PBR texture sheets) and the `*.zip` asset packs
- Rider inputs/outputs beyond `out_v2/` (`04_RIDERS_CCG_Riders/CCG_Riders/{in,out,tripo}`), `07_MEDIA_KIT_ZIPS/`, `08_TRIPO_EXTRAS/`, showcase videos, editor screenshot dumps

If those need to live in git later, add Git LFS for `*.glb`, `*.fbx`, `*.blend`, `*.png` sheets and `*.zip`.

## Status

Cabarete Curb Grind is not done to completion. See the Not-completed list in the handoff.
