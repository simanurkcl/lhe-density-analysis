import sys
import os
import math
import csv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))




# Add MadGraph to Python path
sys.path.append("/home/sima/mg5_density")

import madgraph.various.Density_functions as dens
import madgraph.various.lhe_parser as lhe_parser

from config import LHE_PATH, EVENT_DATA
lhe_path = LHE_PATH 
output_file = EVENT_DATA

with open(output_file, "w", newline="") as csvfile:

    writer = csv.writer(csvfile)

    writer.writerow([
        "Event",
        "Mtt",
        "cos_theta",
        "Purity",
        "Concurrence",
        "EOF",
        "Negativity"
    ])

    event_number = 0

    for event in lhe_parser.EventFile(lhe_path):

        event_number += 1

        density = event.density
        rho = dens.DensityMatrixObservables(density)

        purity = rho.Get_Purity()
        concurrence = rho.Get_Concurrence()
        eof = rho.Get_Entanglement_Formation()

        negativity, log_negativity = rho.Negativity(
            ['fermion', 'fermion']
        )

        top = None
        antitop = None

        for particle in event:

            if particle.pid == 6:
                top = particle

            elif particle.pid == -6:
                antitop = particle

        if top is None or antitop is None:
            continue

        Px = top.px + antitop.px
        Py = top.py + antitop.py
        Pz = top.pz + antitop.pz
        E = top.E + antitop.E

        mass_squared = E**2 - Px**2 - Py**2 - Pz**2

        if mass_squared < 0:
            mass_squared = 0

        Mtt = math.sqrt(mass_squared)

        momentum = math.sqrt(
            top.px**2 +
            top.py**2 +
            top.pz**2
        )

        if momentum == 0:
            cos_theta = 0
        else:
            cos_theta = top.pz / momentum

        writer.writerow([
            event_number,
            Mtt,
            cos_theta,
            purity,
            concurrence,
            eof,
            negativity
        ])

print("=" * 70)
print("Dataset successfully created!")
print(f"Number of events : {event_number}")
print(f"Output file      : {output_file}")
print("=" * 70)