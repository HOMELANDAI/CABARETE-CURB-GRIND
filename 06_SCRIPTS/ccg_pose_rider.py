# Blender 5.x — relax a T-posed Tripo rider into a casual standing stance without an external rig:
# builds a small arm armature from the mesh silhouette, auto-weights it, drops the arms, bakes the pose,
# downsizes textures to 4K and exports a static GLB for UEFN (+ a check render).
# Run inside Blender:  NAME="CCG_Rider_Yara"; exec(open(r"C:/Users/211in/Downloads/ccg_pose_rider.py").read())
import bpy, math, mathutils, os, time
NAME = globals().get("NAME", "CCG_Rider_Yara")
SRC = rf"C:\Users\211in\Downloads\{NAME}.glb"
OUT_DIR = r"C:\Users\211in\Downloads\tripo_posed"; os.makedirs(OUT_DIR, exist_ok=True)
ST = globals().get("STANCE", {})
t0 = time.time()
def ov(obj, sel=None):
    sel = sel or [obj]
    win = bpy.context.window_manager.windows[0]; scr = win.screen
    area = next((a for a in scr.areas if a.type == 'VIEW_3D'), scr.areas[0]); region = next((r for r in area.regions if r.type == 'WINDOW'), area.regions[0])
    return bpy.context.temp_override(window=win, screen=scr, area=area, region=region, active_object=obj, object=obj, selected_objects=sel, selected_editable_objects=sel, edit_object=obj)
bpy.ops.wm.read_homefile(use_empty=True)
bpy.ops.import_scene.gltf(filepath=SRC)
meshes = [o for o in bpy.data.objects if o.type == 'MESH']
# join into one object for a single weight solve
for o in bpy.data.objects: o.select_set(o in meshes)
bpy.context.view_layer.objects.active = meshes[0]
body = meshes[0]
if len(meshes) > 1:
    with ov(body, meshes): bpy.ops.object.join()
body.data.transform(body.matrix_world); body.matrix_world = mathutils.Matrix.Identity(4); body.data.update()
me = body.data
co = [v.co for v in me.vertices]
xs = [c.x for c in co]; ys = [c.y for c in co]; zs = [c.z for c in co]
mnx, mxx, mny, mxy, mnz, mxz = min(xs), max(xs), min(ys), max(ys), min(zs), max(zs)
H = mxz - mnz; cx = (mnx + mxx) / 2; cy = (mny + mxy) / 2
# which horizontal axis is the arm span? (the wider one)
span_x = mxx - mnx > mxy - mny
A = 0 if span_x else 1          # span axis index
F = 1 if span_x else 0          # forward/back axis index
half = (mxx - mnx) / 2 if span_x else (mxy - mny) / 2
def P(c): return (c.x, c.y)[A]
def Q(c): return (c.x, c.y)[F]
ctr = (cx, cy)[A]; fctr = (cx, cy)[F]
# arm height: mean z of the outer 35 % of the span (the arms)
outer = [c for c in co if abs(P(c) - ctr) > 0.65 * half]
armz = sum(c.z for c in outer) / len(outer); armf = sum(Q(c) for c in outer) / len(outer)
# approximate shoulder joint at 0.26 of half-span, elbow 0.58, wrist 0.86 (T-pose anthropometry)
sh, el, wr = ST.get("shoulder", 0.26) * half, ST.get("elbow", 0.58) * half, ST.get("wrist", 0.86) * half
def pt(a, z=None, f=None):
    v = [0.0, 0.0, armz if z is None else z]; v[A] = ctr + a; v[F] = fctr if f is None else f
    return mathutils.Vector(v)
# armature
arm_data = bpy.data.armatures.new("RiderRig"); arm = bpy.data.objects.new("RiderRig", arm_data)
bpy.context.scene.collection.objects.link(arm); bpy.context.view_layer.objects.active = arm
with ov(arm): bpy.ops.object.mode_set(mode='EDIT')
eb = arm_data.edit_bones
root = eb.new("Root"); root.head = pt(0, mnz); root.tail = pt(0, mnz + 0.5 * H)
spine = eb.new("Spine"); spine.head = pt(0, mnz + 0.5 * H); spine.tail = pt(0, mnz + 0.86 * H); spine.parent = root
head = eb.new("Head"); head.head = spine.tail; head.tail = pt(0, mxz); head.parent = spine
bones = {}
for side, s in (("L", 1), ("R", -1)):
    ua = eb.new(f"UpperArm_{side}"); ua.head = pt(s * sh); ua.tail = pt(s * el); ua.parent = spine
    fa = eb.new(f"ForeArm_{side}"); fa.head = pt(s * el); fa.tail = pt(s * wr); fa.parent = ua; fa.use_connect = True
    hd = eb.new(f"Hand_{side}"); hd.head = pt(s * wr); hd.tail = pt(s * half); hd.parent = fa; hd.use_connect = True
    bones[side] = (ua.name, fa.name, hd.name)
for side, s in (("L", 1), ("R", -1)):
    ul = eb.new(f"UpLeg_{side}"); ul.head = pt(s * 0.09 * H, mnz + 0.50 * H); ul.tail = pt(s * 0.09 * H, mnz + 0.27 * H); ul.parent = root
    lg = eb.new(f"Leg_{side}"); lg.head = ul.tail; lg.tail = pt(s * 0.09 * H, mnz + 0.03 * H); lg.parent = ul; lg.use_connect = True
with ov(arm): bpy.ops.object.mode_set(mode='OBJECT')
# parent with automatic weights
for o in bpy.data.objects: o.select_set(False)
body.select_set(True); arm.select_set(True); bpy.context.view_layer.objects.active = arm
# manual distance-based weights (bone heat fails on dense multi-shell AI meshes)
import numpy as np
N = len(body.data.vertices); V = np.empty(N * 3); body.data.vertices.foreach_get("co", V); V = V.reshape(N, 3)
segs = [(b.name, np.array(b.head_local), np.array(b.tail_local)) for b in arm_data.bones]
R = ST.get("blend", 0.07) * H
W = np.zeros((N, len(segs)))
for j, (bn, hd_, tl_) in enumerate(segs):
    d = tl_ - hd_; L2 = float(d.dot(d)) or 1e-9
    t = np.clip(((V - hd_) @ d) / L2, 0.0, 1.0)
    closest = hd_ + t[:, None] * d
    dist = np.linalg.norm(V - closest, axis=1)
    W[:, j] = np.exp(-(dist / R) ** 2)
far = W.max(axis=1) < 1e-6
nearest = np.argmin([np.linalg.norm(V - (hd_ + np.clip(((V - hd_) @ (tl_ - hd_)) / (float((tl_ - hd_).dot(tl_ - hd_)) or 1e-9), 0, 1)[:, None] * (tl_ - hd_)), axis=1) for _, hd_, tl_ in segs], axis=0)
W[far] = 0.0; W[far, nearest[far]] = 1.0
W /= W.sum(axis=1, keepdims=True)
for j, (bn, _, _) in enumerate(segs):
    vg = body.vertex_groups.new(name=bn)
    idx = np.nonzero(W[:, j] > 0.002)[0]
    for i in idx: vg.add([int(i)], float(W[i, j]), 'REPLACE')
mod = body.modifiers.new("Armature", 'ARMATURE'); mod.object = arm; body.parent = arm
t1 = time.time()
# pose
bpy.context.view_layer.objects.active = arm
with ov(arm): bpy.ops.object.mode_set(mode='POSE')
def rot_world(pb, axis, deg):
    R = mathutils.Matrix.Rotation(math.radians(deg), 4, axis)
    headw = (arm.matrix_world @ pb.matrix).to_translation()
    M = mathutils.Matrix.Translation(headw) @ R @ mathutils.Matrix.Translation(-headw)
    pb.matrix = arm.matrix_world.inverted() @ M @ arm.matrix_world @ pb.matrix
    bpy.context.view_layer.update()
UP = mathutils.Vector((0, 0, 1))
FWD = mathutils.Vector((0, 0, 0)); FWD[F] = -1.0 if ST.get("faces_negative", True) else 1.0   # glTF: character faces +Z -> Blender -Y
SPAN = mathutils.Vector((0, 0, 0)); SPAN[A] = 1.0
def tailw(pb): return (arm.matrix_world @ pb.matrix @ mathutils.Matrix.Translation((0, pb.length, 0))).to_translation()
def rot_toward(pb, axis, deg, want):
    """Rotate about a world axis so that the bone tip moves toward direction `want` (sign chosen numerically)."""
    t0_ = tailw(pb); rot_world(pb, axis, deg); d = tailw(pb) - t0_
    if d.dot(want) < 0: rot_world(pb, axis, -2 * deg)
drop = ST.get("arm_drop", 78.0)
for side, s in (("L", 1), ("R", -1)):
    ua, fa, hd = (arm.pose.bones[n] for n in bones[side])
    rot_toward(ua, FWD, drop, -UP)                                   # arm swings down along the body
    rot_toward(ua, SPAN, ST.get("arm_fwd", 7.0), FWD)                # hands hang slightly forward
    rot_toward(fa, SPAN, ST.get("elbow_bend", 16.0), FWD)            # elbow bend
    rot_toward(hd, SPAN, ST.get("hand", 8.0), FWD)
    # pronate: twist the forearm about its own axis so the palm faces the thigh
    ax = (tailw(fa) - (arm.matrix_world @ fa.matrix).to_translation()).normalized()
    rot_world(fa, ax, s * ST.get("twist_sign", -1.0) * ST.get("twist", 80.0))
lean = ST.get("lean", 4.0); free = ST.get("free_leg", "L"); sfree = 1 if free == "L" else -1
rot_toward(arm.pose.bones["Root"], FWD, lean, SPAN * sfree)         # pelvis tips toward the free leg side
rot_toward(arm.pose.bones["Spine"], FWD, lean * 1.1, -SPAN * sfree) # torso counter-tilts
rot_toward(arm.pose.bones[f"UpLeg_{free}"], SPAN, ST.get("leg_fwd", 7.0), FWD)
rot_toward(arm.pose.bones[f"Leg_{free}"], SPAN, ST.get("knee", 12.0), -FWD)
rot_world(arm.pose.bones["Head"], UP, ST.get("head_turn", 9.0))
with ov(arm): bpy.ops.object.mode_set(mode='OBJECT')
# bake
bpy.context.view_layer.objects.active = body
dg = bpy.context.evaluated_depsgraph_get(); ev = body.evaluated_get(dg)
baked = bpy.data.meshes.new_from_object(ev, preserve_all_data_layers=True, depsgraph=dg)
old_me = body.data; body.data = baked
for mod in list(body.modifiers): body.modifiers.remove(mod)
bpy.data.meshes.remove(old_me)
body.parent = None; body.matrix_world = mathutils.Matrix.Identity(4)
for vg in list(body.vertex_groups): body.vertex_groups.remove(vg)
bpy.data.objects.remove(arm)
# textures 8K -> 4K
for img in bpy.data.images:
    if img.size[0] > 4096 or img.size[1] > 4096: img.scale(4096, 4096)
# feet to the floor, origin at the floor centre
co = [body.matrix_world @ v.co for v in body.data.vertices]
mn = mathutils.Vector((min(c.x for c in co), min(c.y for c in co), min(c.z for c in co)))
mx = mathutils.Vector((max(c.x for c in co), max(c.y for c in co), max(c.z for c in co)))
shift = mathutils.Vector(((mn.x + mx.x) / 2, (mn.y + mx.y) / 2, mn.z))
for v in body.data.vertices: v.co -= shift
body.data.update()
body.name = NAME; body.data.name = NAME
for o in bpy.data.objects: o.select_set(o == body)
out = os.path.join(OUT_DIR, f"{NAME}.glb")
with ov(body): bpy.ops.export_scene.gltf(filepath=out, export_format='GLB', use_selection=True, export_apply=True, export_yup=True)
# check render
h = mx.z - mn.z
cam = bpy.data.cameras.new("c"); cob = bpy.data.objects.new("c", cam); bpy.context.scene.collection.objects.link(cob)
cob.location = mathutils.Vector((h * 0.9, -h * 1.7, h * 0.6)); cob.rotation_euler = (mathutils.Vector((0, 0, h * 0.5)) - cob.location).to_track_quat('-Z', 'Y').to_euler()
bpy.context.scene.camera = cob
sun = bpy.data.lights.new("s", 'SUN'); so = bpy.data.objects.new("s", sun); bpy.context.scene.collection.objects.link(so); so.rotation_euler = (math.radians(50), 0, math.radians(30)); sun.energy = 3
w = bpy.context.scene.world or bpy.data.worlds.new("W"); bpy.context.scene.world = w; w.use_nodes = True; w.node_tree.nodes["Background"].inputs[0].default_value = (0.6, 0.6, 0.6, 1)
sc = bpy.context.scene; sc.render.engine = 'BLENDER_EEVEE'; sc.render.resolution_x = 480; sc.render.resolution_y = 640
sc.render.filepath = os.path.join(OUT_DIR, f"check_{NAME}.png")
with ov(body): bpy.ops.render.render(write_still=True)
RESULT = {"name": NAME, "out": out, "height": round(h, 3), "span_axis": "x" if span_x else "y", "armz": round(armz - mnz, 3), "weights_s": round(t1 - t0, 1), "total_s": round(time.time() - t0, 1)}
print("POSED", RESULT)
