# uefn_stills4k.py — CCG (26 Nov 2026). 4K editor stills for HOME LAND's review. Re-runnable.
# Same camera set as uefn_shots.py, at 3840x2160, plus the store interior and the Sign Twins.
# Files land in the project's Saved/Screenshots (WindowsEditor); copy them to
# F:\HOMELANDAI\CURBSIDE GRIND (CCG)\05_IMAGES_AND_STILLS\uefn_4k_2026-11-26\ afterwards.
# Turn the viewport to Lit + Game View (G) and hide the grid before running; one still per tick so the
# viewport finishes streaming Nanite/textures between shots.
import unreal, json
OUT = r"F:/HOMELANDAI/CURBSIDE GRIND (CCG)/02_UEFN_WORKING_FILES/CCG_UEFN/level/stills4k_out.json"
US = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
SHOTS = [  # name, UE location (cm), (pitch, yaw, roll)
    ("CCG4K_01_sign_twins",   (-1800, -1200, 260),   (-3, 30, 0)),     # rider's view of the Cabarete sign
    ("CCG4K_02_start_route",  (-2500, -2300, 900),   (-14, 64.5, 0)),  # start, looking along Highway 5
    ("CCG4K_03_vagamundo",    (4200, 7500, 1600),    (-22, 45, 0)),    # P1 Vagamundo roof
    ("CCG4K_04_store_front",  (12800, 17000, 600),   (-6, 40, 0)),     # Ocean Dream Plaza / HAI Skate
    ("CCG4K_05_store_inside", (14600, 17800, 420),   (-8, 34, 0)),     # deck racks, counter
    ("CCG4K_06_multiplex",    (36500, 18200, 2200),  (-25, 8, 0)),     # P2 Multiplex
    ("CCG4K_07_mojito",       (65500, 17600, 1800),  (-22, 12, 0)),    # P3 Mojito quarter pipes
    ("CCG4K_08_horseshoe",    (80500, 18600, 1400),  (-18, 20, 0)),    # P4 Horseshoe / courtyard
    ("CCG4K_09_aerial",       (42000, 12000, 26000), (-62, 20, 0)),    # whole route
]
state = {"i": 0, "wait": 0, "done": []}

def tick(dt):
    if state["wait"] > 0:
        state["wait"] -= 1; return
    i = state["i"]
    if i >= len(SHOTS):
        unreal.unregister_slate_post_tick_callback(state["h"])
        json.dump({"shots": state["done"]}, open(OUT, "w"), indent=1)
        unreal.log("CCG_STILLS4K_DONE " + str(len(state["done"])))
        return
    name, loc, rot = SHOTS[i]
    if state.get("placed") != i:
        US.set_level_viewport_camera_info(unreal.Vector(*loc), unreal.Rotator(roll=rot[2], pitch=rot[0], yaw=rot[1]))
        state["placed"] = i; state["wait"] = 90          # ~1.5 s of frames to stream in
        return
    unreal.AutomationLibrary.take_high_res_screenshot(3840, 2160, name)
    state["done"].append(name); state["i"] += 1; state["wait"] = 30

state["h"] = unreal.register_slate_post_tick_callback(tick)
