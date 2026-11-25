# exec(open(r'C:/Users/211in/Downloads/CCG_UEFN/level/uefn_probe_fol.py').read())
import unreal, json, traceback
out = {"palms": [], "water": [], "expr": {}, "seq": {}, "heights": [], "err": []}
try:
    reg = unreal.AssetRegistryHelpers.get_asset_registry()
    f = unreal.ARFilter(class_names=["StaticMesh"], recursive_paths=True, package_paths=["/Game", "/Fortnite", "/Epic"])
    n = 0
    for a in reg.get_assets(f):
        nm = str(a.asset_name).lower()
        if any(k in nm for k in ("palm", "tropic", "coconut")):
            out["palms"].append(str(a.package_name))
            n += 1
            if n > 60: break
except Exception: out["err"].append("palms " + traceback.format_exc()[-200:])
for cn in ("WaterBodyOcean", "WaterBodyLake", "WaterBodyCustom", "WaterZone", "ExponentialHeightFog", "SkyAtmosphere", "DirectionalLight", "SkyLight", "VolumetricCloud", "InstancedFoliageActor", "LevelSequenceActor", "PostProcessVolume"):
    out["water"].append([cn, hasattr(unreal, cn)])
for en in ("MaterialExpressionParallaxOcclusionMapping", "MaterialExpressionBumpOffset", "MaterialExpressionQualitySwitch", "MaterialExpressionVertexColor", "MaterialExpressionWorldPosition", "MaterialExpressionFresnel", "MaterialExpressionPanner", "MaterialExpressionTime", "MaterialExpressionSine"):
    out["expr"][en] = hasattr(unreal, en)
for sn in ("LevelSequence", "LevelSequenceFactoryNew", "MovieSceneSequenceExtensions", "LevelSequenceEditorBlueprintLibrary", "MovieSceneBindingExtensions", "MovieSceneTrackExtensions", "MovieSceneSectionExtensions", "MovieSceneScriptingChannel"):
    out["seq"][sn] = hasattr(unreal, sn)
try:
    G = "/9ec1b72d-2111-4319-b015-282d94c768eb/CCG"
    for a in reg.get_assets_by_path(G + "/Materials", recursive=False):
        nm = str(a.asset_name)
        if nm.endswith("_H"): out["heights"].append(nm)
except Exception: out["err"].append("heights " + traceback.format_exc()[-200:])
try:
    ss = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    kinds = {}
    for a in ss.get_all_level_actors():
        l = a.get_actor_label()
        if "Palm" in l:
            k = l.rsplit("_", 1)[0]; kinds[k] = kinds.get(k, 0) + 1
    out["level_palms"] = kinds
except Exception: out["err"].append("lvl " + traceback.format_exc()[-200:])
json.dump(out, open(r"C:\Users\211in\Downloads\CCG_UEFN\level\probe_fol.json", "w"), indent=1)
unreal.log("CCG_PROBE_FOL_DONE")
