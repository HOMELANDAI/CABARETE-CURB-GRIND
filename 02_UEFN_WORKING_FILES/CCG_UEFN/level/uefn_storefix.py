
import unreal, math, json
ss = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
ALL = {a.get_actor_label(): a for a in ss.get_all_level_actors()}
st = ALL["L_Store_OceanDreamPlaza"]; sl = st.get_actor_location(); o, e = st.get_actor_bounds(False)
syaw = st.get_actor_rotation().yaw; rr = math.radians(syaw)
# unit vector from origin toward the body centre, and its sign along local +Y
bx, by = o.x - sl.x, o.y - sl.y
ly = (-math.sin(rr)) * bx + math.cos(rr) * by    # projection on local +Y
side = -1.0 if ly > 0 else 1.0                    # forecourt is the opposite side of the body
out = {"origin": [round(sl.x), round(sl.y)], "bounds_c": [round(o.x), round(o.y)], "ext": [round(e.x), round(e.y)], "ly": round(ly), "forecourt_side": side}
for i in range(23):
    dx = (-6 + (i % 12) * 1.0) * 100; dy = side * (1.2 + (i // 12) * 1.3) * 100
    x = sl.x + dx * math.cos(rr) - dy * math.sin(rr); y = sl.y + dx * math.sin(rr) + dy * math.cos(rr)
    b = ALL.get("FD_Btn_Store_%02d" % i); g = ALL.get("FD_Granter_Store_%02d" % i)
    if b: b.set_actor_location(unreal.Vector(x, y, sl.z), False, False); b.set_actor_rotation(unreal.Rotator(0, 0, syaw + (0 if side > 0 else 180)), False)
    if g: g.set_actor_location(unreal.Vector(x, y, sl.z - 150), False, False)
v = ALL.get("FD_Vol_Store")
if v:
    dy = side * 200; v.set_actor_location(unreal.Vector(sl.x - dy * math.sin(rr), sl.y + dy * math.cos(rr), sl.z + 150), False, False)
# camera on the forecourt looking at the store face
dy = side * 1400; cx, cy = sl.x - dy * math.sin(rr), sl.y + dy * math.cos(rr)
look = math.degrees(math.atan2(sl.y - cy, sl.x - cx))
unreal.EditorLevelLibrary.set_level_viewport_camera_info(unreal.Vector(cx, cy, sl.z + 450), unreal.Rotator(0, -14, look))
unreal.EditorLevelLibrary.save_current_level()
json.dump(out, open(r"C:\Users\211in\Downloads\CCG_UEFN\level\store_fix.json", "w"), indent=1)
