
import unreal, os, json
BASE = r"C:\Users\211in\Downloads\CCG_UEFN\level"
ss = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
a = [x for x in ss.get_all_level_actors() if x.get_actor_label() == "FD_LumenExposure"][0]
ss.set_selected_level_actors([a])
t = unreal.AssetExportTask(); t.object = a.get_world(); t.filename = os.path.join(BASE, "t3d_lumen.t3d"); t.selected = True; t.automated = True; t.replace_identical = True; t.prompt = False
unreal.Exporter.run_asset_export_task(t)
# also list candidate property names by trying common ones
cands = ["MinExposure","MaxExposure","Min Brightness","Max Brightness","MinBrightness","ExposureMin","ExposureMax","Min","Max","HistogramMin","HistogramMax","Histogram Low","Histogram High","Speed Up","Speed Down","Compensation","Exposure Compensation","Bias","AutoExposureBias","LowPercent","HighPercent"]
ok = {}
for n in cands:
    try: ok[n] = str(a.get_editor_property(n))[:40]
    except Exception: pass
json.dump({"ok": ok, "cls": a.get_class().get_name()}, open(os.path.join(BASE, "lumen_probe.json"), "w"))
