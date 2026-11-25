
import unreal, json, random
G = "/9ec1b72d-2111-4319-b015-282d94c768eb/CCG"
EAL = unreal.EditorAssetLibrary; MEL = unreal.MaterialEditingLibrary
reg = unreal.AssetRegistryHelpers.get_asset_registry()
signs = []
for a in reg.get_assets_by_path(f"{G}/Materials/MI", False):
    n = str(a.asset_name)
    if n.startswith("MI_Sign_") and not any(k in n for k in ("Billboard", "Cabarete_Letters", "HAI_", "Puente", "Store")):
        signs.append(a.get_asset())
stucco = EAL.load_asset(f"{G}/Materials/MI/MI_Stucco")
rnd = random.Random(11)
ss = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
n = 0; used = {}
for a in ss.get_all_level_actors():
    l = a.get_actor_label()
    if not l.startswith("L_Fill_"): continue
    smc = a.get_component_by_class(unreal.StaticMeshComponent)
    for i in range(smc.get_num_materials()):
        m = smc.get_material(i)
        if m and "Cabarete_Letters" in m.get_name():
            pick = rnd.choice(signs) if (signs and rnd.random() < 0.6) else stucco
            smc.set_material(i, pick); used[pick.get_name()] = used.get(pick.get_name(), 0) + 1; n += 1
mi = EAL.load_asset(f"{G}/Materials/MI/MI_Road_Wet"); MEL.set_material_instance_scalar_parameter_value(mi, "Wetness", 0.2); MEL.update_material_instance(mi); EAL.save_loaded_asset(mi)
unreal.EditorLevelLibrary.save_current_level()
json.dump({"fills_fixed": n, "signs": len(signs), "used": used}, open(r"C:\Users\211in\Downloads\CCG_UEFN\level\fillsign_out.json", "w"), indent=1)
unreal.log("CCGL fill signs %d" % n)
