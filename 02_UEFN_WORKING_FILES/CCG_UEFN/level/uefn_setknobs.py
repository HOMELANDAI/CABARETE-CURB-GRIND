
import unreal, os, json, re
BASE = r"C:\Users\211in\Downloads\CCG_UEFN\level"
ss = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
ALL = {a.get_actor_label(): a for a in ss.get_all_level_actors()}
out = {"set": {}, "errors": [], "classes": {}, "verify": {}}
def setg(rx, props, tag):
    n = 0; rxc = re.compile(rx)
    for lbl, a in ALL.items():
        if not rxc.match(lbl): continue
        a.modify()
        for p, v in props.items():
            try: a.set_editor_property(p, v)
            except Exception as e: out["errors"].append((lbl, p, str(e)[:80]))
        n += 1
    out["set"][tag] = n
def E(a, prop):
    cls = type(a.get_editor_property(prop)); return cls
lamp0 = ALL["FD_LampLight_000"]; vfx0 = ALL["FD_Sparks_flat_33"]
C = E(lamp0, "Color"); AP = E(lamp0, "ActivateOnPhase")
out["enum_dir"] = {"C": [n for n in dir(C) if n.isupper()], "AP": [n for n in dir(AP) if n.isupper()]}
base = {"InitialState": False, "ActivateOnPhase": AP.NONE, "ColorChangeTime": 1.0}
setg(r"FD_LampLight_\d+$", dict(base, Color=C.ORANGE, BrightnessScale=0.6), "lamps")
setg(r"FD_Flood_.*$",      dict(base, Color=C.WHITE,  BrightnessScale=1.0), "floods")
setg(r"FD_MuralWash_\d+$", dict(base, Color=C.ORANGE, BrightnessScale=0.4), "mural")
setg(r"FD_SparkLight_\d+$",dict(base, Color=C.ORANGE, BrightnessScale=1.0), "sparklights")
V = E(vfx0, "Visual_Effect"); ET = E(vfx0, "EffectType"); EP = E(vfx0, "Enabled On Phase")
out["enum_dir"]["EP"] = [n for n in dir(EP) if n.isupper()]
setg(r"FD_Sparks_.*$", {"Visual_Effect": V.EMBERS, "EffectType": ET.CONTINUOUS, "Enabled On Phase": EP.NONE,
                        "Colorize VFX": False, "SpawnRate": 1.5, "EnableOnReset": False}, "sparks")
# class designers: read slot
for i in range(7):
    a = ALL.get("FD_Class_%d" % i)
    if a:
        try:
            ci = a.get_editor_property("ClassIdentifier")
            out["classes"][i] = {"slot": int(ci.get_editor_property("class_slot")), "type": str(ci.get_editor_property("class_type"))}
        except Exception as e: out["classes"][i] = "ERR " + str(e)[:80]
# verify a sample of each
for lbl in ("FD_LampLight_042", "FD_Flood_P3_2", "FD_MuralWash_4", "FD_Sparks_wave_rail", "FD_Sparks_flat_07"):
    a = ALL.get(lbl)
    if a:
        d = {}
        for p in ("Color", "InitialState", "BrightnessScale", "Visual_Effect", "Enabled On Phase", "SpawnRate"):
            try: d[p] = str(a.get_editor_property(p))[:40]
            except Exception: pass
        out["verify"][lbl] = d
json.dump(out, open(os.path.join(BASE, "knobs_out.json"), "w"), indent=1)
unreal.log("CCGL knobs applied: %s errors=%d" % (out["set"], len(out["errors"])))
