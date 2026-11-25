import unreal
US = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
US.set_level_viewport_camera_info(unreal.Vector(4200, 7500, 1600), unreal.Rotator(roll=0, pitch=-22, yaw=45))
unreal.AutomationLibrary.take_high_res_screenshot(1920, 1080, "CCG_L2_vagamundo")
unreal.log("CCGL shot CCG_L2_vagamundo")
