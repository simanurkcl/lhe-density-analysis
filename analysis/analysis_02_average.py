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
print("=" * 50)
print("Quantum Information Analysis Summary")
print("=" * 50)

print(f"Total number of events: {len(purities)}")

print("\nAverage observables:")
print(f"Purity: {np.mean(purities):.6f}")
print(f"Concurrence: {np.mean(concurrences):.6f}")
print(f"Entanglement of Formation: {np.mean(formations):.6f}")
print(f"Negativity: {np.mean(negativities):.6f}")

print("=" * 50)