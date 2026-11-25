
import unreal
ss = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
acts = ss.get_all_level_actors()
spawn = [a for a in acts if 'Spawn' in a.get_class().get_name() or 'Spawn' in a.get_actor_label()]
base = spawn[0].get_actor_location() if spawn else unreal.Vector(0, 0, 0)
riders = [a for a in acts if a.get_actor_label().startswith("Rider_")]
for i, a in enumerate(sorted(riders, key=lambda x: x.get_actor_label())):
    a.set_actor_location(unreal.Vector(base.x - 150 + i * 150, base.y + 250, base.z), False, False)
    a.set_actor_rotation(unreal.Rotator(0, 0, -90), False)
cam = unreal.Vector(base.x, base.y - 150, base.z + 110)
lvl = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
lvl.set_level_viewport_camera_info(cam, unreal.Rotator(-5, 90, 0))
unreal.AutomationLibrary.take_high_res_screenshot(1600, 900, "ccg_riders_check2.png")
unreal.log(f"CCG_SPAWN2 base={base} spawn={[a.get_actor_label() for a in spawn][:3]} riders={len(riders)}")
