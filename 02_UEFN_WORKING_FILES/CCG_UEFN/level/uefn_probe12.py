import unreal, json, os, zlib, struct
BASE = r"C:\Users\211in\Downloads\CCG_UEFN\level"
def vn(name):
    c = zlib.crc32(name.encode("utf-32-le")) & 0xffffffff
    return "__verse_0x%08X_%s" % (struct.unpack("<I", struct.pack(">I", c))[0], name)
out = {}
ss = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
vo = None
for a in ss.get_all_level_actors():
    if a.get_actor_label() == "DEV_probe_rail":
        for o in unreal.ObjectIterator():
            try:
                if o.get_outer() == a and o.get_class().get_name() == "CCG-Verse-ccg_rail": vo = o; break
            except Exception: pass
        break
P = vn("RailPoints")
pts = [(100, 200, 300), (400, 500, 600), (700, 800, 900)]
arr = vo.get_editor_property(P)
arr.resize(len(pts))
out["after_resize"] = len(arr)
for i, (x, y, z) in enumerate(pts):
    e = arr[i].copy()
    ok = e.import_text("(%s=%f,%s=%f,%s=%f)" % (vn("X"), x, vn("Y"), y, vn("Z"), z))
    arr[i] = e
    out["imp_%d" % i] = (ok, e.export_text())
vo.set_editor_property(P, arr)
out["readback"] = [e.export_text() for e in vo.get_editor_property(P)]
json.dump(out, open(os.path.join(BASE, "probe12.json"), "w"), indent=1, default=str)
unreal.log("CCGL probe12 written")
