import pandas as pd
import matplotlib.pyplot as plt

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import EVENT_DATA, PLOTS, PLOT_SUFFIX


# ==========================================================
# Load dataset
# ==========================================================

df = pd.read_csv(EVENT_DATA)

# ==========================================================
# Plot Negativity vs cos(theta)
# ==========================================================

plt.figure(figsize=(8,6))

plt.scatter(
    df["cos_theta"],
    df["Negativity"],
    s=8,
    alpha=0.5
)

plt.xlabel(r"$\cos(\theta)$", fontsize=12)
plt.ylabel("Negativity", fontsize=12)

plt.title("Negativity vs Scattering Angle", fontsize=14)

plt.grid(True)

plt.tight_layout()


plt.savefig(
    os.path.join(PLOTS, f"negativity_vs_costheta_{PLOT_SUFFIX}.png"),
    dpi=300
)

plt.show()

print("="*60)
print("Figure saved as:")
print("plots/negativity_vs_costheta.png")
print("="*60)