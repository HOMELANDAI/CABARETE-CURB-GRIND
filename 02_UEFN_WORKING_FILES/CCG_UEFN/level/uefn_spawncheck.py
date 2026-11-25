
import unreal, json
ss = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
acts = ss.get_all_level_actors()
pads = [a for a in acts if "PlayerSpawn" in a.get_class().get_name() or "Spawn Pad" in a.get_actor_label() or "SpawnPad" in a.get_actor_label()]
out = []
for p in pads:
    l = p.get_actor_location(); hits = []
    for a in acts:
        lab = a.get_actor_label()
        if not lab.startswith("L_"): continue
        o, e = a.get_actor_bounds(False)
        if abs(l.x - o.x) < e.x and abs(l.y - o.y) < e.y and o.z + e.z > l.z - 50 and o.z - e.z < l.z + 50: hits.append((lab, round(o.z + e.z)))
    out.append({"label": p.get_actor_label(), "cls": p.get_class().get_name(), "loc": [round(l.x), round(l.y), round(l.z)], "under_or_at": hits[:6]})
json.dump(out, open(r"C:\Users\211in\Downloads\CCG_UEFN\level\spawn_check.json", "w"), indent=1)
