import unreal, math
ss = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
ALL = {a.get_actor_label(): a for a in ss.get_all_level_actors()}
rack = ALL["TR_Shop_DeckRack"]; cnt = ALL["TR_Shop_Counter"]
rp = rack.get_actor_location(); cp = cnt.get_actor_location()
d = unreal.Vector(cp.x-rp.x, cp.y-rp.y, 0); L = math.hypot(d.x,d.y); d.x/=L; d.y/=L
cam = unreal.Vector(rp.x + d.x*330, rp.y + d.y*330, rp.z + 150)
tgt = unreal.Vector(rp.x + d.x*100, rp.y + d.y*100, rp.z + 60)
rot = unreal.MathLibrary.find_look_at_rotation(cam, tgt)
unreal.EditorLevelLibrary.set_level_viewport_camera_info(cam, rot)
unreal.log("CCG_LOOK_DONE")
