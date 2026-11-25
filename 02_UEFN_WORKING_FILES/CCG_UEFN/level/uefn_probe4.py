import unreal, json, os
BASE = r"C:\Users\211in\Downloads\CCG_UEFN\level"
out = {}
ss = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
sel = ss.get_selected_level_actors()
out["n_sel"] = len(sel)
if sel:
    a = sel[0]
    out["label"] = a.get_actor_label(); out["class"] = a.get_class().get_path_name(); out["full"] = a.get_full_name()
    for pn in ("RailId", "RideHeightCm", "IsSteel", "RailPoints"):
        try: out["get_" + pn] = str(a.get_editor_property(pn))
        except Exception as e: out["get_" + pn] = "ERR " + str(e)[:120]
    try:
        a.set_editor_property("RailId", "probe_rail"); out["set_RailId"] = str(a.get_editor_property("RailId"))
    except Exception as e: out["set_RailId"] = "ERR " + str(e)[:160]
    try:
        d = ss.duplicate_actor(a, a.get_world(), unreal.Vector(0, 0, 300))
        out["dup_class"] = d.get_class().get_path_name(); out["dup_label"] = d.get_actor_label()
        d.set_editor_property("RailId", "dup_rail"); out["dup_set"] = str(d.get_editor_property("RailId"))
        ss.destroy_actor(d)
    except Exception as e: out["dup_err"] = str(e)[:200]
json.dump(out, open(os.path.join(BASE, "probe4.json"), "w"), indent=1, default=str)
unreal.log("CCGL probe4 written")
