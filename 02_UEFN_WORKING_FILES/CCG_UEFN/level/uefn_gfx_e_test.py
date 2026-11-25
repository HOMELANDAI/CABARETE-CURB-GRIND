
import unreal, json, os
ss = unreal.get_editor_subsystem(unreal.EditorActorSubsystem); EAL = unreal.EditorAssetLibrary
BASE = r"F:\HOMELANDAI\CURBSIDE GRIND (CCG)\02_UEFN_WORKING_FILES\CCG_UEFN\level"
probe = json.load(open(os.path.join(BASE, "probe_bush.json")))["paths"]
ALL = {a.get_actor_label(): a for a in ss.get_all_level_actors()}
n = 0
for l, a in list(ALL.items()):
    if l.startswith("FL_") or l.startswith("FLT_"): ss.destroy_actor(a); n += 1
cands = []
for p, names in probe.items():
    for nm in names:
        if any(k in nm for k in ("Imposter", "Fish", "_Bake", "_bake", "ShadowProxy", "DONTUSE", "Inflatable", "Launchable", "BouncePad", "Hermes", "_Snow", "LeafScree", "_FX", "leaf_A")): continue
        cands.append(p + "/" + nm)
sp = unreal.Vector(-1076.1, -531.1, 106.0)
placed = []
for i, path in enumerate(cands):
    m = EAL.load_asset(path)
    if not m: continue
    a = ss.spawn_actor_from_object(m, unreal.Vector(sp.x + 600 + (i % 16) * 250, sp.y - 2500 + (i // 16) * 250, sp.z), unreal.Rotator(0, 0, 0))
    if not a: continue
    a.set_actor_label("FLT_" + m.get_name()); a.set_folder_path("CCG/FoliageTest"); placed.append(path)
json.dump({"deleted": n, "placed": placed}, open(os.path.join(BASE, "gfx_e_test.json"), "w"), indent=1)
unreal.EditorLevelLibrary.save_current_level()
