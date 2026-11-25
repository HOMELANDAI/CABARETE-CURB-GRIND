# Cabarete Curb Grind — handoff to Claude Code

Written 23 Nov 2026 from the Claude app session (GAME DEVELOPMENT project). Owner: HOME LAND, HomelandAI (HAI).
Start Claude Code in `F:\HOMELANDAI\CURBSIDE GRIND (CCG)\` (a `CLAUDE.md` sits there with the standing rules). Read this file and `10_DOCS\UEFN_INSTALL_STATUS.md` before touching anything. Do not start building until HOME LAND says go.

## The goal

Cabarete Curb Grind (CCG) is a skateboarding game set on the real Highway 5 strip of Cabarete, Dominican Republic: four skate parks (Vagamundo roof, Multiplex, Mojito, Courtyard), the Horseshoe, six signature rail structures, 102 grind rails, the HAI Skate Store with HOME LAND's own deck and apparel catalog, 7 selectable riders (3 dogs, 4 humans), trick scoring, combos, a day-to-sunset cycle. **UEFN (Fortnite) is the primary build and is installed, launching and pushing.** A VIVERSE (Vive Flow, Three.js) build exists as an older, much lighter version. Horizon and UE5 are planned later.

HOME LAND's concern right now: the game must **read as a real, high-detail 3D game**. Standing instruction: seek the highest detail achievable in graphics and resolution; judge by pictures, not documents. The last thing he saw looked simplistic — most likely the VIVERSE build or an early UEFN screenshot; confirm which with him before working.

## How to report (HOME LAND's rules)

- Report precisely what was done and what remains. Three labels: **Completed**, **Not completed**, **Next phase**.
- Every report ends with the line **"Cabarete Curb Grind is not done to completion."** until the game is finished and published. Never claim it is done.
- At 100 % (published), email a gameplay link to the HomelandAI email — ask HOME LAND for the address; never send it anywhere else.
- **Deliver the VIVERSE zip with every game update** (index.html at the zip root, Three.js inlined). Not optional.
- Bypass blockers and return to them later; access expiries and permission prompts are not the user talking — re-request and continue.
- Use every tool available (Tripo Studio, Blender MCP, UEFN Python, computer use, Claude in Chrome).
- All CCG files live on the F drive, organised and labelled. Never leave results on the Desktop.

## Hard constraints

- UEFN: textures cook at 2048² max (4K sources are fine; 8K sources fail validation); `.uasset` cannot be imported from outside; custom skeletal meshes cannot be the player body (riders are statues/NPC-style only); Verse `string` editables cannot be set from Python; `creative_prop` slots only take Fortnite `BuildingProp` blueprints; user materials may not reference `/Game/...` Fortnite textures; most Fortnite gallery foliage fails `AssetReferenceRestrictions` on publish.
- Epic moderation on textures: no URL/handle/hashtag/QR, no alcohol/tobacco, no gambling, no third-party brands, no real people.
- HOME LAND's deck and apparel art is his own IP. The Tripo account also holds hockey dogs, busts, weapons and older models — none of those go into CCG.
- The PC (`homelandai-bg`, RTX 4050 Laptop GPU) is memory-starved. UEFN crashed out of memory on 20 Nov ("paging file too small") while Blender held five 360k-tri decks and Chrome was open. Close Blender and the Fortnite client before heavy UEFN work; recommend a larger Windows paging file.

## Where everything is

```
F:\HOMELANDAI\CURBSIDE GRIND (CCG)\
  00_INDEX\                README.md, CCG_manifest.csv (what is where)
  01_UEFN_PROJECT\         snapshot copy of the UEFN project (NOT what UEFN edits)
  02_UEFN_WORKING_FILES\CCG_UEFN\
      verse2\              the 7 core Verse files (game manager, rail, store, rider select, trick scoring, graphics, timeofday)
      ccg_hud.verse, ccg_trick_input.verse   (8th/9th Verse files)
      uefn\                LEVEL_BUILD_GUIDE.md, UEFN_GRAPHICS.md, README.md, manifest.json, assets/
      level\               ~200 files: gen_level.py (headless Blender level generator), placements.json, route_real.json,
                           decals.json, meshes/, and every uefn_*.py install/placement script (see below)
      ccg_import.py, ccg_mats.py, ccg_matfix2.py   (first-pass asset/material import)
  03_MODELS_3D\tripo_pipeline\
      decks\               20 deck GLB masters (4K), raw\ Tripo exports, web\ 27k-tri WebP GLBs, check\ renders,
                           refs\ art crops, blender_deck_pass.py, flip_deck_gltf.mjs
      foliage\             CCG_Palm_A/B, CCG_SeaGrape, CCG_Bougainvillea (+ web\)
      tripo_posed\, tripo_tex4k\, tripo_web\, tripo_horizon\   riders Yara/Sunny/Rubí/Kai + 7 shop props
  04_RIDERS_CCG_Riders\    the 3 dog riders (Kefla, Koda, Crash) — Rigify rigs, out_v2\
  05_IMAGES_AND_STILLS\    client_check_1.png and other captures
  06_SCRIPTS\              ccg_pose_rider.py, ccg_r.py
  07_MEDIA_KIT_ZIPS\, 08_TRIPO_EXTRAS\
  09_DELIVERABLES\         CabareteCurbGrind_VIVERSE_2026-11-15.zip (the only archived web build)
  10_DOCS\                 UEFN_INSTALL_STATUS.md (the master status table), TRIPO_V5_DECKS.md, TRIPO_V4_FOLIAGE.md, this file
```

Live UEFN project: `C:\Users\211in\FortniteProjects\CabareteCurbGrind` (UEFN 6.x / Fortnite 43.x, Verse path `/haigaming@fortnite.com/CabareteCurbGrind`). Open it from the Epic Games Launcher → UEFN → Browse → `CabareteCurbGrind.uefnproject` (it is missing from Recent). Logs: `C:\Users\211in\AppData\Local\UnrealEditorFortnite\Saved\Logs\UnrealEditorFortnite.log`.

## How the UEFN automation works

- Scripts run in UEFN's Python bar (Output Log → Python). The bar is narrow, so a one-line runner `C:\Users\211in\r.py` holds `exec(open(r"F:/.../level/<script>.py").read())` and the bar runs `exec(open(r"C:/Users/211in/r.py").read())`. A second copy, `C:\Users\211in\Downloads\ccg_r.py`, currently points at `uefn_decks_rain.py`.
- From Claude Code on the PC this is simpler: write `r.py` directly, or use the `unreal-mcp` skill / UEFN remote execution if it is installed. If driving the editor by computer use: the Python bar is at roughly (450–480, 818) on the 2315×1447 desktop, Push Changes at (560, 58); UEFN must be frontmost (Chrome steals focus).
- Verse `@editable` slots from Python: property names are mangled `__verse_0x<HASH>_<Name>` with `HASH = byteswap(crc32(Name.encode('utf-32-le')))`; device references are the inner Verse object; native devices go through an instanced wrapper's `SavedActor`. Full recipe in `uefn\LEVEL_BUILD_GUIDE.md` and the project doc `UEFN_LEVEL_PACK.md`.
- Device "User Options" are plain actor properties (`Color`, `InitialState`, `SpawnRate`, …); Blueprint enums come back as Python enums.
- Never run `EDIT COPY` from Python (crashes the editor). MaterialParameterCollections cannot be authored from Python (no GUID) — use per-actor material tracks instead.
- Import pattern for Tripo meshes: `uefn_decks9.py` / `uefn_decks_rain.py` are the templates — GLB → Nanite static mesh under `/CCG/Tripo/`, normal → TC_NORMALMAP, rm → TC_MASKS, place, write `*_out.json`, log a DONE marker.
- Push Changes verification: log shows `[Push] pushed remote revision …` and no `UEFNValidation: Error`.

## The Tripo → Blender → UEFN asset pipeline

- Tripo Studio (studio.tripo3d.ai, HOME LAND's account, ~22 675 credits left): Model panel → image input → **HD Model, H3.1, 8K off** → 55 credits → Export GLB 4k. For characters: T-pose image → Multiview → HD. Automated so far via Claude-in-Chrome JS (`DataTransfer` on the hidden `input[type=file]`, because the page never reaches `document_idle`).
- Blender 5.2 LTS on the PC (MCP bridge available; namespace does not persist between calls; 80 s timeout per call; big renders hang it). Deck pass = `decks\blender_deck_pass.py` (pack textures, join, merge by distance 0.0001, recalc normals, PCA levelling, 0.82 m, smooth 35°, rename `SM_Deck_<Name>` / `M_Deck_<Name>`, export GLB). Known flaw: the "which side are the wheels on" heuristic failed on 2 of 20 decks — always look at the under-view render.
- Web GLBs: gltf-transform 4.5 `simplify --ratio 0.08 --error 0.001` then `optimize --simplify false --texture-size 2048 --texture-compress webp --compress false`. `flip_deck_gltf.mjs` bakes a 180° X flip when needed.
- Headless check renders without Blender: three.js + Playwright (`check.html` / `shot.js` pattern; renders under/top/side sheets).

## Completed (as of 23 Nov)

| Area | State |
|---|---|
| Level | Highway 5 traced from the real aerial (`route_real.json`), 4 parks, Horseshoe, 6 signature structures, 102 rails, 94 buildings (24 landmarks + 69 fillers + store), bridge, lamps, palms — 372 mesh actors, all Nanite, `M_CCG_Env` with parallax + grunge input, 28 env MIs, 38 sign MIs, mural MIs. |
| Verse | 9 files build clean: game manager, rail (102 instances), store (95-row catalog), rider select (7 classes), trick scoring, graphics, timeofday, trick input (ollie/kickflip/heelflip/shove/tre/grab/bail from stock inputs), HUD (score/combo/park/grind/lifetime/kaftan tier). |
| Devices | Every `@editable` wired (0 failures) except `NeonLit/NeonUnlit`. Lights, spark spawners, class designers/selectors, 23 store buttons + granters (labelled with catalog ids), zone volumes, finish trigger, barrier, HUD, end game. |
| Graphics | Tier A + B done: post-process grade, wet road material, 23 decals, water material, environment light rig, `LS_CCG_Sunset` 6 s sequence driving sun/sky/fog/grade + per-actor wet road + neon emissive, Verse-triggered. 627 gallery understory actors (only the 24 validator-legal meshes), own Tripo palms (35) and shrubs (375). |
| HAI IP | 6 billboards with HomelandAI IP passed moderation; mural swapped. |
| Riders | 3 Tripo dogs (Rigify, 6 anims each, `CCG/Riders/`) + 4 Tripo humans (posed statues) + 7 shop props placed. |
| Decks | 20 Tripo decks from HOME LAND's art (6 HAI Ivory/Dojo, 9 Carved Nine, 5 rain-suit) as 4K masters + web GLBs; 15 placed and pushed in the store. |
| Sessions | Launch Session works after the 19 Nov UEFN update; client capture shows the HUD live and the rider at the start. Validate Project clean. |

## Not completed

- **Run `level\uefn_decks_rain.py` + Push Changes** — the five rain-suit decks are on disk but not in the level (UEFN crashed OOM before the run). Check `decks_rain_out.json` = 5 placed.
- **Human play-test** — Claude has never ridden a rail. The bridge cannot send input to the Fortnite client. Unverified: the grind loop (teleport-along-rail), trick input timings, the store buttons, rider select, the sunset sequence in play. Known bug: phantom **COMBO x1 +1,500** on spawn (1.5 s spawn guard in `ccg_trick_input` is not enough).
- **Decks as real items** — Fortnite cannot grant a custom deck; the decks are display props. Granters need prop pickups or a cosmetic swap design.
- **Regenerations:** Cobalt Trail (wheel-less near truck, surf shape), Stormburn Sunrise (one truck). Kaftan decks have no reference art — ask HOME LAND.
- **Rider clothing pass** — the catalog's flannels/knits/rain suits/kaftans exist as names and store rows only.
- **In-game screenshots** of the store racks, parks and sunset — the editor viewport runs "Streaming Disabled" during a live session.
- **VIVERSE build is stale** — the web source was lost with a cloud reset; only the 15 Nov zip is archived. It has none of the Tripo riders/decks/foliage/graphics. Rebuild from the zip, drop in the 27k-tri web GLBs, proper materials and lighting, re-zip.
- **Horizon and UE5** — nothing started beyond `tripo_horizon\` GLBs.
- **Publishing** — not attempted. Pre-publish: moderation re-check, the gallery palms were swapped out (publish risk gone), `NeonLit/NeonUnlit` still unwired.
- **Leftover graphics items** (`uefn\UEFN_GRAPHICS.md`): grunge vertex painting on park floors, Water Body Ocean (material plane used instead), `SunsetGlow` tint, BuildingProp-based neon props.

## Next phase (proposed — wait for HOME LAND's go)

1. **Prove it reads as 3D.** Open UEFN, finish the rain-deck push, then capture a proper set of in-editor and in-client stills at 4K (store interior, Vagamundo roof at sunset, Highway 5 from the sign, Multiplex stairs, Mojito quarter pipes) and a short fly-through. Put them in `05_IMAGES_AND_STILLS\` and show HOME LAND before anything else.
2. **Play-test with HOME LAND at the keyboard**, fix the phantom combo and the trick timings, confirm grinding works.
3. **VIVERSE rebuild** with the Tripo assets so the web build stops looking like the prototype; deliver the zip.
4. Then the asset backlog (regenerations, rider clothing, deck pickups) and publishing.

**Cabarete Curb Grind is not done to completion.**

## Lessons that save hours

- `unreal.Rotator(roll, pitch, yaw)` — the argument order bit us once (sun ended under the horizon).
- Linear-Color / Linear-Grayscale samplers on mask textures fail to compile in UEFN; use *Masks*.
- A Level Sequence referenced by a device cannot be deleted — strip and reuse it.
- A `VolumetricCloud` actor fails validation (illegal `/Engine` material reference).
- Fortnite's gallery palms and most tropical foliage are "Disallowed reference" at validation even though they place fine.
- A crashed editor process can keep `.uasset` files locked (save error 32) until killed.
- The UEFN launcher update queues forever while a Fortnite client is still running.
- Tripo stands portrait decks on their tail (Z = length); PCA levelling fixes it but check the wheel side visually.
- Blender MCP: re-import everything in every call; keep renders small or do them headless with three.js in the cloud.
- The Claude desktop bridge: `device_bash` is a Linux VM (can read/write the F drive but not `C:\Users`), Blender's Python can write anywhere on the PC when it is responsive.

More detail: claude.ai project "GAME DEVELOPMENT" → `Cabarete_Curb_Grind/` (UEFN_INSTALL_STATUS, UEFN_LEVEL_PACK, UEFN_GRAPHICS_max_tier, TRIPO_V3/V4/V5, RIDERS_V2_TRIPO).
