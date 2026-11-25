import unreal, json
ss = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
out=[]
for a in ss.get_all_level_actors():
    l=a.get_actor_label()
    if any(k in l for k in ("Shop","shop","Rack","HAI_Skate","Store","Deck","Spawn_Start")):
        o,e=a.get_actor_bounds(False); p=a.get_actor_location(); r=a.get_actor_rotation()
        m=None
        try:
            c=a.get_component_by_class(unreal.StaticMeshComponent); m=c.static_mesh.get_name() if c and c.static_mesh else None
        except Exception: pass
        out.append([l,a.get_class().get_name(),[round(p.x),round(p.y),round(p.z)],round(r.yaw),[round(o.x),round(o.y),round(o.z)],[round(e.x),round(e.y),round(e.z)],m])
json.dump(out,open(r"F:\HOMELANDAI\CURBSIDE GRIND (CCG)\02_UEFN_WORKING_FILES\CCG_UEFN\level\probe_shop.json","w"),indent=1)
unreal.log("CCG_PROBE_SHOP %d"%len(out))
