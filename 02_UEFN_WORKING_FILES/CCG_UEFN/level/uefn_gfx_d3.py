# road wetness track + sequence binding cleanup
import unreal, json
G = "/9ec1b72d-2111-4319-b015-282d94c768eb/CCG"
EAL = unreal.EditorAssetLibrary; MEL = unreal.MaterialEditingLibrary
ss = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
TU = getattr(unreal, "MovieSceneTimeUnit", None) or getattr(unreal, "SequenceTimeUnit", None)
ALL = {a.get_actor_label(): a for a in ss.get_all_level_actors()}
out = {"road": {}, "removed": [], "bindings": []}
seq = EAL.load_asset(f"{G}/Sequences/LS_CCG_Sunset")
# which bindings have tracks / children
kids = {}
for b in seq.get_bindings():
    p = b.get_parent()
    if p: kids[str(p.get_display_name())] = kids.get(str(p.get_display_name()), 0) + 1
for b in list(seq.get_bindings()):
    n = str(b.get_display_name()); nt = len(b.get_tracks())
    out["bindings"].append([n, nt, kids.get(n, 0)])
    if nt == 0 and kids.get(n, 0) == 0:
        b.remove(); out["removed"].append(n)
road = ALL.get("L_Road_Highway5")
if road:
    c = road.get_component_by_class(unreal.StaticMeshComponent)
    mats = [m.get_name() if m else None for m in c.get_materials()]
    out["road"] = {"class": road.get_class().get_name(), "mats": mats}
    slot = next((i for i, m in enumerate(mats) if m == "MI_Road_Wet"), None)
    if slot is None:
        mi = EAL.load_asset(f"{G}/Materials/MI/MI_Road_Wet"); c.set_material(0, mi); slot = 0; out["road"]["assigned"] = True
    ab = seq.add_possessable(road); cb = seq.add_possessable(c)
    try: cb.set_parent(ab)
    except Exception: pass
    tr = cb.add_track(unreal.MovieSceneComponentMaterialTrack)
    info = unreal.ComponentMaterialInfo(); info.set_editor_property("material_slot_index", slot)
    try: info.set_editor_property("material_type", unreal.ComponentMaterialType.INDEXED_MATERIAL)
    except Exception: pass
    unreal.MovieSceneMaterialTrackExtensions.set_material_info(tr, info)
    sec = tr.add_section(); sec.set_range(0, 180)
    pinfo = unreal.MaterialParameterInfo(name="Wetness", association=unreal.MaterialParameterAssociation.GLOBAL_PARAMETER, index=-1)
    sec.add_scalar_parameter_key(pinfo, unreal.FrameNumber(0), 0.1, "", "")
    for ch in sec.get_all_channels():
        if str(ch.get_editor_property("channel_name")) == "Wetness":
            for k in list(ch.get_keys()): ch.remove_key(k)
            ch.add_key(unreal.FrameNumber(0), 0.1, 0.0, TU.DISPLAY_RATE, unreal.MovieSceneKeyInterpolation.AUTO)
            ch.add_key(unreal.FrameNumber(180), 0.35, 0.0, TU.DISPLAY_RATE, unreal.MovieSceneKeyInterpolation.AUTO)
            out["road"]["keyed"] = True
else: out["road"] = "L_Road_Highway5 not found"
EAL.save_loaded_asset(seq); unreal.EditorLevelLibrary.save_current_level()
out["final_bindings"] = len(seq.get_bindings())
json.dump(out, open(r"F:\HOMELANDAI\CURBSIDE GRIND (CCG)\02_UEFN_WORKING_FILES\CCG_UEFN\level\gfx_d3.json", "w"), indent=1, default=str)
