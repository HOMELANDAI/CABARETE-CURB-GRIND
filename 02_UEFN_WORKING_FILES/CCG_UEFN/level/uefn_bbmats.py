
import unreal, json, os
ss = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
out = {}
for a in ss.get_all_level_actors():
    l = a.get_actor_label()
    if l.startswith("L_Billboard_"):
        smc = a.get_component_by_class(unreal.StaticMeshComponent)
        out[l] = [smc.get_material(i).get_name() if smc.get_material(i) else None for i in range(smc.get_num_materials())] + [round(a.get_actor_location().x), round(a.get_actor_location().y)]
json.dump(out, open(r"C:\Users\211in\Downloads\CCG_UEFN\level\bbmats.json", "w"), indent=1)
