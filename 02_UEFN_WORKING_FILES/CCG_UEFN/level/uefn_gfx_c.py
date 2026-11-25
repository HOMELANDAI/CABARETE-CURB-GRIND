# exec(open(r'F:/HOMELANDAI/CURBSIDE GRIND (CCG)/02_UEFN_WORKING_FILES/CCG_UEFN/level/uefn_gfx_c.py').read())
# Graphics Tier B (part 2): Environment Light Rig (DirectionalLight, SkyAtmosphere, SkyLight, ExponentialHeightFog,
# VolumetricCloud) authored at the noon state, plus LS_CCG_Sunset (6 s @ 30 fps, frames 0..180) keying every rig actor
# and the post-process grade from noon to sunset (UEFN_GRAPHICS.md 2b / 3).  A cinematic_sequence_device plays it and is
# wired into ccg_graphics.SunsetSequence.  Steps via CCG_GFXC env: rig,seq,device,tod,probe
import unreal, json, os, zlib, struct, traceback
STEPS = os.environ.get("CCG_GFXC", "rig,seq,device,tod").split(",")
BASE = r"F:\HOMELANDAI\CURBSIDE GRIND (CCG)\02_UEFN_WORKING_FILES\CCG_UEFN\level"
G = "/9ec1b72d-2111-4319-b015-282d94c768eb"
GC = G + "/CCG"
EAL = unreal.EditorAssetLibrary; AT = unreal.AssetToolsHelpers.get_asset_tools()
ss = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
MSE = unreal.MovieSceneSequenceExtensions
TU = getattr(unreal, "MovieSceneTimeUnit", None) or getattr(unreal, "SequenceTimeUnit", None)
out = {"rig": {}, "seq": {}, "device": {}, "tod": {}, "err": [], "warn": []}
def col(h, a=1.0):
    h = h.lstrip("#"); return unreal.LinearColor(int(h[0:2], 16) / 255.0, int(h[2:4], 16) / 255.0, int(h[4:6], 16) / 255.0, a)
def fcol(h): c = col(h); return unreal.Color(int(c.r * 255), int(c.g * 255), int(c.b * 255), 255)
def setp(o, d, tag):
    ok = []
    for k, v in d.items():
        try: o.set_editor_property(k, v); ok.append(k)
        except Exception as e: out["warn"].append((tag, k, str(e)[:100]))
    return ok
def vn(name):
    c = zlib.crc32(name.encode("utf-32-le")) & 0xffffffff
    return "__verse_0x%08X_%s" % (struct.unpack("<I", struct.pack(">I", c))[0], name)
ALL = {a.get_actor_label(): a for a in ss.get_all_level_actors()}
RIG_FOLDER = "CCG/LightRig"
ORIGIN = unreal.Vector(0, 0, 400)

# ---------------------------------------------------------------- 1. rig actors at the noon state
def get_or_spawn(label, cls, loc=ORIGIN, rot=unreal.Rotator(0, 0, 0)):
    a = ALL.get(label)
    if not a:
        a = ss.spawn_actor_from_class(cls, loc, rot); a.set_actor_label(label); ALL[label] = a
    a.set_folder_path(RIG_FOLDER); a.modify()
    return a
if "rig" in STEPS:
    try:
        sun = get_or_spawn("LR_Sun", unreal.DirectionalLight, ORIGIN, unreal.Rotator(0.0, -62.0, 150.0))  # Rotator(roll, pitch, yaw)
        sun.set_actor_rotation(unreal.Rotator(0.0, -62.0, 150.0), False)
        sc = sun.get_component_by_class(unreal.DirectionalLightComponent)
        out["rig"]["sun"] = setp(sc, {"intensity": 6.0, "use_temperature": True, "temperature": 6200.0, "light_source_angle": 0.55,
                                      "volumetric_scattering_intensity": 0.2, "bloom_scale": 0.15, "enable_light_shaft_bloom": True, "enable_light_shaft_occlusion": True,
                                      "atmosphere_sun_light": True, "cast_shadows": True, "dynamic_shadow_distance_movable_light": 12000.0,
                                      "dynamic_shadow_cascades": 4, "cascade_distribution_exponent": 2.5, "shadow_bias": 0.4, "cast_volumetric_shadow": True,
                                      "cast_cloud_shadows": True, "cloud_shadow_strength": 0.6, "bloom_threshold": 0.9}, "sun")
        sc.set_mobility(unreal.ComponentMobility.MOVABLE)
        sky = get_or_spawn("LR_SkyAtmosphere", unreal.SkyAtmosphere)
        skc = sky.get_component_by_class(unreal.SkyAtmosphereComponent)
        out["rig"]["skyatmo"] = setp(skc, {"rayleigh_scattering_scale": 0.0331, "mie_scattering_scale": 0.004, "mie_anisotropy": 0.8, "mie_absorption_scale": 0.0,
                                           "multi_scattering_factor": 1.0, "aerial_pespective_view_distance_scale": 1.0, "ground_albedo": fcol("#5C6F7A"),
                                           "height_fog_contribution": 0.6}, "skyatmo")
        skl = get_or_spawn("LR_SkyLight", unreal.SkyLight)
        slc = skl.get_component_by_class(unreal.SkyLightComponent)
        out["rig"]["skylight"] = setp(slc, {"real_time_capture": True, "intensity": 1.0, "light_color": fcol("#DDEBFF"), "lower_hemisphere_color": col("#2A2A2A"),
                                            "lower_hemisphere_is_black": False, "cast_shadows": True, "volumetric_scattering_intensity": 1.0}, "skylight")
        slc.set_mobility(unreal.ComponentMobility.MOVABLE)
        fog = get_or_spawn("LR_Fog", unreal.ExponentialHeightFog, unreal.Vector(0, 0, 0))
        fc = fog.get_component_by_class(unreal.ExponentialHeightFogComponent)
        out["rig"]["fog"] = setp(fc, {"fog_density": 0.006, "fog_height_falloff": 0.6, "start_distance": 1500.0, "fog_max_opacity": 0.3,
                                      "fog_inscattering_luminance": col("#DDEAF5"), "directional_inscattering_luminance": col("#FFFFFF"),
                                      "directional_inscattering_exponent": 4.0, "enable_volumetric_fog": True, "volumetric_fog_scattering_distribution": 0.6,
                                      "volumetric_fog_albedo": fcol("#FFFFFF"), "volumetric_fog_extinction_scale": 0.6, "volumetric_fog_distance": 9000.0,
                                      "second_fog_data": unreal.ExponentialHeightFogData(fog_density=0.0, fog_height_falloff=0.8, fog_height_offset=0.0)}, "fog")
        # Volumetric Cloud: UEFN validation rejects the actor's default /Engine cloud material + tracing overrides -> not used
        # (the Day Sequence cloud layer stays; the rig only owns sun / sky / skylight / fog)
        if "LR_Clouds" in ALL:
            ss.destroy_actor(ALL.pop("LR_Clouds")); out["rig"]["clouds"] = "removed (illegal engine material reference in UEFN)"
        out["rig"]["labels"] = [sun.get_actor_label(), sky.get_actor_label(), skl.get_actor_label(), fog.get_actor_label()]
    except Exception: out["err"].append("rig " + traceback.format_exc()[-500:])

# ---------------------------------------------------------------- 2. LS_CCG_Sunset
def key_float(binding, prop, k0, k1, path=None):
    tr = binding.add_track(unreal.MovieSceneFloatTrack); tr.set_property_name_and_path(prop, path or prop)
    sec = tr.add_section(); sec.set_range(0, 180)
    ch = sec.get_all_channels()[0]
    ch.add_key(unreal.FrameNumber(0), float(k0), 0.0, TU.DISPLAY_RATE, unreal.MovieSceneKeyInterpolation.AUTO)
    ch.add_key(unreal.FrameNumber(180), float(k1), 0.0, TU.DISPLAY_RATE, unreal.MovieSceneKeyInterpolation.AUTO)
    return tr
def key_color(binding, prop, c0, c1, path=None):
    tr = binding.add_track(unreal.MovieSceneColorTrack); tr.set_property_name_and_path(prop, path or prop)
    sec = tr.add_section(); sec.set_range(0, 180)
    chs = sec.get_all_channels()
    for ch, a, b in zip(chs, (c0.r, c0.g, c0.b, c0.a), (c1.r, c1.g, c1.b, c1.a)):
        ch.add_key(unreal.FrameNumber(0), float(a), 0.0, TU.DISPLAY_RATE, unreal.MovieSceneKeyInterpolation.AUTO)
        ch.add_key(unreal.FrameNumber(180), float(b), 0.0, TU.DISPLAY_RATE, unreal.MovieSceneKeyInterpolation.AUTO)
    return tr
def key_bool(binding, prop, b0, b1, path=None):
    tr = binding.add_track(unreal.MovieSceneBoolTrack); tr.set_property_name_and_path(prop, path or prop)
    sec = tr.add_section(); sec.set_range(0, 180)
    ch = sec.get_all_channels()[0]
    ch.add_key(unreal.FrameNumber(0), bool(b0), 0.0, TU.DISPLAY_RATE)
    return tr
def bind_comp(seq, actor, comp):
    ab = seq.add_possessable(actor); cb = seq.add_possessable(comp)
    try: cb.set_parent(ab)
    except Exception as e: out["warn"].append(("set_parent", str(e)[:80]))
    return ab, cb
if "seq" in STEPS:
    try:
        spath = f"{GC}/Sequences/LS_CCG_Sunset"
        seq = EAL.load_asset(spath) if EAL.does_asset_exist(spath) else None
        if seq:   # reuse (the cinematic device already references it) - strip every binding / track first
            for b in list(seq.get_bindings()):
                try: b.remove()
                except Exception as e: out["warn"].append(("binding remove", str(e)[:80]))
            for t in list(seq.get_tracks()):
                try: seq.remove_track(t)
                except Exception: pass
        else:
            seq = AT.create_asset("LS_CCG_Sunset", f"{GC}/Sequences", unreal.LevelSequence, unreal.LevelSequenceFactoryNew())
        seq.set_display_rate(unreal.FrameRate(30, 1)); seq.set_playback_start(0); seq.set_playback_end(180)
        seq.set_work_range_start(0.0); seq.set_work_range_end(6.0); seq.set_view_range_start(0.0); seq.set_view_range_end(6.0)
        ntr = 0
        sun = ALL["LR_Sun"]; sc = sun.get_component_by_class(unreal.DirectionalLightComponent)
        ab, cb = bind_comp(seq, sun, sc)
        # transform: Rotator(pitch -62 -> -6, yaw 150 -> 262); channel order Loc XYZ, Rot XYZ (roll,pitch,yaw), Scale XYZ
        tt = ab.add_track(unreal.MovieScene3DTransformTrack); ts = tt.add_section(); ts.set_range(0, 180)
        chs = ts.get_all_channels(); loc = sun.get_actor_location()
        vals0 = [loc.x, loc.y, loc.z, 0.0, -62.0, 150.0, 1.0, 1.0, 1.0]; vals1 = [loc.x, loc.y, loc.z, 0.0, -6.0, 262.0, 1.0, 1.0, 1.0]
        for ch, a, b in zip(chs, vals0, vals1):
            ch.add_key(unreal.FrameNumber(0), float(a), 0.0, TU.DISPLAY_RATE, unreal.MovieSceneKeyInterpolation.AUTO)
            ch.add_key(unreal.FrameNumber(180), float(b), 0.0, TU.DISPLAY_RATE, unreal.MovieSceneKeyInterpolation.AUTO)
        ntr += 1
        for p, a, b in (("Intensity", 6.0, 5.0), ("Temperature", 6200.0, 2900.0), ("LightSourceAngle", 0.55, 1.2), ("VolumetricScatteringIntensity", 0.2, 0.9), ("BloomScale", 0.15, 2.5)):
            key_float(cb, p, a, b); ntr += 1
        key_bool(cb, "bEnableLightShaftOcclusion", True, True); ntr += 1
        # sky atmosphere
        sky = ALL["LR_SkyAtmosphere"]; skc = sky.get_component_by_class(unreal.SkyAtmosphereComponent); ab, cb = bind_comp(seq, sky, skc)
        for p, a, b in (("MieScatteringScale", 0.004, 0.012), ("MieAbsorptionScale", 0.0, 0.002), ("AerialPespectiveViewDistanceScale", 1.0, 1.4), ("MieAnisotropy", 0.8, 0.85)):
            key_float(cb, p, a, b); ntr += 1
        # sky light
        skl = ALL["LR_SkyLight"]; slc = skl.get_component_by_class(unreal.SkyLightComponent); ab, cb = bind_comp(seq, skl, slc)
        key_float(cb, "Intensity", 1.0, 0.6); key_color(cb, "LightColor", col("#DDEBFF"), col("#8A6AA8")); ntr += 2
        # fog
        fog = ALL["LR_Fog"]; fc = fog.get_component_by_class(unreal.ExponentialHeightFogComponent); ab, cb = bind_comp(seq, fog, fc)
        for p, a, b in (("FogDensity", 0.006, 0.02), ("FogHeightFalloff", 0.6, 0.4), ("StartDistance", 1500.0, 300.0), ("FogMaxOpacity", 0.3, 0.5),
                        ("DirectionalInscatteringExponent", 4.0, 8.0), ("VolumetricFogExtinctionScale", 0.6, 1.0)):
            key_float(cb, p, a, b); ntr += 1
        key_color(cb, "FogInscatteringLuminance", col("#DDEAF5"), col("#E89A6B")); key_color(cb, "DirectionalInscatteringLuminance", col("#FFFFFF"), col("#FFB347")); ntr += 2
        key_float(cb, "SecondFogData.FogDensity", 0.0, 0.004, "SecondFogData.FogDensity"); ntr += 1
        # post-process grade (section 3) — struct members by path
        ppv = ALL.get("PP_CCG_Grade")
        if ppv:
            pb = seq.add_possessable(ppv)
            for p, a, b in (("BloomIntensity", 0.35, 0.7), ("BloomThreshold", 1.0, 0.6), ("VignetteIntensity", 0.3, 0.35), ("LensFlareIntensity", 0.0, 0.25),
                            ("AutoExposureBias", 0.0, -0.4), ("WhiteTemp", 6200.0, 5600.0)):
                key_float(pb, p, a, b, "Settings." + p); ntr += 1
            try:
                s = ppv.get_editor_property("settings")
                for k in ("bloom_intensity", "bloom_threshold", "vignette_intensity", "lens_flare_intensity", "auto_exposure_bias", "white_temp"): s.set_editor_property("override_" + k, True)
                ppv.set_editor_property("settings", s)
            except Exception as e: out["warn"].append(("ppv override", str(e)[:100]))
        else: out["warn"].append(("ppv", "PP_CCG_Grade not found"))
        EAL.save_loaded_asset(seq); EAL.save_directory(f"{GC}/Sequences")
        out["seq"] = {"path": spath, "tracks": ntr, "bindings": len(seq.get_bindings()), "rate": str(seq.get_display_rate().numerator), "end": seq.get_playback_end()}
    except Exception: out["err"].append("seq " + traceback.format_exc()[-600:])

# ---------------------------------------------------------------- 3. cinematic sequence device + Verse wiring
if "device" in STEPS:
    try:
        cls = unreal.load_class(None, "/CRD_CinematicSequence/Device_CinematicSequence.Device_CinematicSequence_C")
        dev = ALL.get("FD_Seq_Sunset") or ss.spawn_actor_from_class(cls, unreal.Vector(-900, -700, 180))
        dev.set_actor_label("FD_Seq_Sunset"); dev.set_folder_path(RIG_FOLDER); ALL["FD_Seq_Sunset"] = dev
        seq = EAL.load_asset(f"{GC}/Sequences/LS_CCG_Sunset")
        try:
            for pname in ("Sequence", "LevelSequence", "SequenceToPlay", "CinematicSequence"):
                try: dev.set_editor_property(pname, seq); out["device"]["seq_prop"] = pname; break
                except Exception: pass
        except Exception as e: out["warn"].append(("seq prop", str(e)[:100]))
        for k, v in (("AutoPlay", False), ("bAutoPlay", False), ("Loop Playback", False), ("LoopPlayback", False), ("bLoop", False), ("bLooping", False),
                     ("Visibility", None), ("Enabled On Phase", None)):
            if v is None: continue
            try: dev.set_editor_property(k, v); out["device"].setdefault("set", []).append(k)
            except Exception: pass
        # dump the device's editable names once so the next pass can refine (visibility = Everyone etc.)
        out["device"]["class"] = str(dev.get_class().get_name())
        # Verse: ccg_graphics.SunsetSequence
        GR = ALL["DEV_ccg_graphics"]
        def inner(actor, cn):
            for ob in unreal.ObjectIterator():
                try:
                    if ob.get_outer() == actor and ob.get_class().get_name() == cn: return ob
                except Exception: pass
        gr = inner(GR, "CCG-Verse-ccg_graphics")
        if gr:
            try:
                sub = gr.get_editor_property(vn("SunsetSequence")); sub.set_editor_property("SavedActor", dev); out["device"]["verse"] = "SunsetSequence -> FD_Seq_Sunset"
            except Exception as e: out["warn"].append(("verse SunsetSequence", str(e)[:140]))
            try:
                gr.set_editor_property(vn("UseCinematicGrade"), True)
            except Exception as e: out["warn"].append(("UseCinematicGrade", str(e)[:100]))
        else: out["warn"].append(("verse", "inner ccg_graphics object not found"))
    except Exception: out["err"].append("device " + traceback.format_exc()[-500:])

# ---------------------------------------------------------------- 4. world settings: let the rig own the sky
if "tod" in STEPS:
    try:
        w = unreal.EditorLevelLibrary.get_editor_world(); wsx = w.get_world_settings()
        out["tod"]["class"] = str(wsx.get_class().get_name()); done = None
        for k in ("DisableAllTimeOfDayManagers", "bDisableAllTimeOfDayManagers", "disable_all_time_of_day_managers", "Disable All Time of Day Managers"):
            try: wsx.set_editor_property(k, True); done = k; break
            except Exception: pass
        out["tod"]["set"] = done
        if not done:
            # look for the property by name among the world settings' editor properties
            cands = [str(n) for n in dir(wsx) if "time" in str(n).lower() or "tod" in str(n).lower()]
            out["tod"]["candidates"] = cands[:40]
    except Exception: out["err"].append("tod " + traceback.format_exc()[-400:])

try: unreal.EditorLevelLibrary.save_current_level()
except Exception as e: out["warn"].append(("save level", str(e)[:120]))
json.dump(out, open(os.path.join(BASE, "gfx_c.json"), "w"), indent=1, default=str)
unreal.log("CCG_GFX_C_DONE err=%d warn=%d" % (len(out["err"]), len(out["warn"])))
