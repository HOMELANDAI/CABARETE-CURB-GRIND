
import unreal, json
ss = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
rows = []
for a in ss.get_all_level_actors():
    l = a.get_actor_label()
    if l.startswith(("L_Bldg_", "L_Fill_", "L_Store")):
        o, e = a.get_actor_bounds(False); p = a.get_actor_location()
        rows.append((l, [round(p.x), round(p.y)], [round(o.x), round(o.y)], [round(e.x), round(e.y), round(e.z)], round(a.get_actor_rotation().yaw, 1)))
json.dump(rows, open(r"C:\Users\211in\Downloads\CCG_UEFN\level\bldg_bounds.json", "w"))
