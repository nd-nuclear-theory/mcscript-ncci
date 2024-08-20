"""runmfdn16.py

    Example diagonalization run for traditional shell-model calculation. Add
    `mcscript-ncci/docs/examples` to NCCI_DATA_DIR_H2 to ensure that this script
    can find the relevant h2 files.

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
    "example-data",
]
ncci.environ.operator_dir_list = [
    # paths to TBME files for observables
    ## "example-data",
]

##################################################################
# run parameters
##################################################################

# nuclide
nuclide_list = [
    (8,10),  # 18O
    (8,12),  # 20O
    (9,9),  # 18F
    (9,10),  # 19F
    (10,10),  # 20N
    (12,13),  # 25Mg
]

# interactions
interaction_list = [
    "w",
    "usdb",
]
orbitals = "sd_orbital"
core_nuclide = (8,8)
tbme_scaling_power = 0.3

# truncation parameters
# pick M=0.0 for A even, 0.5 for A odd
def M_list_by_nuclide(nuclide):
    A = sum(nuclide)
    if A%2:
        return [0.5]
    else:
        return [0.0]

# eigenvector convergence
eigenvectors = 8
max_iterations = 600
tolerance = 1e-6

##################################################################
# build task list
##################################################################

tasks = [
    {
        # nuclide parameters
        "nuclide": nuclide,

        # Hamiltonian parameters
        "interaction": interaction,
        "tbme_scaling_power": tbme_scaling_power,

        # basis parameters
        "basis_mode": ncci.modes.BasisMode.kShellModel,

        # one-body and many-body truncation
        "sp_truncation_mode": ncci.modes.SingleParticleTruncationMode.kManual,
        "mb_truncation_mode": ncci.modes.ManyBodyTruncationMode.kFCI,
        "truncation_parameters": {
            "M": M,
            "parity": +1,
            "sp_filename": orbitals,
            "sp_weight_max": 0.0,
            "mb_core": core_nuclide,
        },

        # diagonalization parameters
        "diagonalization": True,
        "eigenvectors": eigenvectors,
        "max_iterations": max_iterations,
        "tolerance": tolerance,
        "mfdn_inputlist" : {},
        
        # obdme parameters
        "calculate_obdme": False,
        "save_obdme": False,

        # wavefunction storage
        "save_wavefunctions": False,

        # version parameters
        "h2_format": 15099,
        "mfdn_executable": "xmfdn-h2-lan",
        "mfdn_driver": ncci.mfdn_v15
    }
    for nuclide in nuclide_list
    for M in M_list_by_nuclide(nuclide)
    for interaction in interaction_list
]

##################################################################
# task dictionary postprocessing functions
##################################################################

# none

##################################################################
# task control
##################################################################

mcscript.task.init(
    tasks,
    task_descriptor=ncci.descriptors.task_descriptor_10,
    ## task_pool=task_pool,
    phase_handler_list=ncci.handlers.task_handler_mfdn_phases,
    archive_phase_handler_list=[ncci.handlers.archive_handler_mfdn_hsi],
)

################################################################
# termination
################################################################

mcscript.control.termination()
