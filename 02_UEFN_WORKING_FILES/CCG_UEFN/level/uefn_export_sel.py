import unreal, os
BASE = r"C:\Users\211in\Downloads\CCG_UEFN\level\export"
task = unreal.AssetExportTask()
task.set_editor_property("object", unreal.EditorLevelLibrary.get_editor_world())
task.set_editor_property("filename", os.path.join(BASE, "sel.t3d"))
task.set_editor_property("automated", True); task.set_editor_property("prompt", False); task.set_editor_property("replace_identical", True)
task.set_editor_property("selected", True)
unreal.log("CCGL export sel %s" % unreal.Exporter.run_asset_export_task(task))
