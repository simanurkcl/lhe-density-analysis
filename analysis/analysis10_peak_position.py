import os
import sys

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ==========================================================
# PROJECT PATH
# ==========================================================

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import RESULTS_DIR

# ==========================================================
# DATASETS
# ==========================================================

datasets = {
    "350": os.path.join(RESULTS_DIR, "350GeV", "event_data.csv"),
    "365": os.path.join(RESULTS_DIR, "365GeV", "event_data.csv"),
    "500": os.path.join(RESULTS_DIR, "500GeV", "event_data.csv"),
    "700": os.path.join(RESULTS_DIR, "700GeV", "event_data.csv"),
    "1000": os.path.join(RESULTS_DIR, "1000GeV", "event_data.csv"),
    "3000": os.path.join(RESULTS_DIR, "3000GeV", "event_data.csv"),
    "1500": os.path.join(RESULTS_DIR, "1500GeV", "event_data.csv"),
    "2000": os.path.join(RESULTS_DIR, "2000GeV", "event_data.csv"),
    "2500": os.path.join(RESULTS_DIR, "2500GeV", "event_data.csv"),

}

# ==========================================================
# OBSERVABLES
# ==========================================================

observables = [
    "Concurrence",
    "EOF",
    "Negativity",
    "Purity",
]

# ==========================================================
# OUTPUT DIRECTORY
# ==========================================================

comparison_dir = os.path.join(RESULTS_DIR, "comparison")
os.makedirs(comparison_dir, exist_ok=True)

# ==========================================================
# BINNING
# ==========================================================

bins = np.linspace(-1, 1, 21)  # 20 bins, width 0.1

# Minimum number of events required in the peak bin for the
# result to be considered statistically trustworthy.
MIN_EVENTS_IN_PEAK_BIN = 50


# ==========================================================
# FUNCTION: binned profile with counts
# ==========================================================

def get_binned_profile(df, observable):
    """
    Returns a dataframe with bin center, mean observable value,
    and event count per bin (NaN bins already dropped).
    """
    df = df.copy()
    df["bin"] = pd.cut(df["cos_theta"], bins)

    grouped = (
        df.groupby("bin", observed=False)[observable]
        .agg(["mean", "count"])
        .reset_index()
    )
    grouped["center"] = grouped["bin"].apply(lambda x: x.mid)
    grouped = grouped.dropna(subset=["mean"]).reset_index(drop=True)

    return grouped


# ==========================================================
# FUNCTION: parabolic (3-point) sub-bin peak interpolation
# ==========================================================

def parabolic_peak(x0, x1, x2, y0, y1, y2):
    """
    Fits a parabola through three (x, y) points and returns the
    x-coordinate of its vertex. Falls back to x1 (the coarse bin
    center) if the points are degenerate.
    """
    denom = (x0 - x1) * (x0 - x2) * (x1 - x2)
    if denom == 0:
        return x1

    A = (x2 * (y1 - y0) + x1 * (y0 - y2) + x0 * (y2 - y1)) / denom
    B = (x2**2 * (y0 - y1) + x1**2 * (y2 - y0) + x0**2 * (y1 - y2)) / denom

    if A == 0:
        return x1

    peak_x = -B / (2 * A)

    # Sanity check: interpolated peak should stay within the
    # neighborhood of the three points used, otherwise the
    # parabola is unstable (near-flat data) -> fall back.
    lo, hi = sorted([x0, x2])
    if not (lo <= peak_x <= hi):
        return x1

    return peak_x


def get_peak_position(df, observable):
    """
    Computes the sub-bin peak position of the binned observable
    using parabolic interpolation around the coarse maximum bin.

    Returns
    -------
    peak_cos_theta : float
    peak_bin_count : int
        Number of events in the coarse peak bin (for a reliability
        flag - low counts mean the peak may be noise-driven).
    """
    grouped = get_binned_profile(df, observable)

    idx = grouped["mean"].idxmax()
    peak_count = int(grouped.loc[idx, "count"])

    # Edge bins: cannot fit a parabola, return coarse center
    if idx == 0 or idx == len(grouped) - 1:
        return grouped.loc[idx, "center"], peak_count

    x0, x1, x2 = grouped.loc[idx - 1, "center"], grouped.loc[idx, "center"], grouped.loc[idx + 1, "center"]
    y0, y1, y2 = grouped.loc[idx - 1, "mean"], grouped.loc[idx, "mean"], grouped.loc[idx + 1, "mean"]

    peak_x = parabolic_peak(x0, x1, x2, y0, y1, y2)

    return peak_x, peak_count


# ==========================================================
# MAIN LOOP
# ==========================================================

results = []
reliability = []

for energy, path in datasets.items():

    if not os.path.exists(path):
        print(f"Skipping {energy} GeV (file not found)")
        continue

    print(f"Reading {energy} GeV")

    df = pd.read_csv(path)

    row = {"Energy (GeV)": int(energy)}
    rel_row = {"Energy (GeV)": int(energy)}

    for observable in observables:
        peak_x, peak_count = get_peak_position(df, observable)
        row[observable] = peak_x
        rel_row[observable] = peak_count

    results.append(row)
    reliability.append(rel_row)

# ==========================================================
# SAVE TABLES
# ==========================================================

results_df = pd.DataFrame(results).sort_values("Energy (GeV)").reset_index(drop=True)
reliability_df = pd.DataFrame(reliability).sort_values("Energy (GeV)").reset_index(drop=True)

csv_path = os.path.join(comparison_dir, "peak_positions.csv")
results_df.to_csv(csv_path, index=False)

rel_csv_path = os.path.join(comparison_dir, "peak_positions_reliability.csv")
reliability_df.to_csv(rel_csv_path, index=False)

print(results_df)
print("\nEvent counts in peak bin (reliability check):")
print(reliability_df)
print(f"\nSaved table -> {csv_path}")
print(f"Saved reliability table -> {rel_csv_path}")

# ==========================================================
# PLOT
# ==========================================================

plt.figure(figsize=(8, 6))

for observable in observables:
    plt.plot(
        results_df["Energy (GeV)"],
        results_df[observable],
        marker="o",
        linewidth=2,
        label=observable,
    )

    # Flag low-statistics points (dashed marker edge / annotation)
    for _, r in reliability_df.iterrows():
        if r[observable] < MIN_EVENTS_IN_PEAK_BIN:
            e = r["Energy (GeV)"]
            y = results_df.loc[results_df["Energy (GeV)"] == e, observable].values[0]
            plt.scatter([e], [y], facecolors="none", edgecolors="red",
                        s=150, linewidths=1.5, zorder=5)

plt.xlabel(r"Center-of-Mass Energy $\sqrt{s}$ (GeV)")
plt.ylabel(r"Peak Position ($\cos\theta$)")
plt.title("Peak Position Evolution of Quantum Observables\n(red circles = low-statistics / less reliable point)")
plt.grid(True)
plt.legend()
plt.tight_layout()

plot_path = os.path.join(comparison_dir, "peak_position_evolution.png")
plt.savefig(plot_path, dpi=300)
plt.close()

print(f"Saved plot -> {plot_path}")

print("\n=========================================")
print("Peak position analysis completed!")
print("=========================================")