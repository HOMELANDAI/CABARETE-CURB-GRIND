import unreal, json, os
BASE = r"C:\Users\211in\Downloads\CCG_UEFN\level"
out = {}
reg = unreal.AssetRegistryHelpers.get_asset_registry()
try:
    out["roots"] = [str(p) for p in reg.get_sub_paths("/", False)]
except Exception as e:
    out["roots_err"] = str(e)
hits = {}
try:
    allassets = reg.get_all_assets(True)
    out["total_assets"] = len(allassets)
    for a in allassets:
        pk = str(a.package_name)
        cls = str(a.asset_class_path.asset_name)
        if "device" in pk.lower() or "Device" in cls:
            hits.setdefault(cls, [])
            if len(hits[cls]) < 400: hits[cls].append(pk)
except Exception as e:
    out["all_err"] = str(e)
out["device_hits"] = hits
ss = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
dev = {}
for a in ss.get_all_level_actors():
    n = a.get_actor_label()
    if n.startswith("DEV_ccg") or n == "DEV_rail_flat_01":
        c = a.get_class()
        dev[n] = {"class": c.get_path_name(), "name": c.get_name()}
out["dev_actors"] = dev
try:
    vs = reg.get_assets_by_path("/9ec1b72d-2111-4319-b015-282d94c768eb/_Verse", True)
    out["verse_assets"] = [str(a.package_name) + ":" + str(a.asset_name) + ":" + str(a.asset_class_path.asset_name) for a in vs][:80]
except Exception as e:
    out["verse_err"] = str(e)
nat = []
for name in ["FortVolumeDevice","FortPlayerSpawnerDevice","FortTriggerDevice","FortBarrierDevice","FortHUDMessageDevice","FortEndGameDevice","FortButtonDevice","FortItemGranterDevice","FortClassDesignerDevice","FortClassSelectorDevice","FortCustomizableLightDevice","FortDaySequenceDevice","FortVFXSpawnerDevice","FortMutatorZoneDevice","FortVerseDevice","VerseDevice","FortVolumeDeviceBase"]:
    try:
        c = unreal.load_class(None, "/Script/FortniteGame." + name)
        nat.append(name + (":OK" if c else ":none"))
    except Exception as e:
        nat.append(name + ":ERR " + str(e)[:80])
out["native"] = nat
json.dump(out, open(os.path.join(BASE, "devices2.json"), "w"), indent=1)
unreal.log("CCGL devices2.json written")
