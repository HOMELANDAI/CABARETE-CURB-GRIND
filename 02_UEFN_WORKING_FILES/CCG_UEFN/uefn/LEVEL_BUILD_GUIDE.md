# Cabarete Curb Grind — UEFN Level Build Guide

HomelandAI (HAI) · Fortnite / Unreal Editor for Fortnite · Verse 1.0
Source of truth: `../shared/ccg_data.json` (v0.1.0). Anything numeric here is derived from it.

The island is a 1 758 m (design) / ~1 055 m (world) stretch of Highway 5 in Cabarete,
Dominican Republic, from the **Cabarete Sign** east to the **Courtyard Cabarete turn-in**, plus an 80 m spur
south to the **Courtyard Cabarete Skatepark**,
with four skate parks, six road sections each carrying a signature rail structure,
the HAI Skate Store, three HAI billboards, real signage and storefronts, and **no cars**.

---

## 0. Project setup

1. UEFN → **New Project → Blank** (or "Blank Island"). Name it `CabareteCurbGrind`.
2. Verse Explorer → right-click project → **Add new Verse file to project**, then replace the
   generated files with the five `.verse` files from `Verse/`. Keep them in the same folder so
   they share one Verse module (the devices reference each other by type name).
3. **Build Verse** (Ctrl+Shift+B). All five must compile before you place devices.
4. Island Settings: Game Mode = Free-for-all, Max Players = 1–8, Fall damage = off,
   Infinite Ammo / Building = off, **Vehicles: none** (see §9), Time of Day: driven by the two Day Sequence devices
   (`ccg_timeofday`, §8c) — day 12:00 / sunset 17:50.
5. Graphics: Lumen / Nanite / VSM / TSR are Fortnite defaults — see **`UEFN_GRAPHICS.md`** (v2, max tier: 3-section riders, 2K environment sets, signage pack, `ccg_graphics` director) for the Island Settings
   post-process grade (day / sunset), the Volumetric Fog device, Nanite custom props, rider textures and the VFX spawners.

---

## 1. Scale and coordinate frame

| Item | Value |
|---|---|
| Design frame (data) | local metres, origin = Cabarete Sign, **+X east, +Z south, +Y up** (north = −Z) |
| GPS → metres | 1° lat = 111 320 m, 1° lon = 104 800 m (at 19.75° N) |
| worldScale | **0.6** — every design metre becomes 0.6 m in the world |
| Unreal units | **1 uu = 1 cm** |
| Design → UE | UE X = east · 60 cm per design metre, UE Y = south · 60 cm per design metre, UE Z = up |

UE is left-handed with X forward / Y right / Z up, so facing east (+X) your right is south:
the data frame maps onto UE as `(UE.X, UE.Y, UE.Z) = (x_east, z_south, y_up) × 0.6 × 100`.
The Highway 5 spline therefore runs **+X with a sag toward +Y** (south), exactly as the aerials show.

Place the island origin (0,0,0) on the Cabarete Sign roundabout. Road surface at Z = 0.
Sea level is about Z = −800 (the beach is ~8 m lower than the road and 100–250 m to the north).

---

## 2. Reference imagery (import set-2 shot 01 as a reference plane)

Import `set2_screenshots/01_aerial_whole_route_topdown.jpg` as a texture, apply it to a plane with **Collision: none,
Visible in game: off**, then scale the plane so the Cabarete Sign and the Courtyard turn-in land on the coordinates in §3.
The tilted views and park close-ups are for eyeballing building heights and park footprints; do not use them for
coordinates. Extras 43 is the elevation profile behind the Z column.

Reference imagery: **81 files in three sets** under `/home/claude/ccg/in/shots_all/` (`set1_original/`, `set2_screenshots/`, `set3_extras/`; Google imagery + photo-sphere contributors — reference only, never ship it). The three shot lists are copied into this package's `reference/` folder. Waypoint `shot` codes: plain number = set 2, `x` prefix = set 3.

**Set `set1_original/` — 18 files** (`reference/shot_list_original.txt`): first capture — superseded by set 2 (same imagery; parks were 14–18, no street shots 14/15).

Files: `01_aerial_whole_route_topdown.jpg`, `02_aerial_whole_route_oblique.jpg`, `03_aerial_first_path.jpg`, `04_aerial_second_path_A.jpg`, `05_aerial_second_path_B.jpg`, `06_aerial_third_path.jpg`, `07_street_cabarete_sign_start.jpg`, `08_street_vagamundo_frontage.jpg`, `09_street_second_path_A_plaza.jpg`, `10_street_second_path_A_bend.jpg`, `11_street_multiplex_entrance.jpg`, `12_street_second_path_B_town_center.jpg`, `13_street_mojito_frontage.jpg`, `14_skatepark_vagamundo.jpg`, `15_skatepark_multiplex_1.jpg`, `16_skatepark_multiplex_2.jpg`, `17_skatepark_mojito_3.jpg`, `18_skatepark_cab_courtyard_4.jpg`.

**Set `set2_screenshots/` — 20 files** (`reference/shot_list_screenshots.txt`): aerials 01–06, street 07–15 along the yellow path, park close-ups 16–20.

| File | Size | What it shows | Used for |
|---|---|---|---|
| `01_aerial_whole_route_topdown.jpg` | 2440x1291 | Top-down overview of the full yellow route, Cabarete Sign to Courtyard Cabarete | **main reference plane** |
| `02_aerial_whole_route_oblique.jpg` | 2440x1291 | Whole route, tilted 3D view looking north over Cabarete Bay |  |
| `03_aerial_first_path.jpg` | 2440x1291 | FIRST PATH: Cabarete Sign to Vagamundo, looking along the route (heading 150, tilt 45) |  |
| `04_aerial_second_path_A.jpg` | 2440x1291 | SECOND PATH A: Vagamundo to the Multiplex turn-off (heading 115, tilt 45) |  |
| `05_aerial_second_path_B.jpg` | 2440x1291 | SECOND PATH B: Multiplex to Mojito through the town center (heading 79, tilt 45) |  |
| `06_aerial_third_path.jpg` | 2440x1291 | THIRD PATH: Mojito to Courtyard Cabarete (heading 89, tilt 45) |  |
| `07_street_cabarete_sign_start.jpg` | 2452x1308 | Street level at the Cabarete Sign (route start), facing along the route | waypoint `sign` |
| `08_street_vagamundo_frontage.jpg` | 2452x1308 | Street level at the Vagamundo turn-off, facing the Vagamundo frontage | waypoint `vagamundo` |
| `09_street_second_path_A_plaza.jpg` | 2452x1308 | Second Path A at Ocean Dream Plaza, facing along the route | waypoint `store` |
| `10_street_second_path_A_bend.jpg` | 2452x1308 | Second Path A at the bend, facing along the route | waypoint `bend` |
| `11_street_multiplex_entrance.jpg` | 2452x1308 | Multiplex turn-off: the hoarding wall and dirt pull-in that front the Multiplex lots | waypoint `multiplex` |
| `12_street_second_path_B_town_center.jpg` | 2452x1308 | Second Path B in the town center, facing along the route | waypoint `town` |
| `13_street_mojito_frontage.jpg` | 2452x1308 | Mojito Skatepark Three lot seen from the road (beach visible behind) | waypoint `mojito` |
| `14_street_third_path_toward_bridge.jpg` | 2452x1308 | Third Path facing east along the route toward the pedestrian bridge | waypoint `p1500` / Puente Starlight |
| `15_street_cab_courtyard_turn_in.jpg` | 2452x1308 | Courtyard Cabarete turn-in: the opening between the beach mural wall and the hotel garden that le… | waypoint `courtyard_turnin` — **confirms the P4 position** |
| `16_skatepark_vagamundo.jpg` | 2440x1291 | Close-up, Vagamundo Skate Park area (top-down, ~200 m view) | P1 footprint |
| `17_skatepark_multiplex_1.jpg` | 2440x1291 | Close-up, Cabarete Multiplex Skatepark One area (top-down, ~240 m view) | P2 Lot One |
| `18_skatepark_multiplex_2.jpg` | 2440x1291 | Close-up, Cabarete Multiplex Skatepark Two area (top-down, ~240 m view) | P2 Lot Two |
| `19_skatepark_mojito_3.jpg` | 2440x1291 | Close-up, Mojito Skatepark Three area (top-down, ~190 m view) | P3 footprint |
| `20_skatepark_cab_courtyard_4.jpg` | 2440x1291 | Close-up, Courtyard Cabarete Skatepark area (top-down, ~200 m view) | P4 footprint (top-down) |

**Set `set3_extras/` — 43 files** (`reference/shot_list_extras.txt`): route strips every ~290 m (01–07), forward/back street views every ~250 m (08–24), each park from four sides + two photo spheres (25–42), path stats (43).

| File | Size | What it shows | Used for |
|---|---|---|---|
| `01_strip_0-290m_sign_to_vagamundo.jpg` | 2116x1120 | Top-down strip, Cabarete Sign to just past Vagamundo (about 0-290 m along the route) | S1 strip |
| `02_strip_275-565m.jpg` | 2116x1120 | Top-down strip, Second Path A, about 275-565 m | S2–S3 strip |
| `03_strip_545-835m.jpg` | 2116x1120 | Top-down strip, Second Path A bend toward the Multiplex turn-off, about 545-835 m | S3 strip |
| `04_strip_785-1075m_multiplex.jpg` | 2116x1120 | Top-down strip around the Multiplex turn-off, shifted north to include both Multiplex lots,… | S3b / P2 lots strip |
| `05_strip_1045-1335m_town_center.jpg` | 2116x1120 | Top-down strip, Second Path B through the town center, about 1045-1335 m | S4 strip |
| `06_strip_1285-1575m_mojito.jpg` | 2116x1120 | Top-down strip around Mojito Skatepark Three, about 1285-1575 m | S4–S5 strip |
| `07_strip_1455m-end_cab_courtyard.jpg` | 2116x1120 | Top-down strip, Third Path to the Courtyard Cabarete turn-in (route end) | S5 strip to the turn-in |
| `08_street_0m_sign_looking_back.jpg` | 2102x1121 | At the Cabarete Sign start point, looking back up the road (north-west), away from the route |  |
| `09_street_110m_forward.jpg` | 2102x1121 | First Path, about 110 m in, facing along the route toward Vagamundo (the Gypsy Bowls / Cabar… | waypoint `p110` |
| `10_street_300m_forward.jpg` | 1786x953 | Second Path A, about 300 m in, facing along the route | waypoint `p300` |
| `11_street_525m_forward.jpg` | 1786x953 | Second Path A, about 525 m in, facing along the route | waypoint `p525` |
| `12_street_525m_back.jpg` | 1786x953 | Same spot (about 525 m), looking back the way you came |  |
| `13_street_765m_forward.jpg` | 1786x953 | Second Path A, about 765 m in, facing along the route toward the Multiplex stretch | waypoint `p765` |
| `14_street_765m_back.jpg` | 1786x953 | Same spot (about 765 m), looking back toward the bend |  |
| `15_street_905m_back_multiplex_wall.jpg` | 1786x953 | Just past the Multiplex turn-off (about 905 m), looking back west along the hoarding wall th… | waypoint `p905` |
| `16_street_1000m_forward.jpg` | 1786x953 | Second Path B, about 1000 m in, entering the town center | waypoint `p1000` |
| `17_street_1000m_back.jpg` | 1786x953 | Same spot (about 1000 m), looking back west toward the Multiplex turn-off |  |
| `18_street_1205m_forward.jpg` | 1786x953 | Second Path B, about 1205 m in, east end of the town center, facing along the route | waypoint `p1205` |
| `19_street_1205m_back.jpg` | 1786x953 | Same spot (about 1205 m), looking back west through the town center |  |
| `20_street_1383m_forward_at_mojito.jpg` | 1786x953 | In front of Mojito Skatepark Three (about 1383 m), facing east along the route (the Mojito l… |  |
| `21_street_1383m_back_at_mojito.jpg` | 1786x953 | Same spot in front of Mojito, looking back west (the mural wall beside the Mojito lot is on… |  |
| `22_street_1500m_back.jpg` | 1786x953 | Third Path (about 1500 m), looking back west toward Mojito |  |
| `23_street_1560m_forward.jpg` | 1786x953 | Third Path, about 1560 m in, facing east toward the Courtyard Cabarete turn-in | waypoint `p1560` |
| `24_street_route_end_looking_back.jpg` | 1786x953 | At the Courtyard Cabarete turn-in (route end), looking back west along the route |  |
| `25_vagamundo_from_south.jpg` | 1799x952 | Vagamundo Skate Park, tilted view looking north | P1 from four sides |
| `26_vagamundo_from_west.jpg` | 1799x952 | Vagamundo Skate Park, tilted view looking east (camera over the road) | P1 from four sides |
| `27_vagamundo_from_north.jpg` | 1799x952 | Vagamundo Skate Park, tilted view looking south | P1 from four sides |
| `28_vagamundo_from_east.jpg` | 1799x952 | Vagamundo Skate Park, tilted view looking west toward the road | P1 from four sides |
| `29_vagamundo_photo_sphere.jpg` | 2102x1121 | Contributor photo sphere at the Vagamundo entrance, facing the Vagamundo Skate Park pin |  |
| `30_multiplex_1_and_2_from_south.jpg` | 1799x952 | Both Cabarete Multiplex lots, tilted view looking north from the road toward the beach | P2 from four sides |
| `31_multiplex_1_and_2_from_west.jpg` | 1799x952 | Both Multiplex lots, tilted view looking east along the coast | P2 from four sides |
| `32_multiplex_1_and_2_from_north.jpg` | 1799x952 | Both Multiplex lots, tilted view looking south from the beach toward the road | P2 from four sides |
| `33_multiplex_1_and_2_from_east.jpg` | 1799x952 | Both Multiplex lots, tilted view looking west (road on the left, beach on the right) | P2 from four sides |
| `34_mojito_from_south.jpg` | 1799x952 | Mojito Skatepark Three, tilted view looking north from the road to the beach | P3 from four sides |
| `35_mojito_from_west.jpg` | 1799x952 | Mojito Skatepark Three, tilted view looking east (beach on the left, road on the right) | P3 from four sides |
| `36_mojito_from_north.jpg` | 1799x952 | Mojito Skatepark Three, tilted view looking south from over the beach | P3 from four sides |
| `37_mojito_from_east.jpg` | 1799x952 | Mojito Skatepark Three, tilted view looking west (road on the left, beach on the right) | P3 from four sides |
| `38_mojito_photo_sphere_from_beach.jpg` | 2102x1121 | Contributor photo sphere on the beach just north-west of the Mojito lot, facing the lot |  |
| `39_cab_courtyard_from_south.jpg` | 1799x952 | Courtyard Cabarete Skatepark, tilted view looking north toward the road | P4 from four sides — **confirms the P4 position** |
| `40_cab_courtyard_from_west.jpg` | 1799x952 | Courtyard Cabarete Skatepark, tilted view looking east (road and turn-in on the left) | P4 from four sides — **confirms the P4 position** |
| `41_cab_courtyard_from_north.jpg` | 1799x952 | Courtyard Cabarete Skatepark, tilted view looking south from over the road | P4 from four sides — **confirms the P4 position** |
| `42_cab_courtyard_from_east.jpg` | 1799x952 | Courtyard Cabarete Skatepark, tilted view looking west (turn-in path and road on the right) | P4 from four sides — **confirms the P4 position** |
| `43_path_stats_length_elevation_slope.jpg` | 2568x1159 | Length, elevation profile and slope for FIRST PATH (224 m), SECOND PATH A (683 m), SECOND PA… | **elevation profile** used for the Z column |

---

## 3. Highway 5 spline — waypoint coordinates (18 GPS points)

Computed from GPS exactly as `game.coordinateFrame` says, then × worldScale (0.6), then × 100 (cm).
Use a **Spline** (Fortnite Creative "Spline" tool / Landscape Spline for the road mesh) through the 17 road points in
order (#0–#16); #17 is the courtyard spur. Route length `game.routeLengthM` = **1 758 m** design.

| # | key | Name | lat, lon | along (design m) | elev (m ASL → design Y) | **UE X, Y, Z (cm)** | shot |
|---|---|---|---|---|---|---|---|
| 0 | `sign` | Cabarete Sign | 19.753313, -70.416768 | 0 | 6.6 → 1.6 | **0, 0, 96** | shots 07 |
| 1 | `p110` | First Path, 110 m (Cabarete Bakery side) | 19.752496, -70.416351 | 110 | 6.1 → 1.1 | **2 622, 5 457, 67** | extras 09 |
| 2 | `vagamundo` | Vagamundo | 19.751627, -70.415814 | 224 | 5.6 → 0.6 | **5 999, 11 261, 36** | shots 08 |
| 3 | `p300` | Second Path A, 300 m | 19.751054, -70.415331 | 300 | 6.9 → 1.9 | **9 036, 15 088, 115** | extras 10 |
| 4 | `store` | HAI Skate Store (Ocean Dream Plaza) | 19.750381, -70.414531 | 470 | 9.3 → 4.3 | **14 066, 19 583, 259** | shots 09 |
| 5 | `p525` | Second Path A, 525 m | 19.749852, -70.413640 | 525 | 8.8 → 3.8 | **19 669, 23 117, 229** | extras 11 |
| 6 | `bend` | Second Path A bend | 19.749604, -70.412909 | 650 | 7.7 → 2.7 | **24 265, 24 773, 160** | shots 10 |
| 7 | `p765` | Second Path A, 765 m | 19.749350, -70.411462 | 765 | 6.6 → 1.6 | **33 364, 26 470, 97** | extras 13 |
| 8 | `multiplex` | Carve Cabarete Multiplex turn-off | 19.749378, -70.410392 | 833 | 6.0 → 1.0 | **40 092, 26 283, 60** | shots 11 |
| 9 | `p905` | Past the multiplex wall, 905 m | 19.749425, -70.410107 | 905 | 6.5 → 1.5 | **41 884, 25 969, 92** | extras 15 |
| 10 | `p1000` | Entering town center, 1000 m | 19.749569, -70.409247 | 1000 | 7.3 → 2.3 | **47 292, 25 007, 135** | extras 16 |
| 11 | `town` | Town center | 19.749782, -70.408211 | 1100 | 8.0 → 3.0 | **53 806, 23 584, 180** | shots 12 |
| 12 | `p1205` | East end of town center, 1205 m | 19.749940, -70.407359 | 1205 | 8.4 → 3.4 | **59 164, 22 529, 202** | extras 18 |
| 13 | `mojito` | Mojito Skate Park | 19.750241, -70.405830 | 1383 | 9.0 → 4.0 | **68 778, 20 519, 240** | shots 13 |
| 14 | `p1500` | Third Path, 1500 m (toward Puente Starlight) | 19.750444, -70.404595 | 1500 | 8.0 → 3.0 | **76 544, 19 163, 180** | shots 14 |
| 15 | `p1560` | Third Path, 1560 m | 19.750575, -70.404036 | 1560 | 7.3 → 2.3 | **80 059, 18 288, 138** | extras 23 |
| 16 | `courtyard_turnin` | Courtyard Cabarete turn-in (route end on Highway 5) | 19.750683, -70.403463 | 1758 | 5.0 → 0.0 | **83 662, 17 566, 0** | shots 15 |
| 17 | `courtyard` | Courtyard Cabarete Skatepark (spur south of the road) — **spur**, 80 m dirt drive south of the turn-in (P4, finish) | 19.750239, -70.403150 | 1840 | 5.0 → 0.0 | **85 630, 20 532, 0** | shots 20 |

Elevation: the road is **not** flat. Z comes from `game.paths[].elev` / the profile in extras shot 43, interpolated
between these anchors (metres above sea level): sign 6.6, Vagamundo 5.6, ~450 m 9.5, Multiplex 6.0, town 8.0, Mojito 9.0,
1500 m (footbridge) 8.0, turn-in 5.0, courtyard 5.0; **5.0 is subtracted so the lowest point is 0**, then × worldScale.
Max slope is 5.4° (Second Path A). `UCCGDataLibrary::WaypointWorldLocation()` still returns Z = 0 — apply the Z column
when placing the spline points. The road spline **ends at `courtyard_turnin` (1 758 m)**; `courtyard` is off-route
(`spur: true`), reached by the dirt drive (§6, P4).

Road: two lanes + shoulders ≈ 9 m design → **540 cm wide** in world; curb height 15 cm → 9 cm.
Side rails sit on the curb line, ±270 cm from the spline. Tangents: smooth (auto), no kinks except
the deliberate bend at `bend` (#6).

Positions of anything given only as `alongM` in the data are interpolated linearly between the two
bracketing waypoints (that is what the tables in §6–§8 do).

---

## 4. Galleries and props

| Need | Fortnite source | Notes |
|---|---|---|
| Road, curbs, sidewalks | **Road Gallery**, **Sidewalk Gallery** (Creative) | Shoulders in "Dirt Road" pieces east of the town |
| Flat rails, kinked rails | **Skatepark Gallery** (Flat Bar, Round Rail, Kink Rail, Handrail) | Primary rail set |
| Long / shaped rails (Kite Line, Wave, Palm Wrap, Power-Line) | **Pipe Gallery** (Pipe Straight/Curve/Elbow) + Skatepark Round Rail | Pipes bend; rails do not. Build curves from 15°/45° pipe elbows |
| Ramps, quarter pipes, bowls, spine, hip, volcano | **Skatepark Gallery** (Quarter Pipe, Half Pipe, Bank, Spine, Fun Box, Pyramid) | Scale 0.6 to match worldScale, or leave 1.0 for "big park" feel — pick one and be consistent |
| Stairs, hubba ledges | **Stair Gallery**, **Concrete Block Gallery** | 10-stair = two 5-step stair pieces |
| Manual pads, planters | **Concrete Block Gallery**, **Planter props** (Pleasant Park / Lazy Lagoon) | |
| Palms | **Tropical Tree Gallery** (Palm Tall / Palm Short) | Palm Wrap and pole jams |
| Utility poles / power lines | **Power Line Gallery** (Pole, Line) | Power-Line Rail is a Pipe along the line |
| Storefronts, hoarding wall | **Retail Row / Tilted Towers Building Galleries**, **Fence Gallery (Plywood)** | Keep real-world signage *shapes*; use text on Billboard devices for names |
| Beach / sea | Landscape + **Water Gallery** | North of the road |
| Store interior | **Retail Row Shop props**, Skatepark deck props | §7 |
| Billboards | **Billboard device** (text) ×3 | §8 |

---

## 5. Signature rail structures (one per section, six total)

Each is a `ccg_rail` Verse device + a visible mesh + an ordered chain of **marker props** (empty
"Prop Marker" or any tiny invisible prop) that trace the rail centreline. Marker spacing 50–100 uu on
straights, **25 uu** on tight curves. Set `RailId` to the signature id. Place the catch volume as a
thin volume_device over the first 150 uu of the rail (or the whole rail for mid-entry).

Section midpoint coordinates (interpolated along the spline) are where the structure's **entry**
should be; run the structure eastward from there.

| Section | Signature (id) | Midpoint UE X, Y (cm) | How to build it | Trick the data expects |
|---|---|---|---|---|
| S1 sign→vagamundo | **Kite Line** (`kite_line`) | 2 681, 5 559 | Pipe rail that **climbs ~250 uu, dips, climbs again** like a kite string, then forms a **2 m design = 120 cm loop** (vertical ring of 8 pipe elbows). Markers follow the pipe through the loop. `RideHeightCm` 95. | 50-50 through the loop |
| S2 vagamundo→store | **Wave Rail** (`wave_rail`) | 10 427, 16 331 | Sine wave of 4 crests, **1.2 m design = 72 cm** crest height, 6 m design = 360 cm wavelength. Pipe 45° elbows. Also duplicate inside P3 Mojito (its feature list includes it). | switch grinds on each crest |
| S3 store→multiplex | **Palm Wrap** (`palm_wrap`) | 24 384, 24 795 | Pipe spiralling **twice** around a Palm Tall trunk (radius 90 cm, rise 60 cm per turn), exiting onto a 400 cm flat bar. 24 markers per turn. `IsSlideRail` false. | 720 body rotation while grinding |
| S3b multiplex spur | **Chevron Switchback** (`chevron`) | 40 092, 26 283 | Zig-zag kinked rail across the dirt pull-in in front of the hoarding wall (shot 11): 5 segments, 30° kinks, Kink Rail pieces. One `ccg_rail` per straight segment so transfers are real exits/entries. | transfers at each kink |
| S4 multiplex→mojito | **Power-Line Rail** (`powerline`) | 54 215, 23 504 | Pipe strung between two Power Line poles **4 m design = 240 cm up**, entered from a Skatepark **Bank** kicker on the south curb. Set `RideHeightCm` 95, `MaxGrindSeconds` 6. | boardslide at height (`IsSlideRail` true), land to manual |
| S5 mojito→turn-in | **Twin Twist** (`twin_twist`) | 80 250, 18 249 | Two pipe rails that **cross over each other three times** (helix, 150 cm apart, crossing every 400 cm; the under rail dips 40 cm). Two `ccg_rail` devices, each with its own marker chain. | rail transfers at each crossover |

Ordinary roadside rails: every section (except S3b) has rails **both sides**. Use Skatepark Flat
Bar / Round Rail, 400–800 cm long, one `ccg_rail` per piece (bulk-duplicate the device with its
markers and catch volume; markers are children of the device so Alt-drag copies the set).

---

## 6. Parks

Set `ccg_game_manager` ParkZoneP1..P4 to a volume_device covering each footprint (height 1500 uu).

### P1 — Vagamundo Hybrid Park (bonus, **locked**) — UE 5 999, 11 261 (north side)
Keep the Vagamundo restaurant intact (shot 08 frontage). Build an **elevated skate deck on stilts
above the roof** (deck at Z ≈ 450): roof-deck bowl (Skatepark Half Pipe ring), **quarter-pipe ring**
around the deck edge, **two roll-ins** from the road side (Banks from Z 0 to 450), **ridge rails**
along the roof ridge, a **stone-wall ledge** at street level, and **palm pole jams** (Palm Short
leaning 30°). Put a `barrier_device` (VagamundoBarrier) across both roll-ins — Verse enables it at
start and disables it when P2+P3+P4 are mastered. masterScore 0 → the first landed line counts.

### P2 — Carve Cabarete Multiplex (main, masterScore **25 000**) — UE 40 092, 26 283 (north, via spur)
Two lots north of Highway 5 reached by the spur road through the hoarding wall (shot 11).
- **Lot One (street)**: 10-stair with handrails, hubba ledges, stepped ledges, double manual pad,
  flat rails, pyramid, A-frame rail, euro gap. Lot ≈ 60×40 m design → 3 600×2 400 uu.
- **Lot Two (transition)**: bowl, mini ramp, spine, volcano, hip, wallride, roll-in.
Use shots 15/16 for footprints. The Chevron Switchback sits in the pull-in between the road and the lots.

### P3 — Mojito Skate Park (main, masterScore **20 000**) — UE 68 778, 20 519 (north, beach behind)
Open clearing between road and beach (shot 13/17). **Snake run** sloping toward the sand (Banks
in a 3-bend S), **sea-facing quarter pipes** along the north edge, a **hip**, the **Wave Rail**
duplicate, a **manual pad**, **palm pole jams**. Ocean must be visible to the north.

### P4 — Courtyard Cabarete Skatepark (main, masterScore **20 000**) — spur, UE 85 630, 20 532 (south)
Position **confirmed** by shot 15 (the turn-in at street level) and the four tilted views 39–42 in set 3. The route ends on
Highway 5 at `courtyard_turnin` (UE 83 662, 17 566, 1 758 m): a dirt drive between the
**beach-mural wall** (the HAI SKATE billboard stands on top of it, §8) and the ProCab hotel's **bougainvillea hedge** runs
~80 m south (heading ≈ 177°) and **banks down** into the courtyard of the red-roofed ProCab blocks. Build the spur as a
second short spline from the turn-in to the courtyard centre; the finish sits at the bottom of the drive.

Layout (shot 20 top-down + 39–42): a **long west block with pool loungers** along it, **two blocks on the east**, **lawn and
planters in the middle**, open on the road side. Features from the data: entry drive (bank down from the road), planter
manual pad, lawn-edge ledges, mini ramp at the far end, pole jams, lounger-row rail, balcony rails, and a **mural-wall
wallride at the turn-in**. Put the `FinishTrigger` (trigger_device) across the bottom of the drive so the run ends on
arrival; the results HUD shows, then `end_game_device` fires. The P4 volume covers the courtyard, not the road.

### P4 bonus — Horseshoe Rail Skate Ramp (`bonusFeature`)

Two 5.0 m ramps 6.0 m long x 6.0 m wide with a 3.0 m x 2.5 m concrete tunnel through each base (graffiti inside, lit), joined at ground level by a continuous horseshoe grind rail: 60 mm steel tube, 250 mm high, 8.0 m center-arc radius, posts every 1.2 m with base plates, optional LED strip. Riders drop in from one deck, pass through the tunnel, lock onto the horseshoe, grind the full U, and exit through the far tunnel up the other ramp.

| Element | Design spec (ccg_data) | World (× 0.6) |
|---|---|---|
| Ramps | two, 5.0 m high, 6.0 m long × 6.0 m wide, smooth concrete | 3.0 m high, 3.6 × 3.6 m |
| Tunnels | one through each ramp base, 3.0 m wide × 2.5 m high, concrete with graffiti art, lit | 1.8 × 1.50 m |
| Horseshoe rail | ground level, continuous U, centre-arc radius 8.0 m, Ø60 mm steel round tube, 250 mm high | R 4.8 m, Ø36 mm, 150 mm high (≈ 15.1 m of rail) |
| Posts | every 1.2 m with base plates | every 0.72 m |
| Lighting | LED strip (optional) + deck floodlights | LED strip along the rail + a floodlight on each deck (sunset mode) |

**Placement**: beach side of the courtyard, behind the west block, screened from Highway 5 (not visible from the road). Centre ≈ 25 m design west of the courtyard centre (behind the west block): **UE ≈ 84 130, 20 532** (cm), decks on the ±X ends, tunnels facing each other along X, the U bulging toward −Y (north / beach side). Blueprint: `reference/horseshoe_rail_blueprint.png`.

**Intended line**: drop in from one deck → down the ramp → through the tunnel in its base (+200) → lock onto the horseshoe at ground level → grind the full U (80/m) → exit through the far tunnel (+200) → up the other ramp. Full U without bailing = **Horseshoe Bonus +2,500**; sparks run at **2×** on this rail.

**Scoring** (`parks[P4].bonusFeature.scoring`, on top of park mastery): 80/m on the horseshoe, +200 per tunnel pass-through, +2,500 full-U bonus, Metal Sparks ×2.

UEFN build: two Skatepark-gallery **Banks** stacked to 300 cm (5 m design) with a 180 × 150 cm tunnel cut (Concrete Block
gallery arch + graffiti Billboard inside), the U from Pipe-gallery quarter elbows (R 480 cm) on 15 cm posts, LED strip =
emissive trim. Devices: one `ccg_rail` with **`IsHorseshoe` true** and `RailId` `horseshoe` (markers every 25 uu around the
U; `IsSteel` true so `Sparks` runs ×2), two `volume_device`s in the tunnels → `ccg_game_manager.TunnelVolumes[0..1]`
(+200 each), two deck floodlights in `ccg_timeofday.ParkFloodlights[]`. `ccg_rail` calls `Manager.AwardHorseshoe(Agent,
Meters, FullU)` — FullU = the rider reached the last marker.

---

## 7. HAI Skate Store (Ocean Dream Plaza) — UE 14 066, 19 583 (north)

Convert one Ocean Dream Plaza unit (shot 09) into the store. Interior: a flannel wall (free), a knit/tee rack,
the rain-suit rail, the three kaftan racks, deck walls. Only the **23 priced rows** need a **button_device +
item_granter_device** pair, bound by index to `ccg_store.PurchaseButtons[i]` / `PurchaseGranters[i]`
(order listed in the header of `ccg_store.verse`). Free and earned rows are display shelves — ownership is
tracked by `ccg_store` and granted by `ccg_game_manager` events. Put the `StoreVolume` over the doorway so the
HUD shows the player's balance.

| Buttons/granters `[i]` | Rows | Price (points) | Granter contents |
|---|---|---|---|
| 0–4 | 5 rain suits (each with its cruiser deck) | 5 500 | a wrap, or a class change carrying the suit + a deck prop |
| 5–10 | 6 Dapper Dan Remix kaftans (matching deck bundled by `ccg_store`) | 7 500 | wrap / class change + deck prop |
| 11–19 | 9 Carved Nine outfits, each pairs with a Carved Nine deck | 2 500 | a wrap, or a class change via a class designer carrying the outfit |
| 20–22 | Ivory (6 decks) · Carved Nine (9) · Dojo (11) — **refused until one park is mastered** | 4 000 · 6 000 · 5 000 | deck props as pickups, or one wrap |

Fortnite **cannot grant real cosmetics**. The granter should give a deck **prop pickup** (a Skatepark
deck mesh as a consumable) or a **wrap**; clothing is best modelled as a class switch. Prices, names and tiers
are generated into `ccg_store.verse` from `ccg_data.store` — re-run the generator rather than editing by hand.
Optional `CosmeticGranters[]` (one per catalog row, same order as `Catalog()`) fires for free/earned grants.

Deck names (for shelf labels / Billboard text): see `../shared/ccg_data.json → store.collections[].decks`,
`store.starterDecks` (sizes) and `store.kaftanDecks`.

---

## 8. Sign Twins, Sign Gap, billboards, landmarks

**Sign Twins.** At the origin, build the CABARETE letter sign (shot 07) and a mirrored **twin** on the
opposite side of the roundabout so the two stacks face each other across the road, 12 m design =
**720 cm** apart, letter tops at 300 cm. Between them place a **Bank** kicker on each side. The
`SignGapVolume` (volume_device) spans the gap, **bottom at Z 250**, so only an airborne rider clips it:
entering it = **Sign Gap, +1 500** (`scoring.signGap`) added to the open combo.

**Billboards** (Billboard devices, HAI branding is allowed *only* here and in the store):

| alongM | side | Text | Grindable top edge? | UE X, Y (cm) |
|---|---|---|---|---|
| 150 | south | `HOMELAND AI` | yes → `ccg_rail` along the top edge | 3 807, 7 493 |
| 720 | north | `HAI · people places possibilities` | no | 29 804, 25 806 |
| 1740 | south | `HAI SKATE` | yes → `ccg_rail` along the top edge | 83 334, 17 632 — real billboard stands above the mural wall at the courtyard turn-in; use it for the HAI SKATE board |

**Landmarks** (real signage/storefronts to keep — build the shape, label with a Billboard device):

| alongM | side | Name | UE X, Y (cm) |
|---|---|---|---|
| 10 | south | Radio mast compound | 238, 496 |
| 20 | north | Shell station | 477, 992 |
| 110 | north | Cabarete Bakery | 2 622, 5 457 |
| 120 | north | Gypsy Bowls | 2 918, 5 966 |
| 212 | north | Vagamundo | 5 643, 10 650 |
| 330 | south | Gorditos Fresh Mex | 9 924, 15 882 |
| 470 | north | Ocean Dream Plaza | 14 066, 19 583 |
| 560 | south | The Honey Company Cafe | 20 956, 23 581 |
| 800 | north | Isla Verde Beach AI | 36 827, 26 373 |
| 880 | north | Hotel Villa Taina | 41 262, 26 078 |
| 900 | south | Full Moon Bar and restaurant | 41 760, 25 991 |
| 940 | south | Marión Café y más | 43 877, 25 614 |
| 980 | south | Pizza and Spaghetti House | 46 154, 25 209 |
| 1020 | south | Fresh Fresh Café | 48 595, 24 722 |
| 1200 | north | OJO Club | 58 909, 22 579 |
| 1250 | south | Scotiabank Cabarete | 61 594, 22 021 |
| 1290 | north | Olivia's Cabarete | 63 755, 21 569 |
| 1300 | north | Mojito Bar | 64 295, 21 456 |
| 1360 | south | Plaza Garden | 67 536, 20 778 |
| 1500 | over road | Puente Starlight (pedestrian bridge) — grindable handrails | 76 544, 19 163 |
| 1560 | south | Presidential Suites Cabarete | 80 059, 18 288 |
| 1600 | north | La Santa Paella | 80 787, 18 142 |
| 1640 | north | Claro | 81 515, 17 996 |
| 1680 | north | Yummy food Cabarete | 82 242, 17 850 |
| 1740 | south | Beach mural wall + billboard | 83 334, 17 632 |
| 1770 | south | ProCab hotel garden (bougainvillea) | 83 662, 17 566 |

---

## 8b. HAI murals (six wallride walls)

`ccg_data.murals`: six HAI murals painted on real wall spots, in travel order. Textures are in this package's
`assets/murals/<id>.jpg` — import each as a texture, apply it to a flat wall prop sized to the world size below,
flush on the wall. Every mural is a **wallride surface** (keep the wall's collision; a `ccg_rail` with `IsSteel` false
along its base can pay a wallride as a slide), and each gets a **wash light at sunset** (`ccg_timeofday.MuralWashLights`,
one `customizable_light_device` per mural, warm `#FFD9A0`, off in day). A `volume_device` hugging each wall (150 uu deep)
goes into `ccg_game_manager.MuralVolumes[0..5]` **in this order** so the results HUD can count **murals seen x/6**.

| alongM | side | Mural (`id`) | Wall | Size w × h (design m → world) | UE X, Y (cm) |
|---|---|---|---|---|---|
| 150 | south | **Home of the Vicewave** (`mural_vicewave`) | Compound wall after the Shell station (shot 07/x09), first path | 3.2 × 4.0 → 1.92 × 2.40 m | 3 807, 7 493 |
| 420 | north | **Clisante Rush** (`mural_clisante_rush`) | Long white wall before Ocean Dream Plaza (shot x10), second path A | 6.22 × 3.5 → 3.73 × 2.10 m | 12 587, 18 261 |
| 905 | north | **HomelandAI Over Everything** (`mural_over_everything`) | Hoarding wall fronting the multiplex lots (shot 11/x15) — the real graffiti wall | 2.25 × 4.0 → 1.35 × 2.40 m | 41 884, 25 969 |
| 1120 | south | **Schnauzer Detectives** (`mural_schnauzer_detectives`) | Blank side wall in the town center (shot x16-x18) | 6.22 × 3.5 → 3.73 × 2.10 m | 54 827, 23 383 |
| 1383 | north | **PPA Microdrama** (`mural_ppa_microdrama`) | Mural wall beside the Mojito lot (shot x21) | 4.0 × 4.0 → 2.40 × 2.40 m | 68 778, 20 519 |
| 1740 | south | **Paw Power Arena** (`mural_paw_power_arena`) | Beach-mural wall at the Courtyard Cabarete turn-in (shot 15), under the billboard | 4.0 × 4.0 → 2.40 × 2.40 m | 83 334, 17 632 |

---

## 8c. Sunset mode (`ccg_timeofday`)

Two looks from `ccg_data.timeOfDay`: **day** (default, sun 62°, Caribbean noon) and **sunset** (sun 6° from the west —
behind the Cabarete Sign — sky top `#2B1E5A` → horizon `#FF8A3D`, sun `#FFB347`, fog `#E89A6B`, ambient 0.35; long shadows,
sea reflecting the sun, *not* fully dark). In sunset the **park floodlights** (`#FFF2D6`, 9 m masts, 4 per park), **street
lamps** (`#FFD9A0`, every 40 m design = 24 m world, both curbs), the six **mural wash lights** and the **neon signs**
(HAI SKATE, OJO CLUB, Mojito Bar, Full Moon, Olivia's) come on. Toggle: start screen, pause menu, key T.

Author **two Day Sequence devices** (one fixed at 12:00, one at ~17:50 — full value tables in `UEFN_GRAPHICS.md` §2a) and
`ccg_timeofday` cross-fades them (`FadeIn` / `FadeOut`, Fade Speed 0.4, Blend Time 4 s; `UseFade` off = hard swap). Lumen
GI/reflections are on by default in Fortnite, so the floodlights and neon bounce for free. The **max tier** layers
`ccg_graphics` on top: an Environment Light Rig keyed by `LS_CCG_Sunset` (`Play` = sunset, `PlayReverse` = day), the
`LS_CCG_WetRoad` material track (road `Wetness` 0 → 0.35 so puddles reflect the floods), heat haze at the Horseshoe tunnel
exits, a pooled pair of spark lights and the mural-wash flicker — wiring in `UEFN_GRAPHICS.md` §2b, §6. Lights:
`customizable_light_device`s in `ParkFloodlights[]` (16), `StreetLamps[]`, `MuralWashLights[]` (6); neon: `NeonLit[]` /
`NeonUnlit[]` creative_prop pairs shown/hidden (or the `M_CCG_Sign` emissive keyed by the sequence). `ToggleButton` = a
button at the start kiosk. `ModeChangedEvent` lets other devices react.

## 8d. Metal Sparks (`fx_sparks`)

`fx_sparks` (**Metal Sparks**) is an **earned** store row (kind `effect`, unlock key `grind:50` = the first grind worth
≥ 50 points) that is **off by default** even when owned; the player flips it in the store's Effects shelf / pause menu.
While a rider with it active grinds or slides a **steel** rail, orange-white sparks (`#FFF4C2` → `#FF5A1F`) burst from the
rear truck at the rail contact: 220/s at max speed scaled by speed, lifetime 0.25–0.6 s, 2–6 m/s in a 35° cone, gravity +
ground bounce, a 1.5 cd flickering point light and a faint scorch glow along the rail. Twice as intense in sunset mode.

UEFN: mount a **VFX Spawner device** along each steel rail and point `ccg_rail.Sparks` at it (leave `IsSteel` true; set it
false on ledges). `ccg_rail` enables the spawner for the grind only when `ccg_store.IsEffectActive(Player, "fx_sparks")`.
The row is granted by `ccg_game_manager` (`GrantEarned "grind:50"`); `ccg_store.EffectToggleButton` (store > Effects) flips it
with `ToggleEffect`. Author the spawner's particle with the values above (orange-white, cone 35°, gravity, bounce).

---

## 9. The "no cars" rule

`game.rules`: *Remove every car from the world.* In UEFN: no vehicle spawners, no parked-car props
from the Vehicle/Prop galleries, Island Settings → Vehicles disabled, and strip the cars out of any
building gallery preset that ships with them (Retail Row lots). Motorbikes, mopeds and tuk-tuks count
as cars. Bicycles and the pedestrian bridge are fine. Rail both curbs instead — the empty road **is**
the level.

---

## 10. Riders

`ccg_rider_select` expects **7 class_designer_devices**, **7 class_and_team_selector_devices** (each
set to the matching class id) and **7 button_devices** on podiums at the start area, in this order:
Kefla, Koda the Husky, Crash the Collie, Yara (Model 10), Sunny (Model 11), Rubí (Model 6), Kai (Model 2).
Set each class designer's movement speed from the rider's `speed` stat (speed 5 → 1.0×, each point
±0.1×). Fortnite does not allow custom player skeletons: the dogs are represented by a Fortnite
character class with the dog mesh (see `manifest.json` import notes) placed as a **cosmetic prop
stand-in** on the podium and on the results screen, and by a dog-themed wrap/emote during play.
The women use Fortnite skins closest to their `profile` (hair/look) with the model number in the HUD.

---

## 11. Device wiring table

| Device you place | Type | Binds to (Verse device → @editable) |
|---|---|---|
| Park volume over P1 Vagamundo | volume_device | `ccg_game_manager.ParkZoneP1` |
| Park volume over P2 Multiplex (both lots) | volume_device | `ccg_game_manager.ParkZoneP2` |
| Park volume over P3 Mojito | volume_device | `ccg_game_manager.ParkZoneP3` |
| Park volume over P4 Courtyard | volume_device | `ccg_game_manager.ParkZoneP4` |
| Store doorway volume | volume_device | `ccg_game_manager.StoreVolume` |
| Volume between the Sign Twins, bottom Z 250 | volume_device | `ccg_game_manager.SignGapVolume` |
| Trigger at the bottom of the courtyard drive (spur) | trigger_device | `ccg_game_manager.FinishTrigger` |
| Barrier across Vagamundo roll-ins | barrier_device | `ccg_game_manager.VagamundoBarrier` |
| HUD message | hud_message_device | `ccg_game_manager.Hud`, `ccg_store.Hud`, `ccg_rider_select.Hud` (one device is fine) |
| End game | end_game_device | `ccg_game_manager.EndGame` |
| Optional debug buttons ×6 | button_device | `ccg_game_manager.DebugTrickButtons[0..5]` (ollie, kickflip, heelflip, popShoveIt, treFlip, grab) |
| Game manager device itself | ccg_game_manager | `ccg_store.Manager`, every `ccg_rail.Manager` |
| Per rail: marker props (ordered) | creative_prop[] | `ccg_rail.RailPoints` |
| Per rail: visible rail mesh | creative_prop | `ccg_rail.RailMesh` |
| Per rail: thin catch volume | volume_device | `ccg_rail.CatchVolume` |
| Store buttons ×23 | button_device | `ccg_store.PurchaseButtons[0..22]` (order in the `ccg_store.verse` header) |
| Store granters ×23 | item_granter_device | `ccg_store.PurchaseGranters[0..22]` (same order) |
| Store device itself | ccg_store | `ccg_game_manager.Store` (earned-tier grants) |
| Effects toggle button | button_device | `ccg_store.EffectToggleButton` (Metal Sparks on/off) |
| Sparks VFX per steel rail | vfx_spawner_device | `ccg_rail.Sparks` (+ `IsSteel`) |
| Mural volumes ×6 | volume_device | `ccg_game_manager.MuralVolumes[0..5]` (data order, §8b) |
| Horseshoe rail (P4 bonus) | ccg_rail | `IsHorseshoe` true, `RailId` `horseshoe`, `IsSteel` true |
| Tunnel volumes ×2 (P4 bonus) | volume_device | `ccg_game_manager.TunnelVolumes[0..1]` |
| Time-of-day device | ccg_timeofday | `DaySequence`, `SunsetSequence` (day_sequence_device ×2), `ParkFloodlights[]`, `StreetLamps[]`, `MuralWashLights[]`, `NeonLit[]`/`NeonUnlit[]`, `ToggleButton`, `Hud` |
| Rider class designers ×7 | class_designer_device | `ccg_rider_select.ClassSlots[0..6]` |
| Rider class selectors ×7 | class_and_team_selector_device | `ccg_rider_select.ClassSelectors[0..6]` |
| Rider podium buttons ×7 | button_device | `ccg_rider_select.SelectButtons[0..6]` |

Trick scoring hooks: `ccg_game_manager.AwardTrick(Agent, "kickflip")`, `.Land(Agent)`, `.Bail(Agent)`
are public — call them from your animation/emote or input devices (e.g. a `trigger_device` on a
kicker lip = ollie; a timer after airborne = Land). Without those hooks, grinds (`ccg_rail`) and the
Sign Gap still score, and the debug buttons exercise the flat tricks.

---

## 12. Test checklist

- [ ] Build Verse: 0 errors.
- [ ] Spawn at the Sign Twins; roll east; the first roadside rail grinds and the HUD shows `Grind N m +P`.
- [ ] Clear the Sign Gap off the kicker → `SIGN GAP! +1500`.
- [ ] Enter P2 → HUD "Carve Cabarete Multiplex"; land 25 000 points inside it → "MASTERED".
- [ ] Master P2, P3, P4 → Vagamundo barrier drops, HUD "Vagamundo roof deck unlocked".
- [ ] Spawn → HUD says the free kit (28 rows) is yours.
- [ ] Enter the store, buy a rain suit (5 500) → score drops, granter fires, re-buy refused; The Carved Nine (6 000) is refused until a park is mastered.
- [ ] Clear the Sign Gap → Desert Dusk kaftan + deck + Red Lunar Dragon tee unlock; bank 25 000 lifetime → first Original kaftan.
- [ ] Horseshoe: deck → tunnel (+200) → full U → "HORSESHOE BONUS — full U! +2 500 + 80/m" → far tunnel (+200).
- [ ] Reach the Courtyard trigger → results message (incl. murals seen x/6), game ends after 6 s.
- [ ] Press the sunset button → sky swaps, floodlights / lamps / mural washes / neon on; press again → day.
- [ ] Grind a 50-point rail → "UNLOCKED Metal Sparks"; toggle it on in the store → sparks on the next steel grind.
- [ ] No vehicle anywhere on the island.
