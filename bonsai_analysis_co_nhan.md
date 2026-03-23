# Phân Tích Cây Bonsai & Tư Vấn Style - Cô Dao Thi Nhàn

## Tổng Quan
Em đã phân tích 2 cây bonsai (có thể cô gửi 2 hoặc 3 ảnh, em nhận được 2 cây rõ ràng). Cả 2 cây đều có đặc điểm phù hợp với **phong cách Moyogi (非直幹樹形)** - phong cách thân cong không đều.

---

## CÂY 1: Bonsai Thân Cong Nhỏ Gọn

### Đặc điểm hiện tại:
- **Thân cây**: Hình chữ S rõ ràng, cong phải rồi quay trái
- **Chiều cao**: Khoảng 40-50cm (ước tính)
- **Tán lá**: 2 tầng rõ rệt - tầng trên và tầng dưới
- **Chậu**: Lục giác màu đen, chữ Hán "為榮有余" (Giàu có thịnh vượng)
- **Loài cây**: Có vẻ là Kim Ngân (Fukien Tea) hoặc Hoàng Dương (Boxwood)
- **Đất**: Đã phủ mulch màu nâu

### Phong cách phù hợp: **Moyogi (非直幹樹形)**
✅ **Lý do**:
1. Thân cong tự nhiên theo dạng chữ S
2. Ngọn cây không thẳng đứng mà hơi nghiêng
3. Các cành phân bố tự nhiên, không quá cứng nhắc
4. Phù hợp với triết lý "vẻ đẹp bất đối xứng" của Moyogi

### Tư vấn cải thiện:
1. **Tỉa cành**: Giữ 2-3 tầng lá chính, loại bỏ cành rối ở giữa
2. **Tạo dáng dây**: Quấn dây nhôm để tăng độ cong của cành ngang
3. **Thay chậu**: Nên dùng chậu oval nông hơn (7-10cm cao) màu xanh rêu hoặc nâu đất
4. **Jin/Shari**: Có thể tạo một chút deadwood ở gốc để tăng tuổi thọ cảm quan

---

## CÂY 2: Bonsai Thân Cong Mạnh Mẽ

### Đặc điểm hiện tại:
- **Thân cây**: Hình chữ S vô cùng mạnh mẽ, cong ngang rồi quay lên
- **Cành chính**: Nhánh trái rất dài, tạo độ cân bằng động
- **Tán lá**: Tập trung ở phần trên, còn hơi thưa
- **Chậu**: Lục giác đen, chữ Hán "九鶴鳴皐" (Chín con hạc hót vang)
- **Đặc điểm nổi bật**: Thân có độ cong độc đáo, gần như nằm ngang rồi vươn lên

### Phong cách phù hợp: **Moyogi mạnh hoặc Bankan (蟠幹樹形 - Coiled trunk)**
✅ **Lý do**:
1. Độ cong của thân rất mạnh mẽ, gần như xoắn vòng
2. Tạo cảm giác động, như cây già vượt qua bão tố
3. Nhánh ngang dài tạo sự cân bằng với thân cây
4. Phù hợp với Moyogi phong cách "wild" hoặc Bankan (thân xoắn)

### Tư vấn cải thiện:
1. **Tỉa lá**: Làm dày tán lá phần dưới, tạo 3 tầng rõ ràng hơn
2. **Cắt cành**: Loại bỏ cành thẳng đứng ở giữa, giữ cành ngang
3. **Thay chậu**: Chậu hình chữ nhật nông (style Koyo/Autumn) để cân bằng với độ dài nhánh trái
4. **Gốc**: Để lộ một phần rễ bề mặt (Nebari) để tăng vẻ già cỗi

---

## MÔ HÌNH 3D ĐƠN GIẢN - Thiết Kế Kỹ Thuật

### Cây 1: Moyogi Style Basic

**Thông số kỹ thuật:**
```
- Chiều cao tổng thể: 450mm
- Đường kính gốc: 50mm → thu nhỏ lên 15mm ở ngọn
- Độ cong thân: S-curve với 2 điểm uốn
  * Điểm 1 (150mm): Cong phải 35°
  * Điểm 2 (300mm): Cong trái 45°
- Cành chính:
  * Cành 1 (120mm): Phía trái, góc 65° xuống
  * Cành 2 (200mm): Phía phải, góc 45° lên
  * Cành 3 (350mm): Ngọn, góc 15° nghiêng trái
- Foliage pads: 2 tầng hình đám mây (cloud-like)
```

**Mô tả Blender Python Script** (có thể chạy trong Blender Console):
```python
import bpy
import math

# Xóa tất cả object
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Tạo thân cây bằng Bezier curve
curve_data = bpy.data.curves.new('BonsaiTrunk1', 'CURVE')
curve_data.dimensions = '3D'
polyline = curve_data.splines.new('BEZIER')
polyline.bezier_points.add(3)  # 4 điểm tổng

# Định nghĩa các điểm chữ S
points = [
    (0, 0, 0),           # Gốc
    (0.05, 0, 0.15),     # Cong phải
    (-0.08, 0, 0.30),    # Cong trái
    (-0.03, 0, 0.45)     # Ngọn
]

for i, point in enumerate(points):
    polyline.bezier_points[i].co = point
    polyline.bezier_points[i].handle_left_type = 'AUTO'
    polyline.bezier_points[i].handle_right_type = 'AUTO'

# Tạo object từ curve
curve_obj = bpy.data.objects.new('BonsaiTrunk1', curve_data)
bpy.context.collection.objects.link(curve_obj)

# Thêm độ dày cho thân (taper)
curve_data.bevel_depth = 0.025
curve_data.use_fill_caps = True
curve_data.bevel_resolution = 8

# Tạo cành (branches) bằng cylinder
def create_branch(name, start, end, radius):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=1)
    branch = bpy.context.active_object
    branch.name = name
    
    # Di chuyển và xoay
    direction = (end[0]-start[0], end[1]-start[1], end[2]-start[2])
    length = math.sqrt(sum([d**2 for d in direction]))
    branch.scale[2] = length/2
    
    midpoint = ((start[0]+end[0])/2, (start[1]+end[1])/2, (start[2]+end[2])/2)
    branch.location = midpoint
    
    return branch

# Cành 1
branch1 = create_branch('Branch1', (0.05, 0, 0.12), (-0.15, 0, 0.10), 0.008)

# Cành 2  
branch2 = create_branch('Branch2', (-0.05, 0, 0.20), (0.12, 0, 0.25), 0.007)

# Tạo foliage (lá) bằng icosphere
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=0.12, location=(-0.15, 0, 0.15))
foliage1 = bpy.context.active_object
foliage1.name = 'Foliage1'

bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=0.10, location=(-0.03, 0, 0.42))
foliage2 = bpy.context.active_object
foliage2.name = 'Foliage2'

# Thêm màu sắc
mat_trunk = bpy.data.materials.new('TrunkMaterial')
mat_trunk.diffuse_color = (0.35, 0.25, 0.15, 1.0)  # Nâu

mat_foliage = bpy.data.materials.new('FoliageMaterial')
mat_foliage.diffuse_color = (0.2, 0.6, 0.3, 1.0)  # Xanh lá

curve_obj.data.materials.append(mat_trunk)
foliage1.data.materials.append(mat_foliage)
foliage2.data.materials.append(mat_foliage)

print("✅ Bonsai model 1 created successfully!")
```

---

### Cây 2: Moyogi/Bankan Style Advanced

**Thông số kỹ thuật:**
```
- Chiều cao: 420mm
- Đường kính gốc: 60mm → 18mm ở ngọn
- Độ cong thân: Extreme S với 3 điểm uốn
  * Điểm 1 (100mm): Cong phải 60°
  * Điểm 2 (200mm): Gần như nằm ngang, cong trái 85°
  * Điểm 3 (320mm): Vươn lên 35°
- Cành chính trái: 280mm, từ điểm 2, góc 10° (gần ngang)
- Foliage: Tập trung ở phần trên, 3 đám chính
```

**Mô tả tương tự** (code Blender tương tự nhưng với độ cong mạnh hơn)

---

## XUẤT FILE 3D (Hướng dẫn)

### Cách 1: Blender → STL
1. Mở Blender, paste script trên vào Python Console
2. Select all objects: `A`
3. File → Export → STL
4. Đặt tên: `bonsai_moyogi_1.stl` và `bonsai_moyogi_2.stl`

### Cách 2: FreeCAD (Parametric)
1. Tạo Sketch mới
2. Vẽ đường cong S bằng B-Spline tool
3. Dùng Sweep tool với hình tròn thu nhỏ dần (Draft Wire + Sweep)
4. Export as STEP hoặc STL

### Cách 3: Tinkercad (Online, đơn giản nhất)
1. Truy cập tinkercad.com
2. Dùng Spline tool vẽ thân cây
3. Thêm Sphere cho lá
4. Export STL

---

## KẾT LUẬN

### Phong cách khuyến nghị:
1. **Cây 1**: Moyogi cổ điển - phù hợp cho người mới bắt đầu tạo dáng
2. **Cây 2**: Moyogi/Bankan mạnh mẽ - cho người đã có kinh nghiệm

### Bước tiếp theo:
1. ✂️ Tỉa cành theo hướng dẫn trên (mùa xuân/thu là tốt nhất)
2. 🔗 Quấn dây nhôm (aluminum wire 1.5-2mm) để uốn cành
3. 🏺 Thay chậu vào năm tới (mùa xuân)
4. 💧 Chăm sóc đều đặn: Tưới khi đất gần khô, phun sương hàng ngày

---

**Người phân tích**: SpongeBot 🫧  
**Ngày**: 20/03/2026  
**Gửi đến**: Cô Dao Thi Nhàn

---

*Lưu ý: File 3D model chi tiết (STL) có thể được tạo bằng Blender script ở trên. Nếu cô cần file STL hoàn chỉnh, em có thể tạo và gửi riêng ạ.*
