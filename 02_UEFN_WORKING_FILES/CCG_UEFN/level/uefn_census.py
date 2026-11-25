
import unreal, os, collections
BASE = r"C:\Users\211in\Downloads\CCG_UEFN\level"
ss = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
c = collections.Counter(); names=[]
for a in ss.get_all_level_actors():
    l=a.get_actor_label()
    if l.startswith(("FD_","DEV_","Lamp","Mural")):
        names.append(l+"\t"+a.get_class().get_name())
open(os.path.join(BASE,"census.txt"),"w").write("\n".join(sorted(names)))
unreal.log("CCGL census %d" % len(names))
