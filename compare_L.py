"""对比 L 和 z_E 变化对有效区和变形图的影响."""
import numpy as np
from PIL import Image
import sys
sys.path.insert(0, r"E:\2026\agents\CylinMirror")
from anamorph import (R, L, A4_W, A4_H, X_MIN, X_MAX, Y_MIN, Y_MAX,
                      Y_E, Z_E, image_to_object, scan_valid_region,
                      make_test_image, anamorph)
import os
os.chdir(r"E:\2026\agents\CylinMirror")


def region_stats(y_E, z_E, L_val, label):
    """计算给定参数下有效区统计."""
    # 临时改 L
    import anamorph as an
    orig_L = an.L
    an.L = L_val
    T, Z, Xp, Yp, mask = scan_valid_region(y_E=y_E, z_E=z_E)
    th = T[mask]; zm = Z[mask]
    print(f"\n{'='*60}")
    print(f"{label}")
    print(f"  L={L_val}, y_E={y_E}, z_E={z_E}")
    print(f"  zm 上限(min(L,z_E))={min(L_val,z_E)}")
    print(f"  有效区: theta [{np.degrees(th.min()):.1f}°,{np.degrees(th.max()):.1f}°] "
          f"跨度 {np.degrees(th.max()-th.min()):.1f}°")
    print(f"  有效区: zm [{zm.min():.2f},{zm.max():.2f}] 跨度 {zm.max()-zm.min():.2f}mm")
    print(f"  物点: x[{Xp[mask].min():.1f},{Xp[mask].max():.1f}] "
          f"y[{Yp[mask].min():.1f},{Yp[mask].max():.1f}]")
    print(f"  有效点占比: {mask.mean()*100:.1f}%")
    an.L = orig_L
    return zm.max(), zm.max()-zm.min(), np.degrees(th.max()-th.min())


# 四种组合
configs = [
    (Y_E, Z_E, 110, "① 原配置 L=110 z_E=120"),
    (Y_E, Z_E, 220, "② 只加高罐 L=220 z_E=120"),
    (Y_E, 240, 110, "③ 只抬眼 L=110 z_E=240"),
    (Y_E, 240, 220, "④ 都翻倍 L=220 z_E=240"),
]
print("="*60)
print("四种配置对比 (y_E=250 固定)")
results = []
for yE, zE, Lv, label in configs:
    r = region_stats(yE, zE, Lv, label)
    results.append((label, r))

print("\n" + "="*60)
print("汇总表")
print(f"{'配置':<28} {'zm上限':>8} {'zm跨度':>8} {'θ跨度':>8}")
for label, (zmax, zspan, tspan) in results:
    print(f"{label:<28} {zmax:>8.2f} {zspan:>8.2f} {tspan:>7.1f}°")

# 实际生成 ② 的图对比 ①
print("\n" + "="*60)
print("生成 L=220 的变形图对比...")
import anamorph as an
an.L = 220
anamorph("test_input.png", "a4_anamorph_L220.png", y_E=Y_E, z_E=Z_E)
an.L = 110
print("完成: a4_anamorph_L220.png")
