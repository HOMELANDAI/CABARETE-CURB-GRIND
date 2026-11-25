# exec(open(r'C:/Users/211in/Downloads/CCG_UEFN/level/uefn_tripo_retex.py').read())
import unreal, os, glob, json, traceback
G = "/9ec1b72d-2111-4319-b015-282d94c768eb/CCG"
AT = unreal.AssetToolsHelpers.get_asset_tools(); EAL = unreal.EditorAssetLibrary
out = {"done": [], "err": []}
try:
    for f in sorted(glob.glob(r"C:\Users\211in\Downloads\tripo_tex4k\*.png")):
        n = os.path.basename(f)[:-4]; model = n.replace("_basecolor_jpg", "")
        dest = f"{G}/Tripo/{model}/{model}/Textures"
        t = unreal.AssetImportTask(); t.filename = f; t.destination_path = dest; t.automated = True; t.replace_existing = True; t.save = True
        AT.import_asset_tasks([t])
        for p in list(t.imported_object_paths):
            o = EAL.load_asset(str(p)); o.set_editor_property("srgb", True); o.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_DEFAULT); EAL.save_loaded_asset(o)
            out["done"].append([str(p), o.blueprint_get_size_x()])
except Exception:
    out["err"].append(traceback.format_exc())
json.dump(out, open(r"C:\Users\211in\Downloads\CCG_UEFN\level\tripo_retex.json", "w"), indent=1)
unreal.log("CCG_TRIPO_RETEX_DONE")
