import os
import sys

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import RESULTS_DIR

# ==========================================================
# DATASETS
# ==========================================================

datasets = {
    "350 GeV":  os.path.join(RESULTS_DIR, "350GeV", "event_data.csv"),
    "365 GeV":  os.path.join(RESULTS_DIR, "365GeV", "event_data.csv"),
    "500 GeV":  os.path.join(RESULTS_DIR, "500GeV", "event_data.csv"),
    "700 GeV":  os.path.join(RESULTS_DIR, "700GeV", "event_data.csv"),
    "1000 GeV": os.path.join(RESULTS_DIR, "1000GeV", "event_data.csv"),
    "1500 GeV": os.path.join(RESULTS_DIR, "1500GeV", "event_data.csv"),
    "2000 GeV": os.path.join(RESULTS_DIR, "2000GeV", "event_data.csv"),
    "2500 GeV": os.path.join(RESULTS_DIR, "2500GeV", "event_data.csv"),
    "3000 GeV": os.path.join(RESULTS_DIR, "3000GeV", "event_data.csv"),
}

# Not: Events are unweighted (uniform MC weight verified = 0.0275045),
# so simple arithmetic averaging within each bin is statistically valid.

# ==========================================================
# OUTPUT
# ==========================================================

comparison_dir = os.path.join(RESULTS_DIR, "comparison")
os.makedirs(comparison_dir, exist_ok=True)

# Minimum events per bin to be considered statistically reliable.
# Bins below this threshold are still plotted but visually flagged.
MIN_STATS_THRESHOLD = 30

# ==========================================================
# FUNCTION
# ==========================================================

def compare(variable, ylabel, filename, physical_bounds=(0, 1)):

    plt.figure(figsize=(8, 6))

    bins = np.linspace(-1, 1, 21)

    # Sequential colormap since energy is an ordinal variable
    colors = plt.cm.viridis(np.linspace(0, 1, len(datasets)))

    # Collect stats across all energies for CSV export
    all_stats_rows = []

    for (label, path), color in zip(datasets.items(), colors):

        if not os.path.exists(path):
            print(f"Skipping {label}")
            continue

        print(f"Reading {label}")

        df = pd.read_csv(path)

        df["bin"] = pd.cut(df["cos_theta"], bins)

        grouped = df.groupby("bin", observed=False)

        centers = []
        means = []
        errors = []
        low_stats_mask = []

        for interval, group in grouped:

            n = len(group)
            mean = group[variable].mean()

            if n > 1:
                sem = group[variable].std(ddof=1) / np.sqrt(n)
            else:
                sem = 0.0

            centers.append(interval.mid)
            means.append(mean)
            errors.append(sem)
            low_stats_mask.append(n < MIN_STATS_THRESHOLD)

            all_stats_rows.append({
                "energy": label,
                "variable": variable,
                "bin_center": interval.mid,
                "mean": mean,
                "sem": sem,
                "n_events": n,
                "low_stats": n < MIN_STATS_THRESHOLD,
            })

        centers = np.array(centers)
        means = np.array(means)
        errors = np.array(errors)
        low_stats_mask = np.array(low_stats_mask)

        # Clip error bars so they don't visually extend past
        # physically meaningful bounds (e.g. [0,1] for purity/concurrence)
        lower_err = np.minimum(errors, means - physical_bounds[0])
        upper_err = np.minimum(errors, physical_bounds[1] - means)
        lower_err = np.clip(lower_err, 0, None)
        upper_err = np.clip(upper_err, 0, None)

        # Plot reliable bins normally
        plt.errorbar(
            centers[~low_stats_mask],
            means[~low_stats_mask],
            yerr=[lower_err[~low_stats_mask], upper_err[~low_stats_mask]],
            marker="o",
            markersize=4,
            linewidth=2,
            elinewidth=1,
            capsize=3,
            color=color,
            label=label,
        )

        # Plot low-statistics bins with hollow/faded markers, no legend entry
        if low_stats_mask.any():
            plt.errorbar(
                centers[low_stats_mask],
                means[low_stats_mask],
                yerr=[lower_err[low_stats_mask], upper_err[low_stats_mask]],
                marker="o",
                markersize=4,
                markerfacecolor="none",
                linewidth=1,
                linestyle="--",
                elinewidth=1,
                capsize=3,
                color=color,
                alpha=0.5,
            )

    plt.xlabel(r"$\cos\theta$")
    plt.ylabel(ylabel)
    plt.title(f"{ylabel} vs $\\cos\\theta$")
    plt.grid(True)
    plt.legend(fontsize=8, title="(dashed/hollow = n < %d)" % MIN_STATS_THRESHOLD)

    plt.tight_layout()

    output = os.path.join(comparison_dir, filename)
    plt.savefig(output, dpi=300)
    plt.close()

    print(f"Saved -> {output}")

    # Save underlying stats to CSV for later use (bootstrap comparison,
    # tables in the report, etc.)
    stats_df = pd.DataFrame(all_stats_rows)
    stats_csv = os.path.join(
        comparison_dir, filename.replace(".png", "_stats.csv")
    )
    stats_df.to_csv(stats_csv, index=False)
    print(f"Saved stats -> {stats_csv}")

# ==========================================================
# CREATE FIGURES
# ==========================================================

compare("Concurrence", "Concurrence", "comparison_concurrence.png", physical_bounds=(0, 1))
compare("Purity", "Purity", "comparison_purity.png", physical_bounds=(0.25, 1))
compare("Negativity", "Negativity", "comparison_negativity.png", physical_bounds=(0, 0.5))
compare("EOF", "Entanglement of Formation", "comparison_eof.png", physical_bounds=(0, 1))

print("\n==========================================")
print("Energy comparison plots created!")
print("==========================================")