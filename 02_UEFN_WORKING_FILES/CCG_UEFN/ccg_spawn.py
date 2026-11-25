
import unreal
ROOT = "/9ec1b72d-2111-4319-b015-282d94c768eb/CCG"
EAL = unreal.EditorAssetLibrary
ss = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for a in ss.get_all_level_actors():
    if a.get_actor_label().startswith("Rider_"): ss.destroy_actor(a)
out = []
for i, N in enumerate(("Kefla", "Koda", "Crash")):
    sk = EAL.load_asset(f"{ROOT}/Riders/{N}/SK_{N}")
    a = ss.spawn_actor_from_class(unreal.SkeletalMeshActor, unreal.Vector(-200 + i * 200, 400, 0), unreal.Rotator(0, 0, 180))
    a.set_actor_label(f"Rider_{N}")
    c = a.skeletal_mesh_component; c.set_skeletal_mesh_asset(sk)
    anim = EAL.load_asset(f"{ROOT}/Riders/{N}/SK_{N}CCG_Stance")
    try:
        c.set_editor_property('animation_mode', unreal.AnimationMode.ANIMATION_SINGLE_NODE)
        c.set_editor_property('animation_data', unreal.SingleAnimationPlayData(anim_to_play=anim, looping=True, playing=True))
    except Exception as e: out.append(str(e)[:80])
    out.append(a.get_actor_label())
lvl = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
lvl.set_level_viewport_camera_info(unreal.Vector(0, -250, 150), unreal.Rotator(-6, 90, 0))
unreal.AutomationLibrary.take_high_res_screenshot(1600, 900, "ccg_riders_check.png")
unreal.log("CCG_SPAWN_DONE " + ",".join(out))
