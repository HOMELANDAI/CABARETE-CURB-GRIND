
import unreal, os
BASE = r"C:\Users\211in\Downloads\CCG_UEFN\level"
ss = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
want = {"FD_LampLight_1":None,"FD_Flood_P1_1":None,"FD_Sparks_flat_1":None,"FD_Class_0":None,"FD_HUD":None,"FD_ClassSel_0":None,"FD_MuralWash_1":None}
acts = {a.get_actor_label():a for a in ss.get_all_level_actors()}
out=[]
for k in list(want):
    a = acts.get(k)
    if a is None:
        # fallback: first label starting with the stem
        stem=k.rsplit("_",1)[0]
        for l,x in acts.items():
            if l.startswith(stem): a=x; break
    if a is None: out.append("MISSING "+k); continue
    ss.set_selected_level_actors([a])
    t = unreal.AssetExportTask()
    t.object = a.get_world(); t.filename = os.path.join(BASE, "t3d_%s.t3d" % k); t.selected = True
    t.automated = True; t.replace_identical = True; t.prompt = False
    ok = unreal.Exporter.run_asset_export_task(t)
    out.append("%s %s %s" % (k, a.get_actor_label(), ok))
unreal.log("CCGL t3d: " + "; ".join(out))
