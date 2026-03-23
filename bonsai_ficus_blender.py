"""
============================================================
  Ficus Retusa Bonsai – Dáng Ngang (Slanted/Moyogi)
  Blender Python Script – 3D Model Generator
  Tác giả: SpongeBot | Gửi cô Dao Thi Nhan
  Cách dùng: Mở Blender → Scripting → Paste & Run
============================================================
"""

import bpy
import math
import random
from mathutils import Vector, Euler

# ── Tiện ích ──────────────────────────────────────────────
def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for col in bpy.data.collections:
        bpy.data.collections.remove(col)

def set_material(obj, name, color, roughness=0.8, metallic=0.0, emission=None):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    if emission:
        bsdf.inputs["Emission Color"].default_value = (*emission, 1.0)
        bsdf.inputs["Emission Strength"].default_value = 0.3
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)
    return mat

# ── Xóa scene cũ ─────────────────────────────────────────
clear_scene()

# ══════════════════════════════════════════════════════════
# 1. CHẬU BÔN-SAI (Rectangular Pot)
# ══════════════════════════════════════════════════════════
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, -0.15))
pot = bpy.context.active_object
pot.name = "Pot"
pot.scale = (2.0, 1.3, 0.5)
bpy.ops.object.transform_apply(scale=True)
set_material(pot, "PotMaterial", (0.45, 0.28, 0.12), roughness=0.9)

# Vành chậu
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.1))
rim = bpy.context.active_object
rim.name = "PotRim"
rim.scale = (2.15, 1.45, 0.08)
bpy.ops.object.transform_apply(scale=True)
set_material(rim, "PotRimMaterial", (0.52, 0.33, 0.15), roughness=0.85)

# Đế chậu
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, -0.42))
base = bpy.context.active_object
base.name = "PotBase"
base.scale = (1.85, 1.15, 0.08)
bpy.ops.object.transform_apply(scale=True)
set_material(base, "BaseMaterial", (0.38, 0.22, 0.09), roughness=0.95)

# ══════════════════════════════════════════════════════════
# 2. ĐẤT & RÊU (Soil + Moss)
# ══════════════════════════════════════════════════════════
bpy.ops.mesh.primitive_cylinder_add(radius=1.85, depth=0.12, location=(0, 0, 0.16))
soil = bpy.context.active_object
soil.name = "Soil"
soil.scale = (1.0, 0.65, 1.0)
bpy.ops.object.transform_apply(scale=True)
set_material(soil, "SoilMaterial", (0.22, 0.14, 0.07), roughness=1.0)

# Rêu xanh trên đất
for i in range(6):
    angle = i * (math.pi / 3)
    x = 0.6 * math.cos(angle) * random.uniform(0.5, 1.0)
    y = 0.35 * math.sin(angle) * random.uniform(0.5, 1.0)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.25, location=(x, y, 0.22))
    moss = bpy.context.active_object
    moss.name = f"Moss_{i}"
    moss.scale = (1.0, 1.0, 0.4)
    bpy.ops.object.transform_apply(scale=True)
    green_v = random.uniform(0.28, 0.42)
    set_material(moss, f"MossMat_{i}", (0.12, green_v, 0.10), roughness=1.0)

# ══════════════════════════════════════════════════════════
# 3. NEBARI (Exposed Root Base)
# ══════════════════════════════════════════════════════════
root_data = [
    # (start_x, start_y, end_x, end_y, thickness)
    (-0.3,  0.0, -1.4,  0.3, 0.12),
    (-0.2, -0.2, -1.1, -0.5, 0.09),
    ( 0.1,  0.1, -0.8,  0.6, 0.08),
    ( 0.3,  0.0,  1.3,  0.2, 0.11),
    ( 0.2, -0.1,  1.0, -0.4, 0.08),
]
for idx, (sx, sy, ex, ey, thick) in enumerate(root_data):
    verts = []
    steps = 8
    for s in range(steps + 1):
        t = s / steps
        x = sx + (ex - sx) * t
        y = sy + (ey - sy) * t
        z = 0.18 - t * 0.1
        verts.append(Vector((x, y, z)))
    # Create curve for root
    curve_data = bpy.data.curves.new(f"RootCurve_{idx}", type='CURVE')
    curve_data.dimensions = '3D'
    curve_data.bevel_depth = thick
    spline = curve_data.splines.new('NURBS')
    spline.points.add(len(verts) - 1)
    for i, v in enumerate(verts):
        spline.points[i].co = (v.x, v.y, v.z, 1)
    root_obj = bpy.data.objects.new(f"Root_{idx}", curve_data)
    bpy.context.scene.collection.objects.link(root_obj)
    set_material(root_obj, f"RootMat_{idx}", (0.38, 0.24, 0.11), roughness=0.9)

# ══════════════════════════════════════════════════════════
# 4. THÂN CÂY (Main Trunk - Slanted ~35 degrees)
# ══════════════════════════════════════════════════════════
trunk_points = [
    Vector((0.0,  0.0, 0.2)),   # Gốc
    Vector((0.3,  0.0, 1.0)),   # Đoạn 1
    Vector((0.65, 0.0, 1.9)),   # Đoạn 2
    Vector((1.05, 0.0, 2.85)),  # Đoạn 3
    Vector((1.45, 0.1, 3.75)),  # Đoạn 4
    Vector((1.78, 0.05,4.5)),   # Đoạn 5
    Vector((2.05,-0.05,5.1)),   # Đỉnh
]
trunk_thickness = [0.28, 0.24, 0.20, 0.16, 0.12, 0.09, 0.06]

curve_data = bpy.data.curves.new("TrunkCurve", type='CURVE')
curve_data.dimensions = '3D'
curve_data.bevel_depth = 0.0  # We'll use separate segments

# Build trunk as NURBS curve with varying bevel
spline = curve_data.splines.new('NURBS')
spline.points.add(len(trunk_points) - 1)
for i, pt in enumerate(trunk_points):
    spline.points[i].co = (pt.x, pt.y, pt.z, 1)
spline.use_endpoint_u = True
trunk_obj = bpy.data.objects.new("Trunk", curve_data)
curve_data.bevel_depth = 0.22
bpy.context.scene.collection.objects.link(trunk_obj)
set_material(trunk_obj, "TrunkMaterial", (0.32, 0.18, 0.08), roughness=0.92)

# ══════════════════════════════════════════════════════════
# 5. CÀNH SƠ CẤP (Primary Branches)
# ══════════════════════════════════════════════════════════
branches = [
    # (origin_on_trunk_t, direction_vec, length, thickness, sub_branches)
    # Cành 1 - Đối diện hướng nghiêng (về phía trái)
    {"start": Vector((0.65, 0.0, 1.9)), "end": Vector((-1.4, 0.3, 2.4)),
     "thick": 0.14, "name": "Branch1_Main"},
    # Cành 2 - Hướng ra sau/phải  
    {"start": Vector((1.05, 0.0, 2.85)), "end": Vector((2.8, -0.8, 3.1)),
     "thick": 0.11, "name": "Branch2_Main"},
    # Cành 3 - Trung bình, hướng trái
    {"start": Vector((1.45, 0.1, 3.75)), "end": Vector((-0.2, 0.2, 4.1)),
     "thick": 0.09, "name": "Branch3_Main"},
    # Cành 4 - Trên cùng / đỉnh
    {"start": Vector((1.78, 0.05, 4.5)), "end": Vector((1.1, 0.0, 5.3)),
     "thick": 0.07, "name": "Branch4_Apex"},
]

for b in branches:
    cd = bpy.data.curves.new(b["name"] + "_curve", 'CURVE')
    cd.dimensions = '3D'
    cd.bevel_depth = b["thick"]
    sp = cd.splines.new('NURBS')
    sp.points.add(1)
    sp.points[0].co = (b["start"].x, b["start"].y, b["start"].z, 1)
    sp.points[1].co = (b["end"].x,   b["end"].y,   b["end"].z, 1)
    sp.use_endpoint_u = True
    bobj = bpy.data.objects.new(b["name"], cd)
    bpy.context.scene.collection.objects.link(bobj)
    set_material(bobj, b["name"] + "_mat", (0.30, 0.17, 0.08), roughness=0.9)

# Sub-branches
sub_branches = [
    # Branch 1 sub
    {"start": Vector((-0.4, 0.2, 2.15)), "end": Vector((-1.8, 0.5, 2.55)), "thick": 0.07},
    {"start": Vector((-1.0, 0.25, 2.28)), "end": Vector((-2.2, 0.1, 2.38)),"thick": 0.055},
    {"start": Vector((-1.4, 0.3, 2.4)), "end": Vector((-2.5, 0.4, 2.3)),   "thick": 0.045},
    # Branch 2 sub
    {"start": Vector((2.0, -0.5, 2.95)), "end": Vector((3.2, -1.2, 3.0)),  "thick": 0.06},
    {"start": Vector((2.8, -0.8, 3.1)), "end": Vector((3.5, -0.5, 2.9)),   "thick": 0.045},
    # Branch 3 sub
    {"start": Vector((0.8, 0.15, 3.9)), "end": Vector((-0.8, 0.3, 4.0)),   "thick": 0.05},
    # Apex sub
    {"start": Vector((1.45, 0.02, 4.9)), "end": Vector((0.7, 0.0, 5.5)),   "thick": 0.04},
]
for idx, sb in enumerate(sub_branches):
    cd = bpy.data.curves.new(f"SubBranch_{idx}_curve", 'CURVE')
    cd.dimensions = '3D'
    cd.bevel_depth = sb["thick"]
    sp = cd.splines.new('NURBS')
    sp.points.add(1)
    sp.points[0].co = (sb["start"].x, sb["start"].y, sb["start"].z, 1)
    sp.points[1].co = (sb["end"].x,   sb["end"].y,   sb["end"].z, 1)
    sp.use_endpoint_u = True
    sobj = bpy.data.objects.new(f"SubBranch_{idx}", cd)
    bpy.context.scene.collection.objects.link(sobj)
    set_material(sobj, f"SubBranchMat_{idx}", (0.28, 0.16, 0.07), roughness=0.9)

# ══════════════════════════════════════════════════════════
# 6. RỄ KHÍ SINH (Aerial Roots – Ficus đặc trưng)
# ══════════════════════════════════════════════════════════
aerial_roots = [
    {"start": Vector((1.6, 0.0, 3.5)), "end": Vector((1.55, 0.05, 0.22))},
    {"start": Vector((1.8, -0.1, 3.9)),"end": Vector((1.75, -0.08, 0.22))},
    {"start": Vector((1.2, 0.1, 3.2)), "end": Vector((1.15, 0.12, 0.22))},
]
for idx, ar in enumerate(aerial_roots):
    mid = Vector(((ar["start"].x + ar["end"].x)/2 + random.uniform(-0.1,0.1),
                  (ar["start"].y + ar["end"].y)/2 + random.uniform(-0.05,0.05),
                  (ar["start"].z + ar["end"].z)/2))
    cd = bpy.data.curves.new(f"AerialRoot_{idx}_curve", 'CURVE')
    cd.dimensions = '3D'
    cd.bevel_depth = 0.025
    sp = cd.splines.new('NURBS')
    sp.points.add(2)
    sp.points[0].co = (ar["start"].x, ar["start"].y, ar["start"].z, 1)
    sp.points[1].co = (mid.x, mid.y, mid.z, 1)
    sp.points[2].co = (ar["end"].x, ar["end"].y, ar["end"].z, 1)
    sp.use_endpoint_u = True
    arobj = bpy.data.objects.new(f"AerialRoot_{idx}", cd)
    bpy.context.scene.collection.objects.link(arobj)
    set_material(arobj, f"AerialRootMat_{idx}", (0.48, 0.35, 0.20), roughness=0.85)

# ══════════════════════════════════════════════════════════
# 7. TÁN LÁ (Foliage Pads – Cloud-style)
# ══════════════════════════════════════════════════════════
foliage_pads = [
    # (center_x, y, z, rx, ry, rz)  – ellipsoid pads
    # Pad 1 – Cành 1 trái dưới
    (-1.8,  0.3,  2.5,  0.7, 0.45, 0.4),
    (-2.2,  0.1,  2.35, 0.55,0.38, 0.35),
    (-1.4,  0.4,  2.3,  0.5, 0.4,  0.3),
    # Pad 2 – Cành 2 phải
    (3.1,  -1.0,  3.0,  0.65,0.42, 0.38),
    (3.5,  -0.7,  2.85, 0.5, 0.38, 0.3),
    # Pad 3 – Cành 3 trung bình
    (-0.6,  0.25, 4.15, 0.7, 0.45, 0.42),
    (-1.0,  0.3,  4.0,  0.5, 0.4,  0.32),
    # Pad 4 – Đỉnh / Apex
    ( 0.8,  0.05, 5.4,  0.65,0.42, 0.38),
    ( 0.5,  0.0,  5.25, 0.5, 0.38, 0.3),
    ( 1.1, -0.05, 5.3,  0.48,0.35, 0.28),
    # Pad 5 – Lấp đầy trung tâm
    ( 1.2,  0.0,  3.9,  0.55,0.38, 0.35),
]

for idx, (cx, cy, cz, rx, ry, rz) in enumerate(foliage_pads):
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=1.0,
        location=(cx, cy, cz),
        segments=12, ring_count=8
    )
    fpad = bpy.context.active_object
    fpad.name = f"FoliagePad_{idx}"
    fpad.scale = (rx, ry, rz)
    bpy.ops.object.transform_apply(scale=True)
    # Slight random rotation for naturalistic look
    fpad.rotation_euler = Euler((
        random.uniform(-0.1, 0.1),
        random.uniform(-0.1, 0.1),
        random.uniform(-0.15, 0.15)
    ))
    # Vary green shades
    g_val = random.uniform(0.38, 0.52)
    r_val = random.uniform(0.08, 0.18)
    set_material(fpad, f"FoliageMat_{idx}",
                 (r_val, g_val, r_val * 0.6),
                 roughness=random.uniform(0.7, 0.9))

# ══════════════════════════════════════════════════════════
# 8. ÁNH SÁNG & CAMERA
# ══════════════════════════════════════════════════════════
# Key light (Sun from front-top-right)
bpy.ops.object.light_add(type='SUN', location=(4, -5, 8))
sun = bpy.context.active_object
sun.name = "KeyLight"
sun.data.energy = 3.5
sun.data.color = (1.0, 0.98, 0.92)
sun.rotation_euler = Euler((math.radians(45), 0, math.radians(30)))

# Fill light (soft area from left)
bpy.ops.object.light_add(type='AREA', location=(-4, -2, 5))
fill = bpy.context.active_object
fill.name = "FillLight"
fill.data.energy = 150
fill.data.color = (0.85, 0.92, 1.0)
fill.data.size = 3.0

# Rim light (back)
bpy.ops.object.light_add(type='SPOT', location=(0, 5, 7))
rim = bpy.context.active_object
rim.name = "RimLight"
rim.data.energy = 300
rim.data.color = (0.9, 1.0, 0.9)
rim.rotation_euler = Euler((math.radians(-40), 0, 0))

# Camera – 3/4 view
bpy.ops.object.camera_add(location=(5.5, -6.5, 4.5))
cam = bpy.context.active_object
cam.name = "BonsaiCamera"
cam.rotation_euler = Euler((math.radians(65), 0, math.radians(40)))
cam.data.lens = 50
bpy.context.scene.camera = cam

# ══════════════════════════════════════════════════════════
# 9. RENDER SETTINGS
# ══════════════════════════════════════════════════════════
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 128
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.filepath = "/tmp/ficus_bonsai_slanted_render.png"
scene.render.image_settings.file_format = 'PNG'

# World background (sky blue-grey)
world = bpy.data.worlds['World']
world.use_nodes = True
bg = world.node_tree.nodes.get('Background')
if bg:
    bg.inputs['Color'].default_value = (0.72, 0.82, 0.88, 1.0)
    bg.inputs['Strength'].default_value = 0.8

# ══════════════════════════════════════════════════════════
# 10. XUẤT FILE / RENDER
# ══════════════════════════════════════════════════════════
# Render (bỏ comment dòng dưới để render ngay)
# bpy.ops.render.render(write_still=True)

print("=" * 60)
print("✅  Ficus Retusa Bonsai – Dáng Ngang đã được tạo xong!")
print("    Nhấn F12 để render, hoặc bỏ comment dòng bpy.ops.render.render()")
print("    Output: /tmp/ficus_bonsai_slanted_render.png")
print("=" * 60)
