import unreal, json, os, zlib, struct
BASE = r"C:\Users\211in\Downloads\CCG_UEFN\level"
def vn(name):
    c = zlib.crc32(name.encode("utf-32-le")) & 0xffffffff
    return "__verse_0x%08X_%s" % (struct.unpack("<I", struct.pack(">I", c))[0], name)
out = {}
ss = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
def inner(actor, clsname):
    for o in unreal.ObjectIterator():
        try:
            if o.get_outer() == actor and o.get_class().get_name() == clsname: return o
        except Exception: pass
rail = gm = vol = None
for a in ss.get_all_level_actors():
    l = a.get_actor_label()
    if l == "DEV_probe_rail": rail = a
    elif l == "DEV_ccg_game_manager": gm = a
    elif l == "FD_probe_vol": vol = a
vo = inner(rail, "CCG-Verse-ccg_rail"); go = inner(gm, "CCG-Verse-ccg_game_manager")
# 1. single native ref: set SavedActor on the default sub-object
cv = vo.get_editor_property(vn("CatchVolume"))
out["cv_class"] = cv.get_class().get_path_name()
try:
    cv.set_editor_property("SavedActor", vol); out["cv_saved"] = str(cv.get_editor_property("SavedActor"))
except Exception as e: out["cv_err"] = str(e)[:200]
# 2. array of native refs: new_object of the verse wrapper class
VD = unreal.load_class(None, "/CRD_Volume/_Verse.volume_device"); out["VD"] = VD.get_path_name() if VD else None
try:
    arr = go.get_editor_property(vn("MuralVolumes")); out["mv_len0"] = len(arr)
    try:
        n = unreal.new_object(VD, go)
    except Exception as e:
        out["new_object_err"] = str(e)[:200]; n = None
    if n is None:
        # fallback: duplicate the rail's CatchVolume sub-object into the manager
        n = unreal.EditorAssetLibrary.duplicate_loaded_asset(cv, "") if False else None
    if n:
        n.set_editor_property("SavedActor", vol); arr.append(n); go.set_editor_property(vn("MuralVolumes"), arr)
        out["mv_after"] = [str(e_.get_editor_property("SavedActor")) for e_ in go.get_editor_property(vn("MuralVolumes"))]
except Exception as e: out["mv_err"] = str(e)[:300]
# 3. array of verse device refs? (none in design) ; 4. int / float / logic done
json.dump(out, open(os.path.join(BASE, "probe13.json"), "w"), indent=1, default=str)
unreal.log("CCGL probe13 written")
