
import unreal, json
ss = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
P = unreal.Vector(35759.3, 25461.6, 300)
hits = []
for a in ss.get_all_level_actors():
    l = a.get_actor_label()
    if not l.startswith("L_"): continue
    o, e = a.get_actor_bounds(False)
    if abs(P.x - o.x) < e.x and abs(P.y - o.y) < e.y and abs(P.z - o.z) < e.z + 400:
        hits.append((l, [round(o.x), round(o.y), round(o.z)], [round(e.x), round(e.y), round(e.z)], [round(v) for v in (a.get_actor_location().x, a.get_actor_location().y, a.get_actor_location().z)], round(a.get_actor_rotation().yaw, 1)))
json.dump(hits, open(r"C:\Users\211in\Downloads\CCG_UEFN\level\whatshere.json", "w"), indent=1)
