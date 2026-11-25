# open LS_CCG_Sunset in Sequencer and scrub to CCG_FRAME (default 180 = full sunset) for a viewport look
import unreal, os, json
F = int(os.environ.get("CCG_FRAME", "180"))
LSE = unreal.LevelSequenceEditorBlueprintLibrary
seq = unreal.EditorAssetLibrary.load_asset("/9ec1b72d-2111-4319-b015-282d94c768eb/CCG/Sequences/LS_CCG_Sunset")
if F < 0:
    LSE.set_current_time(0); LSE.close_level_sequence(); r = "closed"
else:
    LSE.open_level_sequence(seq); LSE.set_current_time(F); r = "frame %d" % F
json.dump({"scrub": r, "time": LSE.get_current_time()}, open(r"F:\HOMELANDAI\CURBSIDE GRIND (CCG)\02_UEFN_WORKING_FILES\CCG_UEFN\level\gfx_c_scrub.json", "w"))
