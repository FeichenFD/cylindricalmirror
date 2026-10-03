"""
圆柱镜面变形画 (cylindrical mirror anamorphosis) 正向映射脚本
像(镜面坐标 theta,zm) -> 物(A4地面坐标)

实物配置:
  可乐罐 R=33mm, L=110mm
  A4 横向 297x210mm, 圆柱在上半矩形中心(原点O=圆柱底面圆心)
  A4 范围: x in [-148.5,148.5], y in [-52.5,157.5], z=0
  图案定义域 Omega = A4 挖去圆柱底面圆

坐标系:
  O 在圆柱底面圆心
  +x 沿 A4 长边水平
  +y 沿 A4 短边指向前方/观察者
  +z 向上(圆柱高度方向)
  圆柱面: x^2+y^2=R^2, 0<=z<=L
  观察者 E=(0, y_E, z_E), y_E>R, z_E>0

映射公式(像->物, 解析):
  x_p(theta,zm) = cos(theta)*[R(z_E-2zm)+2*zm*y_E*sin(theta)] / (z_E-zm)
  y_p(theta,zm) = [R(z_E-2zm)*sin(theta) - zm*y_E*cos(2theta)] / (z_E-zm)
  成立条件: zm < z_E
"""

import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

try:
    from scipy.interpolate import griddata
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False


# ---------- 实物参数 ----------
R = 33.0          # 圆柱半径 mm (可乐罐)
L = 110.0         # 圆柱高 mm
A4_W = 297.0      # A4 横向宽
A4_H = 210.0      # A4 短边高
# A4 范围(相对 O)
X_MIN, X_MAX = -148.5, 148.5
Y_MIN, Y_MAX = -52.5, 157.5

# ---------- 观察者 ----------
Y_E = 250.0       # 前方距离 mm
Z_E = 120.0       # 眼高 mm


def image_to_object(theta, zm, y_E=Y_E, z_E=Z_E, R=R):
    """像坐标(theta, zm) -> 物坐标(x_p, y_p). 向量化."""
    denom = z_E - zm
    xp = np.cos(theta) * (R * (z_E - 2 * zm) + 2 * zm * y_E * np.sin(theta)) / denom
    yp = (R * (z_E - 2 * zm) * np.sin(theta) - zm * y_E * np.cos(2 * theta)) / denom
    return xp, yp


def scan_valid_region(y_E=Y_E, z_E=Z_E, L_val=None, Nt=600, Nz=600):
    """扫描镜面 (theta,zm), 找物点落在 A4 图案区 Omega 内的有效区."""
    if L_val is None:
        L_val = L
    theta = np.linspace(1e-3, np.pi - 1e-3, Nt)
    zm = np.linspace(0.2, min(L_val, z_E) - 0.2, Nz)
    T, Z = np.meshgrid(theta, zm)
    Xp, Yp = image_to_object(T, Z, y_E, z_E)
    in_a4 = (np.abs(Xp) <= X_MAX) & (Yp >= Y_MIN) & (Yp <= Y_MAX)
    in_omega = in_a4 & (Xp**2 + Yp**2 > (R + 0.5) ** 2)
    return T, Z, Xp, Yp, in_omega


def report_region(y_E=Y_E, z_E=Z_E, L_val=None):
    T, Z, Xp, Yp, mask = scan_valid_region(y_E, z_E, L_val)
    th = T[mask]
    zm = Z[mask]
    Lv = L if L_val is None else L_val
    print(f"观察者 E=(0, y_E={y_E}, z_E={z_E}), 圆柱 L={Lv}")
    print(f"镜面有效区(物点落入A4图案区):")
    print(f"  theta 范围: [{th.min():.3f}, {th.max():.3f}] rad  "
          f"(={np.degrees(th.min()):.1f}° ~ {np.degrees(th.max()):.1f}°)")
    print(f"  theta 跨度: {th.max()-th.min():.3f} rad (={np.degrees(th.max()-th.min()):.1f}°)")
    print(f"  zm 范围: [{zm.min():.2f}, {zm.max():.2f}] mm  (上限 min(L,z_E)={min(Lv,z_E)})")
    print(f"  zm 跨度: {zm.max()-zm.min():.2f} mm")
    print(f"  有效区宽高比 (theta跨度 : zm跨度, 归一): "
          f"{(th.max()-th.min())/(zm.max()-zm.min()):.3f} : 1")
    print(f"  覆盖 A4 物点: x in [{Xp[mask].min():.1f},{Xp[mask].max():.1f}], "
          f"y in [{Yp[mask].min():.1f},{Yp[mask].max():.1f}]")
    print(f"  有效点数/总采样: {mask.sum()}/{mask.size} = {mask.mean()*100:.1f}%")
    return th.min(), th.max(), zm.min(), zm.max()


def make_test_image(path, W=800, H=600):
    """生成测试输入图(模拟圆柱中看到的正常图)."""
    img = Image.new("RGB", (W, H), (245, 245, 250))
    d = ImageDraw.Draw(img)
    # 彩色方格背景
    colors = [(220, 60, 60), (60, 160, 90), (60, 110, 200),
              (240, 180, 40), (150, 80, 200)]
    gw, gh = 4, 3
    for i in range(gw):
        for j in range(gh):
            x0 = i * W // gw
            y0 = j * H // gh
            x1 = (i + 1) * W // gw
            y1 = (j + 1) * H // gh
            d.rectangle([x0, y0, x1, y1], fill=colors[(i + j) % len(colors)])
    # 中心圆
    d.ellipse([W//2-90, H//2-90, W//2+90, H//2+90], fill=(250, 250, 250), outline=(30, 30, 30), width=4)
    # 文字
    try:
        font = ImageFont.truetype("arial.ttf", 56)
    except Exception:
        font = ImageFont.load_default()
    d.text((W//2, H//2), "ANAMORPH", fill=(20, 20, 20), anchor="mm", font=font)
    img.save(path)
    return path


def anamorph(input_path, output_path, y_E=Y_E, z_E=Z_E, L_val=None,
             out_dpi=300, Nt=800, Nz=800):
    """把输入正常图转成 A4 上的变形图."""
    if not HAS_SCIPY:
        print("需要 scipy: pip install scipy")
        sys.exit(1)

    # 1. 扫描有效区
    theta_min, theta_max, zm_min, zm_max = report_region(y_E, z_E, L_val)
    print()

    # 2. 读输入图
    img = Image.open(input_path).convert("RGB")
    img = img.transpose(Image.FLIP_TOP_BOTTOM)  # 实测校准: 先上下对调再处理, 罐中成像才是正立
    iw, ih = img.size
    print(f"输入图: {iw}x{ih} px, 宽高比={iw/ih:.3f} (已上下翻转)")
    img_arr = np.asarray(img)  # (ih, iw, 3)

    # 3. 在有效区均匀采样 (theta, zm), 对应输入图 uv
    theta = np.linspace(theta_min, theta_max, Nt)
    zm = np.linspace(zm_min, zm_max, Nz)
    T, Z = np.meshgrid(theta, zm)
    # uv: u 沿 theta(水平), v 沿 zm(垂直).
    # 物空间方向: zm 大 -> y 大(远离罐, 靠观察者方向, A4 底部行).
    # 输入图坐标系: 顶部行=iy=0=v=0, 底部行=iy=ih-1=v=1.
    # 想要: 输入图顶部(iy=0) -> zm 小(靠罐,A4 顶部行),
    #       输入图底部(iy=ih-1) -> zm 大(远离罐,A4 底部行).
    u = (T - theta_min) / (theta_max - theta_min)    # 0..1
    v = (Z - zm_min) / (zm_max - zm_min)             # 0(靠罐) .. 1(远离罐)
    ix = np.clip((u * (iw - 1)).round().astype(int), 0, iw - 1)
    iy = np.clip((v * (ih - 1)).round().astype(int), 0, ih - 1)
    colors = img_arr[iy, ix]  # (Nz, Nt, 3)

    # 4. 算物点
    Xp, Yp = image_to_object(T, Z, y_E, z_E)
    # 筛选 A4 内 + Omega 内
    mask = (np.abs(Xp) <= X_MAX) & (Yp >= Y_MIN) & (Yp <= Y_MAX) & \
           (Xp**2 + Yp**2 > (R + 0.3) ** 2)

    pts = np.column_stack([Xp[mask], Yp[mask]])  # (M,2) 物点 mm
    vals = colors[mask]                            # (M,3)

    # 5. griddata 插值到 A4 规则网格
    px_per_mm = out_dpi / 25.4
    out_w = int(A4_W * px_per_mm)
    out_h = int(A4_H * px_per_mm)
    xs = np.linspace(X_MIN, X_MAX, out_w)
    ys = np.linspace(Y_MAX, Y_MIN, out_h)  # 顶=Y_MAX(后), 底=Y_MIN(前)... 注意图像行0在顶
    # 图像坐标: 行0 = 纸的上边(y=Y_MAX=-52.5? 等等). 我们让图像顶部=A4上边(y=Y_MAX? )
    # A4: y 范围 [-52.5, 157.5]. 上边(纸物理上)=y=-52.5? 不对.
    # 约定: +y 指向前方(观察者). A4 上半放罐, 上半 y 小(负), 下半 y 大(正).
    # 所以纸的"上边"(靠罐后)=y=Y_MIN=-52.5, "下边"(前方)=y=Y_MAX=157.5.
    # 图像行0(顶)=纸上边=y=-52.5, 行底=纸下边=y=157.5.
    ys = np.linspace(Y_MIN, Y_MAX, out_h)
    GX, GY = np.meshgrid(xs, ys)
    grid_pts = np.column_stack([GX.ravel(), GY.ravel()])
    # 挖去圆柱底面(留白)
    in_cylinder = grid_pts[:, 0]**2 + grid_pts[:, 1]**2 <= R**2
    raster = griddata(pts, vals, grid_pts, method="linear", fill_value=255)
    raster[in_cylinder] = 255  # 罐底留白
    out_img = Image.fromarray(raster.reshape(out_h, out_w, 3).astype(np.uint8), "RGB")
    out_img.save(output_path, dpi=(out_dpi, out_dpi))
    print(f"输出: {output_path}  {out_w}x{out_h} px @ {out_dpi}dpi")

    # 6. 罐中视图预览: 镜面展开图 = 观察者通过罐子应看到的画面
    #    colors 行0=zm_min(视野下方), 行末=zm_max(视野上方);
    #    图像行0在顶 -> 上下翻转后保存, 预览图即正立还原像.
    import os
    preview = Image.fromarray(colors[::-1].astype(np.uint8), "RGB")
    arc_w = R * (theta_max - theta_min)   # 镜面横向弧长 mm
    arc_h = zm_max - zm_min               # 镜面纵向跨度 mm
    pw = 1200
    ph = max(1, int(pw * arc_h / arc_w))
    preview = preview.resize((pw, ph), Image.LANCZOS)
    pv_path = os.path.splitext(output_path)[0] + "_preview.png"
    preview.save(pv_path)
    print(f"罐中预览: {pv_path}  ({pw}x{ph}, 应与输入图方向一致)")
    return output_path


if __name__ == "__main__":
    import os
    import argparse
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    ap = argparse.ArgumentParser(
        description="圆柱镜面变形画: 正常图 -> A4 变形图")
    ap.add_argument("input", nargs="?", default=None,
                    help="输入正常图路径; 不给则用程序生成的测试图")
    ap.add_argument("-o", "--output", default="a4_anamorph.png",
                    help="输出 A4 变形图路径 (默认 a4_anamorph.png)")
    ap.add_argument("--y_E", type=float, default=Y_E,
                    help=f"观察者前方距离 mm (默认 {Y_E})")
    ap.add_argument("--z_E", type=float, default=Z_E,
                    help=f"观察者眼高 mm (默认 {Z_E})")
    ap.add_argument("--L", type=float, default=L,
                    help=f"圆柱高 mm (默认 {L})")
    ap.add_argument("--dpi", type=int, default=300,
                    help="输出 DPI (默认 300)")
    args = ap.parse_args()

    if args.input is None:
        args.input = "test_input.png"
        make_test_image(args.input)

    anamorph(args.input, args.output,
             y_E=args.y_E, z_E=args.z_E, L_val=args.L,
             out_dpi=args.dpi)
