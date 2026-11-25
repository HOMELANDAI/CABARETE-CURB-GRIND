
import unreal
ss = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
ALL = {a.get_actor_label(): a for a in ss.get_all_level_actors()}
for lbl in ("FD_DaySeq_Day", "FD_DaySeq_Sunset"):
    a = ALL[lbl]; a.set_editor_property("SunlightRotationX", 0.0); a.set_editor_property("SunlightRotationZ", 0.0)
# sunset: yaw the sun to set behind the Cabarete sign (west) = +112 deg from the default 150 -> 262
ALL["FD_DaySeq_Sunset"].set_editor_property("SunlightRotationZ", 112.0)
unreal.EditorLevelLibrary.save_current_level()
unreal.log("CCGL sun offsets reset")
