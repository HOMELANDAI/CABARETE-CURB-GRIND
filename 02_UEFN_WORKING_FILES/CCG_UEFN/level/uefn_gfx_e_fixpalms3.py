# palm origin = trunk base?  probe the LOD0 vertices, then seat every palm with its ORIGIN on the surface under it
import unreal, json
BASE = r"F:\HOMELANDAI\CURBSIDE GRIND (CCG)\02_UEFN_WORKING_FILES\CCG_UEFN\level"
EAL = unreal.EditorAssetLibrary
ss = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
world = unreal.EditorLevelLibrary.get_editor_world()
out = {"verts": {}, "moved": [], "nohit": []}
for k in "ABC":
    m = EAL.load_asset(f"/Game/Environments/Props/Trees/Meshes/SM_PalmTree_{k}")
    try:
        verts, tris, normals, uvs, tangents = unreal.ProceduralMeshLibrary.get_section_from_static_mesh(m, 0, 0)
        zs = sorted(v.z for v in verts)
        below = sum(1 for z in zs if z < -5)
        out["verts"][k] = {"n": len(zs), "zmin": round(zs[0]), "zmax": round(zs[-1]), "below0": below, "p5": round(zs[len(zs)//20]), "p25": round(zs[len(zs)//4])}
    except Exception as e: out["verts"][k] = str(e)[:120]
for a in ss.get_all_level_actors():
    l = a.get_actor_label()
    if not l.startswith("L_Palm"): continue
    p = a.get_actor_location(); o, e = a.get_actor_bounds(False)
    hits = unreal.SystemLibrary.line_trace_multi(world, unreal.Vector(p.x, p.y, p.z + 800), unreal.Vector(p.x, p.y, p.z - 1500), unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, True, [a], unreal.DrawDebugTrace.NONE, True, unreal.LinearColor.RED, unreal.LinearColor.GREEN, 0.0)
    gz = None; lbl = None
    for h in hits:
        t = h.to_tuple(); act = t[9]
        try: hl = act.get_actor_label()
        except Exception: continue
        if hl.startswith(("FD_", "DEV_", "FL_", "L_Palm", "L_Lamp", "L_PowerPole", "L_Sign", "L_Mural", "L_Billboard")): continue
        gz = t[5].z; lbl = hl; break
    if gz is None: out["nohit"].append(l); continue
    dz = gz - p.z - 4.0
    p.z += dz; a.set_actor_location(p, False, False); out["moved"].append([l, round(dz), lbl])
unreal.EditorLevelLibrary.save_current_level()
json.dump(out, open(BASE + r"\gfx_e_palms3.json", "w"), indent=1)
