import unreal, math, json
ss = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
ALL = {a.get_actor_label(): a for a in ss.get_all_level_actors()}
st = ALL["L_Store_OceanDreamPlaza"]; v = ALL["FD_Vol_Store"]
sl = st.get_actor_location(); vl = v.get_actor_location()
dx, dy = vl.x - sl.x, vl.y - sl.y; L = math.hypot(dx, dy); nx, ny = dx / L, dy / L
cx, cy = sl.x + nx * 1250, sl.y + ny * 1250
yaw = math.degrees(math.atan2(-ny, -nx))
unreal.EditorLevelLibrary.set_level_viewport_camera_info(unreal.Vector(cx, cy, sl.z + 650), unreal.Rotator(0, -24, yaw))
info = {}
for l in ["L_Store_OceanDreamPlaza", "TR_Shop_Counter", "TR_Shop_Board", "TR_Shop_DeckRack", "TR_Shop_KaftanRack", "TR_Shop_FlannelTable", "FD_Vol_Store", "FD_Btn_Store_00", "FD_Btn_Store_11"]:
    a = ALL.get(l)
    if a:
        o2, e2 = a.get_actor_bounds(False); p = a.get_actor_location()
        info[l] = {"loc": [round(p.x), round(p.y), round(p.z)], "yaw": round(a.get_actor_rotation().yaw), "bmin_z": round(o2.z - e2.z), "bmax_z": round(o2.z + e2.z), "ext": [round(e2.x), round(e2.y), round(e2.z)]}
json.dump(info, open(r"C:\Users\211in\Downloads\CCG_UEFN\level\look_out.json", "w"), indent=1)
