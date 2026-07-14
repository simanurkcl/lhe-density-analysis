# ==========================
# Analysis configuration
# ==========================

ENERGY = "365GeV"

BASE = f"/home/sima/density_analysis/results/{ENERGY}"

LHE_PATH = f"{BASE}/unweighted_events.lhe.gz"

EVENT_DATA = f"{BASE}/event_data.csv"

PLOTS = f"{BASE}/plots"

TABLES = f"{BASE}/tables"

PLOT_SUFFIX = ENERGY

import os

os.makedirs(PLOTS, exist_ok=True)
os.makedirs(TABLES, exist_ok=True)