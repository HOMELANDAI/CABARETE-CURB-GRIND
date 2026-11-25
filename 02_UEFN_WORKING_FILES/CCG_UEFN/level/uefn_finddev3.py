import unreal, json, os, re
BASE = r"C:\Users\211in\Downloads\CCG_UEFN\level"
out = {}
reg = unreal.AssetRegistryHelpers.get_asset_registry()
allassets = reg.get_all_assets(True)
bp = {}
for a in allassets:
    cls = str(a.asset_class_path.asset_name)
    if cls not in ("BlueprintGeneratedClass", "Blueprint"): continue
    pk = str(a.package_name)
    nm = str(a.asset_name)
    if pk.startswith("/CRD_") or "/Creative/Devices" in pk or pk.startswith("/CR_") or "Device" in nm:
        bp[pk] = nm
out["bp_devices"] = bp
try:
    vs = reg.get_assets_by_path("/9ec1b72d-2111-4319-b015-282d94c768eb/_Verse", True)
    out["verse_assets"] = sorted(set(str(a.package_name) + ":" + str(a.asset_name) + ":" + str(a.asset_class_path.asset_name) for a in vs))
except Exception as e:
    out["verse_err"] = str(e)
# verse classes anywhere in the project mount
vc = []
for a in allassets:
    if str(a.asset_class_path.asset_name) in ("VerseClass",) and "9ec1b72d" in str(a.package_name):
        vc.append(str(a.package_name) + ":" + str(a.asset_name))
out["verse_classes"] = sorted(vc)
json.dump(out, open(os.path.join(BASE, "devices3.json"), "w"), indent=1)
unreal.log("CCGL devices3.json written %d" % len(bp))
