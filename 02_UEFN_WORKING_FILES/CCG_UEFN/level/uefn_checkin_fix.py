# exec(open(r"C:/Users/211in/r.py").read())  ->  this file
# Check-in blockers (26 Nov 2026): Lore "Submit to main" validation refused the project because
#  (1) M_CCG_Road (dead first-attempt road material) has Linear-Color samplers on mask textures, and
#  (2) M_CCG_Water's two WaveNormal sampler defaults still point at Fortnite's /Game/Athena foam normal.
# Fix: empty + delete M_CCG_Road; rebuild M_CCG_Water with T_Water_Waves_N as the sampler default; keep MI_Water on the sea.
import unreal, json, os, traceback
G = "/9ec1b72d-2111-4319-b015-282d94c768eb/CCG"
F = r"F:/HOMELANDAI/CURBSIDE GRIND (CCG)/02_UEFN_WORKING_FILES/CCG_UEFN/level"
EAL = unreal.EditorAssetLibrary; MEL = unreal.MaterialEditingLibrary
ss = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
out = {"err": []}

# ---- 1. M_CCG_Road
try:
    p = f"{G}/Materials/M_CCG_Road"
    if EAL.does_asset_exist(p):
        m = EAL.load_asset(p)
        MEL.delete_all_material_expressions(m); MEL.recompile_material(m); EAL.save_loaded_asset(m)
        out["road_emptied"] = True
        try:
            out["road_deleted"] = EAL.delete_asset(p)
        except Exception as e:
            out["road_deleted"] = "err " + str(e)[:200]
    else:
        out["road"] = "absent"
except Exception: out["err"].append("road " + traceback.format_exc()[-500:])

# ---- 2. M_CCG_Water rebuilt on the legal normal map
try:
    tex = EAL.load_asset(f"{G}/Materials/T_Water_Waves_N")
    assert tex, "T_Water_Waves_N missing"
    os.environ["CCG_GFXB"] = "water"; os.environ["CCG_WATER_N"] = f"{G}/Materials/T_Water_Waves_N"
    src = open(F + "/uefn_gfx_b.py", encoding="utf-8").read()
    a = 'wn = EAL.load_asset(cands[0]) if cands else EAL.load_asset(f"{G}/Materials/T_Sand_Cabarete_N")'
    assert a in src, "water source line not found"
    src = src.replace(a, 'wn = EAL.load_asset(os.environ["CCG_WATER_N"])')
    src = src.replace('json.dump(out, open(r"C:\\Users\\211in\\Downloads\\CCG_UEFN\\level\\gfx_b.json", "w"), indent=1)', 'pass')
    g = {}
    exec(src, g)
    out["water_rebuilt"] = g.get("out", {}).get("water")
    out["water_err"] = g.get("out", {}).get("err")
    mat = EAL.load_asset(f"{G}/Materials/M_CCG_Water")
    out["water_defaults"] = [str(MEL.get_material_default_texture_parameter_value(mat, n).get_path_name()) for n in ("WaveNormalA", "WaveNormalB")]
    mi = EAL.load_asset(f"{G}/Materials/MI/MI_Water")
    if mi:
        MEL.set_material_instance_parent(mi, mat)
        MEL.set_material_instance_texture_parameter_value(mi, "WaveNormalA", tex); MEL.set_material_instance_texture_parameter_value(mi, "WaveNormalB", tex)
        MEL.update_material_instance(mi); EAL.save_loaded_asset(mi)
        n = 0
        for act in ss.get_all_level_actors():
            if act.get_actor_label().startswith("L_Sea"):
                c = act.static_mesh_component if hasattr(act, "static_mesh_component") else act.get_component_by_class(unreal.StaticMeshComponent)
                for i in range(len(c.get_materials())): c.set_material(i, mi)
                n += 1
        out["sea_assigned_mi"] = n
except Exception: out["err"].append("water " + traceback.format_exc()[-600:])

try:
    unreal.EditorLevelLibrary.save_current_level()
    EAL.save_directory(f"{G}/Materials", only_if_is_dirty=True, recursive=True)
except Exception: out["err"].append("save " + traceback.format_exc()[-300:])
json.dump(out, open(F + "/checkin_fix_out.json", "w"), indent=1)
unreal.log("CCG_CHECKIN_FIX_DONE %s" % json.dumps(out)[:1500])
