
import unreal
ROOT = "/9ec1b72d-2111-4319-b015-282d94c768eb/CCG"
AT = unreal.AssetToolsHelpers.get_asset_tools(); MEL = unreal.MaterialEditingLibrary; EAL = unreal.EditorAssetLibrary
log = []
# --- master rider material: BC / N / ORM parameters
mpath = f"{ROOT}/Materials/M_CCG_Rider"
if EAL.does_asset_exist(mpath): mat = EAL.load_asset(mpath)
else: mat = AT.create_asset("M_CCG_Rider", f"{ROOT}/Materials", unreal.Material, unreal.MaterialFactoryNew())
def texparam(name, tex, x, y, sampler=None):
    n = MEL.create_material_expression(mat, unreal.MaterialExpressionTextureSampleParameter2D, x, y)
    n.set_editor_property('parameter_name', name); n.set_editor_property('texture', tex)
    if sampler: n.set_editor_property('sampler_type', sampler)
    return n
kef = {k: EAL.load_asset(f"{ROOT}/Riders/Kefla/T_Kefla_{k}") for k in ("BC", "N", "ORM")}
bc = texparam("BaseColor", kef["BC"], -600, -300)
nm = texparam("Normal", kef["N"], -600, 100, unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL)
orm = texparam("ORM", kef["ORM"], -600, 400, unreal.MaterialSamplerType.SAMPLERTYPE_LINEAR_COLOR)
MEL.connect_material_property(bc, "RGB", unreal.MaterialProperty.MP_BASE_COLOR)
MEL.connect_material_property(nm, "RGB", unreal.MaterialProperty.MP_NORMAL)
MEL.connect_material_property(orm, "R", unreal.MaterialProperty.MP_AMBIENT_OCCLUSION)
MEL.connect_material_property(orm, "G", unreal.MaterialProperty.MP_ROUGHNESS)
MEL.connect_material_property(orm, "B", unreal.MaterialProperty.MP_METALLIC)
MEL.recompile_material(mat); EAL.save_loaded_asset(mat); log.append("M_CCG_Rider ok")
# --- instances per rider + assign to the skeletal meshes
for N in ("Kefla", "Koda", "Crash"):
    ipath = f"{ROOT}/Riders/{N}/MI_{N}"
    mi = EAL.load_asset(ipath) if EAL.does_asset_exist(ipath) else AT.create_asset(f"MI_{N}", f"{ROOT}/Riders/{N}", unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    MEL.set_material_instance_parent(mi, mat)
    for k in ("BC", "N", "ORM"):
        MEL.set_material_instance_texture_parameter_value(mi, {"BC": "BaseColor", "N": "Normal", "ORM": "ORM"}[k], EAL.load_asset(f"{ROOT}/Riders/{N}/T_{N}_{k}"))
    MEL.update_material_instance(mi); EAL.save_loaded_asset(mi)
    sk = EAL.load_asset(f"{ROOT}/Riders/{N}/SK_{N}")
    mats = list(sk.get_editor_property('materials'))
    for i in range(len(mats)):
        mats[i] = unreal.SkeletalMaterial(material_interface=mi, material_slot_name=mats[i].get_editor_property('material_slot_name'))
    sk.set_editor_property('materials', mats); EAL.save_loaded_asset(sk)
    log.append(f"{N}: MI assigned to {len(mats)} slot(s)")
open(r"C:\Users\211in\Downloads\CCG_UEFN\mat_log.txt", "w").write("\n".join(log))
unreal.log("CCG_MAT_DONE")
