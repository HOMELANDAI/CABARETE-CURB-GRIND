
import unreal, os, json
BASE = r"C:\Users\211in\Downloads\CCG_UEFN\level"
ss = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
ALL = {a.get_actor_label(): a for a in ss.get_all_level_actors()}
NAMES = ["Kefla", "Koda the Husky", "Crash the Collie", "Yara", "Sunny", "Rubi", "Kai"]
out = {"designers": {}, "selectors": {}, "errors": [], "hud": {}}
def set_slot(a, prop, slot):
    ci = a.get_editor_property(prop); c2 = ci.copy()
    c2.set_editor_property("class_slot", slot)
    try: c2.set_editor_property("class_type", type(ci.get_editor_property("class_type")).CLASS_SLOT)
    except Exception: pass
    a.modify(); a.set_editor_property(prop, c2)
    return int(a.get_editor_property(prop).get_editor_property("class_slot"))
for i in range(7):
    d = ALL.get("FD_Class_%d" % i); s = ALL.get("FD_ClassSel_%d" % i)
    if d:
        try:
            out["designers"][i] = set_slot(d, "ClassIdentifier", i + 1)
            # class name (component-scoped text)
            done = False
            for c in d.get_components_by_class(unreal.ActorComponent):
                if "PlayerClassSettings" in c.get_class().get_name():
                    try: c.set_editor_property("ClassName", unreal.Text(NAMES[i])); done = True
                    except Exception as e: out["errors"].append(("classname", i, str(e)[:80]))
            if not done:
                try: d.set_editor_property("ClassName", unreal.Text(NAMES[i])); done = True
                except Exception as e: out["errors"].append(("classname_actor", i, str(e)[:80]))
            out["designers"]["name_%d" % i] = done
        except Exception as e: out["errors"].append(("designer", i, str(e)[:100]))
    if s:
        for prop in ("ClassToSwitchTo",):
            try: out["selectors"][i] = set_slot(s, prop, i + 1)
            except Exception as e: out["errors"].append(("selector", i, prop, str(e)[:100]))
# HUD: a bit bigger text, top-center placement is default-ish; just size
h = ALL.get("FD_HUD")
if h:
    for p, v in (("Size", 22), ("DisplayTime", 4.0)):
        try: h.set_editor_property(p, v); out["hud"][p] = "ok"
        except Exception as e: out["hud"][p] = str(e)[:80]
json.dump(out, open(os.path.join(BASE, "class_out.json"), "w"), indent=1)
unreal.log("CCGL classes fixed: %s" % out)
