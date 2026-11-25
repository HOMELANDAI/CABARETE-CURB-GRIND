# exec(open(r'C:/Users/211in/Downloads/CCG_UEFN/level/uefn_tripo_place.py').read())
# Places the Tripo rider statues on the class podiums and the shop props at the store / start line.
import unreal, math, json, traceback
G = "/9ec1b72d-2111-4319-b015-282d94c768eb/CCG"
ss = unreal.get_editor_subsystem(unreal.EditorActorSubsystem); EAL = unreal.EditorAssetLibrary
world = unreal.EditorLevelLibrary.get_editor_world()
out = {"placed": [], "errors": []}
LOGF = open(r"C:\Users\211in\Downloads\CCG_UEFN\level\tripo_place_log.txt", "w")
try:
    ALL = {a.get_actor_label(): a for a in ss.get_all_level_actors()}
    for lbl, a in list(ALL.items()):
        if lbl.startswith("TR_"): ss.destroy_actor(a)
    ALL = {a.get_actor_label(): a for a in ss.get_all_level_actors()}
    def ground_z(x, y, zhint):
        hit = unreal.SystemLibrary.line_trace_single(world, unreal.Vector(x, y, zhint + 400), unreal.Vector(x, y, zhint - 800), unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, [], unreal.DrawDebugTrace.NONE, True, unreal.LinearColor.RED, unreal.LinearColor.GREEN, 0.0)
        return zhint   # devices / store / spawn origins already sit on the ground; traces hit device volumes
    def place_sm(label, mesh_path, x, y, zhint, yaw, target_cm, axis="z", lift=0.0):
        m = EAL.load_asset(mesh_path)
        b = m.get_bounds(); e = b.box_extent; o = b.origin
        ext = {"x": e.x, "y": e.y, "z": e.z}[axis]
        s = target_cm / (2.0 * ext)
        gz = ground_z(x, y, zhint)
        a = ss.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(x, y, gz), unreal.Rotator(0, 0, yaw))
        a.set_actor_label(label)
        a.static_mesh_component.set_static_mesh(m)
        a.set_actor_scale3d(unreal.Vector(s, s, s))
        # bottom of the scaled bounds sits on the ground (bounds origin is in local space)
        bottom = (o.z - e.z) * s
        a.set_actor_location(unreal.Vector(x, y, gz - bottom + lift), False, False)
        a.set_mobility(unreal.ComponentMobility.STATIC)
        out["placed"].append([label, round(x), round(y), round(gz), round(s, 3)])
        return a
    def place_sk(label, sk_path, x, y, zhint, yaw, target_cm):
        m = EAL.load_asset(sk_path)
        if m is None: out["errors"].append("missing " + sk_path); return None
        gz = ground_z(x, y, zhint)
        a = ss.spawn_actor_from_class(unreal.SkeletalMeshActor, unreal.Vector(x, y, gz), unreal.Rotator(0, 0, yaw))
        a.set_actor_label(label)
        c = a.skeletal_mesh_component
        try: c.set_skeletal_mesh_asset(m)
        except Exception: c.set_skeletal_mesh(m)
        o, e = a.get_actor_bounds(False)
        s = target_cm / (2.0 * e.z) if e.z > 1 else 1.0
        a.set_actor_scale3d(unreal.Vector(s, s, s))
        o, e = a.get_actor_bounds(False)
        a.set_actor_location(unreal.Vector(x, y, gz + (gz - (o.z - e.z))), False, False)
        out["placed"].append([label, round(x), round(y), round(gz), round(s, 3)])
        return a
    # ---- riders on the class podiums: 1.2 m behind the designer (away from spawn), facing the spawn
    sp = ALL.get("Spawn_Start") or ALL.get("FD_Spawn_Start")
    spl = sp.get_actor_location() if sp else unreal.Vector(-1076.1, -531.1, 106)
    riders = [("Kefla", "sk"), ("Koda", "sk"), ("Crash", "sk"), ("Yara", "sm"), ("Sunny", "sm"), ("Rubi", "sm"), ("Kai", "sm")]
    for i, (n, kind) in enumerate(riders):
        d = ALL.get("FD_Class_%d" % i)
        if not d: out["errors"].append("no FD_Class_%d" % i); continue
        p = d.get_actor_location()
        dx, dy = spl.x - p.x, spl.y - p.y; L = math.hypot(dx, dy) or 1.0; nx, ny = dx / L, dy / L
        yaw = math.degrees(math.atan2(ny, nx))
        x, y = p.x - nx * 120, p.y - ny * 120
        if kind == "sm":
            place_sm("TR_Rider_" + n, f"{G}/Tripo/CCG_Rider_{n}/CCG_Rider_{n}/StaticMeshes/CCG_Rider_{n}", x, y, p.z, yaw - 90, 182.0)
        else:
            place_sk("TR_Rider_" + n, f"{G}/Riders/{n}/SK_{n}", x, y, p.z, yaw - 90, 95.0)
    # ---- shop props around Ocean Dream Plaza
    st = ALL.get("L_Store_OceanDreamPlaza")
    if st:
        sl = st.get_actor_location(); o, e = st.get_actor_bounds(False); syaw = st.get_actor_rotation().yaw; rr = math.radians(syaw)
        bx, by = o.x - sl.x, o.y - sl.y; ly = (-math.sin(rr)) * bx + math.cos(rr) * by; side = -1.0 if ly > 0 else 1.0
        def sp_(dx, dy):  # store-local metres (dx along the facade, dy = forecourt depth)
            DX, DY = dx * 100, side * dy * 100
            return sl.x + DX * math.cos(rr) - DY * math.sin(rr), sl.y + DX * math.sin(rr) + DY * math.cos(rr)
        face = syaw + (0 if side > 0 else 180)   # yaw looking out to the forecourt
        T = "/Tripo/"
        x, y = sp_(-7.5, 1.2);  place_sm("TR_Shop_Counter", f"{G}{T}CCG_ShopCounter/CCG_ShopCounter/StaticMeshes/CCG_ShopCounter", x, y, sl.z, face, 160.0, axis="x")
        x, y = sp_(-7.5, 1.2);  place_sm("TR_Shop_Board", f"{G}{T}CCG_Board/CCG_Board/StaticMeshes/CCG_Board", x, y, sl.z, face + 20, 82.0, axis="y", lift=96.0)
        x, y = sp_(-7.5, 3.4); place_sm("TR_Shop_DeckRack", f"{G}{T}CCG_DeckRack/CCG_DeckRack/StaticMeshes/CCG_DeckRack", x, y, sl.z, face, 135.0)
        x, y = sp_(7.5, 1.2);  place_sm("TR_Shop_KaftanRack", f"{G}{T}CCG_KaftanRack/CCG_KaftanRack/StaticMeshes/CCG_KaftanRack", x, y, sl.z, face, 165.0)
        x, y = sp_(7.5, 3.4); place_sm("TR_Shop_FlannelTable", f"{G}{T}CCG_FlannelTable/CCG_FlannelTable/StaticMeshes/CCG_FlannelTable", x, y, sl.z, face, 125.0, axis="x")
    else:
        out["errors"].append("no store actor")
    # ---- practice line: kicker + rail 14 m / 20 m down the road from the spawn
    byaw = sp.get_actor_rotation().yaw if sp else 26.27; r = math.radians(byaw)
    def off(dx, dy):
        return spl.x + dx * 100 * math.cos(r) - dy * 100 * math.sin(r), spl.y + dx * 100 * math.sin(r) + dy * 100 * math.cos(r)
    x, y = off(14, 1.5);  place_sm("TR_Kicker", f"{G}/Tripo/CCG_Kicker/CCG_Kicker/StaticMeshes/CCG_Kicker", x, y, spl.z, byaw + 180, 170.0, axis="x")
    x, y = off(20, -1.5); place_sm("TR_Rail", f"{G}/Tripo/CCG_Rail/CCG_Rail/StaticMeshes/CCG_Rail", x, y, spl.z, byaw + 90, 300.0, axis="y")
    unreal.EditorLevelLibrary.save_current_level()
except Exception:
    out["errors"].append(traceback.format_exc())
json.dump(out, open(r"C:\Users\211in\Downloads\CCG_UEFN\level\tripo_place.json", "w"), indent=1)
LOGF.write("END\n"); LOGF.close()
unreal.log("CCG_TRIPO_PLACE_DONE %d err %d" % (len(out["placed"]), len(out["errors"])))
