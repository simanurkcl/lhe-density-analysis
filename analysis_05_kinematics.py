import sys
import math

# Add the MadGraph directory to the Python path
sys.path.append("/home/sima/mg5_density")

import madgraph.various.lhe_parser as lhe_parser

# Path to the LHE event file
lhe_path = "/home/sima/mg5_density/density_test2/Events/run_03/unweighted_events.lhe.gz"

# Read only the first event
for event in lhe_parser.EventFile(lhe_path):

    top = None
    antitop = None

    # Find top and anti-top
    for particle in event:

        if particle.pid == 6:
            top = particle

        elif particle.pid == -6:
            antitop = particle

    # Calculate invariant mass
    Px = top.px + antitop.px
    Py = top.py + antitop.py
    Pz = top.pz + antitop.pz
    E  = top.E  + antitop.E

    Mtt = math.sqrt(E**2 - Px**2 - Py**2 - Pz**2)

    # Momentum magnitude
    p_top = math.sqrt(top.px**2 + top.py**2 + top.pz**2)
    p_antitop = math.sqrt(antitop.px**2 + antitop.py**2 + antitop.pz**2)

    # cos(theta)
    cos_theta = top.pz / p_top

    print("=" * 70)
    print("Kinematic Information for the First Event")
    print("=" * 70)

    print(f"Invariant Mass (Mtt): {Mtt:.3f} GeV")
    print(f"cos(theta):           {cos_theta:.5f}")

    print()

    print("Top quark")
    print(f"Px = {top.px:.3f}")
    print(f"Py = {top.py:.3f}")
    print(f"Pz = {top.pz:.3f}")
    print(f"E  = {top.E:.3f}")
    print(f"|p| = {p_top:.3f}")

    print()

    print("Anti-top quark")
    print(f"Px = {antitop.px:.3f}")
    print(f"Py = {antitop.py:.3f}")
    print(f"Pz = {antitop.pz:.3f}")
    print(f"E  = {antitop.E:.3f}")
    print(f"|p| = {p_antitop:.3f}")

    print("=" * 70)

    break