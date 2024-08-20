""" runmfdn13.py

    Example diagonalization run as setup for two-body transitions. Add
    `mcscript-ncci/docs/examples` to NCCI_DATA_DIR_H2 to ensure that this
    script can find the relevant h2 files.

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
nuclide_list = [(3,3)]
A = sum(nuclide_list[0])  # assumes any nuclei in run are isobars

# interaction
interaction_coulomb_truncation_list = [
    ("Daejeon16", True, ("tb",6)),
    ("JISP16",    True, ("tb",6)),
]
hw_coul = 20.

# truncation parameters
Nmax_range = (2, 4, 2)
Nmax_list = mcscript.utils.value_range(*Nmax_range)
M_list = [0.0, 1.0]

# hw
hw_range = (15, 20, 5)
hw_list = mcscript.utils.value_range(*hw_range)

# eigenvector convergence
eigenvectors = 4
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

        # transformation parameters
        "xform_truncation_int": None,
        "xform_truncation_coul": None,
        "hw_coul_rescaled": None,
        "target_truncation": None,

        # traditional oscillator many-body truncation
        "sp_truncation_mode": ncci.modes.SingleParticleTruncationMode.kNmax,
        "mb_truncation_mode": ncci.modes.ManyBodyTruncationMode.kNmax,
        "truncation_parameters": {
            "Nmax": Nmax,
            "Nstep": 2,
            "M": M,
            },

        # diagonalization parameters
        "diagonalization": True,
        "eigenvectors": eigenvectors,
        "initial_vector": -2,
        "max_iterations": max_iterations,
        "tolerance": tolerance,
        "partition_filename": None,

        # obdme parameters
        "obdme_multipolarity": 2,
        "save_obdme": True,
        "ob_observable_sets": ['M1', 'E2'],

        # two-body observables (for expectation values)
        "tb_observable_sets": ["H-components", "isospin"],
        "tb_observables": [
            ## ("CSU3",  (0,0,0), {"CSU3-U": 1/(A-1), "CSU3-V": 1.0}),
            ## ("CSp3R", (0,0,0), {"CSp3R-U": 1/(A-1), "CSp3R-V": 1.0}),
        ],

        # sources (for observable construction)
        "obme_sources": [],
        "tbme_sources": [
            ## ("CSU3-U", {"filename": "CSU3-U-tb-6.bin", "qn": (0,0,0)}),
            ## ("CSU3-V", {"filename": "CSU3-V-tb-6.bin", "qn": (0,0,0)}),
            ## ("CSp3R-U", {"filename": "CSp3R-U-tb-6.bin", "qn": (0,0,0)}),
            ## ("CSp3R-V", {"filename": "CSp3R-V-tb-6.bin", "qn": (0,0,0)}),
        ],

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

def task_pool(current_task):
    pool = "Nmax{truncation_parameters[Nmax]:02d}".format(**current_task)
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
