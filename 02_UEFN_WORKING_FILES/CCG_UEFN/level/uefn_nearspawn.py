
import unreal, json
ss = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
sx, sy = -1076.1, -531.1
out = []
for a in ss.get_all_level_actors():
    l = a.get_actor_label()
    if l.startswith("L_"): continue
    p = a.get_actor_location()
    if abs(p.x - sx) < 900 and abs(p.y - sy) < 900:
        o, e = a.get_actor_bounds(False)
        out.append((l, a.get_class().get_name(), [round(p.x), round(p.y), round(p.z)], [round(e.x), round(e.y), round(e.z)]))
json.dump(out, open(r"C:\Users\211in\Downloads\CCG_UEFN\level\near_spawn.json", "w"), indent=1)
