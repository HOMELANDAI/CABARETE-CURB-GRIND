
import unreal, math, json
ss = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
acts = ss.get_all_level_actors()
pads = sorted([a for a in acts if "Player_Spawner" in a.get_class().get_name()], key=lambda a: a.get_actor_label())
sx, sy, sz, yaw = -1076.1, -531.1, 106.0, 26.27
r = math.radians(yaw); nx, ny = -math.sin(r), math.cos(r)   # left-hand normal to the facing direction
out = []
for i, p in enumerate(pads):
    off = (-1.5 if i == 0 else 1.5) * 100
    loc = unreal.Vector(sx + nx * off, sy + ny * off, sz + 15)
    p.modify(); p.set_actor_location(loc, False, False); p.set_actor_rotation(unreal.Rotator(0, 0, yaw), False)
    out.append((p.get_actor_label(), [round(loc.x), round(loc.y), round(loc.z)]))
# anything solid at the new spot? (buildings / fills only)
hits = []
for a in acts:
    l = a.get_actor_label()
    if not l.startswith(("L_Bldg", "L_Fill", "L_Store", "L_Sign")): continue
    o, e = a.get_actor_bounds(False)
    if abs(sx - o.x) < e.x + 200 and abs(sy - o.y) < e.y + 200: hits.append(l)
unreal.EditorLevelLibrary.save_current_level()
json.dump({"pads": out, "near": hits}, open(r"C:\Users\211in\Downloads\CCG_UEFN\level\spawn_fix.json", "w"), indent=1)
