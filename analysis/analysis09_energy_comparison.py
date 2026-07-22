import os
import sys

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Density Analysis klasörünü Python path'e ekle
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import RESULTS_DIR


# ==========================================================
# DATASETS
# ==========================================================
datasets = {
    "350 GeV": os.path.join(RESULTS_DIR, "350GeV", "event_data.csv"),
    "365 GeV": os.path.join(RESULTS_DIR, "365GeV", "event_data.csv"),
    "500 GeV": os.path.join(RESULTS_DIR, "500GeV", "event_data.csv"),
    "700 GeV": os.path.join(RESULTS_DIR, "700GeV", "event_data.csv"),
    "1000 GeV": os.path.join(RESULTS_DIR, "1000GeV", "event_data.csv"),
    "3000 GeV": os.path.join(RESULTS_DIR, "3000GeV", "event_data.csv"),
    "1500 GeV": os.path.join(RESULTS_DIR, "1500GeV", "event_data.csv"),
    "2000 GeV": os.path.join(RESULTS_DIR, "2000GeV", "event_data.csv"),
    "2500 Gev": os.path.join(RESULTS_DIR, "2500GeV", "event_data.csv"),
}





# ==========================================================
# OUTPUT DIRECTORY
# ==========================================================

comparison_dir = os.path.join(RESULTS_DIR, "comparison")
os.makedirs(comparison_dir, exist_ok=True)


# ==========================================================
# FUNCTION
# ==========================================================

def compare(variable, ylabel, filename):

    plt.figure(figsize=(8, 6))

    bins = np.linspace(-1, 1, 21)

    for label, path in datasets.items():

        if not os.path.exists(path):
            print(f"Skipping {label} (file not found)")
            continue

        print(f"Reading {label}")

        df = pd.read_csv(path)

        df["bin"] = pd.cut(df["cos_theta"], bins)

        centers = []
        means = []

        grouped = df.groupby("bin", observed=False)

        for interval, group in grouped:

            centers.append(interval.mid)
            means.append(group[variable].mean())

        plt.plot(
            centers,
            means,
            marker="o",
            markersize=4,
            linewidth=2,
            label=label,
        )

    plt.xlabel(r"$\cos(\theta)$")
    plt.ylabel(ylabel)

    plt.title(f"{ylabel} vs cos(theta)")

    plt.grid(True)

    plt.legend()

    plt.tight_layout()

    output_path = os.path.join(comparison_dir, filename)

    plt.savefig(output_path, dpi=300)

    plt.close()

    print(f"Saved -> {output_path}")


# ==========================================================
# CREATE ALL COMPARISON PLOTS
# ==========================================================

compare(
    "Concurrence",
    "Concurrence",
    "comparison_concurrence.png"
)

compare(
    "Purity",
    "Purity",
    "comparison_purity.png"
)

compare(
    "Negativity",
    "Negativity",
    "comparison_negativity.png"
)

compare(
    "EOF",
    "Entanglement of Formation",
    "comparison_eof.png"
)

print("\n==========================================")
print("Energy comparison plots created!")
print("==========================================")