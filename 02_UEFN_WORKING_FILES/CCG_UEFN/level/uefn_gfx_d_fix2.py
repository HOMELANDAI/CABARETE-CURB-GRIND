# CollectionParameter nodes need the parameter GUID (parameter_id), not just the name
import unreal, json
G = "/9ec1b72d-2111-4319-b015-282d94c768eb/CCG"
EAL = unreal.EditorAssetLibrary; MEL = unreal.MaterialEditingLibrary
mpc = EAL.load_asset(f"{G}/Materials/MPC_CCG")
ids = {}
for p in mpc.get_editor_property("scalar_parameters"):
    ids[str(p.get_editor_property("parameter_name"))] = p.get_editor_property("id")
out = {"ids": {k: str(v) for k, v in ids.items()}, "fixed": []}
for mname in ("M_CCG_Env", "M_CCG_RoadWet"):
    mat = EAL.load_asset(f"{G}/Materials/{mname}")
    for ob in unreal.ObjectIterator(unreal.MaterialExpressionCollectionParameter):
        try:
            if ob.get_outer() != mat: continue
            pn = str(ob.get_editor_property("parameter_name"))
            if pn in ids:
                ob.set_editor_property("collection", mpc); ob.set_editor_property("parameter_id", ids[pn]); out["fixed"].append([mname, pn])
        except Exception as e: out["fixed"].append([mname, "ERR " + str(e)[:80]])
    MEL.recompile_material(mat); EAL.save_loaded_asset(mat)
json.dump(out, open(r"F:\HOMELANDAI\CURBSIDE GRIND (CCG)\02_UEFN_WORKING_FILES\CCG_UEFN\level\gfx_d_fix2.json", "w"), indent=1)
