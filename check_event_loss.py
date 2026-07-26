import sys, os
import csv

sys.path.append("/home/sima/mg5_density")
import madgraph.various.lhe_parser as lhe_parser

# Her enerji için LHE dosyasının yolunu buraya elle gir
# (config.py'deki MG5_RUN değerlerine göre doldur)
lhe_paths = {
    "350":  "/home/sima/mg5_density/density_test2/Events/run_08/unweighted_events.lhe.gz",
    "365":  "/home/sima/mg5_density/density_test2/Events/run_05/unweighted_events.lhe.gz",
    "500":  "/home/sima/mg5_density/density_test2/Events/run_06/unweighted_events.lhe.gz",
    "700":  "/home/sima/mg5_density/density_test2/Events/run_07/unweighted_events.lhe.gz",
    "1000": "/home/sima/mg5_density/density_test2/Events/run_04/unweighted_events.lhe.gz",
    "1500": "/home/sima/mg5_density/density_test2/Events/run_10/unweighted_events.lhe.gz",
    "2000": "/home/sima/mg5_density/density_test2/Events/run_11/unweighted_events.lhe.gz",
    "2500": "/home/sima/mg5_density/density_test2/Events/run_12/unweighted_events.lhe.gz",
    "3000": "/home/sima/mg5_density/density_test2/Events/run_09/unweighted_events.lhe.gz",
}

output_csv = "/home/sima/density_analysis/results/comparison/event_loss_full_scan.csv"

rows = []

for energy, path in lhe_paths.items():

    if not os.path.exists(path):
        print(f"SKIP {energy} GeV -- file not found: {path}")
        continue

    print(f"Scanning {energy} GeV ...")

    n_checked = 0
    n_missing = 0
    missing_cos_theta_forward = 0   # kayıp event'ler ileri açıda mı (cos_theta > 0.8)
    missing_cos_theta_backward = 0  # geri açıda mı (cos_theta < -0.8)

    for event in lhe_parser.EventFile(path):
        n_checked += 1

        top = None
        antitop = None
        for particle in event:
            if particle.pid == 6:
                top = particle
            elif particle.pid == -6:
                antitop = particle

        if top is None or antitop is None:
            n_missing += 1
            # Eğer top bulunamadıysa açısını bilemeyiz, ama antitop
            # bulunduysa onun açısına bakabiliriz (kaba bir yaklaşım)
            probe = top if top is not None else antitop
            if probe is not None:
                p = (probe.px**2 + probe.py**2 + probe.pz**2) ** 0.5
                if p > 0:
                    ct = -probe.pz / p
                    if ct > 0.8:
                        missing_cos_theta_forward += 1
                    elif ct < -0.8:
                        missing_cos_theta_backward += 1

    survival_rate = 100 * (n_checked - n_missing) / n_checked if n_checked > 0 else 0

    rows.append({
        "energy_GeV": energy,
        "total_events": n_checked,
        "missing_top_antitop": n_missing,
        "missing_forward_ct>0.8": missing_cos_theta_forward,
        "missing_backward_ct<-0.8": missing_cos_theta_backward,
        "survival_rate_percent": round(survival_rate, 3),
    })

    print(f"  -> {n_checked} events, {n_missing} missing ({100*n_missing/n_checked:.3f}%)")

# Save to CSV
with open(output_csv, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

print(f"\nSaved -> {output_csv}")
for r in rows:
    print(r)