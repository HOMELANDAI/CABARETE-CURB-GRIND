import unreal
US = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
US.set_level_viewport_camera_info(unreal.Vector(80500, 18600, 1400), unreal.Rotator(roll=0, pitch=-18, yaw=20))
unreal.AutomationLibrary.take_high_res_screenshot(1920, 1080, "CCG_L6_horseshoe")
unreal.log("CCGL shot CCG_L6_horseshoe")
