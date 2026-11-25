
import unreal, math, os
BASE = r"C:\Users\211in\Downloads\CCG_UEFN\level"
lbl = open(os.path.join(BASE, "cam_target.txt")).read().strip()
ss = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
a = [x for x in ss.get_all_level_actors() if x.get_actor_label() == lbl][0]
loc = a.get_actor_location(); yaw = a.get_actor_rotation().yaw
# billboard face normal points along local +Y? stand 14 m in front (local -Y side is the sign plane at y=0; face offset +0.12 is the back board) -> look from local -Y
r = math.radians(yaw)
fwd = unreal.Vector(-math.sin(r), math.cos(r), 0)   # local +Y in world
SIDE = float(open(os.path.join(BASE, 'cam_side.txt')).read()) if os.path.exists(os.path.join(BASE, 'cam_side.txt')) else -1.0
cam = unreal.Vector(loc.x + SIDE * fwd.x * 1500, loc.y + SIDE * fwd.y * 1500, loc.z + 450)
ss.set_selected_level_actors([])
look = unreal.Vector(loc.x, loc.y, loc.z + 430)
d = unreal.Vector(look.x - cam.x, look.y - cam.y, look.z - cam.z)
rot = unreal.Rotator(0, math.degrees(math.atan2(d.z, math.hypot(d.x, d.y))), math.degrees(math.atan2(d.y, d.x)))
unreal.EditorLevelLibrary.set_level_viewport_camera_info(cam, rot)
unreal.log("CCGL cam at %s" % lbl)
