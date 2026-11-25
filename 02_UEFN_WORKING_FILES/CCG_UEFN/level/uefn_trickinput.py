
import unreal, zlib, struct, json, os
BASE = r"C:\Users\211in\Downloads\CCG_UEFN\level"
G = "/9ec1b72d-2111-4319-b015-282d94c768eb"
ss = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
ALL = {a.get_actor_label(): a for a in ss.get_all_level_actors()}
out = {"errors": []}
def vn(name):
    c = zlib.crc32(name.encode("utf-32-le")) & 0xffffffff
    return "__verse_0x%08X_%s" % (struct.unpack("<I", struct.pack(">I", c))[0], name)
def inner(actor, cls):
    for o in unreal.ObjectIterator():
        try:
            if o.get_outer() == actor and o.get_class().get_name() == cls: return o
        except Exception: pass
    return None
dev = ALL.get("DEV_ccg_trick_input")
if not dev:
    gm = ALL["DEV_ccg_game_manager"]; loc = gm.get_actor_location()
    dev = ss.spawn_actor_from_object(unreal.load_object(None, f"{G}/_Verse.CCG-Verse-ccg_trick_input"), unreal.Vector(loc.x, loc.y + 300, loc.z), unreal.Rotator(0, 0, 0))
    dev.set_actor_label("DEV_ccg_trick_input")
vo = inner(dev, "CCG-Verse-ccg_trick_input"); gmo = inner(ALL["DEV_ccg_game_manager"], "CCG-Verse-ccg_game_manager")
out["inner"] = bool(vo); out["gm_inner"] = bool(gmo)
try: vo.set_editor_property(vn("Manager"), gmo); out["Manager"] = "ok"
except Exception as e: out["errors"].append(("Manager", str(e)[:120]))
try:
    sub = vo.get_editor_property(vn("Hud")); sub.set_editor_property("SavedActor", ALL["FD_HUD"]); out["Hud"] = "ok"
except Exception as e: out["errors"].append(("Hud", str(e)[:120]))
for k, v in (("ComboWindowSeconds", 0.35), ("GrabHoldSeconds", 0.4), ("LateInputBailSeconds", 0.12), ("MinAirSeconds", 0.25), ("ShowControlsOnJoin", True)):
    try: vo.set_editor_property(vn(k), v)
    except Exception as e: out["errors"].append((k, str(e)[:100]))
# read back
try: out["Manager_rb"] = str(vo.get_editor_property(vn("Manager")))[:80]
except Exception as e: out["Manager_rb"] = str(e)[:80]
unreal.EditorLevelLibrary.save_current_level()
json.dump(out, open(os.path.join(BASE, "trickinput_out.json"), "w"), indent=1)
unreal.log("CCGL trick input %s" % out)
