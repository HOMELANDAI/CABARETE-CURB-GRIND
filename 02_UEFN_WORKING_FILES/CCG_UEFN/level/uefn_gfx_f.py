# exec(open(r'F:/HOMELANDAI/CURBSIDE GRIND (CCG)/02_UEFN_WORKING_FILES/CCG_UEFN/level/uefn_gfx_f.py').read())
# Tripo foliage v1: (1) the 35 L_Palm* actors get HAI's own Tripo coconut palms (CCG_Palm_A / _B) instead of the
# gallery SM_PalmTree_* that UEFN's validator rejects on new actors; (2) bougainvillea + sea-grape shrubs (own Nanite
# meshes, so legal) along the beach side of the palms, the park perimeters and the building fronts.  Re-runnable
# (deletes FT_* first).  Mesh origins are at the trunk/stem base (Tripo export, z-min 0).
import unreal, json, os, math, random, traceback
BASE = r"F:\HOMELANDAI\CURBSIDE GRIND (CCG)\02_UEFN_WORKING_FILES\CCG_UEFN\level"
G = "/9ec1b72d-2111-4319-b015-282d94c768eb/CCG/Tripo"
EAL = unreal.EditorAssetLibrary
ss = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
world = unreal.EditorLevelLibrary.get_editor_world()
random.seed(23)
out = {"palms": [], "placed": {}, "rejected": {}, "err": []}
def mesh(n): return EAL.load_asset(f"{G}/{n}/{n}/StaticMeshes/{n}")
M = {n: mesh(n) for n in ("CCG_Palm_A", "CCG_Palm_B", "CCG_SeaGrape", "CCG_Bougainvillea")}
H = {}
for n, m in M.items():
    b = m.get_bounds(); H[n] = 2 * b.box_extent.z
ALL = {a.get_actor_label(): a for a in ss.get_all_level_actors()}
for l, a in list(ALL.items()):
    if l.startswith("FT_"): ss.destroy_actor(a); ALL.pop(l)
def ground(x, y, zhint):
    hits = unreal.SystemLibrary.line_trace_multi(world, unreal.Vector(x, y, zhint + 1500), unreal.Vector(x, y, zhint - 1500), unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, True, [], unreal.DrawDebugTrace.NONE, True, unreal.LinearColor.RED, unreal.LinearColor.GREEN, 0.0)
    for h in hits:
        t = h.to_tuple(); act = t[9]
        try: lbl = act.get_actor_label()
        except Exception: continue
        if lbl.startswith(("FD_", "DEV_", "FL_", "FT_", "L_Palm", "L_Lamp", "L_PowerPole")): continue
        if lbl.startswith("L_Ground"): return t[5].z, lbl
        return None, lbl
    return None, "nothing"
# ---------------------------------------------------------------- 1. palms -> Tripo coconut palms
try:
    for l, a in ALL.items():
        if not l.startswith("L_Palm"): continue
        c = a.get_component_by_class(unreal.StaticMeshComponent)
        o, e = a.get_actor_bounds(False); old_h = 2 * e.z
        n = random.choice(["CCG_Palm_A", "CCG_Palm_A", "CCG_Palm_B"])
        target = max(650.0, min(1300.0, old_h * random.uniform(0.9, 1.1)))
        s = target / H[n]
        c.set_static_mesh(M[n]); a.set_actor_scale3d(unreal.Vector(s, s, s))
        r = a.get_actor_rotation(); r.yaw = random.uniform(0, 360); r.pitch = random.uniform(-2, 2); r.roll = random.uniform(-2, 2); a.set_actor_rotation(r, False)
        out["palms"].append([l, n, round(target)])
except Exception: out["err"].append("palms " + traceback.format_exc()[-400:])
# ---------------------------------------------------------------- 2. shrubs
n_id = [0]
def place(n, x, y, z, target, yaw=None):
    s = target / H[n]
    a = ss.spawn_actor_from_object(M[n], unreal.Vector(x, y, z - 2.0), unreal.Rotator(0, 0, yaw if yaw is not None else random.uniform(0, 360)))
    a.set_actor_scale3d(unreal.Vector(s, s, s)); n_id[0] += 1
    a.set_actor_label("FT_%s_%03d" % (n[4:], n_id[0])); a.set_folder_path("CCG/Foliage")
    out["placed"][n] = out["placed"].get(n, 0) + 1
def rej(lbl): out["rejected"][lbl] = out["rejected"].get(lbl, 0) + 1
def pick():
    return ("CCG_Bougainvillea", random.uniform(150, 240)) if random.random() < 0.5 else ("CCG_SeaGrape", random.uniform(130, 210))
try:
    for l, a in ALL.items():
        if not l.startswith("L_Palm"): continue
        p = a.get_actor_location()
        for i in range(random.randint(1, 2)):
            ang = random.uniform(0, 2 * math.pi); r = random.uniform(250, 520)
            x, y = p.x + r * math.cos(ang), p.y + r * math.sin(ang)
            z, lbl = ground(x, y, p.z)
            if z is None: rej(lbl); continue
            n, t = pick(); place(n, x, y, z, t)
    for l, a in ALL.items():
        if not l.startswith("L_Park_"): continue
        o, e = a.get_actor_bounds(False); zb = o.z - e.z
        edges = [((o.x - e.x, o.y - e.y), (o.x + e.x, o.y - e.y), (0, -1)), ((o.x + e.x, o.y - e.y), (o.x + e.x, o.y + e.y), (1, 0)),
                 ((o.x + e.x, o.y + e.y), (o.x - e.x, o.y + e.y), (0, 1)), ((o.x - e.x, o.y + e.y), (o.x - e.x, o.y - e.y), (-1, 0))]
        for (x0, y0), (x1, y1), (nx, ny) in edges:
            L = math.hypot(x1 - x0, y1 - y0); n = max(1, int(L / 1400))
            for i in range(n):
                t = (i + random.uniform(0.2, 0.8)) / n; off = random.uniform(260, 420)
                x, y = x0 + (x1 - x0) * t + nx * off, y0 + (y1 - y0) * t + ny * off
                z, lbl = ground(x, y, zb)
                if z is None: rej(lbl); continue
                nm, tg = pick(); place(nm, x, y, z, tg)
    # bougainvillea against ~40 % of the building backs / sides (off the sidewalk, on the sand behind the frontage)
    for l, a in ALL.items():
        if not (l.startswith("L_Bldg_") or l.startswith("L_Fill_")) or random.random() > 0.4: continue
        o, e = a.get_actor_bounds(False); p = a.get_actor_location()
        fwd = a.get_actor_forward_vector(); right = a.get_actor_right_vector()
        halfw = abs(right.x) * e.x + abs(right.y) * e.y; depth = abs(fwd.x) * e.x + abs(fwd.y) * e.y
        away = 1.0 if ((o.x - p.x) * fwd.x + (o.y - p.y) * fwd.y) > 0 else -1.0   # body side
        side = random.choice([-1, 1])
        x = p.x + right.x * side * (halfw + 120) + fwd.x * away * random.uniform(100, depth * 1.6)
        y = p.y + right.y * side * (halfw + 120) + fwd.y * away * random.uniform(100, depth * 1.6)
        z, lbl = ground(x, y, p.z)
        if z is None: rej(lbl); continue
        place("CCG_Bougainvillea", x, y, z, random.uniform(180, 260))
except Exception: out["err"].append("shrubs " + traceback.format_exc()[-400:])
try: unreal.EditorLevelLibrary.save_current_level()
except Exception as ex: out["err"].append("save " + str(ex)[:100])
out["total"] = n_id[0]
json.dump(out, open(os.path.join(BASE, "gfx_f.json"), "w"), indent=1, default=str)
unreal.log("CCG_GFX_F_DONE %d" % n_id[0])
