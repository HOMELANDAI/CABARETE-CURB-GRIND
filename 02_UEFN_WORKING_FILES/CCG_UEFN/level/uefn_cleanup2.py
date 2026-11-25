import unreal
ss = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
kill_labels = ("VK Waterbody Ocean Parent0", "Modern Armchair 38", "Modern Armchair 39", "Glass Wave 22", "Decal2", "Modern CoffeeTable 20",
               "Modern Kitchen Cabinet Tall Shelf 8", "Agency Planter 32", "Plane", "Rug Modern 17", "Floors Generic BasicTile34", "CCG Kicker")
n = 0
for a in ss.get_all_level_actors():
    if a.get_actor_label() in kill_labels: ss.destroy_actor(a); n += 1
# player starts / spawn pads to the route start
for a in ss.get_all_level_actors():
    l = a.get_actor_label()
    if "Spawn Pad" in l or a.get_class().get_name() == "FortPlayerStartCreative":
        a.set_actor_location(unreal.Vector(-516.2, -1083.3, 130.0), False, False); a.set_actor_rotation(unreal.Rotator(roll=0.0, pitch=0.0, yaw=64.5), False)
unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
unreal.log("CCGL cleanup2 removed %d" % n)
