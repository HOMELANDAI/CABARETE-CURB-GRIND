
import unreal
reg = unreal.AssetRegistryHelpers.get_asset_registry()
names = []
for a in reg.get_assets_by_path("/9ec1b72d-2111-4319-b015-282d94c768eb", recursive=True):
    n = str(a.package_name)
    if 'ccg_' in n.lower() or 'verse' in n.lower(): names.append(n + " [" + str(a.asset_class_path.asset_name) + "]")
unreal.log("CCG_VERSE_ASSETS " + " | ".join(names[:30]) + f" (total {len(names)})")
