import unreal, json, os
BASE = r"C:\Users\211in\Downloads\CCG_UEFN\level"
G = "/9ec1b72d-2111-4319-b015-282d94c768eb"
out = {}
cls = []
for c in unreal.ObjectIterator(unreal.Class):
    n = c.get_name()
    if "ccg" in n.lower():
        cls.append({"name": n, "path": c.get_path_name(), "super": c.get_super_class().get_name() if hasattr(c,"get_super_class") else "?"})
out["ccg_classes"] = cls[:100]
o = unreal.load_object(None, G + "/_Verse.CCG-Verse-ccg_rail")
out["load_old"] = None if o is None else {"name": o.get_name(), "path": o.get_path_name(), "class": o.get_class().get_name()}
try:
    out["list_verse"] = unreal.EditorAssetLibrary.list_assets(G + "/_Verse", True, False)[:100]
except Exception as e:
    out["list_verse_err"] = str(e)
ss = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for a in ss.get_all_level_actors():
    if a.get_actor_label() == "DEV_ccg_rail_flat_01" or a.get_actor_label() == "DEV_rail_flat_01":
        out["rail_actor_dir"] = [d for d in dir(a) if not d.startswith("_")][:400]
        break
json.dump(out, open(os.path.join(BASE, "probe.json"), "w"), indent=1)
unreal.log("CCGL probe written")
