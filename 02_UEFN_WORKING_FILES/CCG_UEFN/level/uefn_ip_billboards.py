
import unreal, os, json, re
BASE = r"C:\Users\211in\Downloads\CCG_UEFN"; SRC = os.path.join(BASE, "ip_billboards")
G = "/9ec1b72d-2111-4319-b015-282d94c768eb/CCG"
EAL = unreal.EditorAssetLibrary; AT = unreal.AssetToolsHelpers.get_asset_tools(); MEL = unreal.MaterialEditingLibrary
out = {"imported": [], "mis": [], "spawned": [], "errors": []}
def imp(png, dest):
    t = unreal.AssetImportTask(); t.filename = png; t.destination_path = dest; t.replace_existing = True; t.automated = True; t.save = True
    AT.import_asset_tasks([t]); return list(t.imported_object_paths)
for f in sorted(os.listdir(SRC)):
    if not f.endswith(".png") or os.path.exists(os.path.join(BASE, "level", "ipbb_out.json")): continue
    dest = f"{G}/Murals" if f.startswith("T_Mural") else f"{G}/Signs"
    try:
        paths = imp(os.path.join(SRC, f), dest)
        name = f[:-4]; tex = EAL.load_asset(f"{dest}/{name}")
        if tex:
            if name.endswith("_E"):
                tex.set_editor_property("srgb", False); tex.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_GRAYSCALE)
            else:
                tex.set_editor_property("srgb", True)
            EAL.save_loaded_asset(tex)
        out["imported"].append((f, [str(p) for p in paths]))
    except Exception as e: out["errors"].append((f, str(e)[:120]))
# material instances for the 3 new signs (same recipe as uefn_lvl_import.mi)
def mi(name, bcp, emis):
    path = f"{G}/Materials/MI/{name}"
    m = EAL.load_asset(path) if EAL.does_asset_exist(path) else AT.create_asset(name, f"{G}/Materials/MI", unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    m.set_editor_property("parent", EAL.load_asset(f"{G}/Materials/M_CCG_Env"))
    for pn, tp_ in (("BaseColor", bcp), ("Normal", f"{G}/Materials/T_WallPaint_N"), ("ORM", f"{G}/Materials/T_WallPaint_ORM"), ("Emissive", emis)):
        tx = EAL.load_asset(tp_)
        if tx: MEL.set_material_instance_texture_parameter_value(m, pn, tx)
    MEL.set_material_instance_scalar_parameter_value(m, "EmissiveStrength", 3.0)
    MEL.set_material_instance_scalar_parameter_value(m, "Tiling", 1.0)
    MEL.update_material_instance(m); EAL.save_loaded_asset(m); return m
NEW = {"Billboard_PPA_Microdrama": ([40439.2, 24173.3, 71.9], -3.89), "Billboard_HAI_Frequency": ([10797.6, 14478.9, 131.9], 46.36), "Billboard_XPets": ([70288.9, 18547.4, 226.2], -10.73)}
ss = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
ALL = {a.get_actor_label(): a for a in ss.get_all_level_actors()}
ref = ALL.get("L_Billboard_1")
mesh = EAL.load_asset(f"{G}/Meshes/SM_CCG_Billboard") if EAL.does_asset_exist(f"{G}/Meshes/SM_CCG_Billboard") else None
if not mesh and ref:
    mesh = ref.get_component_by_class(unreal.StaticMeshComponent).static_mesh
# which slot is the sign face? copy from Billboard_1: find slot whose material name contains "Sign_Billboard"
sign_slot = None
if ref:
    smc = ref.get_component_by_class(unreal.StaticMeshComponent)
    for i in range(smc.get_num_materials()):
        m = smc.get_material(i)
        if m and "Billboard" in m.get_name(): sign_slot = i
    out["ref_mats"] = [str(smc.get_material(i).get_name()) if smc.get_material(i) else None for i in range(smc.get_num_materials())]
for i, (key, (loc, yaw)) in enumerate(NEW.items()):
    try:
        m = mi(f"MI_Sign_{key}", f"{G}/Signs/T_Sign_{key}_BC", f"{G}/Signs/T_Sign_{key}_E"); out["mis"].append(m.get_name())
        lbl = f"L_Billboard_{4 + i}"
        a = ALL.get(lbl)
        if not a:
            a = ss.spawn_actor_from_object(mesh, unreal.Vector(*loc), unreal.Rotator(0, 0, yaw)) if mesh else None
        if a:
            a.set_actor_label(lbl); a.set_actor_location(unreal.Vector(*loc), False, False); a.set_actor_rotation(unreal.Rotator(0, 0, yaw), False)
            a.set_folder_path("CCG/Props")
            smc = a.get_component_by_class(unreal.StaticMeshComponent)
            if ref:
                rs = ref.get_component_by_class(unreal.StaticMeshComponent)
                for s in range(rs.get_num_materials()): smc.set_material(s, rs.get_material(s))
            if sign_slot is not None: smc.set_material(sign_slot, m)
            out["spawned"].append((lbl, loc, yaw, sign_slot))
    except Exception as e: out["errors"].append((key, str(e)[:160]))
EAL.save_directory(f"{G}/Signs"); EAL.save_directory(f"{G}/Murals"); EAL.save_directory(f"{G}/Materials/MI")
unreal.EditorLevelLibrary.save_current_level()
json.dump(out, open(os.path.join(BASE, "level", "ipbb_out.json"), "w"), indent=1)
unreal.log("CCGL ip billboards: %s" % json.dumps(out)[:400])
