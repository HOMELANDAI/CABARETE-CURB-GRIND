# exec(open(r'F:/HOMELANDAI/CURBSIDE GRIND (CCG)/02_UEFN_WORKING_FILES/CCG_UEFN/level/uefn_gfx_e.py').read())
# Graphics Tier B (part 4): understory foliage from the Fortnite gallery — tropical shrubs / grass / flowers under the
# palms, grass + shrubs around the park perimeters, Helios outdoor planters at the building fronts.  Re-runnable
# (deletes FL_* first).  Ground = a trace that lands on L_Ground (so the road, parks, sea and buildings are avoided).
import unreal, json, os, math, random, traceback
BASE = r"F:\HOMELANDAI\CURBSIDE GRIND (CCG)\02_UEFN_WORKING_FILES\CCG_UEFN\level"
EAL = unreal.EditorAssetLibrary
ss = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
random.seed(11)
out = {"placed": {}, "rejected": {}, "missing": [], "err": []}
probe = json.load(open(os.path.join(BASE, "probe_bush.json")))["paths"]
PATH = {}
for p, names in probe.items():
    for n in names: PATH[n] = p + "/" + n
# only meshes that pass UEFN's AssetReferenceRestrictions validator (tested one-by-one with uefn_gfx_e_test*.py:
# the Asteria/Helios tropical sets, the office/outdoor planters and even new SM_PalmTree_* actors are "Disallowed
# reference" — see gfx_e_legal.json for the full pass/fail list)
SETS = {
    "shrub": ["SM_ThornBush_A", "SM_ThornBush_C", "SM_Brimstone_DeadShrub_A", "SM_ChaparralPlant_JacobsLadder", "SM_JunglePlants_IvyGroundPlant_01", "SM_JunglePlants_IvyClimbingPlant_01", "SM_JunglePlants_IvyClimbingPlant_02"],
    "grass": ["SM_Brimstone_DeadGrass_A"],   # the Artemis sidewalk grass tiles read as floating lawn slabs on the sand - dropped
    "flower": ["SM_ChaparralPlant_JacobsLadder", "SM_JunglePlants_IvyGroundPlant_01"],
    "planter": ["SM_Outdoor_FlowerBoxPot_A"],
}
TARGET = {"shrub": (90, 170), "grass": (40, 75), "flower": (50, 85), "planter": (60, 90)}   # cm height range
MESH = {}
for kind, names in SETS.items():
    MESH[kind] = []
    for n in names:
        m = EAL.load_asset(PATH[n]) if n in PATH else None
        if not m: out["missing"].append(n); continue
        b = m.get_bounds(); MESH[kind].append((m, 2 * b.box_extent.z, b.origin.z - b.box_extent.z))
ALL = {a.get_actor_label(): a for a in ss.get_all_level_actors()}
for l, a in list(ALL.items()):
    if l.startswith("FL_") or l.startswith("FLT_") or l == "L_Palm_998": ss.destroy_actor(a); ALL.pop(l)
world = unreal.EditorLevelLibrary.get_editor_world()
GROUND_OK = ("L_Ground",)
def ground(x, y, zhint, allow_road=False):
    """z of L_Ground under (x, y), else None (road / park / sea / building = rejected)."""
    hits = unreal.SystemLibrary.line_trace_multi(world, unreal.Vector(x, y, zhint + 1500), unreal.Vector(x, y, zhint - 1500), unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, True, [], unreal.DrawDebugTrace.NONE, True, unreal.LinearColor.RED, unreal.LinearColor.GREEN, 0.0)
    for h in hits:
        t = h.to_tuple()          # (blocking, initial_overlap, time, distance, location, impact_point, normal, impact_normal, phys_mat, hit_actor, ...)
        act = t[9] if len(t) > 9 else None
        try: lbl = act.get_actor_label()
        except Exception: continue
        if lbl.startswith("FD_") or lbl.startswith("DEV_") or lbl.startswith("FL_"): continue       # volumes / devices
        if lbl.startswith(GROUND_OK) or (allow_road and lbl.startswith("L_Road")): return t[5].z, lbl   # impact point
        return None, lbl
    return None, "nothing"
n_id = [0]
def place(kind, x, y, z, yaw=None, scale_mul=1.0):
    m, h, base = random.choice(MESH[kind])
    lo, hi = TARGET[kind]; target = random.uniform(lo, hi) * scale_mul
    s = target / h if h > 1 else 1.0
    a = ss.spawn_actor_from_object(m, unreal.Vector(x, y, z - base * s), unreal.Rotator(0, 0, yaw if yaw is not None else random.uniform(0, 360)))   # FortStaticMeshActor
    a.set_actor_scale3d(unreal.Vector(s, s, s)); n_id[0] += 1
    a.set_actor_label("FL_%s_%03d" % (kind, n_id[0])); a.set_folder_path("CCG/Foliage")
    out["placed"][kind] = out["placed"].get(kind, 0) + 1
    return a
def rej(kind, lbl): out["rejected"][lbl] = out["rejected"].get(lbl, 0) + 1
MAX = 700
# ---------------------------------------------------------------- 1. palm understory
try:
    for l, a in ALL.items():
        if not l.startswith("L_Palm") or n_id[0] > MAX: continue
        o, e = a.get_actor_bounds(False); px, py, pz = o.x, o.y, o.z - e.z
        for i in range(random.randint(2, 4)):
            ang = random.uniform(0, 2 * math.pi); r = random.uniform(150, 420)
            x, y = px + r * math.cos(ang), py + r * math.sin(ang)
            z, lbl = ground(x, y, pz)
            if z is None: rej("palm", lbl); continue
            place("shrub" if random.random() < 0.6 else "grass", x, y, z)
        if random.random() < 0.35:
            ang = random.uniform(0, 2 * math.pi); r = random.uniform(250, 480)
            x, y = px + r * math.cos(ang), py + r * math.sin(ang); z, lbl = ground(x, y, pz)
            if z is not None: place("flower", x, y, z)
            else: rej("palmflower", lbl)
except Exception: out["err"].append("palms " + traceback.format_exc()[-400:])
# ---------------------------------------------------------------- 2. park perimeters
try:
    for l, a in ALL.items():
        if not l.startswith("L_Park_") or n_id[0] > MAX: continue
        o, e = a.get_actor_bounds(False); zb = o.z - e.z
        edges = [((o.x - e.x, o.y - e.y), (o.x + e.x, o.y - e.y), (0, -1)), ((o.x + e.x, o.y - e.y), (o.x + e.x, o.y + e.y), (1, 0)),
                 ((o.x + e.x, o.y + e.y), (o.x - e.x, o.y + e.y), (0, 1)), ((o.x - e.x, o.y + e.y), (o.x - e.x, o.y - e.y), (-1, 0))]
        for (x0, y0), (x1, y1), (nx, ny) in edges:
            L = math.hypot(x1 - x0, y1 - y0); n = max(1, int(L / 900))
            for i in range(n):
                t = (i + random.uniform(0.2, 0.8)) / n; off = random.uniform(180, 320)
                x, y = x0 + (x1 - x0) * t + nx * off, y0 + (y1 - y0) * t + ny * off
                z, lbl = ground(x, y, zb)
                if z is None: rej("park", lbl); continue
                place("grass" if random.random() < 0.55 else ("shrub" if random.random() < 0.7 else "flower"), x, y, z)
except Exception: out["err"].append("parks " + traceback.format_exc()[-400:])
# ---------------------------------------------------------------- 3. building fronts (planters on the sidewalk)
try:
    for l, a in ALL.items():
        if not (l.startswith("L_Bldg_") or l.startswith("L_Fill_")) or n_id[0] > MAX: continue
        if random.random() > 0.55: continue
        o, e = a.get_actor_bounds(False); p = a.get_actor_location(); yaw = a.get_actor_rotation().yaw
        fwd = a.get_actor_forward_vector(); right = a.get_actor_right_vector()
        halfw = abs(right.x) * e.x + abs(right.y) * e.y
        # which way is the road?  the body extends away from the origin, so the road side is -fwd if the bounds centre is ahead
        toward = -1.0 if ((o.x - p.x) * fwd.x + (o.y - p.y) * fwd.y) > 0 else 1.0
        for side in (random.choice([-1, 1]),) if random.random() < 0.5 else (-1, 1):
            x = p.x + right.x * side * (halfw - 90) + fwd.x * toward * 70
            y = p.y + right.y * side * (halfw - 90) + fwd.y * toward * 70
            z, lbl = ground(x, y, p.z, allow_road=True)
            if z is None: rej("bldg", lbl); continue
            place("planter", x, y, z, yaw=yaw + random.uniform(-8, 8))
except Exception: out["err"].append("bldg " + traceback.format_exc()[-400:])
try: unreal.EditorLevelLibrary.save_current_level()
except Exception as ex: out["err"].append("save " + str(ex)[:100])
out["total"] = n_id[0]
json.dump(out, open(os.path.join(BASE, "gfx_e.json"), "w"), indent=1, default=str)
unreal.log("CCG_GFX_E_DONE %d" % n_id[0])
