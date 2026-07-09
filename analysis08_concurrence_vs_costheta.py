import pandas as pd
import matplotlib.pyplot as plt

# Read data
df = pd.read_csv("event_data.csv")

# Scatter plot
plt.figure(figsize=(7,5))

plt.scatter(
    df["cos_theta"],
    df["Concurrence"],
    s=8,
    alpha=0.5
)

plt.xlabel(r"$\cos(\theta)$")
plt.ylabel("Concurrence")
plt.title("Concurrence vs cos(theta)")

plt.grid(True)

plt.tight_layout()

plt.savefig("concurrence_vs_costheta.png", dpi=300)

plt.show()