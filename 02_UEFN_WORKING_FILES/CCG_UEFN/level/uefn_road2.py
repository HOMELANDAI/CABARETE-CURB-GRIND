
import unreal, os, json, math
BASE = r"C:\Users\211in\Downloads\CCG_UEFN\level"
G = "/9ec1b72d-2111-4319-b015-282d94c768eb/CCG"
EAL = unreal.EditorAssetLibrary; AT = unreal.AssetToolsHelpers.get_asset_tools(); MEL = unreal.MaterialEditingLibrary
ss = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
ALL = {a.get_actor_label(): a for a in ss.get_all_level_actors()}
out = {"road": None, "errors": []}
def col(h, a=1.0):
    h = h.lstrip("#"); return unreal.LinearColor(int(h[0:2], 16) / 255.0, int(h[2:4], 16) / 255.0, int(h[4:6], 16) / 255.0, a)
# detach MI from the old master, delete it, rebuild
mpath = f"{G}/Materials/M_CCG_RoadWet"
mi_path = f"{G}/Materials/MI/MI_Road_Wet"
if EAL.does_asset_exist(mi_path):
    mi0 = EAL.load_asset(mi_path); mi0.set_editor_property("parent", EAL.load_asset(f"{G}/Materials/M_CCG_Env")); EAL.save_loaded_asset(mi0)

# ---------------- D. M_CCG_Road: asphalt + world-aligned wetness (puddles reflect the floods)
def tex(n): return EAL.load_asset(f"{G}/Materials/{n}")
mpath = f"{G}/Materials/M_CCG_RoadWet"
if not EAL.does_asset_exist(mpath):
    mat = AT.create_asset("M_CCG_RoadWet", f"{G}/Materials", unreal.Material, unreal.MaterialFactoryNew())
    def node(cls, x, y): return MEL.create_material_expression(mat, cls, x, y)
    def tp(name, t, x, y, st=unreal.MaterialSamplerType.SAMPLERTYPE_COLOR):
        e = node(unreal.MaterialExpressionTextureSampleParameter2D, x, y); e.set_editor_property("parameter_name", name); e.set_editor_property("texture", t); e.set_editor_property("sampler_type", st); return e
    def sp(name, v, x, y):
        e = node(unreal.MaterialExpressionScalarParameter, x, y); e.set_editor_property("parameter_name", name); e.set_editor_property("default_value", v); return e
    uv = node(unreal.MaterialExpressionTextureCoordinate, -1400, -200)
    til = sp("Tiling", 1.0, -1400, -80); muv = node(unreal.MaterialExpressionMultiply, -1200, -150)
    MEL.connect_material_expressions(uv, "", muv, "A"); MEL.connect_material_expressions(til, "", muv, "B")
    bc = tp("BaseColor", tex("T_Asphalt_Hwy5_BC"), -1000, -300); nm = tp("Normal", tex("T_Asphalt_Hwy5_N"), -1000, 0, unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL); orm = tp("ORM", tex("T_Asphalt_Hwy5_ORM"), -1000, 300, unreal.MaterialSamplerType.SAMPLERTYPE_MASKS)
    for e in (bc, nm, orm): MEL.connect_material_expressions(muv, "", e, "UVs")
    # world-aligned wet mask: WorldPosition.xy / WetScale (900 cm)
    wp = node(unreal.MaterialExpressionWorldPosition, -1400, 600); msk = node(unreal.MaterialExpressionComponentMask, -1250, 600); msk.set_editor_property("r", True); msk.set_editor_property("g", True); msk.set_editor_property("b", False)
    MEL.connect_material_expressions(wp, "", msk, "")
    wscale = sp("WetScale", 900.0, -1400, 720); dv = node(unreal.MaterialExpressionDivide, -1100, 620)
    MEL.connect_material_expressions(msk, "", dv, "A"); MEL.connect_material_expressions(wscale, "", dv, "B")
    wet = tp("WetMask", tex("T_Road_Wet_Mask"), -950, 600, unreal.MaterialSamplerType.SAMPLERTYPE_MASKS); MEL.connect_material_expressions(dv, "", wet, "UVs")
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
        if smc.get_material(i) and smc.get_material(i).get_name() in ("MI_Asphalt", "MI_Road_Wet"): smc.set_material(i, mi); out["road"] = i

mat.set_editor_property("used_with_nanite", True); MEL.recompile_material(mat); EAL.save_loaded_asset(mat)
EAL.save_directory(f"{G}/Materials"); unreal.EditorLevelLibrary.save_current_level()
json.dump(out, open(os.path.join(BASE, "road2_out.json"), "w"), indent=1)
unreal.log("CCGL road rebuilt %s" % out)
