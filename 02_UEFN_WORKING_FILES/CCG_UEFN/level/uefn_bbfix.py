
import unreal, math, os, json
BASE = r"C:\Users\211in\Downloads\CCG_UEFN\level"
ss = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
acts = ss.get_all_level_actors()
SKIP = ("Road", "Curb", "Sidewalk", "Ground", "Sand", "Sea", "Beach", "Shoulder", "Billboard", "Lamp", "Palm", "Pole", "Mast", "Bar", "Rail", "Catch")
blockers = []
for a in acts:
    l = a.get_actor_label()
    if not l.startswith("L_") or any(k in l for k in SKIP): continue
    o, e = a.get_actor_bounds(False)
    if e.x < 100 or e.y < 100: continue
    blockers.append((l, o, e))
def overlaps(o, e):
    for l, bo, be in blockers:
        if abs(o.x - bo.x) < e.x + be.x and abs(o.y - bo.y) < e.y + be.y and abs(o.z - bo.z) < e.z + be.z: return l
    return None
out = {}
for lbl in ("L_Billboard_4", "L_Billboard_5", "L_Billboard_6"):
    a = [x for x in acts if x.get_actor_label() == lbl][0]
    yaw = a.get_actor_rotation().yaw; r = math.radians(yaw)
    t = unreal.Vector(math.cos(r), math.sin(r), 0)   # along-road tangent (billboard local X)
    start = a.get_actor_location(); o, e = a.get_actor_bounds(False); off = unreal.Vector(o.x - start.x, o.y - start.y, o.z - start.z)
    hit0 = overlaps(o, e); best = None
    if hit0:
        for step in range(1, 40):
            for sgn in (1, -1):
                d = step * 500 * sgn
                p = unreal.Vector(start.x + t.x * d, start.y + t.y * d, start.z)
                if not overlaps(unreal.Vector(p.x + off.x, p.y + off.y, p.z + off.z), e):
                    best = (d, p); break
            if best: break
        if best:
            a.set_actor_location(best[1], False, False)
    out[lbl] = {"hit": hit0, "moved_cm": best[0] if best else 0, "loc": [round(v, 1) for v in (a.get_actor_location().x, a.get_actor_location().y, a.get_actor_location().z)]}
json.dump(out, open(os.path.join(BASE, "bbfix_out.json"), "w"), indent=1)
unreal.EditorLevelLibrary.save_current_level()
unreal.log("CCGL bbfix %s" % out)
