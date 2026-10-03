"""Generate the setup diagram (top view + side view) for README."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mp
import numpy as np
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

R, L = 33.0, 110.0
X_MIN, X_MAX = -148.5, 148.5
Y_MIN, Y_MAX = -52.5, 157.5
Y_E, Z_E = 250.0, 120.0

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.6))

# ---------------- Top view ----------------
ax1.add_patch(mp.Rectangle((X_MIN, Y_MIN), X_MAX - X_MIN, Y_MAX - Y_MIN,
                           fc="#fdfdfa", ec="#333", lw=1.5, zorder=1))
# shaded Omega (pattern area = A4 minus cylinder circle)
ax1.add_patch(mp.Rectangle((X_MIN, Y_MIN), X_MAX - X_MIN, Y_MAX - Y_MIN,
                           fc="#cfe3f7", ec="none", alpha=.55, zorder=1))
ax1.add_patch(mp.Circle((0, 0), R, fc="white", ec="#c0392b", lw=2, zorder=3))
ax1.add_patch(mp.Circle((0, 0), 2.2, fc="#c0392b", ec="none", zorder=4))
ax1.text(0, -8, "can\n(R=33)", ha="center", va="top", fontsize=8, color="#c0392b")

# axes
ax1.annotate("", xy=(60, 0), xytext=(0, 0),
             arrowprops=dict(arrowstyle="->", color="#555", lw=1.2))
ax1.annotate("", xy=(0, 90), xytext=(0, 0),
             arrowprops=dict(arrowstyle="->", color="#555", lw=1.2))
ax1.text(63, 0, "+x", fontsize=10, va="center", color="#555")
ax1.text(2, 93, "+y\n(front)", fontsize=9, color="#555")

# observer
ax1.add_patch(mp.Circle((0, Y_E), 5, fc="#2c3e50", ec="none", zorder=5))
ax1.text(10, Y_E, "eye  E=(0, 250mm, 120mm)", fontsize=9, va="center", color="#2c3e50")
ax1.annotate("", xy=(0, R), xytext=(0, Y_E),
             arrowprops=dict(arrowstyle="->", color="#2c3e50", lw=1.3,
                             linestyle="--", shrinkA=8, shrinkB=4))
ax1.text(6, 150, "view", fontsize=8, color="#2c3e50", rotation=0)

# dimension labels
def dim(ax, x0, y0, x1, y1, txt, off=(0, 0), color="#1565c0"):
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                arrowprops=dict(arrowstyle="<->", color=color, lw=1))
    ax.text((x0 + x1) / 2 + off[0], (y0 + y1) / 2 + off[1], txt,
            fontsize=8.5, ha="center", va="center", color=color,
            bbox=dict(fc="white", ec="none", pad=1))

dim(ax1, X_MIN, Y_MIN - 16, X_MAX, Y_MIN - 16, "297 mm  (A4 landscape)")
dim(ax1, X_MAX + 14, Y_MAX, X_MAX + 14, Y_MIN, "210 mm")
dim(ax1, X_MAX + 14, 0, X_MAX + 14, -52.5, "52.5")
dim(ax1, X_MAX + 14, 0, X_MAX + 14, 157.5, "157.5")
dim(ax1, -60, 0, -60, 33, "gap 19.5", off=(-3, 0))
dim(ax1, -60, 33, -60, 157.5, "pattern 124.5", off=(-6, 0))

ax1.set_title("Top view: A4 sheet + can at center of upper half",
              fontsize=11)
ax1.set_aspect("equal")
ax1.set_xlim(X_MIN - 45, X_MAX + 70)
ax1.set_ylim(Y_MIN - 42, Y_E + 35)
ax1.axis("off")

# ---------------- Side view ----------------
ax2.add_patch(mp.Rectangle((-R, 0), 2 * R, L, fc="#d5d8dc", ec="#333", lw=1.5))
ax2.annotate("", xy=(R + 30, 0), xytext=(0, 0),
             arrowprops=dict(arrowstyle="->", color="#555", lw=1.2))
ax2.annotate("", xy=(0, L + 28), xytext=(0, 0),
             arrowprops=dict(arrowstyle="->", color="#555", lw=1.2))
ax2.text(R + 34, 0, "+y (front)", fontsize=9, va="center", color="#555")
ax2.text(2, L + 32, "+z", fontsize=10, color="#555")
ax2.text(0, L / 2, "can\nL=110\nR=33", ha="center", va="center", fontsize=9, color="#333")

# ground = A4 surface
ax2.plot([-230, 230], [0, 0], color="#333", lw=1.5)
ax2.text(-225, 8, "paper (z=0)", fontsize=9, color="#333")

# eye
ax2.add_patch(mp.Circle((Y_E, Z_E), 5, fc="#2c3e50", ec="none", zorder=5))
ax2.text(Y_E, Z_E + 14, "eye  $z_E$=120mm", fontsize=9, ha="center", color="#2c3e50")
ax2.annotate("", xy=(R, Z_E * R / (R + Y_E)), xytext=(Y_E, Z_E),
             arrowprops=dict(arrowstyle="->", color="#c0392b", lw=1.3, shrinkB=3))
ax2.text(120, 95, "ray to mirror point M($\\theta$, $z_m$)", fontsize=8.5,
         color="#c0392b", ha="center")
ax2.text(150, 55, "$z_m < z_E$\n$0 \\leq z_m \\leq L$", fontsize=9, color="#555")

dim(ax2, Y_E + 12, 0, Y_E + 12, Z_E, "$z_E$=120", off=(0, 0))
ax2.text(Y_E, -22, "250 mm", fontsize=9, ha="center", color="#1565c0")
ax2.annotate("", xy=(Y_E, -12), xytext=(0, -12),
             arrowprops=dict(arrowstyle="<->", color="#1565c0", lw=1))

ax2.set_title("Side view: observer geometry", fontsize=11)
ax2.set_aspect("equal")
ax2.set_xlim(-235, 300)
ax2.set_ylim(-45, 265)
ax2.axis("off")

plt.tight_layout()
plt.savefig("images/setup.png", dpi=150, bbox_inches="tight")
print("saved images/setup.png")
