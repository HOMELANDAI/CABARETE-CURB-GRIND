# Temporarily move the start spawn pads onto the HAI Skate Store floor, facing the deck racks, so a live-session
# capture shows the store instead of the beach. Run with CCG_SPAWN=store to move, CCG_SPAWN=restore to put them back.
import unreal, json, os
F = r"F:/HOMELANDAI/CURBSIDE GRIND (CCG)/02_UEFN_WORKING_FILES/CCG_UEFN/level"
MODE = os.environ.get("CCG_SPAWN", "store")
ss = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
pads = sorted([a for a in ss.get_all_level_actors() if "Player_Spawner" in a.get_class().get_name()], key=lambda a: a.get_actor_label())
saved_path = F + "/spawn_saved.json"
out = {"mode": MODE, "pads": [], "err": []}
if MODE == "store":
    saved = {}
    # store floor: rain-suit row centre (14068, 17842, 300) ; shop floor is towards store-local forward (yaw 34)
    cx, cy = 14068 + 560 * 0.829, 17842 + 560 * 0.559
    for i, a in enumerate(pads):
        t = a.get_actor_transform()
        saved[a.get_actor_label()] = {"loc": [t.translation.x, t.translation.y, t.translation.z],
                                      "rot": [t.rotation.rotator().roll, t.rotation.rotator().pitch, t.rotation.rotator().yaw]}
        a.set_actor_location(unreal.Vector(cx + i * 90 * 0.559, cy - i * 90 * 0.829, 262), False, False)
        a.set_actor_rotation(unreal.Rotator(0, 0, 214), False)
        out["pads"].append(a.get_actor_label())
    json.dump(saved, open(saved_path, "w"), indent=1)
else:
    saved = json.load(open(saved_path))
    for a in pads:
        s = saved.get(a.get_actor_label())
        if s:
            a.set_actor_location(unreal.Vector(*s["loc"]), False, False); a.set_actor_rotation(unreal.Rotator(*s["rot"]), False)
            out["pads"].append(a.get_actor_label())
try:
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
except Exception as e: out["err"].append(str(e)[:200])
json.dump(out, open(F + "/spawn_store_out.json", "w"), indent=1)
unreal.log("CCG_SPAWN_%s_DONE %s" % (MODE.upper(), out))
