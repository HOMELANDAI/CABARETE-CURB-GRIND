
import unreal
ROOT = "/9ec1b72d-2111-4319-b015-282d94c768eb/CCG"
EAL = unreal.EditorAssetLibrary; MEL = unreal.MaterialEditingLibrary
mat = EAL.load_asset(f"{ROOT}/Materials/M_CCG_Rider")
mat.set_editor_property('used_with_skeletal_mesh', True)
mat.set_editor_property('used_with_morph_targets', True)
# ORM sampler must be Masks for a TC_Masks texture
for e in [n for n in MEL.get_material_expressions(mat) if False] if not hasattr(MEL, 'get_material_expressions') else []: pass
try:
    exprs = mat.get_editor_property('expressions')
except Exception:
    exprs = []
fixed = 0
for e in exprs:
    if isinstance(e, unreal.MaterialExpressionTextureSampleParameter2D) and str(e.get_editor_property('parameter_name')) == 'ORM':
        e.set_editor_property('sampler_type', unreal.MaterialSamplerType.SAMPLERTYPE_MASKS); fixed += 1
MEL.recompile_material(mat); EAL.save_loaded_asset(mat)
errs = []
for N in ("Kefla", "Koda", "Crash"):
    mi = EAL.load_asset(f"{ROOT}/Riders/{N}/MI_{N}"); MEL.update_material_instance(mi); EAL.save_loaded_asset(mi)
unreal.log(f"CCG_MATFIX_DONE fixed={fixed} n_expr={len(exprs)}")
