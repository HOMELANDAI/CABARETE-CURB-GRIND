
import unreal, os, json
ss = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
ALL = {a.get_actor_label(): a for a in ss.get_all_level_actors()}
mode = open(r"C:\Users\211in\Downloads\CCG_UEFN\level\diag_mode.txt").read().strip()
p = ALL.get("PP_CCG_Grade")
if mode == "ppv_off" and p: p.set_editor_property("enabled", False)
if mode == "ppv_on" and p: p.set_editor_property("enabled", True)
if mode == "ppv_noexp" and p:
    s = p.get_editor_property("settings")
    for k in ("auto_exposure_min_brightness", "auto_exposure_max_brightness", "auto_exposure_speed_up", "auto_exposure_speed_down", "auto_exposure_bias"):
        s.set_editor_property("override_" + k, False)
    p.set_editor_property("settings", s); p.set_editor_property("enabled", True)
if mode == "up":
    loc, rot = unreal.EditorLevelLibrary.get_level_viewport_camera_info()
    unreal.EditorLevelLibrary.set_level_viewport_camera_info(unreal.Vector(loc.x, loc.y, loc.z + 3000), unreal.Rotator(0, -35, rot.yaw))
unreal.log("CCGL diag " + mode)
