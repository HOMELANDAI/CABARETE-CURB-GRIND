import unreal, json, os, zlib, struct
BASE = r"C:\Users\211in\Downloads\CCG_UEFN\level"
def vn(name):
    c = zlib.crc32(name.encode("utf-32-le")) & 0xffffffff
    return "__verse_0x%08X_%s" % (struct.unpack("<I", struct.pack(">I", c))[0], name)
out = {}
ss = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
T = None
def v3(x, y, z):
    i = T(); i.import_text("(%s=%f,%s=%f,%s=%f)" % (vn("X"), x, vn("Y"), y, vn("Z"), z)); return i
vo = None
for a in ss.get_all_level_actors():
    if a.get_actor_label() == "DEV_probe_rail":
        for o in unreal.ObjectIterator():
            try:
                if o.get_outer() == a and o.get_class().get_name() == "CCG-Verse-ccg_rail": vo = o; break
            except Exception: pass
        break
cur = vo.get_editor_property(vn("RailPoints"))
T = type(cur[0]); out["elem_type"] = str(T); out["elem_mod"] = str(T.__module__)
# find the struct by scanning ScriptStructs whose python type matches
for s_ in unreal.ObjectIterator(unreal.ScriptStruct):
    try:
        if unreal.get_type_from_struct(s_) is T: out["elem_struct"] = s_.get_path_name(); break
    except Exception: pass
pts = [v3(100, 200, 300), v3(400, 500, 600), v3(700, 800, 900)]
out["pts_export"] = [p.export_text() for p in pts]
vo.set_editor_property(vn("RailPoints"), pts)
out["readback"] = [e.export_text() for e in vo.get_editor_property(vn("RailPoints"))]
# also test via array append path
arr = vo.get_editor_property(vn("RailPoints")); arr.append(v3(1, 2, 3)); vo.set_editor_property(vn("RailPoints"), arr)
out["readback2"] = [e.export_text() for e in vo.get_editor_property(vn("RailPoints"))]
json.dump(out, open(os.path.join(BASE, "probe11.json"), "w"), indent=1, default=str)
unreal.log("CCGL probe11 written")
