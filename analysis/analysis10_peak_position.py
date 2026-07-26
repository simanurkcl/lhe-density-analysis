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

bins = np.linspace(-1, 1, 21)  # 20 bins, width 0.1

MIN_EVENTS_IN_PEAK_BIN = 50

# Bootstrap settings
N_BOOTSTRAP = 200          # increase later (e.g. 500-1000) once you confirm it runs OK
RANDOM_SEED = 42
CI_LOW, CI_HIGH = 16, 84   # percentiles ~ 1-sigma equivalent for a normal dist

rng = np.random.default_rng(RANDOM_SEED)


# ==========================================================
# FUNCTION: binned profile with counts
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
# FUNCTION: parabolic (3-point) sub-bin peak interpolation
# ==========================================================

def parabolic_peak(x0, x1, x2, y0, y1, y2):
    denom = (x0 - x1) * (x0 - x2) * (x1 - x2)
    if denom == 0:
        return x1

    A = (x2 * (y1 - y0) + x1 * (y0 - y2) + x0 * (y2 - y1)) / denom
    B = (x2**2 * (y0 - y1) + x1**2 * (y2 - y0) + x0**2 * (y1 - y2)) / denom

    if A == 0:
        return x1

    peak_x = -B / (2 * A)

    lo, hi = sorted([x0, x2])
    if not (lo <= peak_x <= hi):
        return x1

    return peak_x


def get_peak_position(df, observable):
    grouped = get_binned_profile(df, observable)

    if len(grouped) == 0:
        return np.nan, 0

    idx = grouped["mean"].idxmax()
    peak_count = int(grouped.loc[idx, "count"])

    if idx == 0 or idx == len(grouped) - 1:
        return grouped.loc[idx, "center"], peak_count

    x0, x1, x2 = grouped.loc[idx - 1, "center"], grouped.loc[idx, "center"], grouped.loc[idx + 1, "center"]
    y0, y1, y2 = grouped.loc[idx - 1, "mean"], grouped.loc[idx, "mean"], grouped.loc[idx + 1, "mean"]

    peak_x = parabolic_peak(x0, x1, x2, y0, y1, y2)

    return peak_x, peak_count


# ==========================================================
# FUNCTION: bootstrap uncertainty on peak position
# ==========================================================

def bootstrap_peak_position(df, observable, n_bootstrap=N_BOOTSTRAP):
    """
    Resamples events with replacement n_bootstrap times, recomputes
    the binned peak position each time, and returns the array of
    bootstrap peak estimates.
    """
    n_events = len(df)
    peaks = np.empty(n_bootstrap)

    for i in range(n_bootstrap):
        sample_idx = rng.integers(0, n_events, n_events)
        resampled = df.iloc[sample_idx]
        peak_x, _ = get_peak_position(resampled, observable)
        peaks[i] = peak_x

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
        peak_x, peak_count = get_peak_position(df, observable)
        row[observable] = peak_x
        rel_row[observable] = peak_count

        print(f"  Bootstrapping {observable} ({N_BOOTSTRAP} iterations)...")
        boot_peaks = bootstrap_peak_position(df, observable)
        boot_peaks = boot_peaks[~np.isnan(boot_peaks)]

        err_low = peak_x - np.percentile(boot_peaks, CI_LOW)
        err_high = np.percentile(boot_peaks, CI_HIGH) - peak_x
        boot_std = np.std(boot_peaks, ddof=1)

        bootstrap_summary.append({
            "Energy (GeV)": int(energy),
            "Observable": observable,
            "peak_position": peak_x,
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

csv_path = os.path.join(comparison_dir, "peak_positions.csv")
results_df.to_csv(csv_path, index=False)

rel_csv_path = os.path.join(comparison_dir, "peak_positions_reliability.csv")
reliability_df.to_csv(rel_csv_path, index=False)

boot_csv_path = os.path.join(comparison_dir, "peak_positions_bootstrap.csv")
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
# PLOT (with bootstrap error bars)
# ==========================================================

# ==========================================================
# PLOT (with bootstrap error bars)
# ==========================================================

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

offset_map = {"Concurrence": -20, "EOF": 0, "Negativity": 20, "Purity": 0}
color_map = {"Concurrence": "tab:blue", "EOF": "tab:orange", "Negativity": "tab:green", "Purity": "tab:red"}

# Left panel: full view (offsets separate overlapping lines)
for observable in observables:
    sub = bootstrap_df[bootstrap_df["Observable"] == observable].sort_values("Energy (GeV)")
    x_shifted = sub["Energy (GeV)"] + offset_map[observable]

    ax1.errorbar(
        x_shifted, sub["peak_position"],
        yerr=[sub["err_low"], sub["err_high"]],
        marker="o", linewidth=2, elinewidth=1.5, capsize=4,
        color=color_map[observable], label=observable,
    )

ax1.set_xlabel(r"Center-of-Mass Energy $\sqrt{s}$ (GeV)")
ax1.set_ylabel(r"Peak Position ($\cos\theta$)")
ax1.set_title("Full range (small x-offsets to separate\noverlapping Concurrence/EOF/Negativity)")
ax1.grid(True)
ax1.legend()

# Right panel: zoom into high-energy plateau to see error bars clearly
for observable in observables:
    sub = bootstrap_df[bootstrap_df["Observable"] == observable].sort_values("Energy (GeV)")
    sub = sub[sub["Energy (GeV)"] >= 1000]
    x_shifted = sub["Energy (GeV)"] + offset_map[observable]

    ax2.errorbar(
        x_shifted, sub["peak_position"],
        yerr=[sub["err_low"], sub["err_high"]],
        marker="o", linewidth=2, elinewidth=1.5, capsize=4,
        color=color_map[observable], label=observable,
    )

ax2.set_xlabel(r"Center-of-Mass Energy $\sqrt{s}$ (GeV)")
ax2.set_ylabel(r"Peak Position ($\cos\theta$)")
ax2.set_title("Zoomed: 1000-3000 GeV plateau\n(error bars visible at this scale)")
ax2.grid(True)
ax2.legend()

plt.suptitle("Peak Position Evolution of Quantum Observables\n(error bars = bootstrap 16-84 percentile)")
plt.tight_layout()

plot_path = os.path.join(comparison_dir, "peak_position_evolution.png")
plt.savefig(plot_path, dpi=300)
plt.close()

print(f"Saved plot -> {plot_path}")

print("\n=========================================")
print("Peak position analysis completed!")
print("=========================================")