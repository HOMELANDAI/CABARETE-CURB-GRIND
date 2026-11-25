# exec(open(r'C:/Users/211in/Downloads/CCG_UEFN/level/uefn_tripo_tex.py').read())
import unreal, json, traceback
LOGF=open(r"C:\Users\211in\Downloads\CCG_UEFN\level\tripo_tex_log.txt","w")
try:
    G = "/9ec1b72d-2111-4319-b015-282d94c768eb/CCG/Tripo"
    reg = unreal.AssetRegistryHelpers.get_asset_registry(); EAL = unreal.EditorAssetLibrary
    out = []
    for a in reg.get_assets_by_path(G, recursive=True):
        o = a.get_asset()
        if isinstance(o, unreal.Texture2D):
            w, h = o.get_editor_property("size_x") if hasattr(o,"size_x") else o.blueprint_get_size_x(), o.get_editor_property("size_y") if hasattr(o,"size_y") else o.blueprint_get_size_y()
            n = o.get_name(); changed = False
            if max(w, h) > 4096:
                o.set_editor_property("max_texture_size", 4096); changed = True
            if n.lower().endswith(("_normal", "normal", "_n")) or "normal" in n.lower():
                o.set_editor_property("srgb", False); o.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_NORMALMAP); changed = True
            elif "metallicroughness" in n.lower() or "roughness" in n.lower() or "orm" in n.lower():
                o.set_editor_property("srgb", False); o.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_MASKS); changed = True
            if changed: EAL.save_loaded_asset(o)
            out.append([n, w, h, str(o.get_editor_property("compression_settings")), o.get_editor_property("srgb"), changed])
    json.dump(out, open(r"C:\Users\211in\Downloads\CCG_UEFN\level\tripo_tex.json", "w"), indent=1)
    unreal.log("CCG_TRIPO_TEX_DONE %d" % len(out))
except Exception:
    LOGF.write(traceback.format_exc())
LOGF.write("END\n"); LOGF.close()
