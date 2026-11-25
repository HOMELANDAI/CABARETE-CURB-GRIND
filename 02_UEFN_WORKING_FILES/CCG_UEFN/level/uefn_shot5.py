import unreal
US = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
US.set_level_viewport_camera_info(unreal.Vector(65500, 17600, 1800), unreal.Rotator(roll=0, pitch=-22, yaw=12))
unreal.AutomationLibrary.take_high_res_screenshot(1920, 1080, "CCG_L5_mojito")
unreal.log("CCGL shot CCG_L5_mojito")
