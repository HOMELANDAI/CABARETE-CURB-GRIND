import unreal
ss = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for a in ss.get_all_level_actors():
    if a.get_actor_label() == "DEV_probe_rail":
        ss.set_selected_level_actors([a]); unreal.log("CCGL selected"); break
