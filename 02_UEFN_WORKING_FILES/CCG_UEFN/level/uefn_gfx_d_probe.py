import unreal, json
G = "/9ec1b72d-2111-4319-b015-282d94c768eb/CCG"
EAL = unreal.EditorAssetLibrary; MEL = unreal.MaterialEditingLibrary
mat = EAL.load_asset(f"{G}/Materials/M_CCG_RoadWet")
rows = []
for ob in unreal.ObjectIterator(unreal.MaterialExpression):
    try:
        if ob.get_outer() != mat: continue
    except Exception: continue
    r = {"name": ob.get_name(), "cls": ob.get_class().get_name(), "inputs": {}}
    try: r["param"] = str(ob.get_editor_property("parameter_name"))
    except Exception: pass
    try:
        for nm in MEL.get_inputs_for_material_expression(ob):
            try:
                src = MEL.get_input_node_for_material_expression(ob, str(nm))
                r["inputs"][str(nm)] = src.get_name() if src else None
            except Exception as e: r["inputs"][str(nm)] = "ERR " + str(e)[:60]
    except Exception as e: r["inputs_err"] = str(e)[:80]
    rows.append(r)
json.dump({"n": len(rows), "rows": rows, "mel": [m for m in dir(MEL) if "input" in m.lower()]}, open(r"F:\HOMELANDAI\CURBSIDE GRIND (CCG)\02_UEFN_WORKING_FILES\CCG_UEFN\level\gfx_d_probe.json", "w"), indent=1)
