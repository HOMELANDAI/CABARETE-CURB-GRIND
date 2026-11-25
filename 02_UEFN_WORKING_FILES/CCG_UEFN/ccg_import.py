
import unreal, os, json
SRC = r"C:\Users\211in\Downloads\CCG_UEFN\uefn\assets"
ROOT = "/9ec1b72d-2111-4319-b015-282d94c768eb/CCG"
log = []
def imp_textures(folder, dest, names=None):
    tasks = []
    for f in sorted(os.listdir(folder)):
        if not f.lower().endswith('.png'): continue
        if names and f not in names: continue
        t = unreal.AssetImportTask()
        t.filename = os.path.join(folder, f); t.destination_path = dest
        t.automated = True; t.replace_existing = True; t.save = True
        tasks.append(t)
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)
    done = [p for t in tasks for p in list(t.imported_object_paths)]
    log.append(f"{dest}: {len(done)} textures")
    return done
def fix_tex(dest):
    reg = unreal.AssetRegistryHelpers.get_asset_registry()
    for a in reg.get_assets_by_path(dest, recursive=False):
        o = a.get_asset()
        if not isinstance(o, unreal.Texture2D): continue
        n = o.get_name()
        if n.endswith('_N'):
            o.set_editor_property('srgb', False); o.set_editor_property('compression_settings', unreal.TextureCompressionSettings.TC_NORMALMAP)
        elif n.endswith(('_ORM', '_SMR', '_Mask', '_H', '_R', '_M', '_AO')):
            o.set_editor_property('srgb', False); o.set_editor_property('compression_settings', unreal.TextureCompressionSettings.TC_MASKS)
        unreal.EditorAssetLibrary.save_loaded_asset(o)
def imp_fbx(path, dest, skeletal=True):
    t = unreal.AssetImportTask(); t.filename = path; t.destination_path = dest; t.automated = True; t.replace_existing = True; t.save = True
    ui = unreal.FbxImportUI()
    ui.import_mesh = True; ui.import_as_skeletal = skeletal; ui.import_animations = skeletal; ui.import_materials = False; ui.import_textures = False
    ui.mesh_type_to_import = unreal.FBXImportType.FBXIT_SKELETAL_MESH if skeletal else unreal.FBXImportType.FBXIT_STATIC_MESH
    if skeletal:
        ui.skeletal_mesh_import_data.set_editor_property('import_morph_targets', False)
        ui.skeletal_mesh_import_data.set_editor_property('normal_import_method', unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS_AND_TANGENTS)
        ui.anim_sequence_import_data.set_editor_property('import_bone_tracks', True)
    t.options = ui
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([t])
    log.append(f"{os.path.basename(path)} -> {list(t.imported_object_paths)}")
for N in ("Kefla", "Koda", "Crash"):
    d = f"{ROOT}/Riders/{N}"
    imp_textures(os.path.join(SRC, "riders", N), d, names={f"T_{N}_BC.png", f"T_{N}_N.png", f"T_{N}_ORM.png", f"T_{N}_SMR.png"})
    fix_tex(d)
    imp_fbx(os.path.join(SRC, "riders", N, f"SK_{N}.fbx"), d, True)
imp_textures(os.path.join(SRC, "materials"), f"{ROOT}/Materials"); fix_tex(f"{ROOT}/Materials")
imp_textures(os.path.join(SRC, "signs"), f"{ROOT}/Signs"); fix_tex(f"{ROOT}/Signs")
imp_textures(os.path.join(SRC, "murals"), f"{ROOT}/Murals"); fix_tex(f"{ROOT}/Murals")
unreal.EditorAssetLibrary.save_directory(ROOT, only_if_is_dirty=False, recursive=True)
open(r"C:\Users\211in\Downloads\CCG_UEFN\import_log.txt", "w").write("\n".join(log))
unreal.log("CCG_IMPORT_DONE " + str(len(log)))
