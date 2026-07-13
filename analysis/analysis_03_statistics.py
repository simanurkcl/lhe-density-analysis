import sys
import sys
import numpy as np

# Add the MadGraph directory to the Python path
sys.path.append("/home/sima/mg5_density")

import madgraph.various.Density_functions as dens
import madgraph.various.lhe_parser as lhe_parser

# Path to the LHE event file
lhe_path = "/home/sima/mg5_density/density_test2/Events/run_03/unweighted_events.lhe.gz"

# Lists to store observables
purities = []
concurrences = []
formations = []
negativities = []

# Loop over all events
for event in lhe_parser.EventFile(lhe_path):

    density = event.density
    rho = dens.DensityMatrixObservables(density)

    purities.append(rho.Get_Purity())
    concurrences.append(rho.Get_Concurrence())
    formations.append(rho.Get_Entanglement_Formation())

    negativity, log_negativity = rho.Negativity(['fermion', 'fermion'])
    negativities.append(negativity)

# Print summary
print("=" * 75)
print("Quantum Information Analysis Summary")
print("=" * 75)

print(f"Total number of events: {len(purities)}")

print("\nObservable Statistics")
print("-" * 75)

print(f"{'Observable':<30}{'Mean':>12}{'Std':>12}{'Min':>12}{'Max':>12}")
print("-" * 75)

observables = {
    "Purity": purities,
    "Concurrence": concurrences,
    "Entanglement of Formation": formations,
    "Negativity": negativities,
}

for name, values in observables.items():
    values = np.array(values)

    print(
        f"{name:<30}"
        f"{np.mean(values):>12.6f}"
        f"{np.std(values):>12.6f}"
        f"{np.min(values):>12.6f}"
        f"{np.max(values):>12.6f}"
    )

print("=" * 75)