# Cabarete Curb Grind — UEFN package (HomelandAI)

- `Verse/` — seven Verse 1.0 device sources. Put them in one folder of your UEFN project and Build Verse.
  - `ccg_trick_scoring.verse` — `ccg_scoring` constants (from ccg_data.scoring), `combo_tracker`, `ScoreTrick`, `ScoreGrind`
  - `ccg_game_manager.verse` — run manager: parks P1..P4, store + sign-gap volumes, Vagamundo gating, HUD, finish, lifetime-points loop (25k) and the earned-tier `Store.GrantEarned` calls
  - `ccg_store.verse` — generated 94-row catalog (free / purchase / earned), 23 button/granter pairs for the priced rows, `GrantFree` on join, `GrantEarned(Agent, Key)` from the game manager
  - `ccg_rail.verse` — grindable rail (teleport-along-marker-chain; UEFN has no native grind); drives the Metal Sparks VFX spawner on steel rails
  - `ccg_rider_select.verse` — 7 riders → class designer slots (women include model numbers)
  - `ccg_timeofday.verse` — Sunset mode: day / sunset Day Sequence cross-fade (`FadeIn`/`FadeOut`), park floodlights, street lamps, mural wash lights, neon signs
  - `ccg_graphics.verse` — **graphics director (max tier)**: cinematic grade via `LS_CCG_Sunset` (`Play` / `PlayReverse`), wet-road sequence, heat haze, a pooled spark-light system `ccg_rail` borrows from, mural-wash flicker, HighEnd / LowEnd quality tier
- `assets/riders/<Name>/` — **v2 Tripo Smart Mesh riders** `SK_<Name>.fbx` (quad mesh, 8K-sourced 2K BC + DirectX N + ORM + SMR; see `../shared/riders/RIDERS_V2_TRIPO.md`) and the v1 **three-section hero riders** `SK_<Name>_UEFN.fbx` (Head / Upper / Lower material slots, each on its own 2K sheet: BC, DirectX N, ORM, Fortnite SMR, wet/curvature Mask) + the single-sheet LowEnd set
- `assets/materials/` — 2K tileable PBR sets (asphalt, park concrete, adoquín pavers, sand, stucco, corrugated roof, deck wood, rail steel), wall-paint + fur detail normals, road paint / wetness / grunge masks, decal atlas — `TEXTURE_MANIFEST.json`
- `assets/signs/` — 38 signage + billboard textures with neon emissive masks — `SIGN_MANIFEST.json`
- `assets/murals/` — the six HAI murals at power-of-two 2K (`T_Mural_<id>_BC.png`), placement table in the level guide §8b
- `reference/` — the three reference shot lists (81 files)
- `LEVEL_BUILD_GUIDE.md` — layout, scale, waypoint coordinates (cm), galleries, structures, device wiring table
- `UEFN_GRAPHICS.md` — **the max-fidelity spec**: UEFN's hard limits and how the package works inside them, Day Sequence values (day + sunset), Environment Light Rig + `LS_CCG_Sunset` keys, post grade, every custom material graph (riders, road with wetness, parks, pavers with POM, steel, murals, signs, decals), rider import, VFX + light pool, quality tiers, budget, checklist
- `manifest.json` — assets, rider mesh source paths, import notes

Source of truth: `../shared/ccg_data.json` (scoring/rider constants are hand-copied into Verse; the store catalog is regenerated with `python3 ../shared/gen_store.py`).

## Store tiers

Catalog regenerated from `ccg_data.json → store.*` on 2026-10-19 (**95 rows**; counts below are catalog rows).

| Tier | Rows | What | How it is granted |
|---|---|---|---|
| **free** | **28** | 16 flannel sets · 2 knits (Frenchie Varsity, Collie Uplink) · 10 starter boards (8 collection decks + 2 kaftan decks, with sizes) | `ccg_store.OnBegin` grants to everyone present and `PlayerAddedEvent` to late joiners |
| **purchase** | **29** | 5 rain suits (5,500, each with its cruiser) · 6 Dapper Dan Remix kaftans (7,500) + their 6 bundled decks · 9 Carved Nine outfits (2,500) · 3 deck collections (4,000 / 6,000 / 5,000, **only after one park is mastered**) | `TryBuy` from `PurchaseButtons[i]` → `Manager.TrySpend[]` → `PurchaseGranters[i]`; collections check `Mastered.Length >= 1` |
| **earned** | **38** | 7 knits (trick milestones) · 10 Original kaftans (one per 25,000 lifetime points) + 8 bundled decks · 5 Desert Dusk kaftans + 5 decks (P2, P3, P4 mastery, Sign Gap, Vagamundo) · 2 Lunar Dragon tees (first Sign Gap, 100,000 lifetime points) · 1 effect `fx_sparks` Metal Sparks (first 50-point grind; toggle, off by default) | `ccg_game_manager` → `Store.GrantEarned(Agent, Key)` / `Store.GrantLifetimeTier(Agent, N)` |

23 priced rows need a shelf/button; the other 6 purchase rows are kaftan decks bundled with their kaftan.
Unlock keys: `park:P2|P3|P4` (Desert Dusk), `park:P1` (Vagamundo), `signgap`, `lifetime:1..10` (every 25,000 banked, `lifetime:4` = 100k tee),
`grinds:10|25|50`, `trick:treFlip`, `combo:5000|10000`, `grindmeters:100` (knits), `grind:50` (fx_sparks), `with:<kaftan_id>` (bundled decks).
Lifetime points survive a run reset but live in memory for the session only (wrap `Owned` / `LifetimePoints` in a persistable `weak_map(player, …)` to keep them).
