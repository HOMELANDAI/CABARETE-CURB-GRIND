# Cabarete Curb Grind (CCG) — HomelandAI

Skateboarding game set on Highway 5, Cabarete DR. Owner: HOME LAND (HomelandAI). Primary build: UEFN (Fortnite). Secondary: VIVERSE (Three.js). Read `10_DOCS\CLAUDE_CODE_HANDOFF.md` first, then `10_DOCS\UEFN_INSTALL_STATUS.md`.

## Standing rules
- Seek the highest detail achievable in graphics and resolution. Judge results by pictures, not by documents.
- Report with three labels: **Completed / Not completed / Next phase**. Be precise about what was done and what remains.
- End every report with: **"Cabarete Curb Grind is not done to completion."** — until the game is published.
- Deliver the VIVERSE zip (index.html at the zip root, Three.js inlined) with every game update.
- Keep every CCG file on this F drive, in the numbered folders, labelled. Never write to the Desktop.
- Bypass blockers and come back to them. Expired access/permissions are not the user — re-request and continue.
- Use every tool: Tripo Studio, Blender 5.2 (MCP), UEFN Python, computer use, Claude in Chrome.
- Only HOME LAND's own art and the CCG Tripo models go into this game. Nothing from the hockey/busts/weapons sets.
- HOME LAND's email is private — never send it to an external service without asking.

## Layout
- `02_UEFN_WORKING_FILES\CCG_UEFN\verse2\` + `ccg_hud.verse`, `ccg_trick_input.verse` — Verse source (9 files).
- `02_UEFN_WORKING_FILES\CCG_UEFN\level\` — `gen_level.py`, `placements.json`, `route_real.json`, all `uefn_*.py` editor scripts.
- `03_MODELS_3D\tripo_pipeline\` — decks, foliage, riders, props (masters + `web\` GLBs + check renders).
- `09_DELIVERABLES\` — VIVERSE zips. `10_DOCS\` — status and handoff docs.
- Live UEFN project: `C:\Users\211in\FortniteProjects\CabareteCurbGrind` (`01_UEFN_PROJECT\` here is only a snapshot).

## UEFN conventions
- Editor scripts run from the Python bar via `C:\Users\211in\r.py` = one `exec(open(r"F:/.../level/<script>.py").read())` line.
- Scripts are re-runnable: delete their own label prefix first, write `<name>_out.json`, log a `CCG_*_DONE` marker.
- Tripo meshes import as Nanite under `/CCG/Tripo/`; normal maps → TC_NORMALMAP, rm maps → TC_MASKS; 4K sources max.
- After any level change: Validate Project → Push Changes → check the log for `pushed remote revision` and no `UEFNValidation: Error`.
- Close Blender and the Fortnite client before heavy UEFN work — the PC has crashed out of memory.
