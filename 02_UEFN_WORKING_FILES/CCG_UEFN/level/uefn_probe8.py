import unreal, json, os, zlib, struct
BASE = r"C:\Users\211in\Downloads\CCG_UEFN\level"
G = "/9ec1b72d-2111-4319-b015-282d94c768eb"
def vn(name):
    c = zlib.crc32(name.encode("utf-32-le")) & 0xffffffff
    return "__verse_0x%08X_%s" % (struct.unpack("<I", struct.pack(">I", c))[0], name)
out = {}
ss = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
structs = []
for s in unreal.ObjectIterator(unreal.ScriptStruct):
    n = s.get_name()
    if "vector3" in n.lower() and len(structs) < 20: structs.append(s.get_path_name())
out["vector3_structs"] = structs
rail = None
for a in ss.get_all_level_actors():
    if a.get_actor_label() == "DEV_probe_rail": rail = a; break
vo = None
if rail:
    for o in unreal.ObjectIterator():
        try:
            if o.get_outer() == rail and o.get_class().get_name() == "CCG-Verse-ccg_rail": vo = o; break
        except Exception: pass
out["vo"] = vo.get_path_name() if vo else None
if vo:
    try: vo.set_editor_property(vn("RailIndex"), 7); out["railindex"] = str(vo.get_editor_property(vn("RailIndex")))
    except Exception as e: out["railindex_err"] = str(e)[:200]
    try: vo.set_editor_property(vn("RideHeightCm"), 97.0); out["rh"] = str(vo.get_editor_property(vn("RideHeightCm")))
    except Exception as e: out["rh_err"] = str(e)[:200]
    try: vo.set_editor_property(vn("IsSteel"), False); out["steel"] = str(vo.get_editor_property(vn("IsSteel")))
    except Exception as e: out["steel_err"] = str(e)[:200]
    cur = vo.get_editor_property(vn("RailPoints")); out["rp_type"] = str(type(cur)); out["rp_len"] = len(cur)
    # try: get element type by trying to append things
    tries = {}
    for label, val in (("Vector", unreal.Vector(1, 2, 3)), ("tuple", (1.0, 2.0, 3.0)), ("list", [1.0, 2.0, 3.0]), ("dict", {"X": 1.0, "Y": 2.0, "Z": 3.0})):
        try:
            cur2 = vo.get_editor_property(vn("RailPoints")); cur2.append(val); tries[label] = "ok len %d" % len(cur2)
            try: vo.set_editor_property(vn("RailPoints"), cur2); tries[label] += " set-ok %d" % len(vo.get_editor_property(vn("RailPoints")))
            except Exception as e: tries[label] += " set-err " + str(e)[:150]
        except Exception as e: tries[label] = "ERR " + str(e)[:200]
    out["rp_tries"] = tries
    for sp in structs:
        try:
            S = unreal.load_object(None, sp)
            T = unreal.get_type_from_struct(S); inst = T()
            out["struct_" + S.get_name()] = {"type": str(T), "dir": [d for d in dir(inst) if not d.startswith("_")][:40]}
            try:
                cur3 = vo.get_editor_property(vn("RailPoints")); cur3.append(inst); vo.set_editor_property(vn("RailPoints"), cur3)
                out["struct_" + S.get_name()]["append"] = "ok %d" % len(vo.get_editor_property(vn("RailPoints")))
            except Exception as e: out["struct_" + S.get_name()]["append_err"] = str(e)[:200]
        except Exception as e: out["struct_err_" + sp] = str(e)[:200]
json.dump(out, open(os.path.join(BASE, "probe8.json"), "w"), indent=1, default=str)
unreal.log("CCGL probe8 written")
