
import unreal
lvl = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
lvl.set_level_viewport_camera_info(unreal.Vector(250, 768 - 1300, 384 + 420), unreal.Rotator(roll=0.0, pitch=-18.0, yaw=90.0))
unreal.AutomationLibrary.take_high_res_screenshot(1600, 900, "ccg_install_check.png")
ss = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
labels = sorted(a.get_actor_label() for a in ss.get_all_level_actors() if a.get_actor_label().startswith(("DEV_", "Rider_")))
unreal.log("CCG_FINAL " + ",".join(labels))
