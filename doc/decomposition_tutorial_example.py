"""Simple example Lanczos analysis to go with decomposition-tutorial.md.

    Mark A. Caprio
    University of Notre Dame

    Language: Python 3

    - 03/27/25 (mac): Created.

"""

import os

import numpy as np

## import mfdnres
## import mfdnres.ncci
import mfdnres.decomposition

################################################################
# reading data
################################################################

def examine_mfdndecomp01_results():
    """Read results.
    """

    # read in Lanczos file
    print("Reading lanczos file...")
    lanczos_filename = "/home/mcaprio/scratch/runs/runmfdndecomp01/results/lanczos/runmfdndecomp01-mfdn15-Z3-N3-Daejeon16-coul1-hw15.000-a_cm50-Nmax04-Mj1.0-lan600-tol1.0e-06-J01.0-g0-n01-Ntot-dlan1200.lanczos"
    alpha_beta = mfdnres.decomposition.read_lanczos(lanczos_filename)
    alpha, beta = alpha_beta
    print(len(alpha), alpha, len(beta), beta)

    # generate raw decomposition
    print("Raw decomposition...")
    raw_decomposition = mfdnres.decomposition.generate_raw_decomposition(alpha_beta, lanczos_iterations=None)
    ## for entry in raw_decomposition:
    ##     print(entry)
    np.set_printoptions(edgeitems=10)
    print(np.array(raw_decomposition))

    # or with truncated Lanczos iterations
    for lanczos_iterations in [5,10]:
        print("lanczos_iterations {}".format(lanczos_iterations))
        raw_decomposition_truncated = mfdnres.decomposition.generate_raw_decomposition(alpha_beta, lanczos_iterations=lanczos_iterations)
        print(np.array(raw_decomposition_truncated))

    # generate binned decomposition
    print("Binned decomposition...")
    eigenvalue_label_dict = {
        float(Nex+2) : (Nex,)
        for Nex in [0, 2, 4]
    }
    for lanczos_iterations in [2,3,5,10]:
        print("lanczos_iterations {}".format(lanczos_iterations))
        decomposition = mfdnres.decomposition.generate_decomposition(
            alpha_beta, eigenvalue_label_dict, lanczos_iterations=lanczos_iterations,
            verbose=False
        )
        ## print(decomposition)  # oh, that's not so pretty
        mfdnres.decomposition.print_decomposition(decomposition)

    # now for the results from using Nex as the decomposition operator

    # read in Lanczos file
    print("Reading lanczos file...")
    lanczos_filename = "/home/mcaprio/scratch/runs/runmfdndecomp01/results/lanczos/runmfdndecomp01-mfdn15-Z3-N3-Daejeon16-coul1-hw15.000-a_cm50-Nmax04-Mj1.0-lan600-tol1.0e-06-J01.0-g0-n01-Nex-dlan1200.lanczos"
    alpha_beta = mfdnres.decomposition.read_lanczos(lanczos_filename)

    # generate binned decomposition
    print("Binned decomposition (Nex operator)...")
    eigenvalue_label_dict = {
        float(Nex) : (Nex,)
        for Nex in [0, 2, 4]
    }
    for lanczos_iterations in [5]:
        print("lanczos_iterations {}".format(lanczos_iterations))
        decomposition = mfdnres.decomposition.generate_decomposition(
            alpha_beta, eigenvalue_label_dict, lanczos_iterations=lanczos_iterations,
            verbose=True
        )
        ## print(decomposition)  # oh, that's not so pretty
        mfdnres.decomposition.print_decomposition(decomposition)
    
################################################################
# main
################################################################

if (__name__ == "__main__"):

    examine_mfdndecomp01_results()
