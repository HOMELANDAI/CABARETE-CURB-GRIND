import unreal
ss = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
n = 0; h = 0
for a in ss.get_all_level_actors():
    l = a.get_actor_label()
    if l.startswith("BuilderGridPlane"): ss.destroy_actor(a); n += 1
    elif l.startswith("S_BackDrop") or l.startswith("Decal"): a.set_actor_hidden_in_game(True); a.set_is_temporarily_hidden_in_editor(True); h += 1
unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
unreal.log("CCGL template cleanup: deleted %d grid planes, hid %d backdrops" % (n, h))
