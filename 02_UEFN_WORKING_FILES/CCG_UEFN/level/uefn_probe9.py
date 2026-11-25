import unreal, json, os, zlib, struct
BASE = r"C:\Users\211in\Downloads\CCG_UEFN\level"
def vn(name):
    c = zlib.crc32(name.encode("utf-32-le")) & 0xffffffff
    return "__verse_0x%08X_%s" % (struct.unpack("<I", struct.pack(">I", c))[0], name)
out = {}
ss = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
S = unreal.load_object(None, "/VerseSpatialMath/_Verse/VNI/VerseSpatialMath.SpatialMath_vector3")
T = unreal.get_type_from_struct(S)
AX = [d for d in dir(T) if d.startswith("verse_0x") and d.endswith("_x")][0]
AY = [d for d in dir(T) if d.startswith("verse_0x") and d.endswith("_y")][0]
AZ = [d for d in dir(T) if d.startswith("verse_0x") and d.endswith("_z")][0]
out["attrs"] = [AX, AY, AZ]
def v3(x, y, z):
    i = T(); setattr(i, AX, float(x)); setattr(i, AY, float(y)); setattr(i, AZ, float(z)); return i
vo = None
for a in ss.get_all_level_actors():
    if a.get_actor_label() == "DEV_probe_rail":
        for o in unreal.ObjectIterator():
            try:
                if o.get_outer() == a and o.get_class().get_name() == "CCG-Verse-ccg_rail": vo = o; break
            except Exception: pass
        break
arr = vo.get_editor_property(vn("RailPoints"))
out["before"] = [e.to_tuple() for e in arr]
pts = [v3(100, 200, 300), v3(400, 500, 600), v3(700, 800, 900)]
vo.set_editor_property(vn("RailPoints"), pts)
arr2 = vo.get_editor_property(vn("RailPoints"))
out["after"] = [e.to_tuple() for e in arr2]
# also test unreal.Vector direct
vo.set_editor_property(vn("RailPoints"), [unreal.Vector(1, 2, 3), unreal.Vector(4, 5, 6)])
out["after_vec"] = [e.to_tuple() for e in vo.get_editor_property(vn("RailPoints"))]
# restore struct version
vo.set_editor_property(vn("RailPoints"), pts)
# Fortnite device classes: load_class each candidate
cands = {"volume": "/CRD_Volume/Device_Volume.Device_Volume_C", "barrier": "/CRD_VolumetricRegion/Device_Barrier_V2.Device_Barrier_V2_C",
         "hud": "/CreativeCoreDevices/Device_HUDMessage_V2.Device_HUDMessage_V2_C", "button": "/CreativeCoreDevices/Device_Button_V2.Device_Button_V2_C",
         "granter": "/CreativeCoreDevices/Device_ItemGranter_V2.Device_ItemGranter_V2_C", "classdesigner": "/CreativeCoreDevices/Device_ClassDesigner_V2.Device_ClassDesigner_V2_C",
         "classselector": "/CreativeCoreDevices/Device_ClassSelector_V2.Device_ClassSelector_V2_C", "light": "/Game/Creative/Devices/Lights/BP_CustomizableLight.BP_CustomizableLight_C",
         "daysequence": "/Game/Creative/Devices/Lighting/BP_DaySequenceModifier_Device.BP_DaySequenceModifier_Device_C", "vfx": "/CRD_VFX_Spawner/Device_VFXSpawner_V2.Device_VFXSpawner_V2_C",
         "spawn": "/CRD_PlayerSpawn/BP_Creative_Player_Spawner_Prop.BP_Creative_Player_Spawner_Prop_C", "trigger": "/CreativeCoreDevices/Device_Trigger_Parent_V2.Device_Trigger_Parent_V2_C",
         "endgame": "/CRD_GameEnd/SetupAssets/CP_Devices_EndGame.CP_Devices_EndGame_C"}
res = {}
for k, p in cands.items():
    try:
        c = unreal.load_class(None, p); res[k] = c.get_path_name() if c else "NONE"
    except Exception as e: res[k] = "ERR " + str(e)[:100]
out["classes"] = res
# find trigger / endgame / timeofday / cinematic names in registry
reg = unreal.AssetRegistryHelpers.get_asset_registry()
more = {"trigger": [], "endgame": [], "gameend": [], "timeofday": [], "cinematic": [], "spawn": []}
for a in reg.get_all_assets(True):
    cls = str(a.asset_class_path.asset_name)
    if cls not in ("BlueprintGeneratedClass", "Blueprint"): continue
    pk = str(a.package_name); nm = str(a.asset_name).lower()
    if not (pk.startswith("/CRD_") or pk.startswith("/CreativeCoreDevices") or "/Creative/Devices" in pk): continue
    for k in more:
        if k in nm and len(more[k]) < 15: more[k].append(pk)
out["more"] = more
json.dump(out, open(os.path.join(BASE, "probe9.json"), "w"), indent=1, default=str)
unreal.log("CCGL probe9 written")
