import unreal, json, os
BASE = r"C:\Users\211in\Downloads\CCG_UEFN\level"
ss = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
out = {"nonL": [], "ground": None}
for a in ss.get_all_level_actors():
    l = a.get_actor_label(); c = a.get_class().get_name()
    if not l.startswith(("L_", "DEV_", "FD_")):
        o, e = a.get_actor_bounds(False)
        out["nonL"].append((l, c, [round(o.x), round(o.y), round(o.z)], [round(e.x), round(e.y), round(e.z)], a.is_hidden_ed()))
    elif l in ("L_Ground", "L_Sea", "L_Ground_1", "L_Sea_1") or "Ground" in l or "Sea" in l:
        o, e = a.get_actor_bounds(False)
        out.setdefault("ours", []).append((l, [round(o.x), round(o.y), round(o.z)], [round(e.x), round(e.y), round(e.z)], str(a.get_actor_location())))
json.dump(out, open(os.path.join(BASE, "probe14.json"), "w"), indent=1, default=str)
unreal.log("CCGL probe14 written")
