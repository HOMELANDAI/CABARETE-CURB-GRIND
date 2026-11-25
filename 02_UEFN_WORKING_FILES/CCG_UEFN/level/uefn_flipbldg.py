
import unreal, json
ss = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
n = 0
for a in ss.get_all_level_actors():
    l = a.get_actor_label()
    if l.startswith(("L_Bldg_", "L_Fill_", "L_Store")):
        r = a.get_actor_rotation(); a.modify(); a.set_actor_rotation(unreal.Rotator(r.roll, r.pitch, r.yaw + 180.0), False); n += 1
unreal.EditorLevelLibrary.save_current_level()
unreal.log("CCGL flipped %d buildings" % n)
open(r"C:\Users\211in\Downloads\CCG_UEFN\level\flip_out.txt", "w").write(str(n))
