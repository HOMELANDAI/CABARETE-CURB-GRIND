import unreal, json, os
BASE = r"C:\Users\211in\Downloads\CCG_UEFN\level"
G = "/9ec1b72d-2111-4319-b015-282d94c768eb"
P = G + "/_Verse.CCG-Verse-ccg_rail"
out = {}
ss = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
try:
    c = unreal.load_class(None, P); out["load_class"] = None if c is None else c.get_path_name()
    if c:
        t = ss.spawn_actor_from_class(c, unreal.Vector(0, 0, -5000)); out["lc_spawn"] = t.get_class().get_path_name(); ss.destroy_actor(t)
except Exception as e: out["load_class_err"] = str(e)[:300]
try:
    ps = unreal.get_editor_subsystem(unreal.PlacementSubsystem)
    vc = unreal.load_object(None, P)
    info = unreal.AssetPlacementInfo(); info.set_editor_property("asset_to_place", vc)
    info.set_editor_property("finalized_transform", unreal.Transform(unreal.Vector(0, 0, -5000)))
    opts = unreal.PlacementOptions()
    res = ps.place_asset(info, opts)
    out["place"] = []
    for h in res:
        a = h.get_editor_property("actor") if hasattr(h, "get_editor_property") else None
        try: a = unreal.ScriptedPlacementUtilities.get_placed_actor(h) if a is None else a
        except Exception: pass
        out["place"].append(str(a.get_class().get_path_name()) if a else str(h))
        if a:
            try: out["place_props_test"] = str(a.get_editor_property("RailId"))
            except Exception as e: out["place_props_err"] = str(e)[:200]
            ss.destroy_actor(a)
except Exception as e: out["place_err"] = str(e)[:400]
# verse device wrapper map assets
reg = unreal.AssetRegistryHelpers.get_asset_registry()
out["wrapmaps"] = [str(a.package_name) for a in reg.get_all_assets(True) if str(a.asset_class_path.asset_name) == "VerseDeviceWrapperClassMap"][:5]
# the existing DEV_ccg_game_manager: try reading a couple of known editables
for a in ss.get_all_level_actors():
    if a.get_actor_label() == "DEV_ccg_game_manager":
        for pn in ("VerseClass", "verse_class", "Verse Class", "DeviceClass", "ClassToSpawn", "VerseDeviceClass"):
            try: out["gm_" + pn] = str(a.get_editor_property(pn))
            except Exception as e: out["gm_" + pn] = "ERR " + str(e)[:80]
        out["gm_fullname"] = a.get_full_name()
        break
json.dump(out, open(os.path.join(BASE, "probe3.json"), "w"), indent=1, default=str)
unreal.log("CCGL probe3 written")
