import unreal, json
LSE = unreal.LevelSequenceEditorBlueprintLibrary
ss = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
ALL = {a.get_actor_label(): a for a in ss.get_all_level_actors()}
seq = unreal.EditorAssetLibrary.load_asset("/9ec1b72d-2111-4319-b015-282d94c768eb/CCG/Sequences/LS_CCG_Sunset")
out = {"bindings": [], "sun": {}}
for b in seq.get_bindings():
    try:
        bo = LSE.get_bound_objects(b) if hasattr(LSE, "get_bound_objects") else []
    except Exception as e: bo = [str(e)[:60]]
    out["bindings"].append({"name": b.get_display_name() if hasattr(b, "get_display_name") else b.get_name(), "id": str(b.get_id()), "parent": str(b.get_parent().get_name()) if b.get_parent() else None,
                            "tracks": [t.get_class().get_name() + ":" + str(t.get_property_path()) if hasattr(t, "get_property_path") else t.get_class().get_name() for t in b.get_tracks()],
                            "bound": [str(o) for o in bo][:3]})
for f in (0, 180):
    LSE.set_current_time(f); LSE.refresh_current_level_sequence() if hasattr(LSE, "refresh_current_level_sequence") else None
    s = ALL["LR_Sun"]; c = s.get_component_by_class(unreal.DirectionalLightComponent)
    fc = ALL["LR_Fog"].get_component_by_class(unreal.ExponentialHeightFogComponent)
    out["sun"][f] = {"rot": str(s.get_actor_rotation()), "int": c.get_editor_property("intensity"), "temp": c.get_editor_property("temperature"), "fog": fc.get_editor_property("fog_density")}
json.dump(out, open(r"F:\HOMELANDAI\CURBSIDE GRIND (CCG)\02_UEFN_WORKING_FILES\CCG_UEFN\level\gfx_c_probe.json", "w"), indent=1, default=str)
