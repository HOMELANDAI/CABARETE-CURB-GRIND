
import unreal
ROOT = "/9ec1b72d-2111-4319-b015-282d94c768eb/CCG"
EAL = unreal.EditorAssetLibrary; MEL = unreal.MaterialEditingLibrary
mat = EAL.load_asset(f"{ROOT}/Materials/M_CCG_Rider")
MEL.delete_all_material_expressions(mat)
mat.set_editor_property('used_with_skeletal_mesh', True)
def texparam(name, tex, x, y, sampler):
    n = MEL.create_material_expression(mat, unreal.MaterialExpressionTextureSampleParameter2D, x, y)
    n.set_editor_property('parameter_name', name); n.set_editor_property('texture', tex); n.set_editor_property('sampler_type', sampler)
    return n
kef = {k: EAL.load_asset(f"{ROOT}/Riders/Kefla/T_Kefla_{k}") for k in ("BC", "N", "ORM")}
bc = texparam("BaseColor", kef["BC"], -600, -300, unreal.MaterialSamplerType.SAMPLERTYPE_COLOR)
nm = texparam("Normal", kef["N"], -600, 100, unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL)
orm = texparam("ORM", kef["ORM"], -600, 400, unreal.MaterialSamplerType.SAMPLERTYPE_MASKS)
MEL.connect_material_property(bc, "RGB", unreal.MaterialProperty.MP_BASE_COLOR)
MEL.connect_material_property(nm, "RGB", unreal.MaterialProperty.MP_NORMAL)
MEL.connect_material_property(orm, "R", unreal.MaterialProperty.MP_AMBIENT_OCCLUSION)
MEL.connect_material_property(orm, "G", unreal.MaterialProperty.MP_ROUGHNESS)
MEL.connect_material_property(orm, "B", unreal.MaterialProperty.MP_METALLIC)
MEL.recompile_material(mat); EAL.save_loaded_asset(mat)
for N in ("Kefla", "Koda", "Crash"):
    mi = EAL.load_asset(f"{ROOT}/Riders/{N}/MI_{N}"); MEL.update_material_instance(mi); EAL.save_loaded_asset(mi)
unreal.log("CCG_MATFIX2_DONE")
