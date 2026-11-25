# exec(open(r'F:/HOMELANDAI/CURBSIDE GRIND (CCG)/02_UEFN_WORKING_FILES/CCG_UEFN/level/uefn_decks.py').read())
# Tripo v5: HAI deck set in the HAI Skate Store (Ocean Dream Plaza).  (1) six CCG_Deck_* Nanite meshes on the
# deck rack as a leaning display row + one flat on the counter; (2) store device labels carry the catalog ids
# (ccg_store.verse purchase-row order) so the inventory reads by name in the outliner.  Re-runnable (deletes TD_* first).
import unreal, json, os, math, traceback
BASE = r"F:\HOMELANDAI\CURBSIDE GRIND (CCG)\02_UEFN_WORKING_FILES\CCG_UEFN\level"
G = "/9ec1b72d-2111-4319-b015-282d94c768eb/CCG/Tripo"
EAL = unreal.EditorAssetLibrary
ss = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
out = {"placed": [], "renamed": [], "err": []}
DECKS = ["IvoryMandalaFlow", "IvoryEngraveSupreme", "IvoryGridSupremeRemix", "GoldenPawStrike", "EmeraldPawKata", "ShadowRuffCombat"]
NAMES = {"IvoryMandalaFlow": "Ivory Mandala Flow", "IvoryEngraveSupreme": "Ivory Engrave Supreme", "IvoryGridSupremeRemix": "Dapper Dan Luxe Ivory Grid Supreme Remix",
         "GoldenPawStrike": "Golden Paw Strike", "EmeraldPawKata": "Emerald Paw Kata", "ShadowRuffCombat": "Shadow Ruff Combat"}
ROWS = ["rain_spicefront","rain_vicewave_shepherd","rain_vicewave_husky","rain_stormburn","rain_purpledown","kaftan_ruff_royalty","kaftan_paw_prestige",
        "kaftan_bark_opulence","kaftan_howl_dynasty","kaftan_ruff_legacy","kaftan_paw_icon","maroon_crest_wrap","auburn_sunrise_cardigan","purplescale_crest_cardigan",
        "carbon_slice_block","cobalt_core_split","logo_flood_luxe","suede_stripe_statement","comic_frame_split","neon_circuit_cardigan","ivory","carved_nine","dojo"]
def mesh(n):
    p = f"{G}/CCG_Deck_{n}/CCG_Deck_{n}"
    m = EAL.load_asset(p)
    if not m: m = EAL.load_asset(f"{G}/CCG_Deck_{n}/CCG_Deck_{n}/StaticMeshes/CCG_Deck_{n}")
    return m
ALL = {a.get_actor_label(): a for a in ss.get_all_level_actors()}
for l, a in list(ALL.items()):
    if l.startswith("TD_"): ss.destroy_actor(a); ALL.pop(l)
try:
    rack = ALL["TR_Shop_DeckRack"]; counter = ALL["TR_Shop_Counter"]
    rp = rack.get_actor_location(); cp = counter.get_actor_location()
    o, e = rack.get_actor_bounds(False); floor = o.z - e.z
    d = unreal.Vector(cp.x - rp.x, cp.y - rp.y, 0); L = math.hypot(d.x, d.y); d.x /= L; d.y /= L      # rack -> counter (viewer side)
    yaw = math.degrees(math.atan2(d.y, d.x))
    side = unreal.Vector(-d.y, d.x, 0)
    n = len(DECKS) - 1
    for i, nm in enumerate(DECKS[:-1]):
        m = mesh(nm)
        if not m: out["err"].append("missing " + nm); continue
        t = (i - (n - 1) / 2.0) * 30.0
        x = rp.x + d.x * (max(e.x, e.y) + 28) + side.x * t
        y = rp.y + d.y * (max(e.x, e.y) + 28) + side.y * t
        a = ss.spawn_actor_from_object(m, unreal.Vector(x, y, floor + 41.5), unreal.Rotator(0, 102, yaw))   # nose up, graphic to the viewer, 12 deg lean back
        a.set_actor_label("TD_Deck_" + nm); a.set_folder_path("CCG/Store"); out["placed"].append([nm, round(x), round(y)])
    # last deck flat on the counter top
    m = mesh(DECKS[-1]); o2, e2 = counter.get_actor_bounds(False)
    a = ss.spawn_actor_from_object(m, unreal.Vector(o2.x, o2.y, o2.z + e2.z + 0.5), unreal.Rotator(0, 0, yaw + 25))
    a.set_actor_label("TD_Deck_" + DECKS[-1]); a.set_folder_path("CCG/Store"); out["placed"].append([DECKS[-1], "counter"])
except Exception: out["err"].append("place " + traceback.format_exc()[-500:])
try:
    for i, rid in enumerate(ROWS):
        for pre in ("FD_Granter_Store_", "FD_Btn_Store_"):
            l = "%s%02d" % (pre, i); a = ALL.get(l)
            if a: a.set_actor_label("%s_%s" % (l, rid)); out["renamed"].append(l)
except Exception: out["err"].append("rename " + traceback.format_exc()[-300:])
try: unreal.EditorLevelLibrary.save_current_level()
except Exception as ex: out["err"].append("save " + str(ex)[:100])
json.dump(out, open(os.path.join(BASE, "decks_out.json"), "w"), indent=1, default=str)
unreal.log("CCG_DECKS_DONE %d" % len(out["placed"]))
