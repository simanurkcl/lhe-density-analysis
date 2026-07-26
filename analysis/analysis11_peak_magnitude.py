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
    "1500": os.path.join(RESULTS_DIR, "1500GeV", "event_data.csv"),
    "2000": os.path.join(RESULTS_DIR, "2000GeV", "event_data.csv"),
    "2500": os.path.join(RESULTS_DIR, "2500GeV", "event_data.csv"),
    "3000": os.path.join(RESULTS_DIR, "3000GeV", "event_data.csv"),
}

observables = ["Concurrence", "EOF", "Negativity", "Purity"]

comparison_dir = os.path.join(RESULTS_DIR, "comparison")
os.makedirs(comparison_dir, exist_ok=True)

bins = np.linspace(-1, 1, 21)

MIN_EVENTS_IN_PEAK_BIN = 50

# Bootstrap settings (same as Analysis10 for consistency)
N_BOOTSTRAP = 200
RANDOM_SEED = 42
CI_LOW, CI_HIGH = 16, 84

rng = np.random.default_rng(RANDOM_SEED)


# ==========================================================
# FUNCTION: binned average profile with event counts
# ==========================================================

def get_binned_profile(df, observable):
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
    grouped = get_binned_profile(df, observable)

    if len(grouped) == 0:
        return np.nan, 0

    idx = grouped["mean"].idxmax()
    peak_value = grouped.loc[idx, "mean"]
    peak_count = int(grouped.loc[idx, "count"])

    return peak_value, peak_count


# ==========================================================
# FUNCTION: bootstrap uncertainty on peak magnitude
# ==========================================================

def bootstrap_peak_magnitude(df, observable, n_bootstrap=N_BOOTSTRAP):
    n_events = len(df)
    peaks = np.empty(n_bootstrap)

    for i in range(n_bootstrap):
        sample_idx = rng.integers(0, n_events, n_events)
        resampled = df.iloc[sample_idx]
        peak_value, _ = get_peak_magnitude(resampled, observable)
        peaks[i] = peak_value

    return peaks


# ==========================================================
# MAIN LOOP
# ==========================================================

results = []
reliability = []
bootstrap_summary = []

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

        print(f"  Bootstrapping {observable} ({N_BOOTSTRAP} iterations)...")
        boot_peaks = bootstrap_peak_magnitude(df, observable)
        boot_peaks = boot_peaks[~np.isnan(boot_peaks)]

        err_low = peak_value - np.percentile(boot_peaks, CI_LOW)
        err_high = np.percentile(boot_peaks, CI_HIGH) - peak_value
        boot_std = np.std(boot_peaks, ddof=1)

        bootstrap_summary.append({
            "Energy (GeV)": int(energy),
            "Observable": observable,
            "peak_magnitude": peak_value,
            "err_low": err_low,
            "err_high": err_high,
            "bootstrap_std": boot_std,
            "n_bootstrap": len(boot_peaks),
        })

    results.append(row)
    reliability.append(rel_row)

# ==========================================================
# SAVE TABLES
# ==========================================================

results_df = pd.DataFrame(results).sort_values("Energy (GeV)").reset_index(drop=True)
reliability_df = pd.DataFrame(reliability).sort_values("Energy (GeV)").reset_index(drop=True)
bootstrap_df = pd.DataFrame(bootstrap_summary).sort_values(["Observable", "Energy (GeV)"]).reset_index(drop=True)

csv_path = os.path.join(comparison_dir, "peak_magnitudes.csv")
results_df.to_csv(csv_path, index=False)

rel_csv_path = os.path.join(comparison_dir, "peak_magnitudes_reliability.csv")
reliability_df.to_csv(rel_csv_path, index=False)

boot_csv_path = os.path.join(comparison_dir, "peak_magnitudes_bootstrap.csv")
bootstrap_df.to_csv(boot_csv_path, index=False)

print(results_df)
print("\nEvent counts in peak bin (reliability check):")
print(reliability_df)
print("\nBootstrap uncertainty summary:")
print(bootstrap_df)
print(f"\nSaved table -> {csv_path}")
print(f"Saved reliability table -> {rel_csv_path}")
print(f"Saved bootstrap table -> {boot_csv_path}")

# ==========================================================
# PLOT (with bootstrap error bars, two panels like Analysis10)
# ==========================================================

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

offset_map = {"Concurrence": -20, "EOF": 0, "Negativity": 20, "Purity": 0}
color_map = {"Concurrence": "tab:blue", "EOF": "tab:orange", "Negativity": "tab:green", "Purity": "tab:red"}

for observable in observables:
    sub = bootstrap_df[bootstrap_df["Observable"] == observable].sort_values("Energy (GeV)")
    x_shifted = sub["Energy (GeV)"] + offset_map[observable]

    ax1.errorbar(
        x_shifted, sub["peak_magnitude"],
        yerr=[sub["err_low"], sub["err_high"]],
        marker="o", linewidth=2, elinewidth=1.5, capsize=4,
        color=color_map[observable], label=observable,
    )

ax1.set_xlabel(r"Center-of-Mass Energy $\sqrt{s}$ (GeV)")
ax1.set_ylabel("Maximum Observable Value")
ax1.set_title("Full range (small x-offsets to separate\noverlapping Concurrence/EOF/Negativity)")
ax1.grid(True)
ax1.legend()

for observable in observables:
    sub = bootstrap_df[bootstrap_df["Observable"] == observable].sort_values("Energy (GeV)")
    sub = sub[sub["Energy (GeV)"] >= 1000]
    x_shifted = sub["Energy (GeV)"] + offset_map[observable]

    ax2.errorbar(
        x_shifted, sub["peak_magnitude"],
        yerr=[sub["err_low"], sub["err_high"]],
        marker="o", linewidth=2, elinewidth=1.5, capsize=4,
        color=color_map[observable], label=observable,
    )

ax2.set_xlabel(r"Center-of-Mass Energy $\sqrt{s}$ (GeV)")
ax2.set_ylabel("Maximum Observable Value")
ax2.set_title("Zoomed: 1000-3000 GeV\n(error bars visible at this scale)")
ax2.grid(True)
ax2.legend()

plt.suptitle("Peak Magnitude Evolution of Quantum Information Observables\n"
             "(error bars = bootstrap 16-84 percentile)")
plt.tight_layout()

plot_path = os.path.join(comparison_dir, "peak_magnitude_evolution.png")
plt.savefig(plot_path, dpi=300)
plt.close()

print(f"Saved plot -> {plot_path}")

print("\n=========================================")
print("Peak magnitude analysis completed!")
print("=========================================")