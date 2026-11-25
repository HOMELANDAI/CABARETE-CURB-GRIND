# Cabarete Curb Grind — Tripo v5: HAI deck set + named store inventory (19 Nov 2026)

Six HAI skateboards from HOME LAND's own deck art, generated as full 3D cruisers (deck + trucks + wheels, carved relief on the
underside, wood/grip top) and installed as the display stock of the HAI Skate Store (Ocean Dream Plaza, Highway 5).
**v5b (same day, 20:50–21:18):** the nine Carved Nine decks added the same way — see the second section.
**v5c (20 Nov):** the five rain-suit bundle decks — see the third section.

Pipeline per deck (Claude-in-Chrome on Tripo Studio, ~4 min each): the deck was cropped out of the collection sheet
(`03_MODELS_3D\tripo_pipeline\decks\refs\Deck_<Name>.png`, from `HomelandAI_Ivory_Skateboard_Collection.png` and
`HomelandAI_HAI_Dojo_Deck_Collection.png`) → **Model panel, image input (file set from JS — the page never reaches
`document_idle`, so the upload goes through a `DataTransfer` on the hidden `input[type=file]`) → HD Model, H3.1, 8K OFF**
(55 credits, 4K PBR) → Export GLB 4k. Credits 23 775 → 23 445 (330).

| Deck (catalog name) | Collection | Tripo id | Faces (HD) | File |
|---|---|---|---|---|
| Ivory Mandala Flow | HomelandAI Ivory | 6a7624e6 | 355 494 | `CCG_Deck_IvoryMandalaFlow` |
| Ivory Engrave Supreme | HomelandAI Ivory | ae1f0f0b | 361 192 | `CCG_Deck_IvoryEngraveSupreme` |
| Dapper Dan Luxe Ivory Grid Supreme Remix | HomelandAI Ivory | 571a4b96 | 349 234 | `CCG_Deck_IvoryGridSupremeRemix` |
| Golden Paw Strike | HAI Dojo (Karate Gi) | 87729ff0 | 345 818 | `CCG_Deck_GoldenPawStrike` |
| Emerald Paw Kata | HAI Dojo (Karate Gi) | 1a1891fc | 344 114 | `CCG_Deck_EmeraldPawKata` |
| Shadow Ruff Combat | HAI Dojo (Karate Gi) | 410bb3e2 | 342 677 | `CCG_Deck_ShadowRuffCombat` |

Blender 5.2 (MCP, bmesh — edit-mode operators have no context from the bridge): textures packed, shells joined, merge by
distance 0.1 mm, loose verts dropped, normals recalculated, smooth shading with 35° sharp edges, **re-oriented** (Tripo
stands a portrait deck on its tail, Z = length; the landscape Mandala sheet came out X = length — both mapped to
length = X, up = +Z, wheels down, graphic/truck side = −Z), **scaled to 0.82 m** (32" cruiser), origin centred at the
wheel-contact plane, renamed `SM_Deck_<Name>` / `M_Deck_<Name>`, transforms applied. Files on the F drive,
`03_MODELS_3D\tripo_pipeline\decks\`: `CCG_Deck_<Name>.glb` (4K masters, 19–26 MB), `raw\…_tripo.glb` (untouched exports),
`web\CCG_Deck_<Name>_web.glb` (gltf-transform `simplify --ratio 0.08 --error 0.001` → ~27 k tris, 2K WebP, 1.4–2.5 MB —
for VIVERSE / Horizon), `check\check_decks_art.png` (Eevee check sheet of the six undersides), `refs\` (the crops).

UEFN: `uefn_tripo_import.py` (`CCG_SRC` = the decks folder, Nanite on) + `uefn_tripo_tex.py` → `/CCG/Tripo/CCG_Deck_<Name>/`.
`uefn_decks.py` (re-runnable, deletes `TD_*`) places them in outliner folder `CCG/Store`: five stand nose-up on the
counter side of `TR_Shop_DeckRack` (30 cm apart, 12° lean back, carved side to the shopper), `TD_Deck_ShadowRuffCombat`
lies flat on `TR_Shop_Counter`. Push Changes to the live session succeeded (45 s, 0 validation errors).

**Named inventory.** The 95-row catalog in `ccg_store.verse` already carries every garment and board name (flannels,
knits, rain suits, kaftans + their decks, starter decks, tees, effects, clothing, collections). What had no names was
the level: the 23 purchase buttons/granters were `FD_Btn_Store_NN` / `FD_Granter_Store_NN`. They are now
`FD_Granter_Store_00_rain_spicefront … FD_Granter_Store_22_dojo` (same index order as the `PurchaseButtons[]` /
`PurchaseGranters[]` arrays — labels only, the Verse references are untouched). Deck actors are `TD_Deck_<CatalogName>`.

---

## v5b — the Carved Nine (19 Nov, 20:50–21:18)

Source: the nine wall-leaning product photos of the HAI Carved Nine collection, cropped to one deck each
(`refs\Deck_<Name>.png`, ~500×860). Same Tripo settings (HD Model, H3.1, 8K off, 55 credits each; credits 23 335 → 22 950).
All nine came back as complete cruisers with the relief carving on the underside.

| Deck (catalog `carved_nine` set) | Tripo task | Faces (HD) | After Blender |
|---|---|---|---|
| Bulldog Crest | 26e974be | 357 336 | 357 336 tris, 0.82 × 0.22 × 0.13 m |
| Sunrise Scholar | 2f75280c | 359 028 | 313 974 tris (a phantom second wheel set that floated above the deck was cut: 24 779 verts above z = 16.8 cm) |
| Howl Couture | e8551287 | 343 988 | 343 976 |
| Carbon Bark | 8d50fd10 | 356 430 | 356 384 |
| Cobalt Trail | 10346ca9 | 344 462 | 344 462 — **flagged**: 34 cm wide surf-skate shape, big blue wheels on the far truck only, the near truck came out wheel-less and a side bumper plate is fused to the rail (the photo hid the near wheels). Usable as a display prop; regenerate from a different crop when the time comes |
| Ruff Royale | 61690c68 | 351 270 | 351 222 |
| Pawshion Avenue | 297dd815 | 345 460 | 345 454 |
| Pawsibility | 6a99cdb2 | 354 702 | 354 680 |
| Terrierbyte | 84d5e19a | 345 164 | 345 116 |

Blender pass as v5 plus **levelling**: the photos were shot with the decks leaning, so the raw meshes came in pitched 5–15°.
A PCA of the mesh now sets length = X and the thin axis = Z, the wheel side is detected by where the off-plane mass sits and
flipped to −Z, then scale 0.82 m / centre / z-min = 0 as before. Check renders: `check\decks9_under.png` (nine undersides,
all art reads), `decks9_side.png` (all level, wheels down), `decks9_top.png`, `cobalt_iso.png` (the flagged deck).
Files: `CCG_Deck_<Name>.glb` masters (19–24 MB), `raw\CCG_Deck_<Name>_tripo.glb`, `web\CCG_Deck_<Name>_web.glb` (1.3–1.7 MB).

UEFN: `uefn_decks9.py` (new, re-runnable, deletes `TD_C9_*`) imports the nine GLBs as Nanite static meshes with the texture
fixes inline (18 textures: normal → TC_NORMALMAP, rm → TC_MASKS) and places them as a second display row along the **back
wall of the store, left of the counter** (store-local forward −895 cm, right −330 ± 32 cm steps, 12° lean back, carved side
to the shop floor), outliner folder `CCG/Store/CarvedNine`, labels `TD_C9_Deck_<Name>`. `decks9_out.json`: 9 placed,
0 errors. Push Changes: 63 s upload, remote revision `872a386e…`, `0 Edits – 0 Pending Push`, no validation errors.
`C:\Users\211in\r.py` now points at `uefn_decks9.py` (the Python bar runs `exec(open(r"C:/Users/211in/r.py").read())`).

Store stock now: 15 Tripo decks (6 HAI + 9 Carved Nine) out of the catalog's 95 rows.

Not done (as of v5b): the kaftan/rain-suit boards have no meshes yet (rain-suit boards done in v5c below); Cobalt Trail wants a
regeneration; the decks are display props only (Fortnite cannot grant a real deck — the granters still need prop pickups);
no in-game screenshot of either rack (the editor viewport runs with "Streaming Disabled" while the session is live and the
bridge cannot drive the Fortnite client — walk to Ocean Dream Plaza to check); VIVERSE/Horizon placement of the web GLBs
waits on the recovered web source.

---

## v5c — the rain-suit bundle decks (20 Nov, 09:40–11:00)

Source: the five deck panels of the rain-suit bundle artwork (`refs\Deck_<Name>.png`). Same Tripo settings (HD Model,
H3.1, 8K off, 55 credits each; credits 22 950 → 22 675). The kaftan decks were skipped — there is no reference art for them.

| Deck (catalog `rain_suit` set) | Tripo task | After Blender | Flip |
|---|---|---|---|
| Sage Spice Drizzle Drop (`SpiceDrizzleDrop`) | 8f411f17 | 359 942 tris, 0.82 × 0.27 × 0.128 m | — |
| Vicewave Swell | 6e1fcc6d | 359 892 tris, 0.82 × 0.284 × 0.116 m | **flipped** |
| Vice Monsoon Luxe Remix | 6274aa89 | 344 908 tris, 0.82 × 0.209 × 0.093 m | — |
| Stormburn Sunrise | 48711ec6 | 343 382 tris, 0.82 × 0.281 × 0.136 m | **flipped** |
| Purpledown Drip | 7c47f8bc | 360 998 tris, 0.82 × 0.239 × 0.083 m | — |

Blender pass as v5b (`decks\blender_deck_pass.py` — the full script is now saved there). The mass-count heuristic that
decides which side the wheels are on picked the wrong side for Stormburn Sunrise and Vicewave Swell (art and trucks ended
up on +Z). Blender then became unresponsive (the PC was out of memory — see below), so those two were corrected in the
cloud with gltf-transform: `decks\flip_deck_gltf.mjs` rotates the mesh 180° about X and re-seats it at y-min = 0, baked
into the vertices (masters and web GLBs). Check renders `check\rain5_under.png` (five undersides — all art reads, trucks
visible), `rain5_top.png`, `rain5_side.png` were rendered headlessly with three.js/Playwright from the web GLBs.
Note: Stormburn Sunrise came out of Tripo with only one truck/wheel pair (the far one) — usable as a display prop, regenerate
with Cobalt Trail when the time comes.

Files: `CCG_Deck_<Name>.glb` masters (20.9–24.4 MB), `raw\CCG_Deck_<Name>_tripo.glb`, `web\CCG_Deck_<Name>_web.glb`
(1.4–1.7 MB, ~27 k tris, 2K WebP).

UEFN: `uefn_decks_rain.py` is written (re-runnable, deletes `TD_RS_*`, imports the five GLBs as Nanite with the texture
fixes, places them as a third display row on the back wall **right of the counter** — store-local forward −895 cm,
right +330 ± 32 cm, 12° lean back, carved side to the shop floor — outliner folder `CCG/Store/RainSuit`, labels
`TD_RS_Deck_<Name>`, writes `decks_rain_out.json`). **NOT yet run.** When the UEFN session was reopened to run it, the
editor had already crashed with "Ran out of memory allocating 1 496 267 072 bytes — the paging file is too small", the
Fortnite client showed an Application Hang dialog, Blender had stopped answering the bridge, and the PC then dropped off
the bridge entirely. A copy of the one-line runner is in `C:\Users\211in\Downloads\ccg_r.py`
(`exec(open(r"C:/Users/211in/Downloads/ccg_r.py").read())` in the UEFN Python bar) because `C:\Users\211in\r.py` could
not be rewritten without Blender.

Store stock after this push will be 20 Tripo decks (6 HAI + 9 Carved Nine + 5 rain-suit) out of the catalog's 95 rows.

Still not done: run `uefn_decks_rain.py` and Push Changes (needs the PC back, Blender and the Fortnite client closed to
free memory — consider raising the Windows paging file); Cobalt Trail and Stormburn Sunrise regenerations; the kaftan
boards (no art); granters as prop pickups; in-game screenshot of the three racks; VIVERSE/Horizon placement of the 20
web GLBs.
