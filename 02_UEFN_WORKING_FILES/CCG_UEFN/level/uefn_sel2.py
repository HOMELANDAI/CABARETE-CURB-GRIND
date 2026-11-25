import unreal
ss = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
want = open(r"C:\Users\211in\Downloads\CCG_UEFN\level\sel_target.txt").read().strip()
for a in ss.get_all_level_actors():
    if a.get_actor_label() == want:
        ss.set_selected_level_actors([a]); unreal.log("CCGL selected " + want); break
