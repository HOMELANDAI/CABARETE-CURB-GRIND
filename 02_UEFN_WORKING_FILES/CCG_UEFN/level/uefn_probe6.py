import unreal, json, os
BASE = r"C:\Users\211in\Downloads\CCG_UEFN\level"
G = "/9ec1b72d-2111-4319-b015-282d94c768eb"
out = {}
vc = unreal.load_object(None, G + "/_Verse.CCG-Verse-ccg_rail")
try:
    t = unreal.get_type_from_class(vc); out["pytype"] = str(t); out["type_dir"] = [d for d in dir(t) if not d.startswith("_")]
except Exception as e: out["pytype_err"] = str(e)[:200]
cdo = unreal.get_default_object(vc)
out["cdo_dir"] = [d for d in dir(cdo) if not d.startswith("_")]
# try copy actor as T3D via editor: select the one placed by hand and use EditorActorSubsystem? not exposed. Try unreal.EditorLevelLibrary? no.
# brute-force candidate names
cands = ["RailId", "rail_id", "RailId_0", "Rail Id", "railid", "RailId_C", "RailId__RailId"]
res = {}
for c in cands:
    try: res[c] = str(cdo.get_editor_property(c))
    except Exception as e: res[c] = "ERR"
out["cands"] = res
# look at the class's full export via export_text if available
try:
    out["export"] = unreal.SystemLibrary.get_object_name(cdo)
except Exception as e: pass
json.dump(out, open(os.path.join(BASE, "probe6.json"), "w"), indent=1, default=str)
unreal.log("CCGL probe6 written")
