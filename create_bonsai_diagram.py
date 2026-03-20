#!/usr/bin/env python3
"""
Simple ASCII and text-based bonsai diagram generator
Since we don't have matplotlib/PIL, we'll create a text-based visualization
"""

def create_ascii_bonsai_1():
    """Cây 1: Moyogi style với thân cong S nhẹ"""
    diagram = """
BONSAI 1: MOYOGI CỔ ĐIỂN (Thân cong chữ S)
═══════════════════════════════════════════

                    ╭─🍃🍃🍃─╮
                   🍃   ╰🌿╯   🍃     ← Tầng lá trên (350-450mm)
                    🍃🍃 │ 🍃🍃
                        ╱│╲
                       ╱ │ ╲
                      ╱  │  ╲         Ngọn nghiêng trái 15°
                     ╱   │   ╲
                    ╱    │    ╲
                   │     │     │
            🍃─────┤     │     │      ← Cành 2 (200mm, góc 45°)
          🍃🍃     │     │     │
         🍃  🍃    │    ╱      │
                   │   ╱       │
                   │  ╱        │      Điểm uốn 2: Cong TRÁI 45°
                   │ ╱         │
    🍃🍃           │╱          │
   🍃🍃🍃─────────┤            │      ← Cành 1 (120mm, góc 65°)
    🍃🍃           ╲            │
                    ╲          │
                     ╲         │
                      ╲       ╱       Điểm uốn 1: Cong PHẢI 35°
                       ╲     ╱
                        ╲   ╱
                         ╲ ╱
                          │
                          │           Thân: 50mm → 15mm
                          │
                        ══╧══
                      ╔═══════╗
                      ║ 為榮  ║       Chậu lục giác
                      ║ 有余  ║
                      ╚═══════╝

THÔNG SỐ KỸ THUẬT:
├─ Chiều cao: 450mm
├─ Đường kính gốc: 50mm
├─ Phong cách: Moyogi (非直幹樹形)
├─ Số tầng lá: 2
└─ Độ cong: Trung bình (S-curve cổ điển)
"""
    return diagram

def create_ascii_bonsai_2():
    """Cây 2: Moyogi/Bankan với thân cong mạnh"""
    diagram = """
BONSAI 2: MOYOGI/BANKAN MẠNH (Thân xoắn vòng)
═══════════════════════════════════════════════

                         ╭─🍃🍃─╮
                        🍃   🌿   🍃    ← Tầng lá chính (320-420mm)
                         🍃🍃│🍃🍃
                            ╱│╲
                           ╱ │ ╲
                          ╱  │  ╲      Ngọn vươn lên 35°
                         │   │   │
🍃🍃🍃🍃─────────────────┤   │   │     ← Cành trái DÀI (280mm)
 🍃🍃🍃                  │  ╱    │       Góc 10° (gần ngang)
  🍃🍃                  │ ╱     │
                        │╱      │
                       ╱        │
                      ╱         │      Điểm uốn 3: Vươn lên
                     ╱          │
                    ╱          ╱
                   ╱          ╱
                  ╱          ╱         Điểm uốn 2: Nằm NGANG 85° !!
                 ╱══════════╯
                ╱
               ╱
              ╱                         Điểm uốn 1: Cong PHẢI 60°
             ╱
            ╱
           │
           │                            Thân: 60mm → 18mm
           │
         ══╧══
       ╔═══════╗
       ║ 九鶴  ║                       Chậu lục giác
       ║ 鳴皐  ║
       ╚═══════╝

THÔNG SỐ KỸ THUẬT:
├─ Chiều cao: 420mm
├─ Đường kính gốc: 60mm
├─ Phong cách: Moyogi mạnh / Bankan (蟠幹樹形)
├─ Đặc điểm: Thân gần như nằm ngang rồi vươn lên
├─ Cành ngang: 280mm (rất dài, tạo cân bằng động)
└─ Độ cong: CỰC MẠNH (Dynamic S-curve)
"""
    return diagram

def create_3d_coordinates():
    """Export 3D coordinates for external tools"""
    coords = """
═══════════════════════════════════════════════════
TỌA ĐỘ 3D CHO BLENDER/FREECAD (X, Y, Z in meters)
═══════════════════════════════════════════════════

BONSAI 1 - MOYOGI CỔ ĐIỂN:
──────────────────────────
Trunk spine (Bezier curve points):
  P0: (0.000, 0.000, 0.000)    # Gốc
  P1: (0.050, 0.000, 0.150)    # Cong phải 35°
  P2: (-0.080, 0.000, 0.300)   # Cong trái 45°
  P3: (-0.030, 0.000, 0.450)   # Ngọn

Branch 1 (left, 120mm):
  Start: (0.050, 0.000, 0.120)
  End: (-0.150, 0.000, 0.100)
  Radius: 0.008m

Branch 2 (right, 200mm):
  Start: (-0.050, 0.000, 0.200)
  End: (0.120, 0.000, 0.250)
  Radius: 0.007m

Foliage 1 (icosphere):
  Center: (-0.150, 0.000, 0.150)
  Radius: 0.120m

Foliage 2 (icosphere):
  Center: (-0.030, 0.000, 0.420)
  Radius: 0.100m

───────────────────────────────────────────────────

BONSAI 2 - MOYOGI/BANKAN MẠNH:
───────────────────────────────
Trunk spine (Bezier curve points):
  P0: (0.000, 0.000, 0.000)    # Gốc
  P1: (0.100, 0.000, 0.100)    # Cong phải 60°
  P2: (0.250, 0.000, 0.150)    # Nằm ngang 85° !!
  P3: (0.150, 0.000, 0.320)    # Vươn lên 35°
  P4: (0.120, 0.000, 0.420)    # Ngọn

Main branch (left horizontal, 280mm):
  Start: (0.250, 0.000, 0.150)
  End: (-0.030, 0.000, 0.160)
  Radius: 0.010m

Foliage 1 (left branch):
  Center: (-0.100, 0.000, 0.180)
  Radius: 0.140m

Foliage 2 (main top):
  Center: (0.120, 0.000, 0.400)
  Radius: 0.130m

═══════════════════════════════════════════════════

Lưu ý: Tọa độ ở đơn vị mét (m). 
Nhân với 1000 để chuyển sang mm.
"""
    return coords

def main():
    print("Generating bonsai diagrams...\n")
    
    # Generate diagrams
    diagram1 = create_ascii_bonsai_1()
    diagram2 = create_ascii_bonsai_2()
    coords = create_3d_coordinates()
    
    # Save to file
    output_file = "/data/workspace/bonsai_3d_diagrams.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(diagram1)
        f.write("\n\n")
        f.write(diagram2)
        f.write("\n\n")
        f.write(coords)
    
    print(f"✅ Diagrams saved to: {output_file}")
    print("\nPreview:\n")
    print(diagram1)
    print("\n" + "="*60 + "\n")
    print(diagram2[:800] + "...")

if __name__ == "__main__":
    main()
