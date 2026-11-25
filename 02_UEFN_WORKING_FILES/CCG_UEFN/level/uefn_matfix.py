
import unreal, os, json
G = "/9ec1b72d-2111-4319-b015-282d94c768eb/CCG"
EAL = unreal.EditorAssetLibrary; MEL = unreal.MaterialEditingLibrary
out = {"fixed": [], "nanite_flag": [], "blend": None, "errors": []}
MASKY = ("_ORM", "_Mask", "_SMR", "_H")
def fix_samplers(mat):
    n = 0
    for e in MEL.get_material_expressions(mat) if hasattr(MEL, "get_material_expressions") else []:
        pass
    # fall back: walk expressions via the editor-only data
    try:
        exprs = mat.get_editor_property("expressions")
    except Exception:
        exprs = []
    for e in exprs:
        if isinstance(e, unreal.MaterialExpressionTextureSampleParameter2D) or isinstance(e, unreal.MaterialExpressionTextureSample):
            t = e.get_editor_property("texture")
            if t and any(k in t.get_name() for k in MASKY):
                e.set_editor_property("sampler_type", unreal.MaterialSamplerType.SAMPLERTYPE_MASKS); n += 1
    return n
for mn in ("M_CCG_Road", "M_CCG_Env", "M_CCG_Decal"):
    p = f"{G}/Materials/{mn}"
    if not EAL.does_asset_exist(p): continue
    m = EAL.load_asset(p)
    try:
        n = fix_samplers(m); out["fixed"].append((mn, n))
    except Exception as e: out["errors"].append((mn, "samplers", str(e)[:100]))
    if mn != "M_CCG_Decal":
        try:
            m.set_editor_property("used_with_nanite", True); m.set_editor_property("used_with_static_lighting", False); out["nanite_flag"].append(mn)
        except Exception as e: out["errors"].append((mn, "nanite", str(e)[:100]))
    else:
        try:
            m.set_editor_property("material_domain", unreal.MaterialDomain.MD_DEFERRED_DECAL)
            m.set_editor_property("blend_mode", unreal.BlendMode.BLEND_ALPHA_COMPOSITE)
            out["blend"] = str(m.get_editor_property("blend_mode"))
        except Exception as e: out["errors"].append((mn, "blend", str(e)[:100]))
    MEL.recompile_material(m); EAL.save_loaded_asset(m)
# also flag every other master under Materials that is used on nanite meshes
reg = unreal.AssetRegistryHelpers.get_asset_registry()
for a in reg.get_assets_by_path(f"{G}/Materials", False):
    if str(a.asset_class_path.asset_name) == "Material":
        m = a.get_asset()
        try:
            if not m.get_editor_property("used_with_nanite") and m.get_editor_property("material_domain") == unreal.MaterialDomain.MD_SURFACE:
                m.set_editor_property("used_with_nanite", True); MEL.recompile_material(m); EAL.save_loaded_asset(m); out["nanite_flag"].append(str(a.asset_name))
        except Exception as e: out["errors"].append((str(a.asset_name), "flag", str(e)[:80]))
json.dump(out, open(r"C:\Users\211in\Downloads\CCG_UEFN\level\matfix_out.json", "w"), indent=1)
unreal.log("CCGL matfix %s" % out)
