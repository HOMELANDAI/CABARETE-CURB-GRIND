import unreal, json, os, zlib, struct
BASE = r"C:\Users\211in\Downloads\CCG_UEFN\level"
def vn(name):
    c = zlib.crc32(name.encode("utf-32-le")) & 0xffffffff
    return "__verse_0x%08X_%s" % (struct.unpack("<I", struct.pack(">I", c))[0], name)
out = {}
ss = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
S = unreal.load_object(None, "/VerseSpatialMath/_Verse/VNI/VerseSpatialMath.SpatialMath_vector3")
T = unreal.get_type_from_struct(S)
i = T()
out["export_empty"] = i.export_text()
AX = [d for d in dir(T) if d.startswith("verse_0x") and d.endswith("_x")][0]
try:
    setattr(i, AX, 123.0); out["after_setattr"] = i.export_text(); out["getattr"] = getattr(i, AX)
except Exception as e: out["setattr_err"] = str(e)[:200]
try:
    i.set_editor_property(AX, 456.0); out["after_sep"] = i.export_text()
except Exception as e: out["sep_err"] = str(e)[:200]
for nm in (vn("X"), "X", "__verse_0x51F8FD2F_X", "verse_0x51F8FD2F_X"):
    try:
        i.set_editor_property(nm, 789.0); out["sep_" + nm] = i.export_text()
    except Exception as e: out["sep_" + nm] = "ERR " + str(e)[:120]
try:
    j = T(); j.import_text("(" + vn("X") + "=1.5," + vn("Y") + "=2.5," + vn("Z") + "=3.5)"); out["import1"] = j.export_text()
except Exception as e: out["import1_err"] = str(e)[:200]
try:
    k = T(); ok = k.import_text("(X=1.5,Y=2.5,Z=3.5)"); out["import2"] = (ok, k.export_text())
except Exception as e: out["import2_err"] = str(e)[:200]
try:
    m = T(); m.assign(unreal.Vector(7, 8, 9)); out["assign_vec"] = m.export_text()
except Exception as e: out["assign_err"] = str(e)[:200]
try:
    n = T(); n.copy(); out["to_dict"] = str(n.to_dict())
except Exception as e: out["dict_err"] = str(e)[:200]
json.dump(out, open(os.path.join(BASE, "probe10.json"), "w"), indent=1, default=str)
unreal.log("CCGL probe10 written")
