
import unreal, os, re
BASE = r"C:\Users\211in\Downloads\CCG_UEFN\level"
pat = open(os.path.join(BASE, "sel_pattern.txt")).read().strip()
rx = re.compile(pat)
ss = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
hits = [a for a in ss.get_all_level_actors() if rx.match(a.get_actor_label())]
ss.set_selected_level_actors(hits)
unreal.log("CCGL selected %d actors for /%s/: %s" % (len(hits), pat, ", ".join(a.get_actor_label() for a in hits[:12])))
