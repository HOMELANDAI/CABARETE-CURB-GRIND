import unreal, math, json
ss = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
ALL = {a.get_actor_label(): a for a in ss.get_all_level_actors()}
cfg = json.load(open(r"C:\Users\211in\Downloads\CCG_UEFN\level\look.json"))
t = ALL[cfg["target"]]; o, e = t.get_actor_bounds(False)
d = cfg.get("dist", 900); yaw = cfg.get("yaw", 0); pitch = cfg.get("pitch", -15)
r = math.radians(yaw)
cx, cy, cz = o.x - d * math.cos(r), o.y - d * math.sin(r), o.z + cfg.get("up", 250)
unreal.EditorLevelLibrary.set_level_viewport_camera_info(unreal.Vector(cx, cy, cz), unreal.Rotator(0, pitch, yaw))
info = {}
for l in cfg.get("report", []):
    a = ALL.get(l)
    if a:
        o2, e2 = a.get_actor_bounds(False); p = a.get_actor_location()
        info[l] = {"loc": [round(p.x), round(p.y), round(p.z)], "bmin_z": round(o2.z - e2.z), "bmax_z": round(o2.z + e2.z), "ext": [round(e2.x), round(e2.y), round(e2.z)]}
json.dump(info, open(r"C:\Users\211in\Downloads\CCG_UEFN\level\look_out.json", "w"), indent=1)
