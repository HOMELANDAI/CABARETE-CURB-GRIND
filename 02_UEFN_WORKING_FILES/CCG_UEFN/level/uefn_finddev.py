import unreal, json, os
BASE = r"C:\Users\211in\Downloads\CCG_UEFN\level"
reg = unreal.AssetRegistryHelpers.get_asset_registry()
want = ["Volume", "Trigger", "Barrier", "HUDMessage", "HudMessage", "EndGame", "Button", "ItemGranter", "ClassDesigner", "ClassAndTeam", "ClassSelector", "CustomizableLight", "DaySequence", "VFXSpawner", "Billboard", "PlayerSpawn", "Prop", "Cinematic", "Mutator"]
out = {w: [] for w in want}
n_total = 0
for cls in (unreal.TopLevelAssetPath("/Script/Engine", "Blueprint"), unreal.TopLevelAssetPath("/Script/Engine", "BlueprintGeneratedClass")):
    try:
        assets = reg.get_assets_by_class(cls, True)
    except Exception as e:
        assets = []
    n_total += len(assets)
    for a in assets:
        n = str(a.asset_name); pk = str(a.package_name)
        if "device" not in n.lower() and "device" not in pk.lower(): continue
        for w in want:
            if w.lower() in n.lower() and len(out[w]) < 12: out[w].append(pk)
# also: what class is a placed static mesh prop in this level, and the spawn pad
ss = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
out["_level_classes"] = sorted(set(a.get_class().get_path_name() for a in ss.get_all_level_actors()))[:60]
out["_total"] = n_total
json.dump(out, open(os.path.join(BASE, "devices.json"), "w"), indent=1)
unreal.log("CCGL devices.json written " + str(n_total))
