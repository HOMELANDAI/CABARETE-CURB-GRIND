# exec(open(r'C:/Users/211in/Downloads/CCG_UEFN/level/uefn_gfx_b2.py').read())
# Graphics Tier B (part 2): own water normal map (UEFN forbids referencing Fortnite's /Game textures from user
# materials), MI_Water on the bay, and a validation sweep of the palm replacement.
import unreal, json, traceback, os
G = "/9ec1b72d-2111-4319-b015-282d94c768eb/CCG"
EAL = unreal.EditorAssetLibrary; MEL = unreal.MaterialEditingLibrary; AT = unreal.AssetToolsHelpers.get_asset_tools()
ss = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
out = {"err": []}
try:
    t = unreal.AssetImportTask(); t.filename = r"C:\Users\211in\Downloads\T_Water_Waves_N.png"; t.destination_path = f"{G}/Materials"
    t.automated = True; t.replace_existing = True; t.save = True
    AT.import_asset_tasks([t])
    tex = EAL.load_asset(f"{G}/Materials/T_Water_Waves_N")
    tex.set_editor_property("srgb", False); tex.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_NORMALMAP); EAL.save_loaded_asset(tex)
    mat = EAL.load_asset(f"{G}/Materials/M_CCG_Water")
    # swap the master's texture parameter defaults to the legal texture (parameters are expressions; set via instance instead)
    path = f"{G}/Materials/MI/MI_Water"
    mi = EAL.load_asset(path) if EAL.does_asset_exist(path) else AT.create_asset("MI_Water", f"{G}/Materials/MI", unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    MEL.set_material_instance_parent(mi, mat)
    MEL.set_material_instance_texture_parameter_value(mi, "WaveNormalA", tex); MEL.set_material_instance_texture_parameter_value(mi, "WaveNormalB", tex)
    MEL.update_material_instance(mi); EAL.save_loaded_asset(mi)
    # the master still references the Fortnite texture as the parameter default -> rebuild its two samplers' defaults
    # (cheapest legal fix: point the defaults at our texture by re-setting the expression textures)
    try:
        for e in (MEL.get_material_default_texture_parameter_value, ):
            pass
    except Exception: pass
    n = 0
    for a in ss.get_all_level_actors():
        if a.get_actor_label().startswith("L_Sea"):
            c = a.static_mesh_component if hasattr(a, "static_mesh_component") else a.get_component_by_class(unreal.StaticMeshComponent)
            for i in range(len(c.get_materials())): c.set_material(i, mi)
            n += 1
    out["sea_assigned"] = n
except Exception: out["err"].append("water " + traceback.format_exc()[-500:])
# master default fix: rebuild just the two sampler defaults by editing expressions is not readable; instead re-run the
# water build with our texture by calling the part-1 script with a forced texture
try:
    os.environ["CCG_GFXB"] = "water"; os.environ["CCG_WATER_N"] = f"{G}/Materials/T_Water_Waves_N"
    src = open(r"C:/Users/211in/Downloads/CCG_UEFN/level/uefn_gfx_b.py").read()
    src = src.replace('wn = EAL.load_asset(cands[0]) if cands else EAL.load_asset(f"{G}/Materials/T_Sand_Cabarete_N")', 'wn = EAL.load_asset(os.environ["CCG_WATER_N"])')
    src = src.replace('json.dump(out, open(r"C:\\Users\\211in\\Downloads\\CCG_UEFN\\level\\gfx_b.json", "w"), indent=1)', 'pass')
    exec(src)
    out["water_rebuilt"] = True
    # re-assign the instance (the rebuild assigned the master)
    mi = EAL.load_asset(f"{G}/Materials/MI/MI_Water"); MEL.update_material_instance(mi); EAL.save_loaded_asset(mi)
    for a in ss.get_all_level_actors():
        if a.get_actor_label().startswith("L_Sea"):
            c = a.static_mesh_component if hasattr(a, "static_mesh_component") else a.get_component_by_class(unreal.StaticMeshComponent)
            for i in range(len(c.get_materials())): c.set_material(i, mi)
except Exception: out["err"].append("rebuild " + traceback.format_exc()[-500:])
try:
    # palms: list the meshes now in use (for the validation note)
    kinds = {}
    for a in ss.get_all_level_actors():
        if a.get_actor_label().startswith("L_Palm"):
            c = a.static_mesh_component if hasattr(a, "static_mesh_component") else a.get_component_by_class(unreal.StaticMeshComponent)
            m = c.static_mesh.get_name() if c and c.static_mesh else None; kinds[m] = kinds.get(m, 0) + 1
    out["palm_meshes"] = kinds
    unreal.EditorLevelLibrary.save_current_level()
except Exception: out["err"].append("palms " + traceback.format_exc()[-300:])
json.dump(out, open(r"C:\Users\211in\Downloads\CCG_UEFN\level\gfx_b2.json", "w"), indent=1)
unreal.log("CCG_GFX_B2_DONE err=%d" % len(out["err"]))
