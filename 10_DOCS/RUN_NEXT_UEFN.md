# Run next in UEFN (written 26 Nov 2026, cloud session)

For the Claude Code session running **on the PC** in `F:\HOMELANDAI\CURBSIDE GRIND (CCG)\`.
First pull the cloud work: `git fetch origin hai/admiring-feynman-he2egg` and merge it (or copy the files below).
Paths: `L` = `F:/HOMELANDAI/CURBSIDE GRIND (CCG)/02_UEFN_WORKING_FILES/CCG_UEFN/level`.
Each step: write `C:\Users\211in\r.py` = `exec(open(r"L/<script>.py").read())`, run `exec(open(r"C:/Users/211in/r.py").read())` in the Python bar, check the `*_out.json` and the `CCG_*_DONE` log line.

0. Close Blender and the Fortnite client. Open UEFN → Browse → `CabareteCurbGrind.uefnproject`.
1. `uefn_decks_rain.py` → `decks_rain_out.json` must show 5 placed.
2. **Phantom combo fix (Verse):** copy `02_UEFN_WORKING_FILES\CCG_UEFN\verse2\ccg_game_manager.verse` and `ccg_trick_input.verse` into the live project's Verse folder (`C:\Users\211in\FortniteProjects\CabareteCurbGrind\Plugins\CabareteCurbGrind\Content\`… wherever the current copies live — search for `ccg_game_manager.verse`). Verse → Build Verse Code. Must build clean.
3. `uefn_signgap_fix.py` → `signgap_fix_out.json`: `after.pads_inside` must be empty.
4. `uefn_spawn_diag.py` → `spawn_diag_out.json` + `CCG_spawn_eye` still. If `counts.hidden_in_game / editor_only / not_spatially_loaded` > 0, that is why the client showed bare sand — fix those flags.
5. Validate Project → Push Changes → log shows `pushed remote revision` and no `UEFNValidation: Error`.
6. Viewport: Lit, Game View (G), grid off. `uefn_stills4k.py` → 9 stills in the project's `Saved\Screenshots\WindowsEditor\`; copy them to `05_IMAGES_AND_STILLS\uefn_4k_2026-11-26\` and show HOME LAND.
7. Launch Session; with HOME LAND at the keyboard confirm no +1,500 on spawn, then jump the Sign Gap and confirm it still pays.

Report with Completed / Not completed / Next phase, ending: "Cabarete Curb Grind is not done to completion."
