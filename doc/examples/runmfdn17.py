"""runmfdn17.py

    Example diagonalization run with uniform orbital set for different Nmax.

    A uniform orbital set (and uniform partitioning) is typically needed if
    mfdn-transitions is to be run with bra and ket from different Nmax spaces.
    (More precisely, the partitioning for the smaller space has to be a *subset*
    of that for the large space, obtained by truncation.  But it is typically
    more convenient to just run with the same partition file and orbital set for
    all Nmax.)


    Add `mcscript-ncci/docs/examples` to NCCI_DATA_DIR_H2 to ensure that this
    script can find the relevant h2 files.

    Example invocation:

        qsubm mfdn17 --toc

        qsubm mfdn17 --pool="*" --serialthread=8 --phase=0

        qsubm mfdn17 --pool=Nmax02 --serialthread=8 --threads=8 --ranks=1 --phase=1

        qsubm mfdn17 --pool=Nmax04 --serialthread=8 --threads=8 --ranks=1 --phase=1

        # qsubm mfdn17 --pool=Nmax04 --serialthread=8 --threads=1 --ranks=6 --phase=1

        qsubm mfdn17 --pool="*" --serialthread=8 --phase=2

    See examples/README.md for full description.

    Patrick J. Fasano, Mark A. Caprio
    University of Notre Dame

"""

import mcscript
import mcscript.control
import mcscript.task
import mcscript.utils

import mcscript.ncci as ncci
import mcscript.ncci.mfdn_v15

# initialize mcscript
mcscript.control.init()

##################################################################
# environment
##################################################################

# TBME paths
ncci.environ.interaction_dir_list = [
    # paths to TBME files for interactions
    "daejeon16-tb-6",
    "jisp16-tb-6",
    "coulomb-tb-6",
]
ncci.environ.operator_dir_list = [
    # paths to TBME files for observables
    "casimir-tb-6",
]


##################################################################
# run parameters
##################################################################

# nuclide
nuclide_list = [(3,3)]
A = sum(nuclide_list[0])  # assumes any nuclei in run are isobars

# interaction
interaction_coulomb_truncation_list = [
    ("Daejeon16", True, ("tb",6)),
]
hw_coul = 20.

# truncation parameters
Nmax_range = (2, 4, 2)
Nmax_list = mcscript.utils.value_range(*Nmax_range)
M_list = [1.0]
Nmax_orb = 5  # set high enough to cover the highest Nmax we will calculate

# hw
hw_range = (15, 15, 5)
hw_list = mcscript.utils.value_range(*hw_range)

# eigenvector convergence
eigenvectors = 1
max_iterations = 600
tolerance = 1e-6

# Lawson
a_cm = 50.


##################################################################
# build task list
##################################################################

tasks = [
    {
        # nuclide parameters
        "nuclide": nuclide,

        # Hamiltonian parameters
        "interaction": interaction,
        "use_coulomb": coulomb,
        "a_cm": a_cm,
        "hw_cm": None,

        # input TBME parameters
        "truncation_int": truncation_int,
        "hw_int": hw,
        "truncation_coul": truncation_int,
        "hw_coul": hw_coul,

        # basis parameters
        "basis_mode": ncci.modes.BasisMode.kDirect,
        "hw": hw,

        # traditional oscillator many-body truncation
        "sp_truncation_mode": ncci.modes.SingleParticleTruncationMode.kNmax,
        "mb_truncation_mode": ncci.modes.ManyBodyTruncationMode.kNmax,
        "truncation_parameters": {
            "Nmax": Nmax,
            "Nstep": 2,
            "M": M,
            "Nmax_orb": Nmax_orb,
            },

        # diagonalization parameters
        "diagonalization": True,
        "eigenvectors": eigenvectors,
        "initial_vector": -2,
        "max_iterations": max_iterations,
        "tolerance": tolerance,
        "partition_filename": None,

        # obdme parameters
        "save_obdme": False,

        # wavefunction storage
        "save_wavefunctions": True,

        # version parameters
        "h2_format": 15099,
        "mfdn_executable": "xmfdn-h2-lan",
        "mfdn_driver": ncci.mfdn_v15,
    }
    for M in M_list
    for nuclide in nuclide_list
    for Nmax in Nmax_list
    for (interaction,coulomb,truncation_int) in interaction_coulomb_truncation_list
    for hw in hw_list
]


##################################################################
# task dictionary postprocessing functions
##################################################################

def task_pool(task):
    pool = "Nmax{truncation_parameters[Nmax]:02d}".format(**task)
    return pool


##################################################################
# task control
##################################################################

mcscript.task.init(
    tasks,
    task_descriptor=ncci.descriptors.task_descriptor_7,
    task_pool=task_pool,
    phase_handler_list=ncci.handlers.task_handler_mfdn_phases,
    archive_phase_handler_list=[ncci.handlers.archive_handler_mfdn_hsi],
)


################################################################
# termination
################################################################

mcscript.control.termination()
