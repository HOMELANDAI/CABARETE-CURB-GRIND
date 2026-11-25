# probe the lighting state after the Tier B rig + move the viewport camera to the spawn view
import unreal, json, math
BASE = r"F:\HOMELANDAI\CURBSIDE GRIND (CCG)\02_UEFN_WORKING_FILES\CCG_UEFN\level"
ss = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
ALL = {a.get_actor_label(): a for a in ss.get_all_level_actors()}
out = {"lights": [], "tod_actors": [], "world": {}}
for a in ss.get_all_level_actors():
    cn = a.get_class().get_name()
    if any(k in cn for k in ("DaySequence", "TimeOfDay", "SkyAtmosphere", "SkyLight", "DirectionalLight", "HeightFog", "VolumetricCloud", "PostProcess", "Sky")):
        out["tod_actors"].append([a.get_actor_label(), cn, bool(a.is_hidden_ed()), a.get_actor_location().z])
sun = ALL.get("LR_Sun")
if sun:
    c = sun.get_component_by_class(unreal.DirectionalLightComponent)
    out["lights"].append({"sun_intensity": c.get_editor_property("intensity"), "rot": str(sun.get_actor_rotation()), "vis": c.is_visible(), "mob": str(c.mobility)})
w = unreal.EditorLevelLibrary.get_editor_world(); wsx = w.get_world_settings()
for k in ("bDisableAllTimeOfDayManagers",):
    try: out["world"][k] = wsx.get_editor_property(k)
    except Exception as e: out["world"][k] = str(e)[:80]
sp = ALL.get("Spawn_Start"); p = sp.get_actor_location() if sp else unreal.Vector(-1076, -531, 106)
yaw = 26.27
unreal.EditorLevelLibrary.set_level_viewport_camera_info(unreal.Vector(p.x - 600 * math.cos(math.radians(yaw)), p.y - 600 * math.sin(math.radians(yaw)), p.z + 260), unreal.Rotator(0, -12, yaw))
json.dump(out, open(BASE + r"\gfx_c_look.json", "w"), indent=1, default=str)
