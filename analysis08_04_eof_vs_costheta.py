import pandas as pd
import matplotlib.pyplot as plt

# ==========================================================
# Load dataset
# ==========================================================

df = pd.read_csv("event_data.csv")

# ==========================================================
# Plot EOF vs cos(theta)
# ==========================================================

plt.figure(figsize=(8,6))

plt.scatter(
    df["cos_theta"],
    df["EOF"],
    s=8,
    alpha=0.5
)

plt.xlabel(r"$\cos(\theta)$", fontsize=12)
plt.ylabel("Entanglement of Formation", fontsize=12)

plt.title("Entanglement of Formation vs Scattering Angle", fontsize=14)

plt.grid(True)

plt.tight_layout()

plt.savefig(
    "plots/eof_vs_costheta.png",
    dpi=300
)

plt.show()

print("="*60)
print("Figure saved as:")
print("plots/eof_vs_costheta.png")
print("="*60)