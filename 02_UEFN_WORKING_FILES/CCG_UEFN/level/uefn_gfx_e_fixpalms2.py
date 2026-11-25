# the gallery palm meshes carry ~1.7 m (at L_Palm_008's scale) of root geometry below the visible trunk base:
# sink every palm by that plug depth, scaled by its own scale (L_Palm_008 was tuned by eye and is skipped)
import unreal, json
BASE = r"F:\HOMELANDAI\CURBSIDE GRIND (CCG)\02_UEFN_WORKING_FILES\CCG_UEFN\level"
ss = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
ALL = {a.get_actor_label(): a for a in ss.get_all_level_actors()}
ref = ALL["L_Palm_008"]; s0 = ref.get_actor_scale3d().z; plug = 170.0 / s0
out = {"s0": s0, "plug_per_unit": plug, "moved": []}
for l, a in ALL.items():
    if not l.startswith("L_Palm") or l == "L_Palm_008": continue
    s = a.get_actor_scale3d().z; dz = -plug * s
    p = a.get_actor_location(); p.z += dz; a.set_actor_location(p, False, False); out["moved"].append([l, round(dz)])
unreal.EditorLevelLibrary.save_current_level()
json.dump(out, open(BASE + r"\gfx_e_palms2.json", "w"), indent=1)
