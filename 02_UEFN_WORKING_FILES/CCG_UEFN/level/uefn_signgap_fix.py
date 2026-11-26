# uefn_signgap_fix.py — CCG (26 Nov 2026). Re-runnable.
# The phantom "COMBO x1 +1,500" on spawn = the Sign Gap award (ccg_scoring.SignGap = 1500).
# uefn_lvl_place2.py scaled FD_Vol_SignGap by size/100, which assumes a 100 cm base volume. If the
# Fortnite volume device's base is larger, the volume reaches the ground and the spawn pads.
# This script measures the real bounds, rescales the volume to the intended 600 x 600 x 200 cm box
# centred 4.46 m up between the Sign Twins, and reports whether any spawn pad is still inside.
# Pair with the Verse fix in verse2/ccg_game_manager.verse (airborne-only, 5 s grace, 3 s cooldown).
import unreal, json, math
OUT = r"F:/HOMELANDAI/CURBSIDE GRIND (CCG)/02_UEFN_WORKING_FILES/CCG_UEFN/level/signgap_fix_out.json"
TARGET = (600.0, 600.0, 200.0)          # cm, from placements.json devices.volumes Vol_SignGap
CENTER = unreal.Vector(0.0, 0.0, 446.0)
ss = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
acts = ss.get_all_level_actors()
vol = [a for a in acts if a.get_actor_label() == "FD_Vol_SignGap"]
pads = [a for a in acts if "Player_Spawner" in a.get_class().get_name()]
res = {"found": len(vol)}

def inside(a, v):
    o, e = v.get_actor_bounds(False); p = a.get_actor_location()
    return abs(p.x - o.x) <= e.x and abs(p.y - o.y) <= e.y and abs(p.z - o.z) <= e.z + 200  # +2 m = player height

if vol:
    v = vol[0]
    o, e = v.get_actor_bounds(False); s = v.get_actor_scale3d()
    res["before"] = {"origin": [o.x, o.y, o.z], "extent": [e.x, e.y, e.z], "scale": [s.x, s.y, s.z],
                     "pads_inside": [p.get_actor_label() for p in pads if inside(p, v)]}
    # bounds are axis-aligned on a yawed box; use the scale ratio on the local size instead
    base = [2 * ext / sc if sc else 0 for ext, sc in zip((e.x, e.y, e.z), (s.x, s.y, s.z))]
    yaw = math.radians(v.get_actor_rotation().yaw)
    # local XY base from the AABB of a yawed square: aabb = b*(|cos|+|sin|) when base x == base y
    k = abs(math.cos(yaw)) + abs(math.sin(yaw))
    bx, by, bz = base[0] / k, base[1] / k, base[2]
    v.modify()
    v.set_actor_scale3d(unreal.Vector(TARGET[0] / bx, TARGET[1] / by, TARGET[2] / bz))
    v.set_actor_location(CENTER, False, False)
    o, e = v.get_actor_bounds(False); s = v.get_actor_scale3d()
    res["base_cm"] = [bx, by, bz]
    res["after"] = {"origin": [o.x, o.y, o.z], "extent": [e.x, e.y, e.z], "scale": [s.x, s.y, s.z],
                    "pads_inside": [p.get_actor_label() for p in pads if inside(p, v)]}
    unreal.EditorLevelLibrary.save_current_level()
json.dump(res, open(OUT, "w"), indent=1)
unreal.log("CCG_SIGNGAP_DONE " + json.dumps(res))
