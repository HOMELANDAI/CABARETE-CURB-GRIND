
import unreal, os, json
BASE = r"C:\Users\211in\Downloads\CCG_UEFN\level"
ss = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
a = [x for x in ss.get_all_level_actors() if x.get_actor_label()=="FD_LampLight_000"][0]
out = {}
# which object holds PlayerOptionData?
cands = [a] + list(a.get_components_by_class(unreal.ActorComponent))
for o in cands:
    try:
        v = o.get_editor_property("PlayerOptionData")
        out["owner"] = o.get_name() + " : " + o.get_class().get_name()
        out["type"] = type(v).__name__
        try: out["export"] = v.export_text()[:3000]
        except Exception as e: out["export_err"]=str(e)
        try:
            po = v.get_editor_property("PropertyOverrides")
            out["n_over"] = len(po)
            e0 = po[0]
            out["e0_type"] = type(e0).__name__
            out["e0_export"] = e0.export_text()
            # try to modify: find Color and set to Blue
            for i in range(len(po)):
                e = po[i]
                if e.get_editor_property("PropertyName") == "Color":
                    e2 = e.copy(); e2.set_editor_property("PropertyData", "Blue"); po[i] = e2
            v.set_editor_property("PropertyOverrides", po)
            o.set_editor_property("PlayerOptionData", v)
            v2 = o.get_editor_property("PlayerOptionData")
            out["after"] = [ (x.get_editor_property("PropertyName"), x.get_editor_property("PropertyData")) for x in v2.get_editor_property("PropertyOverrides") if x.get_editor_property("PropertyName") in ("Color","BrightnessScale","InitialState")]
        except Exception as e:
            out["mod_err"] = str(e)
        break
    except Exception as e:
        pass
if "owner" not in out:
    out["comps"] = [c.get_name()+":"+c.get_class().get_name() for c in cands]
json.dump(out, open(os.path.join(BASE,"probe_pod.json"),"w"), indent=1)
unreal.log("CCGL probe_pod written")
