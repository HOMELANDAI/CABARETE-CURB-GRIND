# UEFN Python console:  exec(open(r'C:/Users/211in/Downloads/CCG_UEFN/level/uefn_lvl_place2.py').read())
# Stage 2 (v2): place every mesh actor, the Verse devices, the Fortnite devices (volumes, trigger, barrier, HUD,
# end game, buttons, granters, class designers/selectors, lights, day sequences, VFX spawners) and wire every
# @editable slot.  v2 uses what the probes established about UEFN's Verse reflection:
#   * a placed Verse device is a VerseDevice_C actor; the Verse object is an inner sub-object of it
#   * @editable UE property names are  __verse_0x<bswap(crc32(utf32le(Name)))>_<Name>
#   * Verse->Verse device refs are plain object pointers to the other device's inner Verse object
#   * Verse->native device refs: the editable holds an instanced wrapper object (class volume_device etc.);
#     set its  SavedActor  to the device actor. Arrays: new_object(wrapper class, outer=verse obj) per element.
#   * []vector3 elements: arr.resize(n) then element.import_text("(__verse_.._X=..,.._Y=..,.._Z=..)")
#   * strings (VerseStringProperty) cannot be set from Python -> RailIndex:int is used instead of RailId
import unreal, os, json, math, traceback, zlib, struct
BASE = r"C:\Users\211in\Downloads\CCG_UEFN\level"
LOG = open(os.path.join(BASE, "log_place2.txt"), "w")
def log(*a):
    s = " ".join(str(x) for x in a); LOG.write(s + "\n"); LOG.flush(); unreal.log("CCGL " + s)
G = "/9ec1b72d-2111-4319-b015-282d94c768eb"; CCG = G + "/CCG"
EAL = unreal.EditorAssetLibrary; ss = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
P = json.load(open(os.path.join(BASE, "placements.json")))
def V(l): return unreal.Vector(l[0], l[1], l[2])
def R(rot): return unreal.Rotator(roll=rot[0], pitch=rot[1], yaw=rot[2])
def Ry(yaw): return unreal.Rotator(roll=0.0, pitch=0.0, yaw=yaw)
def vn(name):
    c = zlib.crc32(name.encode("utf-32-le")) & 0xffffffff
    return "__verse_0x%08X_%s" % (struct.unpack("<I", struct.pack(">I", c))[0], name)
FAILS = []
try:
    # ------------------------------------------------------------------ clean previous run
    n_del = 0
    for a in ss.get_all_level_actors():
        if a.get_actor_label().startswith(("L_", "DEV_", "Rider_", "FD_", "CCG-Verse")): ss.destroy_actor(a); n_del += 1
    log("cleaned", n_del)
    # ------------------------------------------------------------------ Fortnite device classes (verified paths)
    DEVPATH = {"volume": "/CRD_Volume/Device_Volume.Device_Volume_C", "trigger": "/CreativeCoreDevices/Device_Trigger_V2.Device_Trigger_V2_C",
               "barrier": "/CRD_VolumetricRegion/Device_Barrier_V2.Device_Barrier_V2_C", "hud": "/CreativeCoreDevices/Device_HUDMessage_V2.Device_HUDMessage_V2_C",
               "endgame": "/CRD_GameEnd/Device_GameEnd.Device_GameEnd_C", "button": "/CreativeCoreDevices/Device_Button_V2.Device_Button_V2_C",
               "granter": "/CreativeCoreDevices/Device_ItemGranter_V2.Device_ItemGranter_V2_C", "classdesigner": "/CreativeCoreDevices/Device_ClassDesigner_V2.Device_ClassDesigner_V2_C",
               "classselector": "/CreativeCoreDevices/Device_ClassSelector_V2.Device_ClassSelector_V2_C", "light": "/Game/Creative/Devices/Lights/BP_CustomizableLight.BP_CustomizableLight_C",
               "daysequence": "/Game/Creative/Devices/Lighting/BP_DaySequenceModifier_Device.BP_DaySequenceModifier_Device_C", "vfx": "/CRD_VFX_Spawner/Device_VFXSpawner_V2.Device_VFXSpawner_V2_C"}
    DEVCLS = {}
    for k, p in DEVPATH.items():
        try: DEVCLS[k] = unreal.load_class(None, p)
        except Exception as e: log("class load fail", k, str(e)[:100])
    log("device classes:", {k: (v.get_name() if v else None) for k, v in DEVCLS.items()})
    # Verse wrapper classes for native devices (used for array elements)
    WRAP = {}
    for c in unreal.ObjectIterator(unreal.Class):
        n = c.get_name()
        if n.endswith("_device") and "/_Verse" in c.get_path_name() and n not in WRAP: WRAP[n] = c
    log("wrapper classes:", sorted(WRAP.keys())[:40])
    def spawn_dev(kind, label, loc, yaw=0.0, scale=None):
        c = DEVCLS.get(kind)
        if not c: log("no class for", kind, label); return None
        try: a = ss.spawn_actor_from_class(c, V(loc), Ry(yaw))
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
    log("mesh actors", len(ACT))
    # ------------------------------------------------------------------ Verse devices
    def verse_cls(n): return unreal.load_object(None, f"{G}/_Verse.CCG-Verse-{n}")
    VDEV = []   # (actor, classname)
    def spawn_verse(n, label, loc, yaw=0.0):
        a = ss.spawn_actor_from_object(verse_cls(n), V(loc), Ry(yaw)); a.set_actor_label(label); VDEV.append((a, "CCG-Verse-" + n)); return a
    spawn = next((m for m in P["devices"]["misc"] if m["kind"] == "spawn"), None)
    base = spawn["loc"] if spawn else [0, 0, 100]; byaw = spawn["yaw"] if spawn else 0.0
    def off(dx, dy, dz=0):
        r = math.radians(byaw); return [base[0] + dx * math.cos(r) - dy * math.sin(r), base[1] + dx * math.sin(r) + dy * math.cos(r), base[2] + dz]
    GM = spawn_verse("ccg_game_manager", "DEV_ccg_game_manager", off(-10, 10)); ST = spawn_verse("ccg_store", "DEV_ccg_store", off(-10, 13))
    TOD = spawn_verse("ccg_timeofday", "DEV_ccg_timeofday", off(-10, 16)); GR = spawn_verse("ccg_graphics", "DEV_ccg_graphics", off(-10, 19)); RS = spawn_verse("ccg_rider_select", "DEV_ccg_rider_select", off(-10, 22))
    # ------------------------------------------------------------------ Fortnite devices
    def vol(label, loc, size, yaw):
        a = spawn_dev("volume", label, loc, yaw)
        if a:
            try: a.set_actor_scale3d(unreal.Vector(max(0.1, size[0] / 100.0), max(0.1, size[1] / 100.0), max(0.1, size[2] / 100.0)))
            except Exception: pass
        return a
    VOLS = {}
    for v in P["devices"]["volumes"]: VOLS[v["label"]] = vol("FD_" + v["label"], v["loc"], v["size"], v["yaw"])
    misc = {m["label"]: m for m in P["devices"]["misc"]}
    trig = spawn_dev("trigger", "FD_Trig_Finish", misc["Trig_Finish"]["loc"], misc["Trig_Finish"]["yaw"], (6, 6, 3)) if "Trig_Finish" in misc else None
    bar = spawn_dev("barrier", "FD_Barrier_Vagamundo", misc["Barrier_Vagamundo"]["loc"], misc["Barrier_Vagamundo"]["yaw"], (16, 1, 4)) if "Barrier_Vagamundo" in misc else None
    hud = spawn_dev("hud", "FD_HUD", off(-10, 25)); endg = spawn_dev("endgame", "FD_EndGame", off(-10, 28))
    tbtn = spawn_dev("button", "FD_Btn_Sunset", off(-6, 6, 0), byaw); fxbtn = spawn_dev("button", "FD_Btn_Effects", off(-6, -6, 0), byaw)
    dbg = [spawn_dev("button", f"FD_Btn_Debug_{i}", off(-14 + i * 1.5, -9, 0), byaw) for i in range(6)]
    day = spawn_dev("daysequence", "FD_DaySeq_Day", off(-10, 31)); sun = spawn_dev("daysequence", "FD_DaySeq_Sunset", off(-10, 34))
    pods = misc.get("RiderPodiums"); CD = []; CS = []; SB = []
    for i in range(7):
        loc = off(-18 + i * 2.5, -6, 0) if not pods else [pods["loc"][0] + i * 250 * math.cos(math.radians(pods["yaw"])), pods["loc"][1] + i * 250 * math.sin(math.radians(pods["yaw"])), pods["loc"][2]]
        CD.append(spawn_dev("classdesigner", f"FD_Class_{i}", loc, byaw)); CS.append(spawn_dev("classselector", f"FD_ClassSel_{i}", off(-18 + i * 2.5, -8, 0), byaw)); SB.append(spawn_dev("button", f"FD_Btn_Rider_{i}", off(-18 + i * 2.5, -4, 0), byaw))
    for i, c in enumerate(CD):
        if c:
            for pn in ("class_slot", "ClassSlot", "Class Slot"):
                try: c.set_editor_property(pn, i + 1); break
                except Exception: pass
    store_act = ACT.get("Store_OceanDreamPlaza"); PB = []; PG = []
    if store_act:
        sl = store_act.get_actor_location(); syaw = store_act.get_actor_rotation().yaw; r = math.radians(syaw)
        for i in range(23):
            dx = -6 + (i % 12) * 1.0; dy = 3 + (i // 12) * 2.0
            loc = [sl.x + dx * math.cos(r) - dy * math.sin(r), sl.y + dx * math.sin(r) + dy * math.cos(r), sl.z]
            PB.append(spawn_dev("button", f"FD_Btn_Store_{i:02d}", loc, syaw)); PG.append(spawn_dev("granter", f"FD_Granter_Store_{i:02d}", [loc[0], loc[1], loc[2] - 150], syaw))
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
    # ------------------------------------------------------------------ rails (no marker props: RailPoints are world vector3s)
    RAILS = []   # (dev, railinfo, catch, fx)
    for r_ in P["rails"]:
        pts = r_["markers"]; first = pts[0]; last = pts[-1]
        yaw = math.degrees(math.atan2(pts[1][1] - first[1], pts[1][0] - first[0])) if len(pts) > 1 else 0.0
        dev = spawn_verse("ccg_rail", "DEV_rail_" + r_["id"], [first[0], first[1], first[2] - 60], yaw)
        L = math.dist(first[:2], last[:2]); cl = min(300.0, max(150.0, L))
        cx = first[0] + (cl / 2) * math.cos(math.radians(yaw)); cy = first[1] + (cl / 2) * math.sin(math.radians(yaw))
        cv = vol(f"FD_Catch_{r_['id']}", [cx, cy, first[2] + 20], [cl, 120, 160], yaw)
        fx = spawn_dev("vfx", f"FD_Sparks_{r_['id']}", [first[0], first[1], first[2]], yaw) if r_["steel"] else None
        RAILS.append((dev, r_, cv, fx))
    log("rails", len(RAILS))
    # ------------------------------------------------------------------ resolve the inner Verse objects (one pass)
    actor_set = {a: cn for a, cn in VDEV}
    INNER = {}
    for o in unreal.ObjectIterator():
        try:
            outer = o.get_outer()
            if outer in actor_set and o.get_class().get_name() == actor_set[outer]: INNER[outer] = o
        except Exception: pass
    log("inner verse objects", len(INNER), "of", len(VDEV))
    def VO(actor): return INNER.get(actor)
    # ------------------------------------------------------------------ setters
    def set_prim(actor, name, value):
        try: VO(actor).set_editor_property(vn(name), value); return True
        except Exception as e: FAILS.append((actor.get_actor_label(), name, str(e)[:120])); return False
    def set_vref(actor, name, other):      # Verse device -> Verse device
        if other is None: return False
        try: VO(actor).set_editor_property(vn(name), VO(other)); return True
        except Exception as e: FAILS.append((actor.get_actor_label(), name, str(e)[:120])); return False
    def set_nref(actor, name, dev_actor):  # Verse device -> native Fortnite device (single)
        if dev_actor is None: return False
        try:
            sub = VO(actor).get_editor_property(vn(name)); sub.set_editor_property("SavedActor", dev_actor); return True
        except Exception as e: FAILS.append((actor.get_actor_label(), name, str(e)[:120])); return False
    def set_narr(actor, name, wrapper, dev_actors):  # Verse device -> []native device
        dev_actors = [d for d in dev_actors if d]
        try:
            vo = VO(actor); W = WRAP.get(wrapper)
            if not W: FAILS.append((actor.get_actor_label(), name, "no wrapper class " + wrapper)); return False
            arr = vo.get_editor_property(vn(name))
            while len(arr): arr.pop()
            for d in dev_actors:
                n = unreal.new_object(W, vo); n.set_editor_property("SavedActor", d); arr.append(n)
            vo.set_editor_property(vn(name), arr); return True
        except Exception as e: FAILS.append((actor.get_actor_label(), name, str(e)[:160])); return False
    def set_v3arr(actor, name, points):
        try:
            vo = VO(actor); arr = vo.get_editor_property(vn(name)); arr.resize(len(points))
            for i, p in enumerate(points):
                e = arr[i].copy(); e.import_text("(%s=%f,%s=%f,%s=%f)" % (vn("X"), p[0], vn("Y"), p[1], vn("Z"), p[2])); arr[i] = e
            vo.set_editor_property(vn(name), arr); return True
        except Exception as e: FAILS.append((actor.get_actor_label(), name, str(e)[:160])); return False
    # ------------------------------------------------------------------ wiring
    for idx, (dev, r_, cv, fx) in enumerate(RAILS):
        set_prim(dev, "RailIndex", idx); set_v3arr(dev, "RailPoints", r_["markers"]); set_nref(dev, "CatchVolume", cv)
        set_vref(dev, "Manager", GM); set_vref(dev, "Graphics", GR); set_prim(dev, "UseGraphics", True)
        set_prim(dev, "IsSteel", bool(r_["steel"])); set_prim(dev, "IsSlideRail", bool(r_["slide"])); set_prim(dev, "IsHorseshoe", bool(r_["horseshoe"]))
        if r_.get("ride_height_cm"): set_prim(dev, "RideHeightCm", float(r_["ride_height_cm"]))
        if fx: set_nref(dev, "Sparks", fx)
    def volof(k): return VOLS.get(k)
    set_nref(GM, "ParkZoneP1", volof("Vol_Park_P1")); set_nref(GM, "ParkZoneP2", volof("Vol_Park_P2")); set_nref(GM, "ParkZoneP3", volof("Vol_Park_P3")); set_nref(GM, "ParkZoneP4", volof("Vol_Park_P4"))
    set_nref(GM, "StoreVolume", volof("Vol_Store")); set_nref(GM, "SignGapVolume", volof("Vol_SignGap"))
    set_narr(GM, "MuralVolumes", "volume_device", [volof(f"Vol_Mural_{i}") for i in range(1, 7)])
    set_narr(GM, "TunnelVolumes", "volume_device", [v for k, v in VOLS.items() if k.startswith("Vol_Tunnel")])
    set_nref(GM, "FinishTrigger", trig); set_nref(GM, "VagamundoBarrier", bar)
    set_nref(GM, "Hud", hud); set_nref(ST, "Hud", hud); set_nref(RS, "Hud", hud); set_nref(TOD, "Hud", hud)
    set_nref(GM, "EndGame", endg)
    set_vref(GM, "Store", ST); set_narr(GM, "DebugTrickButtons", "button_device", dbg)
    set_narr(ST, "PurchaseButtons", "button_device", PB); set_narr(ST, "PurchaseGranters", "item_granter_device", PG)
    set_nref(ST, "EffectToggleButton", fxbtn)
    set_narr(TOD, "ParkFloodlights", "customizable_light_device", LIGHTS["flood"]); set_narr(TOD, "StreetLamps", "customizable_light_device", LIGHTS["lamp"]); set_narr(TOD, "MuralWashLights", "customizable_light_device", LIGHTS["mural"])
    set_nref(TOD, "ToggleButton", tbtn); set_nref(TOD, "DaySequence", day); set_nref(TOD, "SunsetSequence", sun)
    set_vref(GR, "TimeOfDay", TOD); set_narr(GR, "SparkLights", "customizable_light_device", spark); set_narr(GR, "MuralWashLights", "customizable_light_device", LIGHTS["mural"]); set_prim(GR, "UseCinematicGrade", False)
    set_narr(RS, "ClassSlots", "class_designer_device", CD); set_narr(RS, "ClassSelectors", "class_and_team_selector_device", CS); set_narr(RS, "SelectButtons", "button_device", SB)
    # spawn pads from the template: move them to the start
    for a in ss.get_all_level_actors():
        if "Spawn Pad" in a.get_actor_label() or "PlayerSpawn" in a.get_class().get_name():
            if not a.get_actor_label().startswith("FD_"): a.set_actor_location(V(off(-2, 0, 20)), False, False); a.set_actor_rotation(Ry(byaw), False)
    for f in FAILS[:80]: log("FAIL", *f)
    log("fails total", len(FAILS))
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
    log("DONE_PLACE2 actors", len(ACT), "rails", len(RAILS), "vols", len([v for v in VOLS.values() if v]), "lights", sum(len(v) for v in LIGHTS.values()), "verse", len(VDEV))
except Exception:
    log("ERROR", traceback.format_exc())
LOG.close()
