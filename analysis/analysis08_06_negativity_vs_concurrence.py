import pandas as pd
import matplotlib.pyplot as plt

# ==========================================================
# Load dataset
# ==========================================================

df = pd.read_csv("event_data.csv")

# ==========================================================
# Plot Negativity vs Concurrence
# ==========================================================

plt.figure(figsize=(8,6))

plt.scatter(
    df["Concurrence"],
    df["Negativity"],
    s=8,
    alpha=0.5
)

plt.xlabel("Concurrence", fontsize=12)
plt.ylabel("Negativity", fontsize=12)

plt.title("Negativity vs Concurrence", fontsize=14)

plt.grid(True)

plt.tight_layout()

plt.savefig(
    "plots/negativity_vs_concurrence.png",
    dpi=300
)

plt.show()

print("="*60)
print("Figure saved as:")
print("plots/negativity_vs_concurrence.png")
print("="*60)