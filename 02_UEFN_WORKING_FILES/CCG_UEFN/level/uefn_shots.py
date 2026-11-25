import unreal, math
US = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
AL = unreal.AutomationLibrary
shots = [
 ("CCG_L1_start",    (-2500, -2300, 900),  (-14, 64.5, 0)),   # start / Cabarete sign looking along route
 ("CCG_L2_vagamundo",(4200, 7500, 1600),   (-22, 45, 0)),      # P1 Vagamundo
 ("CCG_L3_store",    (12800, 17000, 900),  (-12, 40, 0)),      # Ocean Dream Plaza store
 ("CCG_L4_multiplex",(36500, 18200, 2200), (-25, 8, 0)),       # P2 Multiplex
 ("CCG_L5_mojito",   (65500, 17600, 1800), (-22, 12, 0)),      # P3 Mojito
 ("CCG_L6_horseshoe",(80500, 18600, 1400), (-18, 20, 0)),      # P4 Horseshoe / courtyard
 ("CCG_L7_aerial",   (42000, 12000, 26000),(-62, 20, 0)),      # whole route aerial
]
import time
for name, loc, rot in shots:
    US.set_level_viewport_camera_info(unreal.Vector(*loc), unreal.Rotator(roll=rot[2], pitch=rot[0], yaw=rot[1]))
    AL.take_high_res_screenshot(1920, 1080, name)
    unreal.log("CCGL shot queued " + name)
