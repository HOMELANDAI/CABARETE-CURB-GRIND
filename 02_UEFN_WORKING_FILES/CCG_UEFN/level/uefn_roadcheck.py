
import unreal, os, json
G = "/9ec1b72d-2111-4319-b015-282d94c768eb/CCG"
EAL = unreal.EditorAssetLibrary; MEL = unreal.MaterialEditingLibrary
out = {}
mat = EAL.load_asset(f"{G}/Materials/M_CCG_Road")
for pn in ("BaseColor", "Normal", "ORM", "WetMask"):
    try:
        t = MEL.get_material_default_texture_parameter_value(mat, pn); out[pn] = t.get_name() if t else None
    except Exception as e: out[pn] = "ERR " + str(e)[:60]
for pn in ("Tiling", "Wetness", "WetScale"):
    try: out[pn] = MEL.get_material_default_scalar_parameter_value(mat, pn)
    except Exception as e: out[pn] = "ERR"
mi = EAL.load_asset(f"{G}/Materials/MI/MI_Road_Wet")
out["mi_tiling"] = MEL.get_material_instance_scalar_parameter_value(mi, "Tiling"); out["mi_wet"] = MEL.get_material_instance_scalar_parameter_value(mi, "Wetness")
old = EAL.load_asset(f"{G}/Materials/MI/MI_Asphalt"); out["asphalt_tiling"] = MEL.get_material_instance_scalar_parameter_value(old, "Tiling")
try: out["asphalt_bc"] = MEL.get_material_instance_texture_parameter_value(old, "BaseColor").get_name()
except Exception as e: out["asphalt_bc"] = str(e)[:60]
ss = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
ALL = {a.get_actor_label(): a for a in ss.get_all_level_actors()}
s = ALL.get("FD_DaySeq_Sunset")
if s: s.set_editor_property("Priority", 1900); out["sunset_prio"] = s.get_editor_property("Priority")
p = ALL.get("PP_CCG_Grade")
if p:
    st = p.get_editor_property("settings")
    for k in ("auto_exposure_min_brightness", "auto_exposure_max_brightness", "auto_exposure_speed_up", "auto_exposure_speed_down"):
        st.set_editor_property("override_" + k, False)
    p.set_editor_property("settings", st); p.set_editor_property("enabled", True); out["ppv"] = "on, exposure window off"
json.dump(out, open(r"C:\Users\211in\Downloads\CCG_UEFN\level\road_check.json", "w"), indent=1)
unreal.log("CCGL road check %s" % out)
