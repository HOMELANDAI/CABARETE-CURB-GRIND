# exec(open(r'F:/HOMELANDAI/CURBSIDE GRIND (CCG)/02_UEFN_WORKING_FILES/CCG_UEFN/level/uefn_gfx_d.py').read())
# Graphics Tier B (part 3): MaterialParameterCollection MPC_CCG (Wetness / NeonOn / SunsetGlow) driven by LS_CCG_Sunset.
#  - M_CCG_RoadWet: instance Wetness (max) x MPC.Wetness  -> the road dries by day and glistens at sunset
#  - M_CCG_Env   : emissive x lerp(NeonMin, 1, NeonOn) x (1 + SunsetGlow*GlowBoost) -> neon / lit signs switch on at dusk
#  - LS_CCG_Sunset gets an MPC track (Wetness 0->1, SunsetGlow 0->1 over 0..180, NeonOn 0->1 over 120..180)
import unreal, json, os, traceback
BASE = r"F:\HOMELANDAI\CURBSIDE GRIND (CCG)\02_UEFN_WORKING_FILES\CCG_UEFN\level"
G = "/9ec1b72d-2111-4319-b015-282d94c768eb/CCG"
EAL = unreal.EditorAssetLibrary; AT = unreal.AssetToolsHelpers.get_asset_tools(); MEL = unreal.MaterialEditingLibrary
reg = unreal.AssetRegistryHelpers.get_asset_registry()
TU = getattr(unreal, "MovieSceneTimeUnit", None) or getattr(unreal, "SequenceTimeUnit", None)
out = {"mpc": None, "road": {}, "env": {}, "signs": [], "seq": {}, "err": [], "warn": []}
NEON = ("HAI_Skate_Neon", "Mojito_Bar", "OJO_Club", "Full_Moon", "Olivias")

# ---------------------------------------------------------------- 1. the collection
try:
    mpath = f"{G}/Materials/MPC_CCG"
    mpc = EAL.load_asset(mpath) if EAL.does_asset_exist(mpath) else AT.create_asset("MPC_CCG", f"{G}/Materials", unreal.MaterialParameterCollection, unreal.MaterialParameterCollectionFactoryNew())
    params = []
    for n, v in (("Wetness", 0.0), ("NeonOn", 0.0), ("SunsetGlow", 0.0)):
        p = unreal.CollectionScalarParameter(); p.set_editor_property("parameter_name", n); p.set_editor_property("default_value", v); params.append(p)
    mpc.set_editor_property("scalar_parameters", params)
    EAL.save_loaded_asset(mpc); out["mpc"] = mpath
except Exception: out["err"].append("mpc " + traceback.format_exc()[-400:])

def all_exprs(mat):
    res = []
    for ob in unreal.ObjectIterator(unreal.MaterialExpression):
        try:
            if ob.get_outer() == mat: res.append(ob)
        except Exception: pass
    return res

def same(a, b):
    try: return a is not None and b is not None and a.get_name() == b.get_name()
    except Exception: return False

def rewire_outputs(mat, old, new):
    """Every input (on any expression, or a material output) that reads `old` now reads `new`. Returns count."""
    n = 0; exprs = all_exprs(mat)
    for e in exprs:
        if same(e, new): continue
        try: names = list(MEL.get_inputs_for_material_expression(e))
        except Exception: continue
        for nm in names:
            try:
                src = MEL.get_input_node_for_material_expression(e, nm)
                if same(src, old):
                    MEL.connect_material_expressions(new, "", e, nm); n += 1
            except Exception: pass
    for prop in (unreal.MaterialProperty.MP_BASE_COLOR, unreal.MaterialProperty.MP_EMISSIVE_COLOR, unreal.MaterialProperty.MP_ROUGHNESS, unreal.MaterialProperty.MP_NORMAL, unreal.MaterialProperty.MP_SPECULAR, unreal.MaterialProperty.MP_OPACITY, unreal.MaterialProperty.MP_METALLIC, unreal.MaterialProperty.MP_AMBIENT_OCCLUSION):
        try:
            if same(MEL.get_material_property_input_node(mat, prop), old):
                MEL.connect_material_property(new, "", prop); n += 1
        except Exception: pass
    return n, len(exprs)

def find_param(mat, pname):
    for e in all_exprs(mat):
        try:
            if isinstance(e, unreal.MaterialExpressionScalarParameter) and str(e.get_editor_property("parameter_name")) == pname: return e
        except Exception: pass
    return None

def cparam(mat, name, x, y):
    c = MEL.create_material_expression(mat, unreal.MaterialExpressionCollectionParameter, x, y)
    c.set_editor_property("collection", mpc); c.set_editor_property("parameter_name", name); return c

# ---------------------------------------------------------------- 2. wet road
try:
    mat = EAL.load_asset(f"{G}/Materials/M_CCG_RoadWet")
    old = find_param(mat, "WetnessMax") or find_param(mat, "Wetness")
    if old is None: raise RuntimeError("Wetness parameter not found in M_CCG_RoadWet")
    old.set_editor_property("parameter_name", "WetnessMax")          # the instance value becomes the sunset maximum
    cw = None; mul = None
    for e in all_exprs(mat):
        if isinstance(e, unreal.MaterialExpressionCollectionParameter) and str(e.get_editor_property("parameter_name")) == "Wetness": cw = e
        if isinstance(e, unreal.MaterialExpressionMultiply):
            try:
                if same(MEL.get_input_node_for_material_expression(e, "A"), old) and isinstance(MEL.get_input_node_for_material_expression(e, "B"), unreal.MaterialExpressionCollectionParameter): mul = e
            except Exception: pass
    if cw is None: cw = cparam(mat, "Wetness", -950, 950)
    if mul is None:
        mul = MEL.create_material_expression(mat, unreal.MaterialExpressionMultiply, -800, 900)
        MEL.connect_material_expressions(old, "", mul, "A"); MEL.connect_material_expressions(cw, "", mul, "B")
    n, total = rewire_outputs(mat, old, mul)
    MEL.recompile_material(mat); EAL.save_loaded_asset(mat)
    out["road"] = {"rewired": n, "expressions": total}
    mi = EAL.load_asset(f"{G}/Materials/MI/MI_Road_Wet")
    if mi:
        MEL.set_material_instance_scalar_parameter_value(mi, "WetnessMax", 0.35); MEL.update_material_instance(mi); EAL.save_loaded_asset(mi); out["road"]["mi"] = "WetnessMax 0.35"
except Exception: out["err"].append("road " + traceback.format_exc()[-500:])

# ---------------------------------------------------------------- 3. env emissive gate
try:
    mat = EAL.load_asset(f"{G}/Materials/M_CCG_Env")
    if find_param(mat, "NeonMin") is None:
        src = MEL.get_material_property_input_node(mat, unreal.MaterialProperty.MP_EMISSIVE_COLOR)
        if src is None: raise RuntimeError("M_CCG_Env has no emissive input")
        nmin = MEL.create_material_expression(mat, unreal.MaterialExpressionScalarParameter, 100, 900); nmin.set_editor_property("parameter_name", "NeonMin"); nmin.set_editor_property("default_value", 1.0)
        one = MEL.create_material_expression(mat, unreal.MaterialExpressionConstant, 100, 960); one.set_editor_property("r", 1.0)
        non = cparam(mat, "NeonOn", 100, 1020)
        gate = MEL.create_material_expression(mat, unreal.MaterialExpressionLinearInterpolate, 300, 950)
        MEL.connect_material_expressions(nmin, "", gate, "A"); MEL.connect_material_expressions(one, "", gate, "B"); MEL.connect_material_expressions(non, "", gate, "Alpha")
        glow = cparam(mat, "SunsetGlow", 100, 1100)
        gb = MEL.create_material_expression(mat, unreal.MaterialExpressionScalarParameter, 100, 1160); gb.set_editor_property("parameter_name", "GlowBoost"); gb.set_editor_property("default_value", 0.0)
        gm = MEL.create_material_expression(mat, unreal.MaterialExpressionMultiply, 300, 1120); MEL.connect_material_expressions(glow, "", gm, "A"); MEL.connect_material_expressions(gb, "", gm, "B")
        ga = MEL.create_material_expression(mat, unreal.MaterialExpressionAdd, 450, 1100); MEL.connect_material_expressions(one, "", ga, "A"); MEL.connect_material_expressions(gm, "", ga, "B")
        m1 = MEL.create_material_expression(mat, unreal.MaterialExpressionMultiply, 500, 850); MEL.connect_material_expressions(src, "", m1, "A"); MEL.connect_material_expressions(gate, "", m1, "B")
        m2 = MEL.create_material_expression(mat, unreal.MaterialExpressionMultiply, 650, 900); MEL.connect_material_expressions(m1, "", m2, "A"); MEL.connect_material_expressions(ga, "", m2, "B")
        MEL.connect_material_property(m2, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
        MEL.recompile_material(mat); EAL.save_loaded_asset(mat); out["env"]["gate"] = "built"
    else: out["env"]["gate"] = "already present"
    # instances: every sign MI with an emissive map is a night light; the 5 neon fascias nearly off by day
    for a in reg.get_assets_by_path(f"{G}/Materials/MI", recursive=False):
        mi = a.get_asset()
        if not isinstance(mi, unreal.MaterialInstanceConstant): continue
        nm = mi.get_name()
        if not nm.startswith("MI_Sign"): continue
        try: em = MEL.get_material_instance_texture_parameter_value(mi, "Emissive"); es = MEL.get_material_instance_scalar_parameter_value(mi, "EmissiveStrength")
        except Exception: continue
        if not em or not es or es <= 0.0: continue
        neon = any(k in nm for k in NEON)
        MEL.set_material_instance_scalar_parameter_value(mi, "NeonMin", 0.12 if neon else 0.35)
        MEL.set_material_instance_scalar_parameter_value(mi, "GlowBoost", 0.4 if neon else 0.15)
        MEL.update_material_instance(mi); EAL.save_loaded_asset(mi)
        out["signs"].append([nm, "neon" if neon else "lit", es])
except Exception: out["err"].append("env " + traceback.format_exc()[-500:])

# ---------------------------------------------------------------- 4. sequence track
try:
    seq = EAL.load_asset(f"{G}/Sequences/LS_CCG_Sunset")
    for t in list(seq.get_tracks()):
        if isinstance(t, unreal.MovieSceneMaterialParameterCollectionTrack): seq.remove_track(t)
    tr = seq.add_track(unreal.MovieSceneMaterialParameterCollectionTrack); tr.set_editor_property("mpc", mpc)
    sec = tr.add_section(); sec.set_range(0, 180)
    keys = {"Wetness": [(0, 0.0), (180, 1.0)], "SunsetGlow": [(0, 0.0), (180, 1.0)], "NeonOn": [(0, 0.0), (120, 0.0), (180, 1.0)]}
    created = {}
    for pname, ks in keys.items():
        sec.add_scalar_parameter_key(pname, unreal.FrameNumber(0), ks[0][1])   # creates the channel
    chans = sec.get_all_channels()
    for ch in chans:
        try: cn = str(ch.get_editor_property("channel_name"))
        except Exception: cn = ""
        created[cn] = created.get(cn, 0)
        ks = keys.get(cn)
        if not ks: continue
        for k in list(ch.get_keys()):
            try: ch.remove_key(k)
            except Exception: pass
        for f, v in ks:
            ch.add_key(unreal.FrameNumber(f), float(v), 0.0, TU.DISPLAY_RATE, unreal.MovieSceneKeyInterpolation.AUTO); created[cn] += 1
    EAL.save_loaded_asset(seq)
    out["seq"] = {"channels": created, "tracks": len(seq.get_tracks())}
except Exception: out["err"].append("seq " + traceback.format_exc()[-600:])

try: unreal.EditorLevelLibrary.save_current_level()
except Exception as e: out["warn"].append(("save level", str(e)[:120]))
json.dump(out, open(os.path.join(BASE, "gfx_d.json"), "w"), indent=1, default=str)
unreal.log("CCG_GFX_D_DONE err=%d" % len(out["err"]))
