import pandas as pd
import matplotlib.pyplot as plt

# ==========================================================
# Load dataset
# ==========================================================

df = pd.read_csv("event_data.csv")

# ==========================================================
# Plot
# ==========================================================

plt.figure(figsize=(8,6))

plt.scatter(
    df["cos_theta"],
    df["Purity"],
    s=8,
    alpha=0.5
)

plt.xlabel(r"$\cos(\theta)$", fontsize=12)
plt.ylabel("Purity", fontsize=12)

plt.title("Purity vs Scattering Angle", fontsize=14)

plt.grid(True)

plt.tight_layout()

plt.savefig("plots/purity_vs_costheta.png", dpi=300)

plt.show()

print("="*60)
print("Figure saved as:")
print("plots/purity_vs_costheta.png")
print("="*60)