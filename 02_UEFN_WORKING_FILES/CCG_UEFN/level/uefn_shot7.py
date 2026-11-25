import unreal
US = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
US.set_level_viewport_camera_info(unreal.Vector(42000, 12000, 26000), unreal.Rotator(roll=0, pitch=-62, yaw=20))
unreal.AutomationLibrary.take_high_res_screenshot(1920, 1080, "CCG_L7_aerial")
unreal.log("CCGL shot CCG_L7_aerial")
