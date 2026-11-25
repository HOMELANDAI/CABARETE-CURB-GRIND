import unreal, json, os
BASE = r"C:\Users\211in\Downloads\CCG_UEFN\level"
G = "/9ec1b72d-2111-4319-b015-282d94c768eb"
out = {"objs": []}
vc = unreal.load_object(None, G + "/_Verse.CCG-Verse-ccg_rail")
for o in unreal.ObjectIterator():
    try:
        if o.get_class() == vc or o.get_class().get_name() == "CCG-Verse-ccg_rail":
            out["objs"].append({"name": o.get_name(), "path": o.get_path_name(), "outer": o.get_outer().get_full_name() if o.get_outer() else None})
    except Exception: pass
    if len(out["objs"]) > 20: break
# for a level one, try set
for e in out["objs"]:
    if "PersistentLevel" in e["path"]:
        o = unreal.find_object(None, e["path"])
        if o:
            try: o.set_editor_property("RailId", "probe_sub"); e["set"] = str(o.get_editor_property("RailId"))
            except Exception as ex: e["set_err"] = str(ex)[:160]
            try: e["props"] = {k: str(o.get_editor_property(k)) for k in ("RideHeightCm", "IsSteel", "MinSpeed")}
            except Exception as ex: e["props_err"] = str(ex)[:160]
            # which actor owns it?
            try: e["owner_actor"] = o.get_typed_outer(unreal.Actor).get_actor_label()
            except Exception as ex: e["owner_err"] = str(ex)[:100]
json.dump(out, open(os.path.join(BASE, "probe5.json"), "w"), indent=1, default=str)
unreal.log("CCGL probe5 written")
