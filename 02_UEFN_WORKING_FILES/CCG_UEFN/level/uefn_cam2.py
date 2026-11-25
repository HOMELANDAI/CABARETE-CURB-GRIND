
import unreal, os
ss = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for a in ss.get_all_level_actors():
    if a.get_actor_label() == "FD_LumenExposure": ss.destroy_actor(a)
ss.set_selected_level_actors([])
BASE = r"C:\Users\211in\Downloads\CCG_UEFN\level"
v = open(os.path.join(BASE, "cam_pose.txt")).read().split()
unreal.EditorLevelLibrary.set_level_viewport_camera_info(unreal.Vector(float(v[0]), float(v[1]), float(v[2])), unreal.Rotator(0, float(v[4]), float(v[3])))
unreal.EditorLevelLibrary.save_current_level()
