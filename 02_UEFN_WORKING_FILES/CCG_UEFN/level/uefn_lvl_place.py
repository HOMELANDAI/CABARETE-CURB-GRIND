# UEFN Python console:  exec(open(r'C:/Users/211in/Downloads/CCG_UEFN/level/uefn_lvl_place.py').read())
# Stage 2: place every mesh actor, the Verse devices, the Fortnite devices (volumes, trigger, barrier, HUD, end game,
# buttons, granters, class designers/selectors, lights, day sequences, VFX spawners) and wire every @editable slot.
import unreal, os, json, math, traceback
BASE = r"C:\Users\211in\Downloads\CCG_UEFN\level"
LOG = open(os.path.join(BASE, "log_place.txt"), "w")
def log(*a):
    s = " ".join(str(x) for x in a); LOG.write(s + "\n"); LOG.flush(); unreal.log("CCGL " + s)
G = "/9ec1b72d-2111-4319-b015-282d94c768eb"; CCG = G + "/CCG"
EAL = unreal.EditorAssetLibrary; ss = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
reg = unreal.AssetRegistryHelpers.get_asset_registry()
P = json.load(open(os.path.join(BASE, "placements.json")))
def V(l): return unreal.Vector(l[0], l[1], l[2])
def R(rot): return unreal.Rotator(roll=rot[0], pitch=rot[1], yaw=rot[2])
def Ry(yaw): return unreal.Rotator(roll=0.0, pitch=0.0, yaw=yaw)
try:
    # ------------------------------------------------------------------ clean previous run
    for a in ss.get_all_level_actors():
        if a.get_actor_label().startswith(("L_", "DEV_", "Rider_", "FD_")): ss.destroy_actor(a)
    # ------------------------------------------------------------------ Fortnite device classes (discover by name)
    DEVKEYS = {"volume": ["VolumeDevice", "Volume_Device", "B_Device_Volume", "Volume"], "trigger": ["TriggerDevice", "Trigger"], "barrier": ["BarrierDevice", "Barrier"],
               "hud": ["HUDMessageDevice", "HudMessageDevice", "HUDMessage"], "endgame": ["EndGameDevice", "EndGame"], "button": ["ButtonDevice", "Button"],
               "granter": ["ItemGranterDevice", "ItemGranter"], "classdesigner": ["ClassDesignerDevice", "ClassDesigner"], "classselector": ["ClassAndTeamSelectorDevice", "ClassSelector", "TeamSelector"],
               "light": ["CustomizableLightDevice", "CustomizableLight"], "daysequence": ["DaySequenceDevice", "DaySequence"], "vfx": ["VFXSpawnerDevice", "VFXSpawner"], "spawn": ["PlayerSpawnerDevice", "PlayerSpawn"]}
    cands = {}
    for cls in (unreal.TopLevelAssetPath("/Script/Engine", "Blueprint"),):
        for a in reg.get_assets_by_class(cls, True):
            n = str(a.asset_name); pk = str(a.package_name)
            if "device" not in pk.lower() and "device" not in n.lower(): continue
            for k, keys in DEVKEYS.items():
                for kw in keys:
                    if kw.lower() in n.lower():
                        cands.setdefault(k, []).append((len(n), pk, n)); break
    DEVCLS = {}
    for k, lst in cands.items():
        lst.sort()
        for _, pk, n in lst:
            c = unreal.load_class(None, f"{pk}.{n}_C") or unreal.load_object(None, f"{pk}.{n}")
            if c: DEVCLS[k] = c; break
    log("device classes:", {k: str(v.get_name() if hasattr(v, 'get_name') else v) for k, v in DEVCLS.items()})
    def spawn_dev(kind, label, loc, yaw=0.0, scale=None):
        c = DEVCLS.get(kind)
        if not c: log("no class for", kind, label); return None
        a = None
        try: a = ss.spawn_actor_from_class(c, V(loc), Ry(yaw))
        except Exception:
            try: a = ss.spawn_actor_from_object(c, V(loc), Ry(yaw))
            except Exception as e: log("spawn fail", kind, label, str(e)[:120]); return None
        if a:
            a.set_actor_label(label)
            if scale: a.set_actor_scale3d(unreal.Vector(*scale))
        return a
    # ------------------------------------------------------------------ mesh actors
    meshcache = {}
    def mesh(name):
        if name not in meshcache: meshcache[name] = EAL.load_asset(f"{CCG}/Level/Meshes/{name}")
        return meshcache[name]
    signs = json.load(open(os.path.join(BASE, "signs.json")))["signs"] if os.path.exists(os.path.join(BASE, "signs.json")) else []
    def sign_mi(key):
        p = f"{CCG}/Materials/MI/MI_Sign_{key}"
        return EAL.load_asset(p) if key and EAL.does_asset_exist(p) else None
    ACT = {}
    for a in P["actors"]:
        sm = mesh(a["mesh"])
        if not sm: log("missing mesh", a["mesh"]); continue
        act = ss.spawn_actor_from_object(sm, V(a["loc"]), R(a["rot"]))
        if not act: log("spawn failed", a["label"]); continue
        act.set_actor_label("L_" + a["label"]); act.set_actor_scale3d(unreal.Vector(*a["scale"]))
        comp = act.static_mesh_component if hasattr(act, "static_mesh_component") else act.get_component_by_class(unreal.StaticMeshComponent)
        if comp and a.get("sign"):
            mi = sign_mi(a["sign"])
            if mi:
                for i, m in enumerate(comp.get_materials()):
                    if m and m.get_name() == "MI_Sign_Cabarete_Letters": comp.set_material(i, mi)
        if comp and a["mesh"] in ("SM_CCG_Ground", "SM_CCG_Sea"): comp.set_editor_property("cast_shadow", False)
        ACT[a["label"]] = act
    log("mesh actors", len(ACT), "spawned, first class", next(iter(ACT.values())).get_class().get_name() if ACT else None)
    # ------------------------------------------------------------------ Verse devices
    def verse_cls(n): return unreal.load_object(None, f"{G}/_Verse.CCG-Verse-{n}")
    def spawn_verse(n, label, loc, yaw=0.0):
        a = ss.spawn_actor_from_object(verse_cls(n), V(loc), Ry(yaw)); a.set_actor_label(label); return a
    def setp(a, name, value):
        try: a.set_editor_property(name, value); return True
        except Exception as e: log("setp fail", a.get_actor_label(), name, str(e)[:140]); return False
    spawn = next((m for m in P["devices"]["misc"] if m["kind"] == "spawn"), None)
    base = spawn["loc"] if spawn else [0, 0, 100]; byaw = spawn["yaw"] if spawn else 0.0
    def off(dx, dy, dz=0):  # offset in the start-area frame (dx along the road, dy to the right/south)
        r = math.radians(byaw); return [base[0] + dx * math.cos(r) - dy * math.sin(r), base[1] + dx * math.sin(r) + dy * math.cos(r), base[2] + dz]
    GM = spawn_verse("ccg_game_manager", "DEV_ccg_game_manager", off(-10, 10)); ST = spawn_verse("ccg_store", "DEV_ccg_store", off(-10, 13))
    TOD = spawn_verse("ccg_timeofday", "DEV_ccg_timeofday", off(-10, 16)); GR = spawn_verse("ccg_graphics", "DEV_ccg_graphics", off(-10, 19)); RS = spawn_verse("ccg_rider_select", "DEV_ccg_rider_select", off(-10, 22))
    # ------------------------------------------------------------------ Fortnite devices
    def vol(label, loc, size, yaw):
        a = spawn_dev("volume", label, loc, yaw)
        if a:
            # volume devices scale with the actor; default volume is 1 m^3 -> scale = size in metres
            try: a.set_actor_scale3d(unreal.Vector(max(0.1, size[0] / 100.0), max(0.1, size[1] / 100.0), max(0.1, size[2] / 100.0)))
            except Exception: pass
        return a
    VOLS = {}
    for v in P["devices"]["volumes"]: VOLS[v["label"]] = vol("FD_" + v["label"], v["loc"], v["size"], v["yaw"])
    misc = {m["label"]: m for m in P["devices"]["misc"]}
    trig = spawn_dev("trigger", "FD_Trig_Finish", misc["Trig_Finish"]["loc"], misc["Trig_Finish"]["yaw"], (6, 6, 3)) if "Trig_Finish" in misc else None
    bar = spawn_dev("barrier", "FD_Barrier_Vagamundo", misc["Barrier_Vagamundo"]["loc"], misc["Barrier_Vagamundo"]["yaw"], (16, 1, 4)) if "Barrier_Vagamundo" in misc else None
    hud = spawn_dev("hud", "FD_HUD", off(-10, 25)); endg = spawn_dev("endgame", "FD_EndGame", off(-10, 28))
    spawner = spawn_dev("spawn", "FD_PlayerSpawn_Start", base, byaw)
    tbtn = spawn_dev("button", "FD_Btn_Sunset", off(-6, 6, 0), byaw); fxbtn = spawn_dev("button", "FD_Btn_Effects", off(-6, -6, 0), byaw)
    dbg = [spawn_dev("button", f"FD_Btn_Debug_{i}", off(-14 + i * 1.5, -9, 0), byaw) for i in range(6)]
    day = spawn_dev("daysequence", "FD_DaySeq_Day", off(-10, 31)); sun = spawn_dev("daysequence", "FD_DaySeq_Sunset", off(-10, 34))
    # rider podiums: 7 x (class designer, selector, button)
    pods = misc.get("RiderPodiums"); CD = []; CS = []; SB = []
    for i in range(7):
        loc = off(-18 + i * 2.5, -6, 0) if not pods else [pods["loc"][0] + i * 250 * math.cos(math.radians(pods["yaw"])), pods["loc"][1] + i * 250 * math.sin(math.radians(pods["yaw"])), pods["loc"][2]]
        CD.append(spawn_dev("classdesigner", f"FD_Class_{i}", [loc[0], loc[1] - 200 * 0, loc[2] + 0], byaw)); CS.append(spawn_dev("classselector", f"FD_ClassSel_{i}", off(-18 + i * 2.5, -8, 0), byaw)); SB.append(spawn_dev("button", f"FD_Btn_Rider_{i}", off(-18 + i * 2.5, -4, 0), byaw))
    for i, c in enumerate(CD):
        if c:
            try: c.set_editor_property("class_slot", i + 1)
            except Exception: pass
    # store buttons / granters (23) along the store front
    store_act = ACT.get("Store_OceanDreamPlaza"); PB = []; PG = []
    if store_act:
        sl = store_act.get_actor_location(); syaw = store_act.get_actor_rotation().yaw; r = math.radians(syaw)
        for i in range(23):
            dx = -6 + (i % 12) * 1.0; dy = 3 + (i // 12) * 2.0
            loc = [sl.x + dx * math.cos(r) - dy * math.sin(r), sl.y + dx * math.sin(r) + dy * math.cos(r), sl.z]
            PB.append(spawn_dev("button", f"FD_Btn_Store_{i:02d}", loc, syaw)); PG.append(spawn_dev("granter", f"FD_Granter_Store_{i:02d}", [loc[0], loc[1], loc[2] - 150], syaw))
    # lights
    LIGHTS = {"flood": [], "lamp": [], "mural": []}
    def hexcol(h): h = h.lstrip("#"); return unreal.LinearColor(int(h[0:2], 16) / 255, int(h[2:4], 16) / 255, int(h[4:6], 16) / 255, 1)
    for l in P["devices"]["lights"]:
        a = spawn_dev("light", "FD_" + l["label"], l["loc"])
        if a:
            for pn, val in (("light_color", hexcol(l["color"])), ("color", hexcol(l["color"])), ("radius", float(l["radius"])), ("attenuation_radius", float(l["radius"])), ("intensity", 8.0), ("enabled_at_game_start", False), ("is_enabled_at_game_start", False), ("cast_shadows", False)):
                try: a.set_editor_property(pn, val)
                except Exception: pass
            LIGHTS.setdefault(l["kind"], []).append(a)
    spark = [spawn_dev("light", f"FD_SparkLight_{i}", off(-30, 20 + i * 3)) for i in range(2)]
    # ------------------------------------------------------------------ rails
    marker_mesh = mesh("SM_CCG_FlatBar5")  # any tiny prop would do; markers are scaled down
    RAILDEV = []
    for r_ in P["rails"]:
        pts = r_["markers"]; first = pts[0]; last = pts[-1]
        yaw = math.degrees(math.atan2(pts[1][1] - first[1], pts[1][0] - first[0])) if len(pts) > 1 else 0.0
        dev = spawn_verse("ccg_rail", "DEV_rail_" + r_["id"], [first[0], first[1], first[2] - 60], yaw)
        markers = []
        for i, p in enumerate(pts):
            m = ss.spawn_actor_from_object(marker_mesh, V(p), Ry(yaw))
            if m: m.set_actor_label(f"L_mk_{r_['id']}_{i:02d}"); m.set_actor_scale3d(unreal.Vector(0.01, 0.01, 0.01)); m.set_actor_hidden_in_game(True); markers.append(m)
        # catch volume: thin box over the first 1.5 m of the rail (whole rail for short ones)
        L = math.dist(first[:2], last[:2]); cl = min(300.0, max(150.0, L))
        cx = first[0] + (cl / 2) * math.cos(math.radians(yaw)); cy = first[1] + (cl / 2) * math.sin(math.radians(yaw))
        cv = vol(f"FD_Catch_{r_['id']}", [cx, cy, first[2] + 20], [cl, 120, 160], yaw)
        setp(dev, "RailId", r_["id"]); setp(dev, "RailPoints", markers); setp(dev, "CatchVolume", cv); setp(dev, "Manager", GM); setp(dev, "Graphics", GR); setp(dev, "UseGraphics", True)
        setp(dev, "IsSteel", bool(r_["steel"])); setp(dev, "IsSlideRail", bool(r_["slide"])); setp(dev, "IsHorseshoe", bool(r_["horseshoe"]))
        if r_.get("ride_height_cm"): setp(dev, "RideHeightCm", float(r_["ride_height_cm"]))
        if r_.get("mesh_actor") and r_["mesh_actor"] in ACT: setp(dev, "RailMesh", ACT[r_["mesh_actor"]])
        if r_["steel"] and DEVCLS.get("vfx"):
            fx = spawn_dev("vfx", f"FD_Sparks_{r_['id']}", [first[0], first[1], first[2]], yaw)
            if fx: setp(dev, "Sparks", fx)
        RAILDEV.append(dev)
    log("rails", len(RAILDEV))
    # ------------------------------------------------------------------ wiring
    def volof(k): return VOLS.get(k)
    setp(GM, "ParkZoneP1", volof("Vol_Park_P1")); setp(GM, "ParkZoneP2", volof("Vol_Park_P2")); setp(GM, "ParkZoneP3", volof("Vol_Park_P3")); setp(GM, "ParkZoneP4", volof("Vol_Park_P4"))
    setp(GM, "StoreVolume", volof("Vol_Store")); setp(GM, "SignGapVolume", volof("Vol_SignGap"))
    setp(GM, "MuralVolumes", [volof(f"Vol_Mural_{i}") for i in range(1, 7) if volof(f"Vol_Mural_{i}")])
    setp(GM, "TunnelVolumes", [v for k, v in VOLS.items() if k.startswith("Vol_Tunnel") and v])
    if trig: setp(GM, "FinishTrigger", trig)
    if bar: setp(GM, "VagamundoBarrier", bar)
    if hud: setp(GM, "Hud", hud); setp(ST, "Hud", hud); setp(RS, "Hud", hud); setp(TOD, "Hud", hud)
    if endg: setp(GM, "EndGame", endg)
    setp(GM, "Store", ST); setp(GM, "DebugTrickButtons", [b for b in dbg if b])
    setp(ST, "PurchaseButtons", [b for b in PB if b]); setp(ST, "PurchaseGranters", [g for g in PG if g])
    if fxbtn: setp(ST, "EffectToggleButton", fxbtn)
    setp(TOD, "ParkFloodlights", LIGHTS["flood"]); setp(TOD, "StreetLamps", LIGHTS["lamp"]); setp(TOD, "MuralWashLights", LIGHTS["mural"])
    if tbtn: setp(TOD, "ToggleButton", tbtn)
    if day: setp(TOD, "DaySequence", day)
    if sun: setp(TOD, "SunsetSequence", sun)
    setp(GR, "TimeOfDay", TOD); setp(GR, "SparkLights", [s for s in spark if s]); setp(GR, "MuralWashLights", LIGHTS["mural"]); setp(GR, "UseCinematicGrade", False)
    setp(RS, "ClassSlots", [c for c in CD if c]); setp(RS, "ClassSelectors", [c for c in CS if c]); setp(RS, "SelectButtons", [b for b in SB if b])
    # spawn pads from the template: move them to the start
    for a in ss.get_all_level_actors():
        if "Spawn Pad" in a.get_actor_label() or "PlayerSpawn" in a.get_class().get_name():
            if not a.get_actor_label().startswith("FD_"): a.set_actor_location(V(off(-2, 0, 20)), False, False); a.set_actor_rotation(Ry(byaw), False)
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
    log("DONE_PLACE actors", len(ACT), "rails", len(RAILDEV), "vols", len([v for v in VOLS.values() if v]), "lights", sum(len(v) for v in LIGHTS.values()))
except Exception:
    log("ERROR", traceback.format_exc())
LOG.close()
