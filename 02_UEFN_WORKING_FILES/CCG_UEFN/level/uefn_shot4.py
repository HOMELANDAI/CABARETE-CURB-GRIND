import unreal
US = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
US.set_level_viewport_camera_info(unreal.Vector(36500, 18200, 2200), unreal.Rotator(roll=0, pitch=-25, yaw=8))
unreal.AutomationLibrary.take_high_res_screenshot(1920, 1080, "CCG_L4_multiplex")
unreal.log("CCGL shot CCG_L4_multiplex")
