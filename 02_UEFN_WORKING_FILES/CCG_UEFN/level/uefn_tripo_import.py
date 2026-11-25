# exec(open(r'C:/Users/211in/Downloads/CCG_UEFN/level/uefn_tripo_import.py').read())
import unreal, os, json, glob, traceback
SRC = os.environ.get("CCG_SRC", r"C:\Users\211in\Downloads")
G = "/9ec1b72d-2111-4319-b015-282d94c768eb/CCG"
EAL = unreal.EditorAssetLibrary; AT = unreal.AssetToolsHelpers.get_asset_tools()
out = {"imported": {}, "errors": []}
files = sorted(glob.glob(os.path.join(SRC, "CCG_*.glb")))
only = os.environ.get("CCG_ONLY")
if only: files = [f for f in files if os.path.basename(f)[:-4] in only.split(",")]
for f in files:
    name = os.path.basename(f)[:-4]
    dest = f"{G}/Tripo/{name}"
    try:
        t = unreal.AssetImportTask(); t.filename = f; t.destination_path = dest
        t.automated = True; t.replace_existing = True; t.save = True
        AT.import_asset_tasks([t])
        paths = [str(p) for p in list(t.imported_object_paths)]
        meshes = []
        for p in paths:
            o = EAL.load_asset(p)
            if isinstance(o, unreal.StaticMesh):
                try:
                    ns = o.get_editor_property("nanite_settings"); ns.enabled = True; o.set_editor_property("nanite_settings", ns)
                except Exception as e: out["errors"].append(f"{name} nanite {e}")
                b = o.get_bounds(); e = b.box_extent
                meshes.append({"path": p, "extent": [e.x, e.y, e.z], "origin": [b.origin.x, b.origin.y, b.origin.z], "mats": [str(m.material_interface.get_path_name()) if m.material_interface else None for m in o.static_materials], "tris": o.get_num_triangles(0)})
                EAL.save_loaded_asset(o)
        out["imported"][name] = {"paths": paths, "meshes": meshes}
    except Exception:
        out["errors"].append(f"{name}: {traceback.format_exc()}")
json.dump(out, open(r"C:\Users\211in\Downloads\CCG_UEFN\level\tripo_import.json", "w"), indent=1)
unreal.log("CCG_TRIPO_IMPORT_DONE " + str(len(out["imported"])) + " err " + str(len(out["errors"])))
