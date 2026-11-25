
import unreal
lvl = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
lvl.set_level_viewport_camera_info(unreal.Vector(0, -300, 170), unreal.Rotator(-8, 0, 90))
unreal.AutomationLibrary.take_high_res_screenshot(1600, 900, "ccg_riders_check.png", None, False, False, unreal.ComparisonTolerance.LOW, "", 0.0, True)
unreal.log("CCG_SHOT_REQUESTED")
