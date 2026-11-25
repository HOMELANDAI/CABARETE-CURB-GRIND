# UEFN Python console:  exec(open(r'C:/Users/211in/Downloads/CCG_UEFN/level/uefn_lvl_import.py').read())
# Stage 1: import the level meshes, build the environment / sign / mural materials, assign per slot.
import unreal, os, json, zipfile, traceback
BASE = r"C:\Users\211in\Downloads\CCG_UEFN\level"
LOG = open(os.path.join(BASE, "log_import.txt"), "w")
def log(*a):
    s = " ".join(str(x) for x in a); LOG.write(s + "\n"); LOG.flush(); unreal.log("CCGL " + s)
G = "/9ec1b72d-2111-4319-b015-282d94c768eb/CCG"
EAL = unreal.EditorAssetLibrary; MEL = unreal.MaterialEditingLibrary; AT = unreal.AssetToolsHelpers.get_asset_tools()
try:
    z = os.path.join(BASE, "ccg_level_meshes.zip")
    if os.path.exists(z) and not os.path.isdir(os.path.join(BASE, "meshes")):
        zipfile.ZipFile(z).extractall(BASE)
    P = json.load(open(os.path.join(BASE, "placements.json")))
    # ---------------- import static meshes
    tasks = []
    for name, info in P["meshes"].items():
        t = unreal.AssetImportTask(); t.filename = os.path.join(BASE, "meshes", info["file"]); t.destination_path = f"{G}/Level/Meshes"
        t.automated = True; t.replace_existing = True; t.save = True
        ui = unreal.FbxImportUI(); ui.import_mesh = True; ui.import_as_skeletal = False; ui.import_animations = False; ui.import_materials = False; ui.import_textures = False
        ui.mesh_type_to_import = unreal.FBXImportType.FBXIT_STATIC_MESH
        ui.static_mesh_import_data.set_editor_property("combine_meshes", True)
        ui.static_mesh_import_data.set_editor_property("generate_lightmap_u_vs", True)
        ui.static_mesh_import_data.set_editor_property("auto_generate_collision", True)
        ui.static_mesh_import_data.set_editor_property("normal_import_method", unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS)
        t.options = ui; tasks.append(t)
    AT.import_asset_tasks(tasks)
    imported = {}
    for t in tasks:
        for p in list(t.imported_object_paths): imported[os.path.basename(str(p)).split(".")[0]] = str(p)
    log("imported meshes", len(imported), "of", len(tasks))
    # ---------------- master env material (BaseColor / Normal / ORM + Tiling + Tint + Emissive)
    mpath = f"{G}/Materials/M_CCG_Env"
    if EAL.does_asset_exist(mpath): mat = EAL.load_asset(mpath); MEL.delete_all_material_expressions(mat)
    else: mat = AT.create_asset("M_CCG_Env", f"{G}/Materials", unreal.Material, unreal.MaterialFactoryNew())
    mat.set_editor_property("two_sided", True)
    def tp(name, tex, x, y, sampler):
        n = MEL.create_material_expression(mat, unreal.MaterialExpressionTextureSampleParameter2D, x, y)
        n.set_editor_property("parameter_name", name); n.set_editor_property("texture", tex); n.set_editor_property("sampler_type", sampler); return n
    asph = {k: EAL.load_asset(f"{G}/Materials/T_Asphalt_Hwy5_{k}") for k in ("BC", "N", "ORM")}
    tc = MEL.create_material_expression(mat, unreal.MaterialExpressionTextureCoordinate, -1100, 0)
    til = MEL.create_material_expression(mat, unreal.MaterialExpressionScalarParameter, -1100, 150); til.set_editor_property("parameter_name", "Tiling"); til.set_editor_property("default_value", 1.0)
    mul = MEL.create_material_expression(mat, unreal.MaterialExpressionMultiply, -900, 50)
    MEL.connect_material_expressions(tc, "", mul, "A"); MEL.connect_material_expressions(til, "", mul, "B")
    bc = tp("BaseColor", asph["BC"], -600, -300, unreal.MaterialSamplerType.SAMPLERTYPE_COLOR)
    nm = tp("Normal", asph["N"], -600, 100, unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL)
    orm = tp("ORM", asph["ORM"], -600, 400, unreal.MaterialSamplerType.SAMPLERTYPE_MASKS)
    for n in (bc, nm, orm): MEL.connect_material_expressions(mul, "", n, "UVs")
    tint = MEL.create_material_expression(mat, unreal.MaterialExpressionVectorParameter, -600, -550); tint.set_editor_property("parameter_name", "Tint"); tint.set_editor_property("default_value", unreal.LinearColor(1, 1, 1, 1))
    mul2 = MEL.create_material_expression(mat, unreal.MaterialExpressionMultiply, -300, -350)
    MEL.connect_material_expressions(bc, "RGB", mul2, "A"); MEL.connect_material_expressions(tint, "", mul2, "B")
    MEL.connect_material_property(mul2, "", unreal.MaterialProperty.MP_BASE_COLOR)
    MEL.connect_material_property(nm, "RGB", unreal.MaterialProperty.MP_NORMAL)
    MEL.connect_material_property(orm, "R", unreal.MaterialProperty.MP_AMBIENT_OCCLUSION)
    rs = MEL.create_material_expression(mat, unreal.MaterialExpressionScalarParameter, -300, 500); rs.set_editor_property("parameter_name", "RoughnessScale"); rs.set_editor_property("default_value", 1.0)
    mul3 = MEL.create_material_expression(mat, unreal.MaterialExpressionMultiply, -100, 450)
    MEL.connect_material_expressions(orm, "G", mul3, "A"); MEL.connect_material_expressions(rs, "", mul3, "B")
    MEL.connect_material_property(mul3, "", unreal.MaterialProperty.MP_ROUGHNESS)
    MEL.connect_material_property(orm, "B", unreal.MaterialProperty.MP_METALLIC)
    em = tp("Emissive", EAL.load_asset(f"{G}/Signs/T_Sign_HAI_Skate_Neon_E"), -600, 700, unreal.MaterialSamplerType.SAMPLERTYPE_COLOR)
    es = MEL.create_material_expression(mat, unreal.MaterialExpressionScalarParameter, -300, 800); es.set_editor_property("parameter_name", "EmissiveStrength"); es.set_editor_property("default_value", 0.0)
    mul4 = MEL.create_material_expression(mat, unreal.MaterialExpressionMultiply, -100, 750)
    MEL.connect_material_expressions(em, "RGB", mul4, "A"); MEL.connect_material_expressions(es, "", mul4, "B")
    MEL.connect_material_property(mul4, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    MEL.recompile_material(mat); EAL.save_loaded_asset(mat); log("M_CCG_Env built")
    # ---------------- instances
    def mi(name, bcp=None, np=None, ormp=None, tiling=1.0, tint=None, emis=None, estr=0.0, rough=1.0):
        path = f"{G}/Materials/MI/{name}"
        m = EAL.load_asset(path) if EAL.does_asset_exist(path) else AT.create_asset(name, f"{G}/Materials/MI", unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
        MEL.set_material_instance_parent(m, mat)
        for pn, tp_ in (("BaseColor", bcp), ("Normal", np), ("ORM", ormp), ("Emissive", emis)):
            if tp_ and EAL.does_asset_exist(tp_): MEL.set_material_instance_texture_parameter_value(m, pn, EAL.load_asset(tp_))
        MEL.set_material_instance_scalar_parameter_value(m, "Tiling", tiling)
        MEL.set_material_instance_scalar_parameter_value(m, "EmissiveStrength", estr)
        MEL.set_material_instance_scalar_parameter_value(m, "RoughnessScale", rough)
        if tint: MEL.set_material_instance_vector_parameter_value(m, "Tint", unreal.LinearColor(*tint))
        MEL.update_material_instance(m); EAL.save_loaded_asset(m); return m
    def envset(name, tex, tiling, tint=None, rough=1.0):
        return mi(name, f"{G}/Materials/T_{tex}_BC", f"{G}/Materials/T_{tex}_N", f"{G}/Materials/T_{tex}_ORM", tiling, tint, None, 0.0, rough)
    # UV: the meshes already carry metre-scaled UVs (1 UV unit = tile size from the manifest), so Tiling 1.
    MIS = {}
    MIS["M_Asphalt"] = envset("MI_Asphalt", "Asphalt_Hwy5", 1.0)
    MIS["M_Concrete"] = envset("MI_Concrete", "Concrete_Park", 1.0)
    MIS["M_Pavers"] = envset("MI_Pavers", "Pavers_Adoquin", 1.0)
    MIS["M_Sand"] = envset("MI_Sand", "Sand_Cabarete", 1.0)
    MIS["M_Dirt"] = envset("MI_Dirt", "Sand_Cabarete", 1.0, (0.55, 0.45, 0.35, 1))
    MIS["M_Grass"] = envset("MI_Grass", "Sand_Cabarete", 1.0, (0.35, 0.7, 0.25, 1))
    MIS["M_Stucco"] = envset("MI_Stucco", "Stucco_White", 1.0)
    MIS["M_Roof"] = envset("MI_Roof", "Roof_Corrugated", 1.0, (0.75, 0.35, 0.3, 1))
    MIS["M_Wood"] = envset("MI_Wood", "Wood_Deck", 1.0)
    MIS["M_Trunk"] = envset("MI_Trunk", "Wood_Deck", 1.0, (0.6, 0.45, 0.3, 1))
    MIS["M_Steel"] = envset("MI_Steel", "Steel_Rail", 1.0)
    MIS["M_WallPaint"] = envset("MI_WallPaint", "WallPaint", 1.0)
    MIS["M_Palm"] = envset("MI_Palm", "Sand_Cabarete", 1.0, (0.15, 0.5, 0.12, 1))
    MIS["M_Letters"] = envset("MI_Letters", "Stucco_White", 1.0, (0.9, 0.15, 0.08, 1), 0.5)
    MIS["M_Glass"] = envset("MI_Glass", "Stucco_White", 1.0, (0.2, 0.35, 0.45, 1), 0.15)
    MIS["M_Black"] = envset("MI_Black", "Steel_Rail", 1.0, (0.05, 0.05, 0.05, 1))
    MIS["M_Sea"] = envset("MI_Sea", "Sand_Cabarete", 0.1, (0.03, 0.3, 0.45, 1), 0.08)
    MIS["M_Graffiti"] = mi("MI_Graffiti", f"{G}/Signs/T_Sign_HAI_Store_Square_BC", f"{G}/Materials/T_WallPaint_N", f"{G}/Materials/T_WallPaint_ORM", 1.0)
    # signs: one MI per sign texture (BC + E where present)
    reg = unreal.AssetRegistryHelpers.get_asset_registry()
    SIGNS = {}
    for a in reg.get_assets_by_path(f"{G}/Signs", recursive=False):
        n = str(a.asset_name)
        if n.endswith("_BC"):
            key = n[len("T_Sign_"):-3]
            e = f"{G}/Signs/T_Sign_{key}_E"
            SIGNS[key] = mi(f"MI_Sign_{key}", f"{G}/Signs/{n}", f"{G}/Materials/T_WallPaint_N", f"{G}/Materials/T_WallPaint_ORM", 1.0, None, e if EAL.does_asset_exist(e) else None, 3.0 if EAL.does_asset_exist(e) else 0.0)
    MIS["M_Sign_HAI_Skate_Neon"] = SIGNS.get("HAI_Skate_Neon"); MIS["M_Sign_HAI_Store_Square"] = SIGNS.get("HAI_Store_Square"); MIS["M_Sign_Puente_Starlight"] = SIGNS.get("Puente_Starlight")
    MIS["M_SignFace"] = SIGNS.get("Cabarete_Letters")
    for a in reg.get_assets_by_path(f"{G}/Murals", recursive=False):
        n = str(a.asset_name)  # T_Mural_mural_x_BC
        key = n[len("T_Mural_"):-3]
        MIS[f"M_{key}"] = mi(f"MI_{key}", f"{G}/Murals/{n}", f"{G}/Materials/T_WallPaint_N", f"{G}/Materials/T_WallPaint_ORM", 1.0)
    log("materials", len(MIS), "signs", len(SIGNS))
    # ---------------- assign per slot
    for name, info in P["meshes"].items():
        path = imported.get(name) or f"{G}/Level/Meshes/{name}.{name}"
        sm = EAL.load_asset(path.split(".")[0]) if not EAL.does_asset_exist(path.split(".")[0]) is False else EAL.load_asset(path.split(".")[0])
        if not sm: log("MISSING", name); continue
        mats = list(sm.get_editor_property("static_materials"))
        for i, sm_ in enumerate(mats):
            slot = str(sm_.get_editor_property("material_slot_name")) or (info["materials"][i] if i < len(info["materials"]) else "")
            m = MIS.get(slot) or (MIS.get(info["materials"][i]) if i < len(info["materials"]) else None)
            if m: mats[i] = unreal.StaticMaterial(material_interface=m, material_slot_name=sm_.get_editor_property("material_slot_name"))
            else: log("no material for slot", name, slot)
        sm.set_editor_property("static_materials", mats); EAL.save_loaded_asset(sm)
    json.dump({"signs": sorted(SIGNS.keys())}, open(os.path.join(BASE, "signs.json"), "w"))
    log("DONE_IMPORT")
except Exception:
    log("ERROR", traceback.format_exc())
LOG.close()
