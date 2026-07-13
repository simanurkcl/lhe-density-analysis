import pandas as pd
import matplotlib.pyplot as plt

# ==========================================================
# Load dataset
# ==========================================================

df = pd.read_csv("event_data.csv")

# ==========================================================
# Plot EOF vs Concurrence
# ==========================================================

plt.figure(figsize=(8,6))

plt.scatter(
    df["Concurrence"],
    df["EOF"],
    s=8,
    alpha=0.5
)

plt.xlabel("Concurrence", fontsize=12)
plt.ylabel("Entanglement of Formation", fontsize=12)

plt.title("Entanglement of Formation vs Concurrence", fontsize=14)

plt.grid(True)

plt.tight_layout()

plt.savefig(
    "plots/eof_vs_concurrence.png",
    dpi=300
)

plt.show()

print("="*60)
print("Figure saved as:")
print("plots/eof_vs_concurrence.png")
print("="*60)