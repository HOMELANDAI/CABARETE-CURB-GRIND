import unreal, json, os, zlib, struct
BASE = r"C:\Users\211in\Downloads\CCG_UEFN\level"
G = "/9ec1b72d-2111-4319-b015-282d94c768eb"
def vn(name):
    c = zlib.crc32(name.encode("utf-32-le")) & 0xffffffff
    return "__verse_0x%08X_%s" % (struct.unpack("<I", struct.pack(">I", c))[0], name)
out = {"vn_Manager": vn("Manager")}
ss = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
def inner_objs(actor):
    res = []
    for o in unreal.ObjectIterator():
        try:
            if o.get_outer() == actor: res.append(o)
        except Exception: pass
    return res
def verse_obj(actor):
    for o in inner_objs(actor):
        n = o.get_class().get_name()
        if n.startswith("CCG-Verse-") or n.endswith("_device") or n == "creative_prop": return o
    return None
rail = None
for a in ss.get_all_level_actors():
    if a.get_actor_label() == "DEV_probe_rail": rail = a; break
out["rail_found"] = rail is not None
if rail:
    vo = verse_obj(rail); out["rail_inner"] = [(o.get_name(), o.get_class().get_name()) for o in inner_objs(rail)]
    try:
        vo.set_editor_property(vn("RailId"), "zzprobe"); vo.set_editor_property(vn("RideHeightCm"), 97.0); vo.set_editor_property(vn("IsSteel"), False)
        out["set_prims"] = [str(vo.get_editor_property(vn("RailId"))), str(vo.get_editor_property(vn("RideHeightCm"))), str(vo.get_editor_property(vn("IsSteel")))]
    except Exception as e: out["set_prims_err"] = str(e)[:300]
    try: out["railpoints_cur"] = repr(vo.get_editor_property(vn("RailPoints")))[:300]
    except Exception as e: out["railpoints_err"] = str(e)[:300]
    try:
        vo.set_editor_property(vn("RailPoints"), [unreal.Vector(1, 2, 3), unreal.Vector(4, 5, 6)]); out["railpoints_set"] = repr(vo.get_editor_property(vn("RailPoints")))[:300]
    except Exception as e: out["railpoints_set_err"] = str(e)[:300]
    # volume device
    try:
        VC = unreal.load_class(None, "/CRD_Volume/Device_Volume.Device_Volume_C"); out["volcls"] = VC.get_path_name() if VC else None
        v = ss.spawn_actor_from_class(VC, unreal.Vector(0, 0, 300)); v.set_actor_label("FD_probe_vol")
        out["vol_inner"] = [(o.get_name(), o.get_class().get_name()) for o in inner_objs(v)]
        vvo = verse_obj(v); out["vol_verse_obj"] = vvo.get_path_name() if vvo else None
        try: vo.set_editor_property(vn("CatchVolume"), vvo); out["catch_set_obj"] = str(vo.get_editor_property(vn("CatchVolume")))
        except Exception as e: out["catch_set_obj_err"] = str(e)[:300]
        try: vo.set_editor_property(vn("CatchVolume"), v); out["catch_set_actor"] = str(vo.get_editor_property(vn("CatchVolume")))
        except Exception as e: out["catch_set_actor_err"] = str(e)[:300]
    except Exception as e: out["vol_err"] = str(e)[:300]
    # creative prop
    for a in ss.get_all_level_actors():
        if a.get_actor_label() == "L_Billboard_1":
            out["sm_inner"] = [(o.get_name(), o.get_class().get_name()) for o in inner_objs(a)]
            po = verse_obj(a)
            try: vo.set_editor_property(vn("RailMesh"), po if po else a); out["railmesh_set"] = str(vo.get_editor_property(vn("RailMesh")))
            except Exception as e: out["railmesh_set_err"] = str(e)[:300]
            break
    # manager ref
    for a in ss.get_all_level_actors():
        if a.get_actor_label() == "DEV_ccg_game_manager":
            mo = verse_obj(a)
            try: vo.set_editor_property(vn("Manager"), mo); out["manager_set"] = str(vo.get_editor_property(vn("Manager")))
            except Exception as e: out["manager_set_err"] = str(e)[:300]
            break
json.dump(out, open(os.path.join(BASE, "probe7.json"), "w"), indent=1, default=str)
unreal.log("CCGL probe7 written")
