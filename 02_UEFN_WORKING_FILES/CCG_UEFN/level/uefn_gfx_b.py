# exec(open(r'C:/Users/211in/Downloads/CCG_UEFN/level/uefn_gfx_b.py').read())
# Graphics Tier B (part 1): Fortnite gallery palms in place of the procedural palm meshes, an animated water material
# for the bay plane, and BumpOffset parallax (+ QualitySwitch) in the environment master material.
import unreal, json, random, traceback, os
os.environ.setdefault("CCG_GFXB", "palms,water,parallax")
STEPS = os.environ["CCG_GFXB"].split(",")
G = "/9ec1b72d-2111-4319-b015-282d94c768eb/CCG"
EAL = unreal.EditorAssetLibrary; MEL = unreal.MaterialEditingLibrary; AT = unreal.AssetToolsHelpers.get_asset_tools()
ss = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
reg = unreal.AssetRegistryHelpers.get_asset_registry()
out = {"palms": {}, "water": {}, "parallax": {}, "err": []}
random.seed(7)

def comp(a):
    return a.static_mesh_component if hasattr(a, "static_mesh_component") else a.get_component_by_class(unreal.StaticMeshComponent)

# ---------------------------------------------------------------- 1. palms
if "palms" in STEPS:
    try:
        PALMS = [EAL.load_asset(f"/Game/Environments/Props/Trees/Meshes/SM_PalmTree_{k}") for k in "ABC"]
        PALMS = [p for p in PALMS if p]
        heights = {}
        for p in PALMS:
            b = p.get_bounds(); heights[p.get_name()] = (2 * b.box_extent.z, b.origin.z - b.box_extent.z)
        out["palms"]["gallery"] = heights
        n = 0; skipped = 0
        for a in ss.get_all_level_actors():
            l = a.get_actor_label()
            if not l.startswith("L_Palm"): continue
            c = comp(a)
            if not c or not PALMS: skipped += 1; continue
            old_o, old_e = a.get_actor_bounds(False)
            old_h = 2 * old_e.z; base_z = old_o.z - old_e.z
            p = random.choice(PALMS); ph, pbase = heights[p.get_name()]
            target = max(700.0, min(1300.0, old_h * random.uniform(0.95, 1.15)))
            s = target / ph if ph > 1 else 1.0
            c.set_static_mesh(p)
            rot = a.get_actor_rotation(); rot.yaw = random.uniform(0, 360); rot.roll = random.uniform(-3, 3); rot.pitch = random.uniform(-3, 3)
            a.set_actor_rotation(rot, False)
            a.set_actor_scale3d(unreal.Vector(s, s, s))
            loc = a.get_actor_location(); loc.z = base_z - pbase * s; a.set_actor_location(loc, False, False)
            n += 1
        out["palms"]["replaced"] = n; out["palms"]["skipped"] = skipped
    except Exception: out["err"].append("palms " + traceback.format_exc()[-400:])

# ---------------------------------------------------------------- 2. water
if "water" in STEPS:
    try:
        # find a water normal map in the Fortnite content
        wn = None
        f = unreal.ARFilter(class_names=["Texture2D"], recursive_paths=True, package_paths=["/Game/Environments", "/Game/Athena", "/Game/Effects"])
        cands = []
        for a in reg.get_assets(f):
            nm = str(a.asset_name).lower()
            if "water" in nm and ("_n" in nm or "normal" in nm) and "wave" in nm or nm.startswith("t_water_n") or nm in ("t_water_normal", "t_waternormal_01", "t_ocean_n"):
                cands.append(str(a.package_name))
            elif "water" in nm and nm.endswith("_n"):
                cands.append(str(a.package_name))
            if len(cands) > 12: break
        out["water"]["normal_candidates"] = cands
        wn = EAL.load_asset(cands[0]) if cands else EAL.load_asset(f"{G}/Materials/T_Sand_Cabarete_N")
        mpath = f"{G}/Materials/M_CCG_Water"
        if EAL.does_asset_exist(mpath): mat = EAL.load_asset(mpath); MEL.delete_all_material_expressions(mat)
        else: mat = AT.create_asset("M_CCG_Water", f"{G}/Materials", unreal.Material, unreal.MaterialFactoryNew())
        mat.set_editor_property("used_with_nanite", True)
        def node(cls, x, y): return MEL.create_material_expression(mat, cls, x, y)
        def scalar(name, v, x, y):
            n_ = node(unreal.MaterialExpressionScalarParameter, x, y); n_.set_editor_property("parameter_name", name); n_.set_editor_property("default_value", v); return n_
        def vec(name, c, x, y):
            n_ = node(unreal.MaterialExpressionVectorParameter, x, y); n_.set_editor_property("parameter_name", name); n_.set_editor_property("default_value", unreal.LinearColor(*c)); return n_
        # world-aligned UVs (the sea plane is one big mesh)
        wp = node(unreal.MaterialExpressionWorldPosition, -1500, 0)
        mask = node(unreal.MaterialExpressionComponentMask, -1300, 0); mask.set_editor_property("r", True); mask.set_editor_property("g", True); mask.set_editor_property("b", False)
        MEL.connect_material_expressions(wp, "", mask, "")
        tile = scalar("WaveTile", 1.0 / 900.0, -1300, 120)   # 9 m waves
        uv = node(unreal.MaterialExpressionMultiply, -1100, 40); MEL.connect_material_expressions(mask, "", uv, "A"); MEL.connect_material_expressions(tile, "", uv, "B")
        spd = scalar("WaveSpeed", 0.03, -1100, 200)
        p1 = node(unreal.MaterialExpressionPanner, -900, -60); p1.set_editor_property("speed_x", 1.0); p1.set_editor_property("speed_y", 0.35)
        p2 = node(unreal.MaterialExpressionPanner, -900, 140); p2.set_editor_property("speed_x", -0.6); p2.set_editor_property("speed_y", 0.8)
        for p_ in (p1, p2):
            MEL.connect_material_expressions(uv, "", p_, "Coordinate"); MEL.connect_material_expressions(spd, "", p_, "Speed")
        uv2 = node(unreal.MaterialExpressionMultiply, -1000, 300); k2 = scalar("WaveTile2", 2.3, -1200, 320)
        MEL.connect_material_expressions(uv, "", uv2, "A"); MEL.connect_material_expressions(k2, "", uv2, "B"); MEL.connect_material_expressions(uv2, "", p2, "Coordinate")
        n1 = node(unreal.MaterialExpressionTextureSampleParameter2D, -700, -80); n1.set_editor_property("parameter_name", "WaveNormalA"); n1.set_editor_property("texture", wn); n1.set_editor_property("sampler_type", unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL)
        n2 = node(unreal.MaterialExpressionTextureSampleParameter2D, -700, 140); n2.set_editor_property("parameter_name", "WaveNormalB"); n2.set_editor_property("texture", wn); n2.set_editor_property("sampler_type", unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL)
        MEL.connect_material_expressions(p1, "", n1, "UVs"); MEL.connect_material_expressions(p2, "", n2, "UVs")
        blend = node(unreal.MaterialExpressionAdd, -450, 40); MEL.connect_material_expressions(n1, "RGB", blend, "A"); MEL.connect_material_expressions(n2, "RGB", blend, "B")
        strength = scalar("WaveStrength", 0.35, -450, 200)
        half = node(unreal.MaterialExpressionConstant3Vector, -450, 300); half.set_editor_property("constant", unreal.LinearColor(0, 0, 1, 1))
        # flatten: lerp(flat, blend*0.5, strength)
        mul = node(unreal.MaterialExpressionMultiply, -300, 40); c05 = node(unreal.MaterialExpressionConstant, -450, 120); c05.set_editor_property("r", 0.5)
        MEL.connect_material_expressions(blend, "", mul, "A"); MEL.connect_material_expressions(c05, "", mul, "B")
        lerpn = node(unreal.MaterialExpressionLinearInterpolate, -150, 60)
        MEL.connect_material_expressions(half, "", lerpn, "A"); MEL.connect_material_expressions(mul, "", lerpn, "B"); MEL.connect_material_expressions(strength, "", lerpn, "Alpha")
        MEL.connect_material_property(lerpn, "", unreal.MaterialProperty.MP_NORMAL)
        # colour: shallow turquoise near the beach (fresnel-ish view fade to deep)
        shallow = vec("ShallowColor", (0.11, 0.60, 0.66, 1), -700, 450); deep = vec("DeepColor", (0.02, 0.22, 0.36, 1), -700, 600)
        fr = node(unreal.MaterialExpressionFresnel, -700, 760); fr.set_editor_property("exponent", 3.0); fr.set_editor_property("base_reflect_fraction", 0.04)
        lc = node(unreal.MaterialExpressionLinearInterpolate, -450, 520)
        MEL.connect_material_expressions(deep, "", lc, "A"); MEL.connect_material_expressions(shallow, "", lc, "B"); MEL.connect_material_expressions(fr, "", lc, "Alpha")
        MEL.connect_material_property(lc, "", unreal.MaterialProperty.MP_BASE_COLOR)
        rough = scalar("Roughness", 0.06, -300, 700); MEL.connect_material_property(rough, "", unreal.MaterialProperty.MP_ROUGHNESS)
        spec = node(unreal.MaterialExpressionConstant, -300, 780); spec.set_editor_property("r", 1.0); MEL.connect_material_property(spec, "", unreal.MaterialProperty.MP_SPECULAR)
        met = node(unreal.MaterialExpressionConstant, -300, 860); met.set_editor_property("r", 0.0); MEL.connect_material_property(met, "", unreal.MaterialProperty.MP_METALLIC)
        # foam-ish emissive sparkle: sine of time on the second normal's red channel, very subtle
        MEL.recompile_material(mat); EAL.save_loaded_asset(mat)
        # assign to the sea actors
        n = 0
        for a in ss.get_all_level_actors():
            if a.get_actor_label().startswith("L_Sea"):
                c = comp(a)
                if c:
                    for i in range(len(c.get_materials())): c.set_material(i, mat)
                    n += 1
        out["water"]["assigned"] = n; out["water"]["normal"] = wn.get_path_name() if wn else None
    except Exception: out["err"].append("water " + traceback.format_exc()[-500:])

# ---------------------------------------------------------------- 3. parallax (BumpOffset + QualitySwitch) on M_CCG_Env
if "parallax" in STEPS:
    try:
        mat = EAL.load_asset(f"{G}/Materials/M_CCG_Env")
        MEL.delete_all_material_expressions(mat)
        mat.set_editor_property("two_sided", True); mat.set_editor_property("used_with_nanite", True)
        def node(cls, x, y): return MEL.create_material_expression(mat, cls, x, y)
        def tp(name, tex, x, y, sampler):
            n_ = node(unreal.MaterialExpressionTextureSampleParameter2D, x, y)
            n_.set_editor_property("parameter_name", name); n_.set_editor_property("texture", tex); n_.set_editor_property("sampler_type", sampler); return n_
        asph = {k: EAL.load_asset(f"{G}/Materials/T_Asphalt_Hwy5_{k}") for k in ("BC", "N", "ORM", "H")}
        tc = node(unreal.MaterialExpressionTextureCoordinate, -1500, 0)
        til = node(unreal.MaterialExpressionScalarParameter, -1500, 150); til.set_editor_property("parameter_name", "Tiling"); til.set_editor_property("default_value", 1.0)
        mul = node(unreal.MaterialExpressionMultiply, -1300, 50)
        MEL.connect_material_expressions(tc, "", mul, "A"); MEL.connect_material_expressions(til, "", mul, "B")
        # height sample -> BumpOffset (high quality only)
        ht = tp("Height", asph["H"], -1100, 350, unreal.MaterialSamplerType.SAMPLERTYPE_MASKS)   # _H textures are TC_MASKS
        MEL.connect_material_expressions(mul, "", ht, "UVs")
        bo = node(unreal.MaterialExpressionBumpOffset, -850, 200)
        ratio = node(unreal.MaterialExpressionScalarParameter, -1100, 560); ratio.set_editor_property("parameter_name", "ParallaxRatio"); ratio.set_editor_property("default_value", 0.0)
        MEL.connect_material_expressions(mul, "", bo, "Coordinate"); MEL.connect_material_expressions(ht, "R", bo, "Height"); MEL.connect_material_expressions(ratio, "", bo, "HeightRatioInput")
        qs = node(unreal.MaterialExpressionQualitySwitch, -650, 100)
        MEL.connect_material_expressions(bo, "", qs, "Default"); MEL.connect_material_expressions(mul, "", qs, "Low"); MEL.connect_material_expressions(mul, "", qs, "Medium")
        bc = tp("BaseColor", asph["BC"], -450, -300, unreal.MaterialSamplerType.SAMPLERTYPE_COLOR)
        nm = tp("Normal", asph["N"], -450, 100, unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL)
        orm = tp("ORM", asph["ORM"], -450, 400, unreal.MaterialSamplerType.SAMPLERTYPE_MASKS)
        for n_ in (bc, nm, orm): MEL.connect_material_expressions(qs, "", n_, "UVs")
        tint = node(unreal.MaterialExpressionVectorParameter, -450, -550); tint.set_editor_property("parameter_name", "Tint"); tint.set_editor_property("default_value", unreal.LinearColor(1, 1, 1, 1))
        mul2 = node(unreal.MaterialExpressionMultiply, -150, -350)
        MEL.connect_material_expressions(bc, "RGB", mul2, "A"); MEL.connect_material_expressions(tint, "", mul2, "B")
        # grunge from vertex colour R (paintable): darken 40 % where painted
        vc0 = node(unreal.MaterialExpressionVertexColor, -650, -700)
        # unpainted meshes default to white vertex colour -> invert so white = clean, painted black = grunge
        vcm = node(unreal.MaterialExpressionComponentMask, -550, -700); vcm.set_editor_property("r", True); vcm.set_editor_property("g", False); vcm.set_editor_property("b", False); vcm.set_editor_property("a", False)
        MEL.connect_material_expressions(vc0, "", vcm, "")
        vc = node(unreal.MaterialExpressionOneMinus, -450, -700); MEL.connect_material_expressions(vcm, "", vc, "")
        gr = node(unreal.MaterialExpressionLinearInterpolate, 50, -350)
        g06 = node(unreal.MaterialExpressionMultiply, -150, -500); c06 = node(unreal.MaterialExpressionConstant, -300, -500); c06.set_editor_property("r", 0.6)
        MEL.connect_material_expressions(mul2, "", g06, "A"); MEL.connect_material_expressions(c06, "", g06, "B")
        MEL.connect_material_expressions(mul2, "", gr, "A"); MEL.connect_material_expressions(g06, "", gr, "B"); MEL.connect_material_expressions(vc, "", gr, "Alpha")
        MEL.connect_material_property(gr, "", unreal.MaterialProperty.MP_BASE_COLOR)
        MEL.connect_material_property(nm, "RGB", unreal.MaterialProperty.MP_NORMAL)
        MEL.connect_material_property(orm, "R", unreal.MaterialProperty.MP_AMBIENT_OCCLUSION)
        rs = node(unreal.MaterialExpressionScalarParameter, -150, 500); rs.set_editor_property("parameter_name", "RoughnessScale"); rs.set_editor_property("default_value", 1.0)
        mul3 = node(unreal.MaterialExpressionMultiply, 50, 450)
        MEL.connect_material_expressions(orm, "G", mul3, "A"); MEL.connect_material_expressions(rs, "", mul3, "B")
        # grunge: +0.15 roughness where painted
        ra = node(unreal.MaterialExpressionAdd, 200, 450); c015 = node(unreal.MaterialExpressionMultiply, 50, 560); k015 = node(unreal.MaterialExpressionConstant, -100, 600); k015.set_editor_property("r", 0.15)
        MEL.connect_material_expressions(vc, "", c015, "A"); MEL.connect_material_expressions(k015, "", c015, "B")
        MEL.connect_material_expressions(mul3, "", ra, "A"); MEL.connect_material_expressions(c015, "", ra, "B")
        MEL.connect_material_property(ra, "", unreal.MaterialProperty.MP_ROUGHNESS)
        MEL.connect_material_property(orm, "B", unreal.MaterialProperty.MP_METALLIC)
        em = tp("Emissive", EAL.load_asset(f"{G}/Signs/T_Sign_HAI_Skate_Neon_E"), -450, 700, unreal.MaterialSamplerType.SAMPLERTYPE_COLOR)
        es = node(unreal.MaterialExpressionScalarParameter, -150, 800); es.set_editor_property("parameter_name", "EmissiveStrength"); es.set_editor_property("default_value", 0.0)
        mul4 = node(unreal.MaterialExpressionMultiply, 50, 750)
        MEL.connect_material_expressions(em, "RGB", mul4, "A"); MEL.connect_material_expressions(es, "", mul4, "B")
        MEL.connect_material_property(mul4, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
        MEL.recompile_material(mat); EAL.save_loaded_asset(mat)
        # per-instance height maps + ratios (pavers strongest, concrete / stucco / wood / asphalt subtle)
        RAT = {"Pavers_Adoquin": 0.02, "Concrete_Park": 0.006, "Stucco_White": 0.006, "Wood_Deck": 0.008, "Roof_Corrugated": 0.012, "Asphalt_Hwy5": 0.004, "Steel_Rail": 0.0, "Sand_Cabarete": 0.004, "WallPaint": 0.0}
        done = []
        for a in reg.get_assets_by_path(f"{G}/Materials/MI", recursive=False):
            mi = a.get_asset()
            if not isinstance(mi, unreal.MaterialInstanceConstant): continue
            bc_t = MEL.get_material_instance_texture_parameter_value(mi, "BaseColor")
            if not bc_t: continue
            tn = bc_t.get_name()
            if not (tn.startswith("T_") and tn.endswith("_BC")): continue
            setname = tn[2:-3]
            hp = f"{G}/Materials/T_{setname}_H"
            if setname in RAT and EAL.does_asset_exist(hp):
                MEL.set_material_instance_texture_parameter_value(mi, "Height", EAL.load_asset(hp))
                MEL.set_material_instance_scalar_parameter_value(mi, "ParallaxRatio", RAT[setname])
                MEL.update_material_instance(mi); EAL.save_loaded_asset(mi); done.append([mi.get_name(), setname, RAT[setname]])
        out["parallax"]["instances"] = done
        # the wet-road master gets the same parallax ratio via its own instance? (M_CCG_RoadWet is separate - untouched)
    except Exception: out["err"].append("parallax " + traceback.format_exc()[-600:])

try: unreal.EditorLevelLibrary.save_current_level()
except Exception: pass
json.dump(out, open(r"C:\Users\211in\Downloads\CCG_UEFN\level\gfx_b.json", "w"), indent=1)
unreal.log("CCG_GFX_B_DONE err=%d" % len(out["err"]))
