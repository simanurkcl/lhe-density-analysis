import sys

# MadGraph klasörünü Python'a tanıt
sys.path.append("/home/sima/mg5_density")

import madgraph.various.Density_functions as dens
import madgraph.various.lhe_parser as lhe_parser

# LHE dosyasının yolu
lhe_path = "/home/sima/mg5_density/density_test2/Events/run_03/unweighted_events.lhe.gz"

# İlk eventi oku
for event in lhe_parser.EventFile(lhe_path):

    density = event.density

    print("LHE dosyasından okunan density:")
    print(density)

    rho = dens.DensityMatrixObservables(density)

    print("\n4x4 Spin Density Matrix:")
    print(rho.square_matrix())

    print("\nPurity:")
    print(rho.Get_Purity())

    print("\nConcurrence:")
    print(rho.Get_Concurrence())

    print("\nEntanglement of Formation:")
    print(rho.Get_Entanglement_Formation())

    print("\nNegativity:")
    print(rho.Negativity(['fermion','fermion']))

    print("\nPeres-Horodecki:")
    print(rho.PeresHorodecki_criterion(['fermion','fermion']))

    break