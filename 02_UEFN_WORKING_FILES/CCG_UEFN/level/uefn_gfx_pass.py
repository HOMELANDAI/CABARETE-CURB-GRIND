
import unreal, os, json, math
BASE = r"C:\Users\211in\Downloads\CCG_UEFN\level"
G = "/9ec1b72d-2111-4319-b015-282d94c768eb/CCG"
EAL = unreal.EditorAssetLibrary; AT = unreal.AssetToolsHelpers.get_asset_tools(); MEL = unreal.MaterialEditingLibrary
ss = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
ALL = {a.get_actor_label(): a for a in ss.get_all_level_actors()}
out = {"dayseq": {}, "ppv": None, "nanite": {}, "road": None, "decals": 0, "lumen": None, "errors": []}
def col(h, a=1.0):
    h = h.lstrip("#"); return unreal.LinearColor(int(h[0:2], 16) / 255.0, int(h[2:4], 16) / 255.0, int(h[4:6], 16) / 255.0, a)
def setp(a, d, tag):
    ok = 0
    for k, v in d.items():
        try: a.set_editor_property(k, v); ok += 1
        except Exception as e: out["errors"].append((tag, k, str(e)[:90]))
    return ok
# ---------------- A. Day Sequence devices (UEFN_GRAPHICS.md 2a)
common = {"OverrideSunlight": True, "OverrideSky": True, "OverrideSkylight": True, "OverrideFog": True, "OverrideClouds": True,
          "EnableSunComponent": True, "EnableSkyAtmosphereComponent": True, "EnableSkylightComponent": True, "EnableFogComponent": True, "EnableSkyboxComponent": True,
          "Use Volume": False, "BlendTime": 4.0, "BlendAmount": 100.0, "EnableSunFlare": True, "Priority": 2000}
day = dict(common, DayNightCycleTime=12.0, SunlightRotationX=-62.0, SunlightRotationZ=150.0, SunlightIntensity=6.0, SunlightColor=col("#FFF6E8"),
           SkyGradientLowColor=col("#CFE8FF"), SkyGradientMidColor=col("#6FB4F0"), SkyGradientHighColor=col("#2F7BD1"), SkyGradientBlend=0.5,
           SunSize=0.6, SunIntensity=1.0, SunColor=col("#FFF6E8"), CustomSunColorBlend=0.0,
           SkylightIntensity=1.0, SkylightColor=col("#DDEBFF"),
           CloudCoverage=0.35, CloudSize=0.6, CloudOpacity=0.8, CloudSpeed=0.6, CloudLightColor=col("#FFFFFF"), CloudShadowColor=col("#8CA3BE"),
           FogDensity=0.006, FogHeightFalloff=0.6, FogMaxOpacity=0.3, FogColor=col("#DDEAF5"), FogDirectionalInscatteringColor=col("#FFFFFF"),
           SecondaryFogDensity=0.0, SunlightVolumetricScattering=0.1, StarBrightness=0.0)
sun = dict(common, DayNightCycleTime=17.83, SunlightRotationX=-6.0, SunlightRotationZ=262.0, SunlightIntensity=4.0, SunlightColor=col("#FFB347"),
           SkyGradientLowColor=col("#FF8A3D"), SkyGradientMidColor=col("#B3406B"), SkyGradientHighColor=col("#2B1E5A"), SkyGradientBlend=0.35,
           SunSize=1.4, SunIntensity=1.6, SunColor=col("#FFB347"), CustomSunColorBlend=0.8,
           SkylightIntensity=0.35, SkylightColor=col("#8A6AA8"),
           CloudCoverage=0.45, CloudSize=0.7, CloudOpacity=0.9, CloudSpeed=0.4, CloudLightColor=col("#FFC27A"), CloudShadowColor=col("#5A3C6E"),
           FogDensity=0.02, FogHeightFalloff=0.4, FogMaxOpacity=0.6, FogColor=col("#E89A6B"), FogDirectionalInscatteringColor=col("#FFB347"),
           SecondaryFogDensity=0.004, SecondaryFogFalloff=0.8, SecondaryFogOffset=0.1, SunlightVolumetricScattering=0.6, StarBrightness=0.15)
for lbl, d in (("FD_DaySeq_Day", day), ("FD_DaySeq_Sunset", sun)):
    a = ALL.get(lbl)
    if a:
        a.modify(); out["dayseq"][lbl] = setp(a, d, lbl)
        # phase enum: Day always, Sunset off at start (Verse enables it)
        try:
            E = type(a.get_editor_property("EnableDuringPhase"))
            a.set_editor_property("EnableDuringPhase", E.ALWAYS if lbl.endswith("Day") else E.NONE)
            out["dayseq"][lbl + "_phase"] = str(a.get_editor_property("EnableDuringPhase"))
        except Exception as e: out["errors"].append((lbl, "EnableDuringPhase", str(e)[:90]))
# ---------------- B. Post-process volume (day/sunset blend, unbound)
ppv = ALL.get("PP_CCG_Grade")
if not ppv:
    ppv = ss.spawn_actor_from_class(unreal.PostProcessVolume, unreal.Vector(0, 0, 500)); ppv.set_actor_label("PP_CCG_Grade")
if ppv:
    ppv.set_editor_property("unbound", True); ppv.set_editor_property("priority", 10.0); ppv.set_editor_property("blend_weight", 1.0)
    s = ppv.get_editor_property("settings")
    vals = {"bloom_intensity": 0.45, "bloom_threshold": 0.9, "vignette_intensity": 0.32, "white_temp": 6200.0, "color_saturation": unreal.Vector4(1.06, 1.06, 1.06, 1.0),
            "color_contrast": unreal.Vector4(1.06, 1.06, 1.06, 1.0), "color_gain_highlights": unreal.Vector4(1.04, 0.99, 0.93, 1.0), "color_gain_shadows": unreal.Vector4(0.97, 0.96, 1.04, 1.0),
            "local_exposure_highlight_contrast_scale": 0.8, "local_exposure_shadow_contrast_scale": 0.85, "ambient_occlusion_intensity": 0.5, "ambient_occlusion_radius": 100.0,
            "motion_blur_amount": 0.25, "motion_blur_max": 3.0, "film_grain_intensity": 0.06, "lens_flare_intensity": 0.15, "lens_flare_tint": col("#FFB347"),
            "auto_exposure_min_brightness": 0.6, "auto_exposure_max_brightness": 6.0, "auto_exposure_speed_up": 3.0, "auto_exposure_speed_down": 1.0, "auto_exposure_bias": -0.2}
    okc = 0
    for k, v in vals.items():
        try:
            s.set_editor_property(k, v); s.set_editor_property("override_" + k, True); okc += 1
        except Exception as e: out["errors"].append(("ppv", k, str(e)[:90]))
    ppv.set_editor_property("settings", s); out["ppv"] = okc
# ---------------- C. Nanite on every CCG static mesh
road = ALL.get("L_Road_Highway5"); mesh_dir = None
if road:
    sm = road.get_component_by_class(unreal.StaticMeshComponent).static_mesh
    mesh_dir = sm.get_path_name().rsplit("/", 1)[0]
reg = unreal.AssetRegistryHelpers.get_asset_registry()
smes = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem) if hasattr(unreal, "StaticMeshEditorSubsystem") else None
if mesh_dir:
    n_on = 0; n_all = 0
    for a in reg.get_assets_by_path(mesh_dir, True):
        if str(a.asset_class_path.asset_name) != "StaticMesh": continue
        m = a.get_asset(); n_all += 1
        try:
            ns = m.get_editor_property("nanite_settings")
            if not ns.get_editor_property("enabled"):
                ns.set_editor_property("enabled", True)
                if smes: smes.set_nanite_settings(m, ns, True)
                else: m.set_editor_property("nanite_settings", ns); m.build()
                EAL.save_loaded_asset(m); n_on += 1
        except Exception as e: out["errors"].append(("nanite", str(a.asset_name), str(e)[:90]))
    out["nanite"] = {"dir": mesh_dir, "total": n_all, "enabled_now": n_on}
# ---------------- D. M_CCG_Road: asphalt + world-aligned wetness (puddles reflect the floods)
def tex(n): return EAL.load_asset(f"{G}/Materials/{n}")
mpath = f"{G}/Materials/M_CCG_Road"
if not EAL.does_asset_exist(mpath):
    mat = AT.create_asset("M_CCG_Road", f"{G}/Materials", unreal.Material, unreal.MaterialFactoryNew())
    def node(cls, x, y): return MEL.create_material_expression(mat, cls, x, y)
    def tp(name, t, x, y, st=unreal.MaterialSamplerType.SAMPLERTYPE_COLOR):
        e = node(unreal.MaterialExpressionTextureSampleParameter2D, x, y); e.set_editor_property("parameter_name", name); e.set_editor_property("texture", t); e.set_editor_property("sampler_type", st); return e
    def sp(name, v, x, y):
        e = node(unreal.MaterialExpressionScalarParameter, x, y); e.set_editor_property("parameter_name", name); e.set_editor_property("default_value", v); return e
    uv = node(unreal.MaterialExpressionTextureCoordinate, -1400, -200)
    til = sp("Tiling", 1.0, -1400, -80); muv = node(unreal.MaterialExpressionMultiply, -1200, -150)
    MEL.connect_material_expressions(uv, "", muv, "A"); MEL.connect_material_expressions(til, "", muv, "B")
    bc = tp("BaseColor", tex("T_Asphalt_Hwy5_BC"), -1000, -300); nm = tp("Normal", tex("T_Asphalt_Hwy5_N"), -1000, 0, unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL); orm = tp("ORM", tex("T_Asphalt_Hwy5_ORM"), -1000, 300, unreal.MaterialSamplerType.SAMPLERTYPE_LINEAR_COLOR)
    for e in (bc, nm, orm): MEL.connect_material_expressions(muv, "", e, "UVs")
    # world-aligned wet mask: WorldPosition.xy / WetScale (900 cm)
    wp = node(unreal.MaterialExpressionWorldPosition, -1400, 600); msk = node(unreal.MaterialExpressionComponentMask, -1250, 600); msk.set_editor_property("r", True); msk.set_editor_property("g", True); msk.set_editor_property("b", False)
    MEL.connect_material_expressions(wp, "", msk, "")
    wscale = sp("WetScale", 900.0, -1400, 720); dv = node(unreal.MaterialExpressionDivide, -1100, 620)
    MEL.connect_material_expressions(msk, "", dv, "A"); MEL.connect_material_expressions(wscale, "", dv, "B")
    wet = tp("WetMask", tex("T_Road_Wet_Mask"), -950, 600, unreal.MaterialSamplerType.SAMPLERTYPE_LINEAR_COLOR); MEL.connect_material_expressions(dv, "", wet, "UVs")
    wetness = sp("Wetness", 0.3, -950, 850)
    puddle = node(unreal.MaterialExpressionMultiply, -700, 620); MEL.connect_material_expressions(wet, "R", puddle, "A"); MEL.connect_material_expressions(wetness, "", puddle, "B")
    damp = node(unreal.MaterialExpressionMultiply, -700, 760); MEL.connect_material_expressions(wet, "G", damp, "A"); MEL.connect_material_expressions(wetness, "", damp, "B")
    # base color darkening: BC * lerp(1, 0.55, puddle) * lerp(1, 0.75, damp)
    c1 = node(unreal.MaterialExpressionConstant, -600, 400); c1.set_editor_property("r", 1.0); c55 = node(unreal.MaterialExpressionConstant, -600, 450); c55.set_editor_property("r", 0.55); c75 = node(unreal.MaterialExpressionConstant, -600, 500); c75.set_editor_property("r", 0.75)
    l1 = node(unreal.MaterialExpressionLinearInterpolate, -450, 420); MEL.connect_material_expressions(c1, "", l1, "A"); MEL.connect_material_expressions(c55, "", l1, "B"); MEL.connect_material_expressions(puddle, "", l1, "Alpha")
    l2 = node(unreal.MaterialExpressionLinearInterpolate, -450, 520); MEL.connect_material_expressions(c1, "", l2, "A"); MEL.connect_material_expressions(c75, "", l2, "B"); MEL.connect_material_expressions(damp, "", l2, "Alpha")
    m1 = node(unreal.MaterialExpressionMultiply, -300, -250); MEL.connect_material_expressions(bc, "RGB", m1, "A"); MEL.connect_material_expressions(l1, "", m1, "B")
    m2 = node(unreal.MaterialExpressionMultiply, -150, -250); MEL.connect_material_expressions(m1, "", m2, "A"); MEL.connect_material_expressions(l2, "", m2, "B")
    MEL.connect_material_property(m2, "", unreal.MaterialProperty.MP_BASE_COLOR)
    # roughness: ORM.G -> lerp to 0.05 by puddle, minus 0.3*damp
    c05 = node(unreal.MaterialExpressionConstant, -600, 300); c05.set_editor_property("r", 0.05)
    lr = node(unreal.MaterialExpressionLinearInterpolate, -450, 300); MEL.connect_material_expressions(orm, "G", lr, "A"); MEL.connect_material_expressions(c05, "", lr, "B"); MEL.connect_material_expressions(puddle, "", lr, "Alpha")
    c3 = node(unreal.MaterialExpressionConstant, -450, 360); c3.set_editor_property("r", 0.3); dm = node(unreal.MaterialExpressionMultiply, -350, 360); MEL.connect_material_expressions(damp, "", dm, "A"); MEL.connect_material_expressions(c3, "", dm, "B")
    sub = node(unreal.MaterialExpressionSubtract, -250, 320); MEL.connect_material_expressions(lr, "", sub, "A"); MEL.connect_material_expressions(dm, "", sub, "B")
    sat = node(unreal.MaterialExpressionSaturate, -150, 320); MEL.connect_material_expressions(sub, "", sat, "")
    MEL.connect_material_property(sat, "", unreal.MaterialProperty.MP_ROUGHNESS)
    # normal: flatten in puddles
    flat = node(unreal.MaterialExpressionConstant3Vector, -600, 100); flat.set_editor_property("constant", unreal.LinearColor(0, 0, 1, 1))
    ln = node(unreal.MaterialExpressionLinearInterpolate, -400, 60); MEL.connect_material_expressions(nm, "RGB", ln, "A"); MEL.connect_material_expressions(flat, "", ln, "B"); MEL.connect_material_expressions(puddle, "", ln, "Alpha")
    MEL.connect_material_property(ln, "", unreal.MaterialProperty.MP_NORMAL)
    MEL.connect_material_property(orm, "R", unreal.MaterialProperty.MP_AMBIENT_OCCLUSION)
    spec = node(unreal.MaterialExpressionConstant, -300, 200); spec.set_editor_property("r", 0.5); MEL.connect_material_property(spec, "", unreal.MaterialProperty.MP_SPECULAR)
    MEL.recompile_material(mat); EAL.save_loaded_asset(mat)
mat = EAL.load_asset(mpath)
mi_path = f"{G}/Materials/MI/MI_Road_Wet"
mi = EAL.load_asset(mi_path) if EAL.does_asset_exist(mi_path) else AT.create_asset("MI_Road_Wet", f"{G}/Materials/MI", unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
mi.set_editor_property("parent", mat)
# copy the asphalt tiling from MI_Asphalt
try:
    old = EAL.load_asset(f"{G}/Materials/MI/MI_Asphalt"); tl = MEL.get_material_instance_scalar_parameter_value(old, "Tiling")
    MEL.set_material_instance_scalar_parameter_value(mi, "Tiling", tl if tl else 1.0)
except Exception as e: out["errors"].append(("road", "tiling", str(e)[:80]))
MEL.set_material_instance_scalar_parameter_value(mi, "Wetness", 0.3); MEL.update_material_instance(mi); EAL.save_loaded_asset(mi)
if road:
    smc = road.get_component_by_class(unreal.StaticMeshComponent)
    for i in range(smc.get_num_materials()):
        if smc.get_material(i) and smc.get_material(i).get_name() == "MI_Asphalt": smc.set_material(i, mi); out["road"] = i
# ---------------- E. Decals
dpath = f"{G}/Materials/M_CCG_Decal"
if not EAL.does_asset_exist(dpath):
    dm_ = AT.create_asset("M_CCG_Decal", f"{G}/Materials", unreal.Material, unreal.MaterialFactoryNew())
    dm_.set_editor_property("material_domain", unreal.MaterialDomain.MD_DEFERRED_DECAL); dm_.set_editor_property("blend_mode", unreal.BlendMode.BLEND_TRANSLUCENT)
    def dn(cls, x, y): return MEL.create_material_expression(dm_, cls, x, y)
    uv = dn(unreal.MaterialExpressionTextureCoordinate, -900, 0); half = dn(unreal.MaterialExpressionConstant, -900, 120); half.set_editor_property("r", 0.5)
    sc = dn(unreal.MaterialExpressionMultiply, -750, 0); MEL.connect_material_expressions(uv, "", sc, "A"); MEL.connect_material_expressions(half, "", sc, "B")
    cell = dn(unreal.MaterialExpressionVectorParameter, -900, 250); cell.set_editor_property("parameter_name", "Cell"); cell.set_editor_property("default_value", unreal.LinearColor(0, 0, 0, 0))
    cm = dn(unreal.MaterialExpressionComponentMask, -750, 250); cm.set_editor_property("r", True); cm.set_editor_property("g", True); cm.set_editor_property("b", False); MEL.connect_material_expressions(cell, "", cm, "")
    cm2 = dn(unreal.MaterialExpressionMultiply, -600, 250); MEL.connect_material_expressions(cm, "", cm2, "A"); MEL.connect_material_expressions(half, "", cm2, "B")
    ad = dn(unreal.MaterialExpressionAdd, -500, 60); MEL.connect_material_expressions(sc, "", ad, "A"); MEL.connect_material_expressions(cm2, "", ad, "B")
    ts = dn(unreal.MaterialExpressionTextureSampleParameter2D, -350, 0); ts.set_editor_property("parameter_name", "Atlas"); ts.set_editor_property("texture", tex("T_Decal_Atlas")); MEL.connect_material_expressions(ad, "", ts, "UVs")
    st = dn(unreal.MaterialExpressionScalarParameter, -350, 300); st.set_editor_property("parameter_name", "Strength"); st.set_editor_property("default_value", 1.0)
    op = dn(unreal.MaterialExpressionMultiply, -150, 250); MEL.connect_material_expressions(ts, "A", op, "A"); MEL.connect_material_expressions(st, "", op, "B")
    MEL.connect_material_property(ts, "RGB", unreal.MaterialProperty.MP_BASE_COLOR); MEL.connect_material_property(op, "", unreal.MaterialProperty.MP_OPACITY)
    rg = dn(unreal.MaterialExpressionScalarParameter, -350, 420); rg.set_editor_property("parameter_name", "Roughness"); rg.set_editor_property("default_value", 0.6)
    MEL.connect_material_property(rg, "", unreal.MaterialProperty.MP_ROUGHNESS)
    MEL.recompile_material(dm_); EAL.save_loaded_asset(dm_)
dmat = EAL.load_asset(dpath)
CELLS = {"skid": (0, 0, 0.6), "oil": (1, 0, 0.25), "crack": (0, 1, 0.7), "puddle": (1, 1, 0.05)}
DMI = {}
for k, (cx, cy, rough) in CELLS.items():
    p = f"{G}/Materials/MI/MI_Decal_{k}"
    m = EAL.load_asset(p) if EAL.does_asset_exist(p) else AT.create_asset(f"MI_Decal_{k}", f"{G}/Materials/MI", unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    m.set_editor_property("parent", dmat)
    MEL.set_material_instance_vector_parameter_value(m, "Cell", unreal.LinearColor(cx, cy, 0, 0)); MEL.set_material_instance_scalar_parameter_value(m, "Roughness", rough)
    MEL.set_material_instance_scalar_parameter_value(m, "Strength", 0.35 if k == "puddle" else 0.9)
    MEL.update_material_instance(m); EAL.save_loaded_asset(m); DMI[k] = m
# remove old decals from a previous run
for l, a in list(ALL.items()):
    if l.startswith("DC_CCG_"): ss.destroy_actor(a)
D = json.load(open(os.path.join(BASE, "decals.json")))
for i, d in enumerate(D):
    try:
        loc = unreal.Vector(d["loc"][0], d["loc"][1], d["loc"][2] + 20)
        a = ss.spawn_actor_from_class(unreal.DecalActor, loc, unreal.Rotator(0, -90, d["yaw"]))
        a.set_actor_label("DC_CCG_%s_%02d" % (d["kind"], i)); a.set_folder_path("CCG/Decals")
        dc = a.get_component_by_class(unreal.DecalComponent); dc.set_decal_material(DMI[d["kind"]]); dc.set_editor_property("decal_size", unreal.Vector(*d["size"]))
        out["decals"] += 1
    except Exception as e: out["errors"].append(("decal", i, str(e)[:100]))
# ---------------- F. Lumen exposure manager
try:
    lc = unreal.load_class(None, "/Game/TimeOfDay/TODM_Sequence/UEFN/BP_LumenExposureManager.BP_LumenExposureManager_C")
    le = ALL.get("FD_LumenExposure") or ss.spawn_actor_from_class(lc, unreal.Vector(-1000, -500, 300))
    le.set_actor_label("FD_LumenExposure")
    out["lumen"] = setp(le, {"MinBrightness": 0.6, "MaxBrightness": 6.0, "HistogramLogMin": 70.0, "HistogramLogMax": 95.0, "SpeedUp": 3.0, "SpeedDown": 1.0, "ExposureCompensation": -0.2}, "lumen")
except Exception as e: out["errors"].append(("lumen", str(e)[:120]))
EAL.save_directory(f"{G}/Materials")
unreal.EditorLevelLibrary.save_current_level()
json.dump(out, open(os.path.join(BASE, "gfx_out.json"), "w"), indent=1)
unreal.log("CCGL gfx pass: %s" % json.dumps(out)[:600])
