# uefn_spawn_diag.py — CCG (26 Nov 2026). Read-only diagnosis + one editor still. Re-runnable.
# client_check_1.png shows the rider on bare sand with no level in view, although the pads sit at
# Spawn_Start (-1076, -531) facing the Cabarete sign (yaw 26.27). This lists, for the pads and for
# everything within 80 m of them, what the client could be missing: hidden-in-game, editor-only,
# spatial loading (World Partition) and the pad facing vs. the bearing to the sign. Then it takes a
# 3840x2160 viewport still from the rider's eye at the first pad (Saved/Screenshots).
import unreal, json, math
OUT = r"F:/HOMELANDAI/CURBSIDE GRIND (CCG)/02_UEFN_WORKING_FILES/CCG_UEFN/level/spawn_diag_out.json"
ss = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
acts = ss.get_all_level_actors()
pads = sorted([a for a in acts if "Player_Spawner" in a.get_class().get_name()], key=lambda a: a.get_actor_label())

def prop(a, n):
    try: return a.get_editor_property(n)
    except Exception: return None

res = {"pads": [], "near": [], "counts": {}}
for p in pads:
    l = p.get_actor_location(); yaw = p.get_actor_rotation().yaw
    bearing = math.degrees(math.atan2(0 - l.y, 0 - l.x))
    res["pads"].append({"label": p.get_actor_label(), "loc": [round(l.x), round(l.y), round(l.z)], "yaw": round(yaw, 1),
                        "bearing_to_sign": round(bearing, 1), "enabled": str(prop(p, "enabled_on_phase"))})
if pads:
    c = pads[0].get_actor_location()
    hidden = editor_only = not_spatial = 0
    for a in acts:
        l = a.get_actor_label()
        if not l.startswith(("L_", "TR_", "TD_", "FD_")): continue
        d = (a.get_actor_location() - c).length()
        if d > 8000: continue
        h = bool(prop(a, "hidden")); eo = bool(prop(a, "is_editor_only_actor")); sp = prop(a, "is_spatially_loaded")
        hidden += h; editor_only += eo; not_spatial += (sp is False)
        res["near"].append({"label": l, "dist_m": round(d / 100, 1), "hidden_in_game": h, "editor_only": eo, "spatially_loaded": sp})
    res["near"].sort(key=lambda r: r["dist_m"])
    res["counts"] = {"near": len(res["near"]), "hidden_in_game": hidden, "editor_only": editor_only, "not_spatially_loaded": not_spatial}
    US = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
    p = pads[0]
    US.set_level_viewport_camera_info(p.get_actor_location() + unreal.Vector(0, 0, 160), unreal.Rotator(roll=0, pitch=-4, yaw=p.get_actor_rotation().yaw))
    unreal.AutomationLibrary.take_high_res_screenshot(3840, 2160, "CCG_spawn_eye")
json.dump(res, open(OUT, "w"), indent=1)
unreal.log("CCG_SPAWNDIAG_DONE " + json.dumps(res["counts"]) + " pads=" + json.dumps(res["pads"]))
