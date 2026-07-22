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
# BINNING (identical to Analysis09 / Analysis10)
# ==========================================================

bins = np.linspace(-1, 1, 21)

# Minimum number of events required in the peak bin for the
# result to be considered statistically trustworthy.
MIN_EVENTS_IN_PEAK_BIN = 50


# ==========================================================
# FUNCTION: binned average profile with event counts
# ==========================================================

def get_binned_profile(df, observable):
    """
    Reconstructs the average angular distribution of `observable`
    over cos_theta bins - the same curve shown in Analysis09.

    Returns a dataframe with columns: bin, mean, count, center.
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
# FUNCTION: peak magnitude from the binned average curve
# ==========================================================

def get_peak_magnitude(df, observable):
    """
    Identifies the bin with the largest binned-average value and
    returns that maximum value together with the event count in
    that bin (used as a reliability flag).

    The peak is NOT taken from individual events (idxmax on raw
    data), since single events are dominated by statistical
    fluctuations. It is taken from the binned average curve,
    exactly as plotted in Analysis09.
    """
    grouped = get_binned_profile(df, observable)

    idx = grouped["mean"].idxmax()
    peak_value = grouped.loc[idx, "mean"]
    peak_count = int(grouped.loc[idx, "count"])

    return peak_value, peak_count


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
        peak_value, peak_count = get_peak_magnitude(df, observable)
        row[observable] = peak_value
        rel_row[observable] = peak_count

    results.append(row)
    reliability.append(rel_row)

# ==========================================================
# SAVE TABLES
# ==========================================================

results_df = pd.DataFrame(results).sort_values("Energy (GeV)").reset_index(drop=True)
reliability_df = pd.DataFrame(reliability).sort_values("Energy (GeV)").reset_index(drop=True)

csv_path = os.path.join(comparison_dir, "peak_magnitudes.csv")
results_df.to_csv(csv_path, index=False)

rel_csv_path = os.path.join(comparison_dir, "peak_magnitudes_reliability.csv")
reliability_df.to_csv(rel_csv_path, index=False)

print(results_df)
print("\nEvent counts in peak bin (reliability check):")
print(reliability_df)
print(f"\nSaved table -> {csv_path}")
print(f"Saved reliability table -> {rel_csv_path}")

# ==========================================================
# PLOT
# ==========================================================
# NOTE: Concurrence, EOF and Negativity are expected to overlap
# almost perfectly (as found in Analysis09), so a small vertical
# offset and distinct line styles are used purely for visual
# separation - they do not alter the underlying values, which
# are saved unmodified in peak_magnitudes.csv.

plot_styles = {
    "Concurrence": {"linestyle": "-", "offset": 0.0},
    "EOF": {"linestyle": "--", "offset": 0.01},
    "Negativity": {"linestyle": "-.", "offset": -0.01},
    "Purity": {"linestyle": "-", "offset": 0.0},
}

plt.figure(figsize=(8, 6))

for observable in observables:
    style = plot_styles.get(observable, {"linestyle": "-", "offset": 0.0})

    plt.plot(
        results_df["Energy (GeV)"],
        results_df[observable] + style["offset"],
        marker="o",
        linewidth=2,
        linestyle=style["linestyle"],
        label=observable,
    )

    for _, r in reliability_df.iterrows():
        if r[observable] < MIN_EVENTS_IN_PEAK_BIN:
            e = r["Energy (GeV)"]
            y = results_df.loc[results_df["Energy (GeV)"] == e, observable].values[0]
            plt.scatter([e], [y + style["offset"]], facecolors="none", edgecolors="red",
                        s=150, linewidths=1.5, zorder=5)

plt.xlabel(r"Center-of-Mass Energy $\sqrt{s}$ (GeV)")
plt.ylabel("Maximum Observable Value")
plt.title("Peak Magnitude Evolution of Quantum Information Observables\n"
          "(red circles = low-statistics / less reliable point; small offsets applied for visual clarity)")
plt.grid(True)
plt.legend()
plt.tight_layout()

plot_path = os.path.join(comparison_dir, "peak_magnitude_evolution.png")
plt.savefig(plot_path, dpi=300)
plt.close()

print(f"Saved plot -> {plot_path}")

print("\n=========================================")
print("Peak magnitude analysis completed!")
print("=========================================")