
import unreal, math, json
ss = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
ALL = {a.get_actor_label(): a for a in ss.get_all_level_actors()}
out = {"moved": [], "errors": []}
def mv(lbl, x, y, z, yaw):
    a = ALL.get(lbl)
    if not a: out["errors"].append(("missing", lbl)); return
    a.modify(); a.set_actor_location(unreal.Vector(x, y, z), False, False); a.set_actor_rotation(unreal.Rotator(0, 0, yaw), False); out["moved"].append(lbl)
yaw = 26.27; r = math.radians(yaw); tx, ty = math.cos(r), math.sin(r); nx, ny = -math.sin(r), math.cos(r)
sx, sy, sz = -1076.1, -531.1, 106.0
# rider select: selector zone on each podium, its button 1.5 m toward the spawn, facing the spawn
for i in range(7):
    c = ALL.get("FD_Class_%d" % i)
    if not c: continue
    p = c.get_actor_location()
    mv("FD_ClassSel_%d" % i, p.x, p.y, p.z, yaw)
    mv("FD_Btn_Rider_%d" % i, p.x + nx * 150, p.y + ny * 150, p.z, yaw + 90)
# debug trick buttons: a row 3 m behind the spawn (away from the podiums), 1.5 m apart
for i in range(6):
    d = (i - 2.5) * 150
    mv("FD_Btn_Debug_%d" % i, sx + tx * d - nx * 300, sy + ty * d - ny * 300, sz, yaw - 90)
# sunset + effects: a kiosk 4.5 m behind the spawn
mv("FD_Btn_Sunset", sx - tx * 120 - nx * 450, sy - ty * 120 - ny * 450, sz, yaw - 90)
mv("FD_Btn_Effects", sx + tx * 120 - nx * 450, sy + ty * 120 - ny * 450, sz, yaw - 90)
# store: 23 button/granter pairs in two rows in front of the store (metres -> cm this time)
st = ALL.get("L_Store_OceanDreamPlaza")
if st:
    sl = st.get_actor_location(); syaw = st.get_actor_rotation().yaw; rr = math.radians(syaw)
    # after the building flip the store body extends toward local +Y away from the road; the forecourt is local -Y
    for i in range(23):
        dx = (-6 + (i % 12) * 1.0) * 100; dy = -(3 + (i // 12) * 2.0) * 100
        x = sl.x + dx * math.cos(rr) - dy * math.sin(rr); y = sl.y + dx * math.sin(rr) + dy * math.cos(rr)
        mv("FD_Btn_Store_%02d" % i, x, y, sl.z, syaw + 180)
        mv("FD_Granter_Store_%02d" % i, x, y, sl.z - 150, syaw)
    # store volume centred on the forecourt rows
    v = ALL.get("FD_Vol_Store")
    if v:
        dy = -400; x = sl.x - dy * math.sin(rr); y = sl.y + dy * math.cos(rr)
        v.set_actor_location(unreal.Vector(x, y, sl.z + 150), False, False); out["moved"].append("FD_Vol_Store")
    out["store"] = [round(sl.x), round(sl.y), round(syaw, 1)]
unreal.EditorLevelLibrary.save_current_level()
json.dump(out, open(r"C:\Users\211in\Downloads\CCG_UEFN\level\relayout_out.json", "w"), indent=1)
unreal.log("CCGL relayout %d moved" % len(out["moved"]))
