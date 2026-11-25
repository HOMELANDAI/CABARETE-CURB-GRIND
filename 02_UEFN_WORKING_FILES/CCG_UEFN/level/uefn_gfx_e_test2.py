
import unreal, json, os
ss = unreal.get_editor_subsystem(unreal.EditorActorSubsystem); EAL = unreal.EditorAssetLibrary
BASE = r"F:\HOMELANDAI\CURBSIDE GRIND (CCG)\02_UEFN_WORKING_FILES\CCG_UEFN\level"
legal = json.load(open(os.path.join(BASE, "gfx_e_legal.json")))["ok"]
ALL = {a.get_actor_label(): a for a in ss.get_all_level_actors()}
for l, a in list(ALL.items()):
    if l.startswith("FLT_") or l.startswith("FL_"): ss.destroy_actor(a)
sp = unreal.Vector(-1076.1, -531.1, 106.0)
placed = []
for i, path in enumerate(legal):
    m = EAL.load_asset(path)
    a = ss.spawn_actor_from_object(m, unreal.Vector(sp.x + 600 + (i % 8) * 250, sp.y - 2500 + (i // 8) * 250, sp.z), unreal.Rotator(0, 0, 0))
    a.set_actor_label("FLT_" + m.get_name()); a.set_folder_path("CCG/FoliageTest"); placed.append(path)
# (b) a duplicate of a gallery palm actor, (c) a fresh palm actor with an L_ label and no folder
src = ALL["L_Palm_002"]
d = ss.duplicate_actor(src, unreal.EditorLevelLibrary.get_editor_world(), unreal.Vector(300, 0, 0)); d.set_actor_label("FLT_PalmDup")
pm = EAL.load_asset("/Game/Environments/Props/Trees/Meshes/SM_PalmTree_A")
c = ss.spawn_actor_from_object(pm, unreal.Vector(sp.x + 600, sp.y - 3000, sp.z), unreal.Rotator(0, 0, 0)); c.set_actor_label("L_Palm_998")
json.dump({"placed": placed, "dup": d.get_actor_label(), "src_cls": src.get_class().get_name()}, open(os.path.join(BASE, "gfx_e_test2.json"), "w"), indent=1)
unreal.EditorLevelLibrary.save_current_level()
