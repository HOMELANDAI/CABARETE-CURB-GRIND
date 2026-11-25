# Cabarete Curb Grind — UEFN graphics, maximum tier

HomelandAI (HAI) · Unreal Editor for Fortnite · companion to `LEVEL_BUILD_GUIDE.md` §8c–8d · v2 (max-fidelity pass)

Fortnite's renderer gives every island **Lumen GI + reflections, Nanite, Virtual Shadow Maps and TSR** on PC and
current consoles, with hardware ray-traced Lumen when the player's settings allow it. None of that is configured by the
island — what the island controls is *what it feeds the renderer*: texel density, material response, lighting rig,
grade, atmosphere, VFX and the memory budget. This pass maxes each of those inside UEFN's hard limits:

| Hard limit (Epic docs) | What we do about it |
|---|---|
| Textures cook to **≤ 2048²** (4096 sources are allowed but get LOD-biased down) | Riders are split into **three material sections, each on its own 2K sheet** (≈ 3× the texel density of one sheet, the face alone on a full 2K). Every environment texture ships at 2048², power-of-two, streamable. |
| Normal maps are **DirectX** (green = −Y) | Every `_N.png` in this package is already DirectX. Import as Normalmap, **Flip Green OFF**. |
| Fortnite master materials pack **R = Specular, G = Metallic, B = Roughness** | Riders ship both an `_ORM` (for custom Material Editor graphs) and an `_SMR` (drop straight into a Fortnite master instance). |
| Point / spot lights are expensive and may vanish on low tiers | Lighting is sun + sky (Day Sequence / Environment Light Rig) plus a **pooled** set of dynamic lights: 16 floods, lamps with shadows off, 6 mural washes, **2 pooled spark lights** moved by Verse instead of one light per rail. |
| No Verse access to material parameters | Sunset changes that touch materials (wet road, neon, mural glow) are **Level Sequence tracks** played by `cinematic_sequence_device` from `ccg_graphics.verse` (`Play` = sunset, `PlayReverse` = day). |

Package inventory for this pass (all under `uefn/assets/`):

| Folder | Contents |
|---|---|
| `riders/<Name>/` | `SK_<Name>_UEFN.fbx` (3 material slots, Rigify deform skeleton, 6 clips) + per section `T_<Name>_<Head\|Upper\|Lower>_{BC,N,ORM,SMR,Mask}.png` 2048², `check_<Name>_uefn.png` reference render. The single-sheet set (`SK_<Name>.fbx`, `T_<Name>_{BC,N,ORM}`) stays as the LowEnd fallback. |
| `materials/` | 2K tileable PBR sets: `T_Asphalt_Hwy5`, `T_Concrete_Park`, `T_Pavers_Adoquin`, `T_Sand_Cabarete`, `T_Stucco_White`, `T_Roof_Corrugated`, `T_Wood_Deck`, `T_Steel_Rail` (each `_BC/_N/_ORM/_H`), `T_WallPaint_{N,ORM,H}`, `T_Fur_Detail_{N,H}` (1K), masks `T_Road_Paint_Mask`, `T_Road_Wet_Mask`, `T_Grunge_Mask`, `T_Decal_Atlas` (RGBA). `TEXTURE_MANIFEST.json` lists metres-per-tile for every set. |
| `signs/` | 38 signage / billboard textures (`T_Sign_<id>_BC.png`, lit ones also `_E.png` emissive masks), `SIGN_MANIFEST.json` with placement. HAI marks are HomelandAI's own; third-party storefronts are typographic name boards only (no logos). |
| `murals/` | the six HAI murals at 2048 × 1024 / 1024 × 2048 / 2048² (`T_Mural_<id>_BC.png`) for the `M_CCG_Mural` instances. |

---

## 1. Project + Island settings

1. **Project Settings → Viewport Scalability → Global Illumination: Epic** while authoring (High on consoles, Medium is
   what mobile gets; the island does not pick the player's tier, you only preview it).
2. **Lumen Exposure Manager device** on the island (Island Settings → Lumen Exposure): Min Brightness 0.6, Max 6.0,
   histogram low/high 70/95 %, speed up 3 / down 1. Lumen's auto exposure is what makes the shaded Multiplex lot and the
   Horseshoe tunnels read instead of going black.
3. **Nanite** on every imported *static* mesh (ramps, horseshoe rail, sign panels, mural planes, store furniture): tick
   *Build Nanite* in the import dialog. Skeletal meshes (riders) stay non-Nanite.
4. **World Partition / streaming** off for a 1.8 km route — keep the island as one persistent level so Lumen's scene
   doesn't pop when the rider crosses a cell.
5. Keep **Island Settings → Memory** green. Budget for this pass on PC/console (compressed, with mips): riders 3 × 40 MB
   (3 sections × 5 textures at 2K), environment sets ≈ 70 MB, signs ≈ 45 MB, murals 15 MB — ≈ 250 MB of texture, well
   inside the island memory ceiling; the **Memory Snapshot** tool will confirm per asset. LowEnd tier (§10) halves it.

## 2. Lighting

Two tiers coexist. Tier A always ships; Tier B is the cinematic layer `ccg_graphics.verse` drives when its sequences exist.

### 2a. Tier A — two Day Sequence devices (`ccg_timeofday.verse`)

Both devices: *Enable Sun / Sky Atmosphere / Skylight / Fog* on, **Fade Speed 0.4, Blend Time 4 s** (the device now
cross-fades with `FadeIn()` / `FadeOut()` instead of a hard swap), *Is Volume Enabled* off (whole island).

| Setting | `DaySequence` (12:00) | `SunsetSequence` (≈17:50) |
|---|---|---|
| Sunlight rotation X / Z (pitch / yaw) | −62° / 150° | −6° / 262° (sun sets west, behind the Cabarete Sign) |
| Sunlight intensity / colour | 6.0 / `#FFF6E8` | 4.0 / `#FFB347` |
| Sky gradient low / mid / high | `#CFE8FF` / `#6FB4F0` / `#2F7BD1` | `#FF8A3D` / `#B3406B` / `#2B1E5A` |
| Sky gradient blend / sun size / sun intensity | 0.5 / 0.6 / 1.0 | 0.35 / 1.4 / 1.6 (custom sun colour blend 0.8) |
| Skylight intensity / colour | 1.0 / `#DDEBFF` | 0.35 / `#8A6AA8` (ambient 0.35 from ccg_data) |
| Clouds coverage / size / opacity / speed | 0.35 / 0.6 / 0.8 / 0.6 | 0.45 / 0.7 / 0.9 / 0.4 |
| Cloud light / shadow colour | `#FFFFFF` / `#8CA3BE` | `#FFC27A` / `#5A3C6E` |
| Fog density / height falloff / max opacity | 0.006 / 0.6 / 0.3 | 0.02 / 0.4 / 0.6 |
| Fog colour / directional in-scattering | `#DDEAF5` / `#FFFFFF` | `#E89A6B` / `#FFB347` |
| Secondary fog density / falloff / offset | 0 | 0.004 / 0.8 / 0.1 (low haze over the sea) |
| Sunlight volumetric scattering | 0.1 | 0.6 (god rays through the palms and the Sign Twins) |
| Sun flare | on, 0.3 | on, 0.8 |

### 2b. Tier B — Environment Light Rig + `LS_CCG_Sunset` (the cinematic grade)

Add an **Environment Light Rig** (World Settings → *Disable All Time of Day Managers* on) and author the noon state on
its actors; then one Level Sequence, **`LS_CCG_Sunset` (6 s, 30 fps, not looping)**, keys every actor from noon to
sunset. `ccg_graphics` plays it forward for sunset and `PlayReverse()` for day, so a single rig blends smoothly in both
directions. Keep the Tier A devices on the island too (they are the fallback on tiers where the rig is reduced).

| Rig actor | Noon keys (frame 0) | Sunset keys (frame 180) |
|---|---|---|
| **DirectionalLight** | rotation (−62, 150, 0), intensity 8 lux-ish (UEFN scale: 6.0), temperature 6200 K, source angle 0.55, volumetric scattering 0.2, light-shaft bloom 0.15 | rotation (−6, 262, 0), intensity 4.0, temperature 2900 K, source angle 1.2, volumetric scattering 0.9, light-shaft occlusion on, bloom scale 2.5 |
| **SkyAtmosphere** | Rayleigh scattering scale 0.0331, Mie scattering 0.004, Mie anisotropy 0.8, multiscattering 1.0, aerial perspective view distance scale 1.0 | Mie scattering 0.012 (dusty-humid Caribbean air), Mie absorption 0.002, aerial perspective 1.4, ground albedo `#5C6F7A` |
| **SkyLight** | real-time capture on, intensity 1.0, lower hemisphere `#2A2A2A` | intensity 0.45, colour `#8A6AA8` |
| **ExponentialHeightFog** | density 0.006, falloff 0.6, start distance 1500, volumetric fog on (scattering 0.6, albedo white), max opacity 0.3 | density 0.02, falloff 0.4, start distance 300, albedo `#E89A6B`, directional in-scattering `#FFB347` exponent 8, volumetric scattering 1.0, max opacity 0.6 |
| **Volumetric Cloud** (optional, Rig → add) | layer bottom 2.5 km, height 6 km, coverage 0.35 | coverage 0.45, bottom-lit colour via the directional light (no extra keys) |
| **ColorGradient / post-process volume** | §3 "day" column | §3 "sunset" column |
| **Material parameter tracks** (see §4) | `Wetness` 0, `NeonOn` 0, `SunsetGlow` 0 | `Wetness` 0.35, `NeonOn` 1, `SunsetGlow` 0.6 |

Keep the sequence unbound to the player camera (no camera cut track) so it never steals the view.

### 2c. Artificial lights (sunset only)

| Light | Count | Settings |
|---|---|---|
| Park floodlights (`ParkFloodlights[]`) | 16 (4 per park, 9 m masts) | Rect/spot `customizable_light_device`, `#FFF2D6`, intensity 8 000 cd equivalent (device slider 85 %), cone 60°, **Cast Shadows ON on exactly one per park** (the key), off on the other three |
| Street lamps (`StreetLamps[]`) | every 24 m, both curbs | `#FFD9A0`, 45 %, shadows off, attenuation 14 m |
| Mural washes (`MuralWashLights[]`) | 6 | `#FFD9A0`, 60 %, 35° cone aimed at the wall, shadows off; `ccg_graphics` flickers them (sodium warm-up) |
| Spark lights (`SparkLights[]`) | **2 pooled** | `#FF9A3C`, 1.5 cd, radius 3.5 m, shadows off; moved to the rail by `ccg_graphics.AcquireSparkLight` while a rider grinds with Metal Sparks |
| Neon signs | 5 (HAI SKATE, OJO club, Mojito Bar, Full Moon, Olivia's) | no light actor — emissive `_E` masks (§4 `M_CCG_Sign`) at 5–8 so Lumen reflects them in the wet road |

Hard cap to respect: **≤ 6 shadow-casting dynamic lights in view**; the layout above never exceeds 4 (park key + 2
sparks + the sun).

## 3. Post-process grade

One unbound post-process volume (Tier A: two volumes toggled with the Day Sequence swap; Tier B: keyed by the sequence).

| Setting | Day | Sunset |
|---|---|---|
| Exposure (Lumen Exposure manager) compensation | 0 | −0.4 |
| Bloom intensity / threshold | 0.35 / 1.0 | 0.7 / 0.6 |
| Lens flare | off | 0.25, tint `#FFB347` (sun only) |
| Vignette | 0.3 | 0.35 |
| Colour grading — highlights gain | 1, 1, 1 | 1.08, 0.96, 0.84 |
| Colour grading — shadows gain | 1, 1, 1.02 | 0.92, 0.90, 1.08 |
| White balance | 6500 K | 5200 K |
| Saturation / contrast | 1.05 / 1.05 | 1.10 / 1.08 |
| Local exposure (highlight / shadow contrast) | 0.8 / 0.8 | 0.7 / 0.9 (keeps the tunnels and the lit store readable) |
| Film grain | 0 | 0.15, texel size 1.5 |
| Chromatic aberration | off | off |
| Ambient occlusion (SSAO on top of Lumen) | intensity 0.5, radius 100 | 0.6, radius 120 |
| Motion blur | 0.25, max 3 px | same |

## 4. Materials (UEFN Material Editor)

All custom materials: **Default Lit, Opaque**, *Fully Rough* off, *Use Material Attributes* off. Wrap every tier-only
branch in a **Quality Switch** node (Low = flat constant, High = the textured path) so the same material cooks for
mobile. Texture import defaults: BC → *Default (DXT1)*, sRGB on; N → *Normalmap (BC5)*, sRGB off, Flip Green **off**; ORM /
SMR / Mask / H → *Masks (no sRGB)*; mip gen *From Texture Group*, *Never Stream* off.

### 4a. `M_CCG_Rider` (master) → `MI_<Name>_Head / _Upper / _Lower` ×3 riders

| Input | Graph |
|---|---|
| Base Color | `BC` × (lerp(1, `ORM.R`, `AOStrength` 0.7)) × `Tint` (vector, white) |
| Normal | **BlendAngleCorrectedNormals**(`N`, `T_Fur_Detail_N` sampled at `FurTile` 16 × `FurStrength` 0.35) — the fur micro-normal only on the fur: multiply its strength by (1 − `Mask.B` curvature-flatness) or keep 0.35 everywhere; set `FurStrength` 0 on `_Lower` where trousers dominate |
| Roughness | `ORM.G`, then lerp to 0.12 by `WetMask` = saturate(`Mask.R` + `Mask.G`) (eyes + nose) |
| Specular | 0.5 → 0.95 by `WetMask` |
| Metallic | `ORM.B` (0) |
| Clear Coat / Clear Coat Roughness | if your UEFN build offers the **Clear Coat** shading model: Clear Coat = `WetMask`, roughness 0.05. Otherwise the roughness/specular lerp above already gives the wet read |
| Subsurface | if **Subsurface** shading model is available: Opacity 0.8, Subsurface Color = per-rider `ScatterColor` (Kefla `#C98A6E`, Koda `#B9B3B0`, Crash `#9A7A62`) masked by (1 − `Mask.B` cavity) so ears and nose edges glow at sunset. Otherwise add a **Fresnel sheen**: Base Color += `Fresnel`(exp 4) × 0.08 × `SheenColor` |
| Emissive | none |

Head/Upper/Lower instances differ only in textures and `FurStrength` (0.35 / 0.35 / 0.15). The single-sheet LowEnd set
uses the same master with the `T_<Name>_{BC,N,ORM}` textures and the Mask input left black.

### 4b. `M_CCG_Road` (Highway 5)

Base: `T_Asphalt_Hwy5` tiled at **3 m** (`TexCoord` × 0.333 per metre of UV). Add `T_Road_Paint_Mask` sampled in a second
UV set that runs **along the lane** (U across, V along, 12 m per tile): lerp Base Color to `#E8E4D8` by `R` (edge line),
to `#E2B13C` by `G` (centre dashes), to white by `B` (crosswalk) and drop roughness to 0.6 under the paint. **Wetness**
(scalar, 0 by day, 0.35 at sunset, keyed by `LS_CCG_WetRoad`): sample `T_Road_Wet_Mask` at 9 m; `Puddle` = `R` ×
`Wetness` → roughness lerp to 0.05, normal lerp to flat, Base Color × 0.55; `Damp` = `G` × `Wetness` → roughness −0.3,
Base Color × 0.75; `Oil` = `B` × `Wetness` × 0.5 → tint toward `#2E2A40`. Specular 0.5. The cracks + tar patch are in the
texture; the decal atlas (§7) adds skids and stains per lane.

### 4c. `M_CCG_Concrete` (parks) · `M_CCG_Pavers` (sidewalks) · `M_CCG_Sand` · `M_CCG_Stucco` · `M_CCG_Wood` · `M_CCG_Roof`

Same 4-texture pattern (BC / N / ORM / H). Tiling from `TEXTURE_MANIFEST.json`: concrete 2 m, pavers 1.6 m, sand 2 m,
stucco 2 m (with `Tint`: Mojito `#44C7C1`, ProCab cream `#F6EFE3`, Vagamundo white, Tienda `#F7D02E`), wood 2 m, roof 1 m.
On **High** quality feed `_H` into **ParallaxOcclusionMapping** (pavers: height ratio 0.02, 8–24 steps; concrete 0.005) —
on Low the switch falls back to the plain normal. Vertex-paint (Modeling → Attribute Paint) the R channel to blend
`T_Grunge_Mask` dirt (Base Color × 0.6, roughness +0.15) into gutters, the bank bottoms and the mural wall foot.

### 4d. `M_CCG_Steel` (rails, coping, Sign Twins, store rack)

`T_Steel_Rail` at 1 m: U wraps the pipe, V runs along it; the band at V≈0.5 is the ground-bright grind line (roughness
0.27) so the rail reads as *used*. Metallic from `ORM.B` (1 on steel, 0 on rust). If the **Anisotropy** input exists in
your build: Anisotropy 0.6 with tangent along V. Horseshoe rail: same material, add a `Tint` of `#D8DCE0`.

### 4e. `M_CCG_Mural` ×6

Base Color = `T_Mural_<id>_BC` (unique UVs 0–1 on the plane); Normal = `T_WallPaint_N` at 2 m; Roughness = `T_WallPaint_ORM.G`
× 1.1 (paint is slightly glossier than stucco); AO = `T_WallPaint_ORM.R` (the cracks darken the paint 12 %); Emissive =
`BC` × `SunsetGlow` (scalar 0 → 0.6, keyed by `LS_CCG_Sunset`) so the wash lights and the glow read at golden hour.
Plane sizes from `ccg_data.murals[].size_m`.

### 4f. `M_CCG_Sign` (38 instances)

Base Color = `T_Sign_<id>_BC`; roughness 0.55 (0.3 on the enamel storefront boards); Emissive = `T_Sign_<id>_E` ×
`NeonColor` × `NeonOn` (0 → 1 keyed by the sequence) × strength (HAI SKATE 6, Mojito Bar 5, OJO club 7 magenta, Full
Moon 5, Olivia's 5, billboards 1.5). Signs without an `_E` get Emissive 0. `T_Sign_Cabarete_Letters_BC` is RGBA — Masked
blend mode, opacity mask clip 0.5 — for the letter strip behind the Sign Twins (or model the letters and use it as the
colour reference).

### 4g. `M_CCG_Decal` (Deferred Decal, DBuffer Translucent Color,Normal,Roughness)

`T_Decal_Atlas` is 2 × 2 cells of 1024: (0,0) skid marks, (1,0) oil stain, (0,1) crack web, (1,1) puddle. Instance
parameter `Cell` (vector2) offsets the UV by 0.5 × cell. Opacity = alpha × `Strength`. The puddle cell also sets
roughness 0.05 and a flat normal so the Lumen reflection of the floodlights lands in it. Place 8–12 skid decals on the
Multiplex approach and the Mojito hairpin, puddles only on the sunset-visible side of the road (they stay by day at
`Strength` 0.3 as damp patches, or drive `Strength` from the sequence too).

### 4h. Water + ground

Use the UEFN **Water Body Ocean** for the bay (default water material; wave amplitude 0.35 m, wavelength 9 m, wind along
the beach; absorption tuned to Caribbean turquoise `#1C9AA8` at 2 m depth, scattering `#6FD3D8`). Landscape: a 3-layer
landscape material (sand / grass / dirt) using `T_Sand_Cabarete` + Fortnite's grass and dirt textures, painted with the
beach side in sand and the road verges in dirt. Foliage tool for the palms (Tropical Tree gallery) and bougainvillea.

## 5. Importing the riders (three-section set)

1. **Import `SK_<Name>_UEFN.fbx`** → *Skeletal Mesh* on, *Import Mesh* on, *Import Animations* on (6 clips arrive as
   `CCG_Stance / Idle / Crouch / Pop / Push / Grind`), *Convert Scene* on, *Force Front XAxis* on, *Import Normals and
   Tangents*, Nanite off. The mesh lands with three material slots `M_<Name>_Head / _Upper / _Lower`.
2. Import the 15 textures with the settings in §4 (BC sRGB, N Normalmap/Flip Green off, ORM/SMR/Mask as Masks).
3. Create `MI_<Name>_Head / _Upper / _Lower` from `M_CCG_Rider` (§4a) and assign to the slots. For a Fortnite master
   material instead, use the `_SMR` texture (R spec, G metal, B rough) in its packed slot.
4. LODs: LOD0 40k tris, LOD1 15k, LOD2 5k, auto-reduction, same materials; screen sizes 1.0 / 0.35 / 0.12.
5. Skin cache on; *Cast Ray Traced Shadow* on. Check the reference render `check_<Name>_uefn.png` against the viewport.
6. Players cannot wear custom skeletal meshes in UEFN — the riders are **NPC Spawner characters / props**: start podium,
   results, store display (playing `CCG_Idle`), and the companion NPC that pushes ahead of the player (`CCG_Push`).

Why three sections: UEFN cooks a texture to 2048² at most. One 2K sheet on a 40k dog gives ≈ 47 % texel coverage; the
split gives the head its own sheet (57 % coverage of 2048² for the face alone) and the body two more. The sections are
cut on the rest pose: head = above 80 % height within the torso width; upper = above 42 % height or the arms; lower =
the rest. The bake used the same hi-res scan, 5 mm cage / 15 mm ray, 0.00–0.03 % gaps per sheet.

## 6. VFX + the graphics director

`ccg_graphics.verse` (new) sits beside `ccg_timeofday`:

| Editable | Wire to |
|---|---|
| `TimeOfDay` | the island's `ccg_timeofday` |
| `Quality` | `HighEnd` (PC / consoles) or `LowEnd` (mobile / Switch): LowEnd skips the haze, the spark lights and the flicker |
| `UseCinematicGrade` + `SunsetSequence` | `cinematic_sequence_device` playing `LS_CCG_Sunset` (Everyone, no loop) |
| `WetRoadSequence` | `cinematic_sequence_device` playing `LS_CCG_WetRoad` (material `Wetness` 0 → 0.35 over 8 s on every road/park instance in the level) |
| `HeatHaze[]` | `vfx_spawner_device` ×4: Heat Distortion preset at both Horseshoe tunnel exits and above two floodlight heads per park at sunset; rate low, 0.4 s life |
| `SparkLights[]` | 2 (3 on PC-only islands) `customizable_light_device`, settings in §2c |
| `MuralWashLights[]` + `MuralWashFlicker` | the same six washes `ccg_timeofday` owns |

`ccg_rail` gained `UseGraphics` + `Graphics`: while a rider grinds with Metal Sparks it borrows a pooled light, moves it
along the rail at 10 Hz and releases it on exit. Sparks themselves stay the `vfx_spawner_device` per rail: *Sparks –
Welding* preset, colour `#FFF4C2` → `#FF5A1F`, rate 220, size 2–4 cm, cone 35°, gravity + collision bounce, life
0.25–0.6 s; the Horseshoe rail runs a second spawner at 2× rate.

## 7. Decals, grunge, wear

- Decal atlas (§4g): skids on the lane approaches, oil at the Tienda forecourt and the ProCab gate, crack webs on the
  Multiplex Lot One floor (3–4), puddles on the beach side at sunset.
- `T_Grunge_Mask`: R rain streaks (top-down) under every window line and sign, G leak stains at roof edges, B general
  dirt for the stucco base band (`Tint` × 0.8 below 0.6 m).
- Rails: the grind-line band in `T_Steel_Rail` is the wear; coping on the Mojito bowl uses the same material rotated so
  the bright band faces up.

## 8. Murals

`murals/T_Mural_<id>_BC.png` are the six HAI murals resampled to power-of-two sizes (2048 × 1024 for the two landscape
walls, 1024 × 2048 for the portrait wall, 2048² for the three squares). Plane sizes and positions in
`ccg_data.murals`; wall normal/roughness from `T_WallPaint` (§4e); one wash light each (§2c). Spacing stays as designed —
never two murals in the same view.

## 9. Signage

`signs/SIGN_MANIFEST.json` lists every board's size and placement. Rule of thumb for scale: a 2048 × 512 board is
8–11 m wide on a fascia, 1024 × 256 for 4–6 m boards, the 1024² square for the HAI store cube. Lit signs come with an
`_E` mask (tube + halo) — emissive strength per §4f, `NeonOn` keyed by the sequence (Tier A: swap `NeonLit` /
`NeonUnlit` prop pairs as before). Storefront boards for real Cabarete businesses are typographic only.

## 10. Quality tiers + budget

| | HighEnd (PC, PS5 / Series X) | LowEnd (mobile, Switch) |
|---|---|---|
| Riders | 3-section set, 2K × 5 maps per section, fur detail normal, wet mask, POM off | single-sheet set at 1K BC/N/ORM, Quality Switch flat paths |
| Environment | 2K sets + POM on pavers/concrete, decals, wet road | 1K mips via LOD bias, no POM, no decals |
| Lights | sun + sky, 16 floods (1 shadowed per park), lamps, 6 washes, 2 spark lights, haze | sun + sky, floods only (shadows off), no spark lights, no haze |
| Grade | Tier B sequence | Tier A Day Sequence swap only |
| Texture memory (compressed) | ≈ 250 MB | ≈ 110 MB |

Set `ccg_graphics.Quality` per published version (two islands) or leave HighEnd and let the engine's own scalability
drop mips/shadows on weaker hardware — Quality Switch nodes make the materials safe either way.

## 11. Verification checklist

- [ ] Riders import with 3 slots; `check_<Name>_uefn.png` matches; eyes and nose read wet in the viewport at sunset.
- [ ] No texture shows a LOD-bias warning (all ≤ 2048, power of two, streaming on).
- [ ] Press the sunset button: sky cross-fades over 4 s, floods/lamps/washes/neon on, road darkens and puddles reflect
      the floods, murals glow, haze at the tunnel exits; press again: everything reverses.
- [ ] Grind a steel rail with Metal Sparks on: sparks + an orange glow that follows the board; a second rider gets the
      second light; a third gets sparks only (pool exhausted, by design).
- [ ] Memory Snapshot green; Spatial Profiler steady at 60 on PC / console during a full run with all lights on.
