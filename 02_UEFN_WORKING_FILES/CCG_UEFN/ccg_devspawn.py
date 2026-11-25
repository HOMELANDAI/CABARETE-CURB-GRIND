
import unreal
G = "9ec1b72d-2111-4319-b015-282d94c768eb"
ss = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
base = unreal.Vector(250, 768, 384)
out = []
def cls(n):
    return unreal.load_object(None, f"/{G}/_Verse.CCG-Verse-{n}")
plan = [("ccg_game_manager", (-600, -400)), ("ccg_store", (-400, -400)), ("ccg_timeofday", (-200, -400)), ("ccg_graphics", (0, -400)), ("ccg_rider_select", (200, -400))]
for n, (dx, dy) in plan:
    c = cls(n)
    if not c: out.append(n + ":NOCLASS"); continue
    a = ss.spawn_actor_from_object(c, unreal.Vector(base.x + dx, base.y + dy, base.z), unreal.Rotator(0, 0, 0))
    if a: a.set_actor_label("DEV_" + n); out.append(n + ":ok")
    else: out.append(n + ":spawnfail")
rc = cls("ccg_rail")
for i in range(3):
    a = ss.spawn_actor_from_object(rc, unreal.Vector(base.x + 400 + i * 200, base.y - 400, base.z), unreal.Rotator(0, 0, 0)) if rc else None
    if a: a.set_actor_label(f"DEV_ccg_rail_{i+1}")
out.append("rails:" + str(bool(rc)))
unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
unreal.log("CCG_DEVSPAWN " + ",".join(out))
