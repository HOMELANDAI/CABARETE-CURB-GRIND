# list Fortnite gallery foliage meshes usable for understory
import unreal, json, re
reg = unreal.AssetRegistryHelpers.get_asset_registry()
f = unreal.ARFilter(class_names=["StaticMesh"], recursive_paths=True, package_paths=["/Game/Environments", "/Game/Athena/Apollo", "/Game/Athena/Artemis", "/Game/Athena/Helios"])
keys = ("bush", "shrub", "plant", "fern", "grass", "bougain", "flower", "hedge", "palm", "tropical", "foliage", "weed", "vine", "cactus", "agave", "leaf", "reed", "clump")
hits = {}
for a in reg.get_assets(f):
    n = str(a.asset_name).lower()
    if n.startswith("sm_") and any(k in n for k in keys):
        hits.setdefault(str(a.package_path), []).append(str(a.asset_name))
    if sum(len(v) for v in hits.values()) > 400: break
json.dump({"paths": {k: sorted(v) for k, v in hits.items()}}, open(r"F:\HOMELANDAI\CURBSIDE GRIND (CCG)\02_UEFN_WORKING_FILES\CCG_UEFN\level\probe_bush.json", "w"), indent=1)
unreal.log("CCG_PROBE_BUSH %d" % sum(len(v) for v in hits.values()))
