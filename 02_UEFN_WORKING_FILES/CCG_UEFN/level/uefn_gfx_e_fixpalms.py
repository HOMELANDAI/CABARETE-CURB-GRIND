# re-seat every gallery palm on whatever is under it (ground / sidewalk / park) - several floated after the mesh swap
import unreal, json
BASE = r"F:\HOMELANDAI\CURBSIDE GRIND (CCG)\02_UEFN_WORKING_FILES\CCG_UEFN\level"
ss = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
world = unreal.EditorLevelLibrary.get_editor_world()
out = {"moved": [], "nohit": []}
for a in ss.get_all_level_actors():
    l = a.get_actor_label()
    if not l.startswith("L_Palm"): continue
    o, e = a.get_actor_bounds(False); bottom = o.z - e.z
    hits = unreal.SystemLibrary.line_trace_multi(world, unreal.Vector(o.x, o.y, bottom + 600), unreal.Vector(o.x, o.y, bottom - 1500), unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, [a], unreal.DrawDebugTrace.NONE, True, unreal.LinearColor.RED, unreal.LinearColor.GREEN, 0.0)
    gz = None; lbl = None
    for h in hits:
        t = h.to_tuple(); act = t[9]
        try: hl = act.get_actor_label()
        except Exception: continue
        if hl.startswith(("FD_", "DEV_", "FL_", "L_Palm", "L_Lamp", "L_PowerPole")): continue
        gz = t[5].z; lbl = hl; break
    if gz is None: out["nohit"].append(l); continue
    dz = gz - bottom
    if abs(dz) > 3:
        p = a.get_actor_location(); p.z += dz; a.set_actor_location(p, False, False); out["moved"].append([l, round(dz), lbl])
unreal.EditorLevelLibrary.save_current_level()
json.dump(out, open(BASE + r"\gfx_e_palms.json", "w"), indent=1)
