# finish the wet-road MPC wiring: (WetnessMax x MPC.Wetness) -> puddle (Multiply_1.B) and damp (Multiply_2.B)
# (expression inputs are not readable from Python here; the node order comes from uefn_gfx_pass.py: muv=_0, puddle=_1, damp=_2)
import unreal, json
G = "/9ec1b72d-2111-4319-b015-282d94c768eb/CCG"
EAL = unreal.EditorAssetLibrary; MEL = unreal.MaterialEditingLibrary
mat = EAL.load_asset(f"{G}/Materials/M_CCG_RoadWet")
E = {}
for ob in unreal.ObjectIterator(unreal.MaterialExpression):
    try:
        if ob.get_outer() == mat: E[ob.get_name()] = ob
    except Exception: pass
out = {"done": [], "names": sorted(E)}
wmax = E["MaterialExpressionScalarParameter_2"]; cw = E["MaterialExpressionCollectionParameter_0"]; gate = E["MaterialExpressionMultiply_6"]
MEL.connect_material_expressions(wmax, "", gate, "A"); MEL.connect_material_expressions(cw, "", gate, "B")
for k in ("MaterialExpressionMultiply_1", "MaterialExpressionMultiply_2"):
    MEL.connect_material_expressions(gate, "", E[k], "B"); out["done"].append(k + ".B <- gate")
if "MaterialExpressionMultiply_7" in E:
    try: MEL.delete_material_expression(mat, E["MaterialExpressionMultiply_7"]); out["done"].append("deleted Multiply_7")
    except Exception as ex: out["done"].append("delete fail " + str(ex)[:60])
MEL.recompile_material(mat); EAL.save_loaded_asset(mat)
json.dump(out, open(r"F:\HOMELANDAI\CURBSIDE GRIND (CCG)\02_UEFN_WORKING_FILES\CCG_UEFN\level\gfx_d_fix.json", "w"), indent=1)
