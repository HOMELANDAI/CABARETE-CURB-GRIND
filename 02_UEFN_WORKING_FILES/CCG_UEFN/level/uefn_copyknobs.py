
import unreal, os, json, re
BASE = r"C:\Users\211in\Downloads\CCG_UEFN\level"
ss = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
ALL = {a.get_actor_label(): a for a in ss.get_all_level_actors()}
out = {"probe": {}, "copied": {}, "errors": []}
def probe(a, names):
    r = {}
    for n in names:
        try:
            v = a.get_editor_property(n); r[n] = (type(v).__name__, str(v)[:60])
        except Exception as e:
            r[n] = "ERR " + str(e)[:60]
    return r
LIGHT_PROPS = ["Color", "InitialState", "BrightnessScale", "ActivateOnPhase", "ColorChangeTime", "BaseVisible"]
VFX_PROPS = ["Visual_Effect", "EffectType", "Enabled On Phase", "EnabledOnPhase", "Colorize VFX", "SpawnRate", "Sound_Effect", "EnableOnReset"]
lamp = ALL["FD_LampLight_000"]; vfx = ALL["FD_Sparks_flat_33"]
out["probe"]["lamp"] = probe(lamp, LIGHT_PROPS)
out["probe"]["vfx"] = probe(vfx, VFX_PROPS)
# generic copier: copy the listed props from src to every actor whose label matches rx; optional overrides {prop: value}
def copy_group(src, rx, props, overrides=None, tag=""):
    n = 0; rxc = re.compile(rx)
    for lbl, a in ALL.items():
        if a is src or not rxc.match(lbl): continue
        for p in props:
            try:
                v = src.get_editor_property(p)
                if overrides and p in overrides: v = overrides[p]
                a.set_editor_property(p, v)
            except Exception as e:
                out["errors"].append((lbl, p, str(e)[:80]))
        n += 1
    out["copied"][tag or rx] = n
MODE = open(os.path.join(BASE, "copy_mode.txt")).read().strip() if os.path.exists(os.path.join(BASE, "copy_mode.txt")) else "probe"
if MODE == "lights":
    ok = [p for p in LIGHT_PROPS if not str(out["probe"]["lamp"][p]).startswith("ERR")]
    copy_group(lamp, r"FD_LampLight_\d+$", ok, tag="lamps")
    copy_group(lamp, r"FD_MuralWash_\d+$", ok, {"BrightnessScale": 0.4}, tag="mural")
    copy_group(lamp, r"FD_SparkLight_\d+$", ok, {"BrightnessScale": 1.0}, tag="sparklights")
    # floods: copy from the flood template (set via UI) if present, else from the lamp with brightness 1.0
    fl = ALL.get("FD_Flood_P1_1")
    copy_group(fl, r"FD_Flood_.*$", ok, tag="floods")
if MODE == "vfx":
    ok = [p for p in VFX_PROPS if not str(out["probe"]["vfx"][p]).startswith("ERR")]
    copy_group(vfx, r"FD_Sparks_.*$", ok, tag="sparks")
# class designer slot check
cls = {}
for i in range(7):
    a = ALL.get("FD_Class_%d" % i)
    if a:
        try: cls[i] = str(a.get_editor_property("ClassIdentifier"))[:80]
        except Exception as e: cls[i] = "ERR " + str(e)[:60]
out["classes"] = cls
json.dump(out, open(os.path.join(BASE, "copy_out.json"), "w"), indent=1)
unreal.log("CCGL copy mode=%s done" % MODE)
