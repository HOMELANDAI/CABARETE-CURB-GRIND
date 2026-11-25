
import unreal
reg = unreal.AssetRegistryHelpers.get_asset_registry()
allvc = reg.get_assets_by_class(unreal.TopLevelAssetPath("/Script/CoreUObject", "VerseClass"))
hits = [str(x.package_name) + ":" + str(x.asset_name) for x in allvc if 'ccg' in str(x.asset_name).lower() or 'ccg' in str(x.package_name).lower()]
unreal.log("CCG_DEVCLASSES7 total=" + str(len(allvc)) + " " + str(hits))
