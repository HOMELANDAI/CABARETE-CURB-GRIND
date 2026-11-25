# CCG deck pass (Blender 5.2, run via MCP execute_blender_code or Text Editor).
# raw/CCG_Deck_<Name>_tripo.glb -> clean -> PCA level -> 0.82 m -> CCG_Deck_<Name>.glb
# NOTE: the mass-count flip heuristic picked the wrong side for StormburnSunrise and
# VicewaveSwell (v5c); those were corrected afterwards with flip_deck_gltf.mjs.
# Always eyeball decks\check\*_under.png after a pass: trucks must be visible from below.
import bpy, bmesh, numpy as np, mathutils, os, math, json
SRC=r"F:\HOMELANDAI\CURBSIDE GRIND (CCG)\03_MODELS_3D\tripo_pipeline\decks"; LEN=0.82
def ctx():
    for w in bpy.context.window_manager.windows:
        for a in w.screen.areas:
            if a.type=='VIEW_3D': return dict(window=w,area=a,region=[r for r in a.regions if r.type=='WINDOW'][0])
    return {}
def process(nm):
    for o in list(bpy.data.objects): bpy.data.objects.remove(o,do_unlink=True)
    for c in (bpy.data.meshes,bpy.data.materials,bpy.data.images):
        for x in list(c):
            if x.users==0: c.remove(x)
    bpy.ops.import_scene.gltf(filepath=os.path.join(SRC,"raw","CCG_Deck_%s_tripo.glb"%nm)); bpy.ops.file.pack_all()
    meshes=[o for o in bpy.data.objects if o.type=='MESH']
    for o in meshes: o.select_set(True)
    bpy.context.view_layer.objects.active=meshes[0]
    if len(meshes)>1:
        with bpy.context.temp_override(**ctx()): bpy.ops.object.join()
    ob=bpy.context.view_layer.objects.active; ob.parent=None
    for o in list(bpy.data.objects):
        if o.type!='MESH': bpy.data.objects.remove(o,do_unlink=True)
    bpy.ops.object.select_all(action='DESELECT'); ob.select_set(True)
    with bpy.context.temp_override(**ctx()): bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
    bm=bmesh.new(); bm.from_mesh(ob.data)
    bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=0.0001)
    bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_faces],context='VERTS')
    bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
    P=np.array([v.co[:] for v in bm.verts]); c=P.mean(0); Q=P-c
    w_,V=np.linalg.eigh(Q.T@Q); ax=V[:,2]; nrm=V[:,0]
    if ax[0]<0: ax=-ax
    if nrm[2]<0: nrm=-nrm
    y=np.cross(nrm,ax); y/=np.linalg.norm(y); nrm2=np.cross(ax,y)
    M=mathutils.Matrix((tuple(ax),tuple(y),tuple(nrm2))); cv=mathutils.Vector(c)
    for v in bm.verts: v.co=M@(v.co-cv)
    zs=np.array([v.co.z for v in bm.verts])
    if (zs>0.03).sum()>(zs<-0.03).sum():   # wheels/trucks should be -Z (below deck)
        for v in bm.verts: v.co.y=-v.co.y; v.co.z=-v.co.z
    xs=np.array([v.co.x for v in bm.verts]); s=LEN/(xs.max()-xs.min())
    for v in bm.verts: v.co*=s
    xs=np.array([v.co.x for v in bm.verts]); ys=np.array([v.co.y for v in bm.verts]); zs=np.array([v.co.z for v in bm.verts])
    off=mathutils.Vector(((xs.max()+xs.min())/2,(ys.max()+ys.min())/2,zs.min()))
    for v in bm.verts: v.co-=off
    bm.to_mesh(ob.data); bm.free(); ob.data.update()
    for p in ob.data.polygons: p.use_smooth=True
    with bpy.context.temp_override(**ctx()):
        try: bpy.ops.object.shade_smooth_by_angle(angle=math.radians(35))
        except Exception as e: print("smooth",e)
    ob.name="SM_Deck_"+nm; ob.data.name="SM_Deck_"+nm
    for i,sl in enumerate(ob.material_slots):
        if sl.material: sl.material.name="M_Deck_%s%s"%(nm,"" if i==0 else "_%d"%i)
    out=os.path.join(SRC,"CCG_Deck_%s.glb"%nm)
    with bpy.context.temp_override(**ctx()):
        bpy.ops.export_scene.gltf(filepath=out,export_format='GLB',use_selection=True,export_apply=True,export_image_format='AUTO')
    d=ob.dimensions; return dict(name=nm,tris=len(ob.data.loop_triangles) if ob.data.loop_triangles else len(ob.data.polygons),dims=[round(x,3) for x in d])

if __name__=="__main__":
    for nm in ["SpiceDrizzleDrop","VicewaveSwell","ViceMonsoonLuxeRemix","StormburnSunrise","PurpledownDrip"]:
        print(json.dumps(process(nm)))
