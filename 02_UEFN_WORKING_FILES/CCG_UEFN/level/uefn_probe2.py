import unreal, json, os
BASE = r"C:\Users\211in\Downloads\CCG_UEFN\level"
G = "/9ec1b72d-2111-4319-b015-282d94c768eb"
out = {}
ss = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for a in ss.get_all_level_actors():
    if a.get_actor_label() == "DEV_rail_flat_01":
        out["label"] = a.get_actor_label()
        out["class"] = a.get_class().get_path_name()
        out["dir"] = [d for d in dir(a) if not d.startswith("_")]
        comps = []
        for c in a.get_components_by_class(unreal.ActorComponent):
            comps.append({"name": c.get_name(), "class": c.get_class().get_path_name(), "dir": [d for d in dir(c) if not d.startswith("_") and d[0].isupper()][:60]})
        out["comps"] = comps
        break
vc = unreal.load_object(None, G + "/_Verse.CCG-Verse-ccg_rail")
out["vc_dir"] = [d for d in dir(vc) if not d.startswith("_")][:200]
try:
    cdo = unreal.get_default_object(vc)
    out["cdo"] = {"class": cdo.get_class().get_path_name(), "dir": [d for d in dir(cdo) if not d.startswith("_") and d[0].isupper()]}
except Exception as e:
    out["cdo_err"] = str(e)
# try spawning via spawn_actor_from_class
try:
    t = ss.spawn_actor_from_class(vc, unreal.Vector(0, 0, -5000))
    out["spawn_from_class"] = {"class": t.get_class().get_path_name(), "props": [d for d in dir(t) if d[0].isupper()][:80]}
    ss.destroy_actor(t)
except Exception as e:
    out["spawn_from_class_err"] = str(e)[:300]
json.dump(out, open(os.path.join(BASE, "probe2.json"), "w"), indent=1, default=str)
unreal.log("CCGL probe2 written")
