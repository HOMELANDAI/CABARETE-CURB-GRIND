import unreal
US = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
US.set_level_viewport_camera_info(unreal.Vector(12800, 17000, 900), unreal.Rotator(roll=0, pitch=-12, yaw=40))
unreal.AutomationLibrary.take_high_res_screenshot(1920, 1080, "CCG_L3_store")
unreal.log("CCGL shot CCG_L3_store")
