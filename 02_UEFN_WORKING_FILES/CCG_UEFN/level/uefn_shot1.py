import unreal
US = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
US.set_level_viewport_camera_info(unreal.Vector(-2500, -2300, 900), unreal.Rotator(roll=0, pitch=-14, yaw=64.5))
unreal.AutomationLibrary.take_high_res_screenshot(1920, 1080, "CCG_L1_start")
unreal.log("CCGL shot CCG_L1_start")
