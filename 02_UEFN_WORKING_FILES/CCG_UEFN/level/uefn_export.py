import unreal, os
BASE = r"C:\Users\211in\Downloads\CCG_UEFN\level\export"
G = "/9ec1b72d-2111-4319-b015-282d94c768eb"
# place one rail device, set nothing, export the whole level to T3D so we can read the real Verse property names
ss = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
vc = unreal.load_object(None, G + "/_Verse.CCG-Verse-ccg_rail")
a = ss.spawn_actor_from_object(vc, unreal.Vector(0, 0, 200)); a.set_actor_label("DEV_probe_rail")
task = unreal.AssetExportTask()
task.set_editor_property("object", unreal.EditorLevelLibrary.get_editor_world())
task.set_editor_property("filename", os.path.join(BASE, "level.t3d"))
task.set_editor_property("automated", True); task.set_editor_property("prompt", False); task.set_editor_property("replace_identical", True)
task.set_editor_property("selected", False)
ok = unreal.Exporter.run_asset_export_task(task)
unreal.log("CCGL export %s" % ok)
