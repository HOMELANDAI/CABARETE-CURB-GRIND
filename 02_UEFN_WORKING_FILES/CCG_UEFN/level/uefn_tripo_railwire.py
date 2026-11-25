# exec(open(r'C:/Users/211in/Downloads/CCG_UEFN/level/uefn_tripo_railwire.py').read())
# Registers the Tripo steel rail (TR_Rail) with the grind system: a ccg_rail Verse device with world-space
# RailPoints along the rail top, its catch volume, and a spark VFX spawner (same recipe as uefn_lvl_place2.py).
import unreal, math, json, zlib, struct, traceback
G = "/9ec1b72d-2111-4319-b015-282d94c768eb"
ss = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
out = {"done": [], "fails": []}
def vn(name):
    c = zlib.crc32(name.encode("utf-32-le")) & 0xffffffff
    return "__verse_0x%08X_%s" % (struct.unpack("<I", struct.pack(">I", c))[0], name)
try:
    ALL = {a.get_actor_label(): a for a in ss.get_all_level_actors()}
    for l in ("DEV_rail_tripo_rail", "FD_Catch_tripo_rail", "FD_Sparks_tripo_rail"):
        if l in ALL: ss.destroy_actor(ALL[l])
    ALL = {a.get_actor_label(): a for a in ss.get_all_level_actors()}
    rail = ALL["TR_Rail"]; GM = ALL["DEV_ccg_game_manager"]; GR = ALL["DEV_ccg_graphics"]
    o, e = rail.get_actor_bounds(False); yaw = rail.get_actor_rotation().yaw
    # long axis = the rail actor's right vector (mesh long axis is local Y, placed with yaw+90)
    rv = rail.get_actor_right_vector(); fv = rail.get_actor_forward_vector()
    L = 2.0 * max(e.x, e.y) * 0.92          # bounds are axis-aligned; the long side is the rail length
    # pick the horizontal direction of the long side by projecting the bounds extents
    dirs = [(abs(rv.x) * e.x + abs(rv.y) * e.y, rv), (abs(fv.x) * e.x + abs(fv.y) * e.y, fv)]
    d = max(dirs, key=lambda t: t[0])[1]
    top_z = o.z + e.z - 4.0
    n = 9; pts = []
    for i in range(n):
        t = -0.5 + i / (n - 1.0)
        pts.append([o.x + d.x * L * t, o.y + d.y * L * t, top_z])
    # start the path at the end nearest the spawn so the catch volume sits on the approach side
    sp_ = ALL.get("Spawn_Start"); spl = sp_.get_actor_location() if sp_ else unreal.Vector(-1076.1, -531.1, 106)
    if math.dist(pts[-1][:2], (spl.x, spl.y)) < math.dist(pts[0][:2], (spl.x, spl.y)):
        pts.reverse(); d = unreal.Vector(-d.x, -d.y, 0.0)
    ryaw = math.degrees(math.atan2(d.y, d.x))
    dev = ss.spawn_actor_from_object(unreal.load_object(None, f"{G}/_Verse.CCG-Verse-ccg_rail"), unreal.Vector(pts[0][0], pts[0][1], pts[0][2] - 60), unreal.Rotator(0, 0, ryaw))
    dev.set_actor_label("DEV_rail_tripo_rail")
    volc = unreal.load_class(None, "/CRD_Volume/Device_Volume.Device_Volume_C")
    cl = min(300.0, max(150.0, L))
    cv = ss.spawn_actor_from_class(volc, unreal.Vector(pts[0][0] + d.x * cl / 2, pts[0][1] + d.y * cl / 2, pts[0][2] + 20), unreal.Rotator(0, 0, ryaw))
    cv.set_actor_label("FD_Catch_tripo_rail"); cv.set_actor_scale3d(unreal.Vector(cl / 100.0, 1.2, 1.6))
    fxc = unreal.load_class(None, "/CRD_VFX_Spawner/Device_VFXSpawner_V2.Device_VFXSpawner_V2_C")
    fx = ss.spawn_actor_from_class(fxc, unreal.Vector(pts[0][0], pts[0][1], pts[0][2]), unreal.Rotator(0, 0, ryaw)); fx.set_actor_label("FD_Sparks_tripo_rail")
    # match the other spark spawners (set by uefn_setknobs.py)
    try:
        VE = type(fx.get_editor_property("Visual_Effect")); fx.set_editor_property("Visual_Effect", VE.EMBERS)
        EP = type(fx.get_editor_property("Enabled On Phase")); fx.set_editor_property("Enabled On Phase", EP.NONE)
        fx.set_editor_property("SpawnRate", 1.5); fx.set_editor_property("EnableOnReset", False)
    except Exception as ex: out["fails"].append(("fx knobs", str(ex)[:120]))
    # inner Verse objects
    def inner(actor, cn):
        for ob in unreal.ObjectIterator():
            try:
                if ob.get_outer() == actor and ob.get_class().get_name() == cn: return ob
            except Exception: pass
    vo = inner(dev, "CCG-Verse-ccg_rail"); gm = inner(GM, "CCG-Verse-ccg_game_manager"); gr = inner(GR, "CCG-Verse-ccg_graphics")
    def sp(name, val):
        try: vo.set_editor_property(vn(name), val); return True
        except Exception as ex: out["fails"].append((name, str(ex)[:120])); return False
    def nref(name, act):
        try: sub = vo.get_editor_property(vn(name)); sub.set_editor_property("SavedActor", act); return True
        except Exception as ex: out["fails"].append((name, str(ex)[:120])); return False
    arr = vo.get_editor_property(vn("RailPoints")); arr.resize(len(pts))
    for i, p in enumerate(pts):
        el = arr[i].copy(); el.import_text("(%s=%f,%s=%f,%s=%f)" % (vn("X"), p[0], vn("Y"), p[1], vn("Z"), p[2])); arr[i] = el
    sp("RailPoints", arr); sp("RailIndex", 200)
    sp("Manager", gm); sp("Graphics", gr); sp("UseGraphics", True)
    sp("IsSteel", True); sp("IsSlideRail", False); sp("IsHorseshoe", False); sp("RideHeightCm", 95.0)
    nref("CatchVolume", cv); nref("Sparks", fx)
    unreal.EditorLevelLibrary.save_current_level()
    out["done"] = {"pts": pts, "yaw": ryaw, "L": L}
except Exception:
    out["fails"].append(traceback.format_exc())
json.dump(out, open(r"C:\Users\211in\Downloads\CCG_UEFN\level\tripo_railwire.json", "w"), indent=1)
unreal.log("CCG_TRIPO_RAILWIRE_DONE %d fails" % len(out["fails"]))
