# ==========================
# Analysis configuration
# ==========================

import os

ENERGY = "2500GeV"

# MadGraph run klasörü (bunu her yeni run'da değiştir)
MG5_RUN = "run_12"

# MadGraph dosyaları
LHE_PATH = f"/home/sima/mg5_density/density_test2/Events/{MG5_RUN}/unweighted_events.lhe.gz"

# Analiz çıktıları
BASE_DIR = "/home/sima/density_analysis"
RESULTS_DIR = os.path.join(BASE_DIR, "results")

BASE = os.path.join(RESULTS_DIR, ENERGY)

EVENT_DATA = os.path.join(BASE, "event_data.csv")
PLOTS = os.path.join(BASE, "plots")
TABLES = os.path.join(BASE, "tables")

PLOT_SUFFIX = ENERGY

os.makedirs(PLOTS, exist_ok=True)
os.makedirs(TABLES, exist_ok=True)