import pandas as pd
import matplotlib.pyplot as plt

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import EVENT_DATA, PLOTS, PLOT_SUFFIX

df = pd.read_csv(EVENT_DATA)
quantum = df[
    [
        "Purity",
        "Concurrence",
        "EOF",
        "Negativity"
    ]
]

corr = quantum.corr(method="pearson")

print(corr)
plt.figure(figsize=(6,5))

plt.imshow(corr)

plt.colorbar()

plt.xticks(range(len(corr.columns)), corr.columns, rotation=45)

plt.yticks(range(len(corr.columns)), corr.columns)

plt.title("Correlation Matrix")

plt.tight_layout()


plt.savefig(
    os.path.join(PLOTS, f"correlation_matrix_{PLOT_SUFFIX}.png"),
    dpi=300
)


plt.show()
print(df.describe())
pairs = [
    ("Concurrence", "EOF"),
    ("Concurrence", "Negativity"),
    ("Purity", "Concurrence"),
]

for x, y in pairs:

    plt.figure(figsize=(5,4))

    plt.scatter(df[x], df[y], s=5)

    plt.xlabel(x)

    plt.ylabel(y)

    plt.tight_layout()

    plt.savefig(f"{x}_{y}.png", dpi=300)

    plt.show()