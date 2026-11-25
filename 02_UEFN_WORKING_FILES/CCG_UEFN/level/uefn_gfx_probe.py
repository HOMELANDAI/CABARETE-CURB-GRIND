
import unreal, os, json
BASE = r"C:\Users\211in\Downloads\CCG_UEFN\level"
G = "/9ec1b72d-2111-4319-b015-282d94c768eb/CCG"
out = {}
ss = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
ALL = {a.get_actor_label(): a for a in ss.get_all_level_actors()}
d = ALL.get("FD_DaySeq_Day")
if d:
    ss.set_selected_level_actors([d])
    t = unreal.AssetExportTask(); t.object = d.get_world(); t.filename = os.path.join(BASE, "t3d_dayseq.t3d"); t.selected = True; t.automated = True; t.replace_identical = True; t.prompt = False
    out["dayseq_export"] = unreal.Exporter.run_asset_export_task(t)
    comps = {}
    for c in d.get_components_by_class(unreal.ActorComponent):
        try:
            v = c.get_editor_property("PlayerOptionData")
            comps["PlayerOptionData"] = v.export_text()[:6000]
        except Exception: pass
    out["dayseq"] = comps
# classes
for k, p in {"ppv": "/Script/Engine.PostProcessVolume", "decal": "/Script/Engine.DecalActor", "lumenexp": None}.items():
    if p:
        try: out[k] = str(unreal.load_class(None, p))
        except Exception as e: out[k] = "ERR " + str(e)[:80]
# find lumen exposure device + nanite API
reg = unreal.AssetRegistryHelpers.get_asset_registry()
hits = []
for a in reg.get_all_assets(True):
    n = str(a.asset_name)
    if "LumenExposure" in n or "Lumen_Exposure" in n or "PostProcess" in n and "Device" in n:
        hits.append(str(a.package_name))
out["lumen_hits"] = hits[:20]
# textures present
out["tex"] = {n: unreal.EditorAssetLibrary.does_asset_exist(f"{G}/Materials/{n}") for n in ("T_Road_Paint_Mask", "T_Road_Wet_Mask", "T_Decal_Atlas", "T_Grunge_Mask", "T_Asphalt_Hwy5_BC")}
# static meshes + nanite state
sms = []
for a in reg.get_assets_by_path(f"{G}/Meshes", True):
    if str(a.asset_class_path.asset_name) == "StaticMesh":
        m = a.get_asset(); ns = m.get_editor_property("nanite_settings")
        sms.append((str(a.asset_name), bool(ns.get_editor_property("enabled"))))
out["meshes"] = sms[:80]; out["n_meshes"] = len(sms)
# road actors + their material slots
out["road"] = [(l, [a.get_component_by_class(unreal.StaticMeshComponent).get_material(i).get_name() for i in range(a.get_component_by_class(unreal.StaticMeshComponent).get_num_materials())]) for l, a in ALL.items() if "Road" in l][:6]
json.dump(out, open(os.path.join(BASE, "gfx_probe.json"), "w"), indent=1)
unreal.log("CCGL gfx probe done")
