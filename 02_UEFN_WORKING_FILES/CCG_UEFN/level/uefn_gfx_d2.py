# exec(open(r'F:/HOMELANDAI/CURBSIDE GRIND (CCG)/02_UEFN_WORKING_FILES/CCG_UEFN/level/uefn_gfx_d2.py').read())
# Tier B part 3, take 2: the MaterialParameterCollection route is dead in UEFN Python (parameter GUIDs can't be
# generated/read -> "CollectionParameter has invalid parameter"), so:
#   1. revert the MPC nodes in M_CCG_Env / M_CCG_RoadWet (graph restored, materials compile again)
#   2. LS_CCG_Sunset keys the parameters per actor with Component Material tracks instead:
#        - Highway 5 road slot 0 (MI_Road_Wet): Wetness 0.1 -> 0.35
#        - neon fascias (5): EmissiveStrength 0.3 -> 3.0 (switch between frames 120 and 180)
#        - lit billboards (6): EmissiveStrength 1.0 -> 3.0
import unreal, json, os, re, traceback
BASE = r"F:\HOMELANDAI\CURBSIDE GRIND (CCG)\02_UEFN_WORKING_FILES\CCG_UEFN\level"
G = "/9ec1b72d-2111-4319-b015-282d94c768eb/CCG"
EAL = unreal.EditorAssetLibrary; MEL = unreal.MaterialEditingLibrary
ss = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
TU = getattr(unreal, "MovieSceneTimeUnit", None) or getattr(unreal, "SequenceTimeUnit", None)
out = {"env": [], "road": [], "seq": {"signs": [], "road": None}, "err": [], "warn": []}
NEON = ("HAI_Skate_Neon", "Mojito_Bar", "OJO_Club", "Full_Moon", "Olivias")

def exprs(mat):
    res = {}
    for ob in unreal.ObjectIterator(unreal.MaterialExpression):
        try:
            if ob.get_outer() == mat: res[ob.get_name()] = ob
        except Exception: pass
    return res
def idx(n):
    m = re.search(r"_(\d+)$", n); return int(m.group(1)) if m else -1
def by_class(E, cls):
    return sorted([n for n, e in E.items() if e.get_class().get_name() == cls], key=idx)
def delete(mat, E, names):
    for n in names:
        try: MEL.delete_material_expression(mat, E[n])
        except Exception as ex: out["warn"].append(("delete", n, str(ex)[:60]))

# ---------------------------------------------------------------- 1a. M_CCG_Env revert
try:
    mat = EAL.load_asset(f"{G}/Materials/M_CCG_Env"); E = exprs(mat)
    cols = by_class(E, "MaterialExpressionCollectionParameter")
    if cols:
        muls = by_class(E, "MaterialExpressionMultiply")       # ... mul4, gm, m1, m2
        mul4 = E[muls[-4]]
        MEL.connect_material_property(mul4, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
        kill = cols + muls[-3:] + by_class(E, "MaterialExpressionLinearInterpolate")[-1:] + by_class(E, "MaterialExpressionAdd")[-1:] + by_class(E, "MaterialExpressionConstant")[-1:]
        kill += [n for n, e in E.items() if e.get_class().get_name() == "MaterialExpressionScalarParameter" and str(e.get_editor_property("parameter_name")) in ("NeonMin", "GlowBoost")]
        delete(mat, E, kill); out["env"] = ["emissive <- " + muls[-4], "deleted %d" % len(kill)]
        MEL.recompile_material(mat); EAL.save_loaded_asset(mat)
    else: out["env"] = ["no collection nodes - nothing to revert"]
except Exception: out["err"].append("env " + traceback.format_exc()[-500:])

# ---------------------------------------------------------------- 1b. M_CCG_RoadWet revert
try:
    mat = EAL.load_asset(f"{G}/Materials/M_CCG_RoadWet"); E = exprs(mat)
    cols = by_class(E, "MaterialExpressionCollectionParameter")
    wp = [e for e in E.values() if e.get_class().get_name() == "MaterialExpressionScalarParameter" and str(e.get_editor_property("parameter_name")) in ("WetnessMax", "Wetness")][0]
    wp.set_editor_property("parameter_name", "Wetness")
    for k in ("MaterialExpressionMultiply_1", "MaterialExpressionMultiply_2"):   # puddle, damp (creation order in uefn_gfx_pass.py)
        MEL.connect_material_expressions(wp, "", E[k], "B")
    kill = cols + [n for n in by_class(E, "MaterialExpressionMultiply") if idx(n) >= 6]
    delete(mat, E, kill); out["road"] = ["Wetness -> Multiply_1.B / Multiply_2.B", "deleted %s" % kill]
    MEL.recompile_material(mat); EAL.save_loaded_asset(mat)
    mi = EAL.load_asset(f"{G}/Materials/MI/MI_Road_Wet")
    MEL.set_material_instance_scalar_parameter_value(mi, "Wetness", 0.1); MEL.update_material_instance(mi); EAL.save_loaded_asset(mi)
except Exception: out["err"].append("road " + traceback.format_exc()[-500:])

# ---------------------------------------------------------------- 2. per-actor material tracks
def key_channel(sec, pname, keys):
    try:
        sec.add_scalar_parameter_key(pname, unreal.FrameNumber(0), keys[0][1])
    except Exception:
        pinfo = unreal.MaterialParameterInfo(name=pname, association=unreal.MaterialParameterAssociation.GLOBAL_PARAMETER, index=-1)
        sec.add_scalar_parameter_key(pinfo, unreal.FrameNumber(0), keys[0][1], "", "")
    for ch in sec.get_all_channels():
        try: cn = str(ch.get_editor_property("channel_name"))
        except Exception: cn = ""
        if cn != pname: continue
        for k in list(ch.get_keys()):
            try: ch.remove_key(k)
            except Exception: pass
        for f, v in keys: ch.add_key(unreal.FrameNumber(f), float(v), 0.0, TU.DISPLAY_RATE, unreal.MovieSceneKeyInterpolation.AUTO)
        return True
    return False
def mat_track(seq, actor, comp, slot, pname, keys):
    ab = seq.add_possessable(actor); cb = seq.add_possessable(comp)
    try: cb.set_parent(ab)
    except Exception: pass
    tr = cb.add_track(unreal.MovieSceneComponentMaterialTrack)
    try:
        info = unreal.ComponentMaterialInfo(); info.set_editor_property("material_slot_index", slot)
        try: info.set_editor_property("material_type", unreal.ComponentMaterialType.INDEXED_MATERIAL)
        except Exception: pass
        unreal.MovieSceneMaterialTrackExtensions.set_material_info(tr, info)
    except Exception as ex:
        out["warn"].append(("material_info", str(ex)[:120]))
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            tr.set_editor_property("material_index", slot)
    sec = tr.add_section(); sec.set_range(0, 180)
    return key_channel(sec, pname, keys)
try:
    seq = EAL.load_asset(f"{G}/Sequences/LS_CCG_Sunset")
    for t in list(seq.get_tracks()):
        if isinstance(t, unreal.MovieSceneMaterialParameterCollectionTrack): seq.remove_track(t)
    # drop previous material bindings (anything that is not one of the light-rig / PPV actors)
    keep = ("LR_Sun", "LR_SkyAtmosphere", "LR_SkyLight", "LR_Fog", "PP_CCG_Grade", "LightComponent0", "SkyAtmosphereComponent", "SkyLightComponent0", "HeightFogComponent0")
    for b in list(seq.get_bindings()):
        try:
            if b.get_display_name() not in keep: b.remove()
        except Exception: pass
    for a in ss.get_all_level_actors():
        if not isinstance(a, unreal.StaticMeshActor): continue
        c = a.static_mesh_component
        if not c: continue
        try: mats = c.get_materials()
        except Exception: continue
        for i, m in enumerate(mats):
            if not m: continue
            n = m.get_name()
            if n == "MI_Road_Wet":
                mat_track(seq, a, c, i, "Wetness", [(0, 0.1), (180, 0.35)]); out["seq"]["road"] = [a.get_actor_label(), i]
            elif n.startswith("MI_Sign_") and (any(k in n for k in NEON) or "Billboard" in n):
                neon = any(k in n for k in NEON)
                ks = [(0, 0.3), (120, 0.3), (180, 3.0)] if neon else [(0, 1.0), (180, 3.0)]
                mat_track(seq, a, c, i, "EmissiveStrength", ks); out["seq"]["signs"].append([a.get_actor_label(), i, n])
    EAL.save_loaded_asset(seq)
    out["seq"]["bindings"] = len(seq.get_bindings())
except Exception: out["err"].append("seq " + traceback.format_exc()[-600:])

try: unreal.EditorLevelLibrary.save_current_level()
except Exception as e: out["warn"].append(("save level", str(e)[:120]))
json.dump(out, open(os.path.join(BASE, "gfx_d2.json"), "w"), indent=1, default=str)
unreal.log("CCG_GFX_D2_DONE err=%d" % len(out["err"]))
