
import unreal, math, os, json
BASE = r"C:\Users\211in\Downloads\CCG_UEFN\level"
C = json.load(open(os.path.join(BASE, "bb_candidates.json")))
ss = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
acts = ss.get_all_level_actors()
SKIP = ("Road", "Curb", "Sidewalk", "Ground", "Sand", "Sea", "Beach", "Shoulder", "Billboard", "Lamp", "Palm", "Pole", "Mast", "FlatBar", "Catch", "Fill_")
blockers = []
for a in acts:
    l = a.get_actor_label()
    if not l.startswith("L_") or any(k in l for k in SKIP): continue
    o, e = a.get_actor_bounds(False)
    if e.x < 100 or e.y < 100: continue
    blockers.append((l, o, e))
# also keep 25 m from other billboards and murals
others = [(a.get_actor_label(), a.get_actor_location()) for a in acts if "Billboard" in a.get_actor_label() or "Mural" in a.get_actor_label()]
def clear(lbl, o, e, loc):
    for l, bo, be in blockers:
        if abs(o.x - bo.x) < e.x + be.x + 50 and abs(o.y - bo.y) < e.y + be.y + 50 and abs(o.z - bo.z) < e.z + be.z: return l
    for l, p in others:
        if l != lbl and math.hypot(p.x - loc.x, p.y - loc.y) < 1200: return l
    return None
out = {}
for lbl, cands in C.items():
    a = [x for x in acts if x.get_actor_label() == lbl][0]
    o0, e = a.get_actor_bounds(False); l0 = a.get_actor_location(); off = unreal.Vector(o0.x - l0.x, o0.y - l0.y, o0.z - l0.z)
    chosen = None
    for c in cands:
        loc = unreal.Vector(*c["loc"]); yaw = c["yaw"]
        # bounds extent is yaw dependent; approximate with the larger horizontal extent
        ex = max(e.x, e.y); eb = unreal.Vector(ex, ex, e.z)
        hit = clear(lbl, unreal.Vector(loc.x, loc.y, loc.z + off.z), eb, loc)
        if not hit:
            a.set_actor_location(loc, False, False); a.set_actor_rotation(unreal.Rotator(0, 0, yaw), False)
            chosen = c; break
    out[lbl] = chosen
json.dump(out, open(os.path.join(BASE, "bbfix2_out.json"), "w"), indent=1)
unreal.EditorLevelLibrary.save_current_level()
unreal.log("CCGL bbfix2 %s" % out)
