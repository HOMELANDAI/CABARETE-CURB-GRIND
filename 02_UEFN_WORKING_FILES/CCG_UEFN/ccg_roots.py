
import unreal
reg = unreal.AssetRegistryHelpers.get_asset_registry()
sub = reg.get_sub_paths("/", recurse=False)
umap = [str(a.package_name) for a in reg.get_assets_by_class(unreal.TopLevelAssetPath("/Script/Engine", "World")) if 'Cabarete' in str(a.package_name) or 'Frozen' in str(a.package_name)][:20]
unreal.log("CCG_ROOTS " + " | ".join(str(s) for s in sub) + " || MAPS " + " | ".join(umap))
