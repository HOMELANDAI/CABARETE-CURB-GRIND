# exec(open(r'F:/HOMELANDAI/CURBSIDE GRIND (CCG)/02_UEFN_WORKING_FILES/CCG_UEFN/level/uefn_decks_rain.py').read())
# Tripo v5c: rain-suit bundle deck set (five decks from the rain-suit artwork).  (1) import the five CCG_Deck_* GLBs from tripo_pipeline/decks as Nanite static
# meshes (textures: normal->TC_NORMALMAP, rm->TC_MASKS); (2) place them as a leaning display row along the store's
# back wall, RIGHT of the counter (local fwd -895, right +330 +/- 32 cm steps), graphic facing the shop floor.
# Re-runnable: deletes TD_RS_* first.  Writes decks_rain_out.json.
import unreal, json, os, math, glob, traceback
BASE = r"F:\HOMELANDAI\CURBSIDE GRIND (CCG)\02_UEFN_WORKING_FILES\CCG_UEFN\level"
SRC  = r"F:\HOMELANDAI\CURBSIDE GRIND (CCG)\03_MODELS_3D\tripo_pipeline\decks"
G = "/9ec1b72d-2111-4319-b015-282d94c768eb/CCG"
EAL = unreal.EditorAssetLibrary; AT = unreal.AssetToolsHelpers.get_asset_tools()
ss = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
NINE = ["SpiceDrizzleDrop","VicewaveSwell","ViceMonsoonLuxeRemix","StormburnSunrise","PurpledownDrip"]
out = {"imported": {}, "tex": [], "placed": [], "err": []}
DO_IMPORT = os.environ.get("CCG_SKIP_IMPORT") is None
if DO_IMPORT:
    for nm in NINE:
        f = os.path.join(SRC, "CCG_Deck_%s.glb" % nm); name = "CCG_Deck_" + nm
        try:
            t = unreal.AssetImportTask(); t.filename = f; t.destination_path = "%s/Tripo/%s" % (G, name)
            t.automated = True; t.replace_existing = True; t.save = True
            AT.import_asset_tasks([t])
            paths = [str(p) for p in list(t.imported_object_paths)]; meshes = []
            for p in paths:
                o = EAL.load_asset(p)
                if isinstance(o, unreal.StaticMesh):
                    try:
                        ns = o.get_editor_property("nanite_settings"); ns.enabled = True; o.set_editor_property("nanite_settings", ns)
                    except Exception as e: out["err"].append("%s nanite %s" % (name, e))
                    b = o.get_bounds(); e = b.box_extent
                    meshes.append({"path": p, "extent": [round(e.x,1), round(e.y,1), round(e.z,1)], "tris": o.get_num_triangles(0)})
                    EAL.save_loaded_asset(o)
                elif isinstance(o, unreal.Texture2D):
                    n = o.get_name().lower(); ch = False
                    if "normal" in n: o.set_editor_property("srgb", False); o.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_NORMALMAP); ch = True
                    elif "roughness" in n or n.endswith("_rm") or "metallic" in n: o.set_editor_property("srgb", False); o.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_MASKS); ch = True
                    if ch: EAL.save_loaded_asset(o); out["tex"].append(o.get_name())
            out["imported"][name] = {"paths": len(paths), "meshes": meshes}
        except Exception: out["err"].append("%s: %s" % (name, traceback.format_exc()[-400:]))
def mesh(n):
    p = "%s/Tripo/CCG_Deck_%s/CCG_Deck_%s" % (G, n, n); m = EAL.load_asset(p)
    if not m: m = EAL.load_asset("%s/Tripo/CCG_Deck_%s/CCG_Deck_%s/StaticMeshes/CCG_Deck_%s" % (G, n, n, n))
    return m
ALL = {a.get_actor_label(): a for a in ss.get_all_level_actors()}
for l, a in list(ALL.items()):
    if l.startswith("TD_RS_"): ss.destroy_actor(a); ALL.pop(l)
try:
    store = ALL["L_Store_OceanDreamPlaza"]; sp = store.get_actor_location(); yaw = store.get_actor_rotation().yaw
    r = math.radians(yaw); fwd = unreal.Vector(math.cos(r), math.sin(r), 0); right = unreal.Vector(-math.sin(r), math.cos(r), 0)
    floor = sp.z
    for i, nm in enumerate(NINE):
        m = mesh(nm)
        if not m: out["err"].append("missing " + nm); continue
        F = -895.0; Rr = 330.0 + (i - 2) * 32.0
        x = sp.x + fwd.x * F + right.x * Rr; y = sp.y + fwd.y * F + right.y * Rr
        a = ss.spawn_actor_from_object(m, unreal.Vector(x, y, floor + 41.5), unreal.Rotator(0, 102, yaw))   # nose up, 12 deg lean back onto the wall, graphic to the floor
        a.set_actor_label("TD_RS_Deck_" + nm); a.set_folder_path("CCG/Store/RainSuit"); out["placed"].append([nm, round(x), round(y), round(floor + 41.5)])
except Exception: out["err"].append("place " + traceback.format_exc()[-500:])
try: unreal.EditorLevelLibrary.save_current_level()
except Exception as ex: out["err"].append("save " + str(ex)[:100])
json.dump(out, open(os.path.join(BASE, "decks_rain_out.json"), "w"), indent=1, default=str)
unreal.log("CCG_DECKS_RAIN_DONE %d placed, %d err" % (len(out["placed"]), len(out["err"])))
