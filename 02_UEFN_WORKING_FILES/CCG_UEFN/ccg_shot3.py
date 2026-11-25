
import unreal
lvl = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
lvl.set_level_viewport_camera_info(unreal.Vector(250, 768 - 120, 384 + 110), unreal.Rotator(roll=0.0, pitch=-6.0, yaw=90.0))
unreal.AutomationLibrary.take_high_res_screenshot(1600, 900, "ccg_riders_check3.png")
unreal.log("CCG_SHOT3")
