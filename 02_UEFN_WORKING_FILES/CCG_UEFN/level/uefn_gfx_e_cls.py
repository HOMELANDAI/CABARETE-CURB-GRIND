
import unreal, json
ss = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
out = {}
for a in ss.get_all_level_actors():
    l = a.get_actor_label()
    if l in ("L_Palm_001", "L_Palm_002", "FLT_SM_PalmTree_A", "FLT_SM_ThornBush_A", "FLT_SM_JunglePlants_FanPlant_A", "L_Road_Highway5", "TR_Rail", "L_Palm_PalmWrap"):
        c = a.get_component_by_class(unreal.StaticMeshComponent)
        m = c.get_editor_property("static_mesh") if c else None
        out[l] = {"cls": a.get_class().get_name(), "comp": c.get_class().get_name() if c else None, "mesh": m.get_path_name() if m else None, "mob": str(c.mobility) if c else None,
                  "folder": str(a.get_folder_path())}
json.dump(out, open(r"F:\HOMELANDAI\CURBSIDE GRIND (CCG)\02_UEFN_WORKING_FILES\CCG_UEFN\level\gfx_e_cls.json", "w"), indent=1)
