""" runmfdn05.py

    See runmfdn.txt for description.

    Mark A. Caprio
    University of Notre Dame

    - 01/18/17 (mac): Created.
    - 01/29/17 (pjf): Updated for new truncation_mode parameter.
    - 06/03/17 (pjf): Updated for new scripting.
    - 07/31/17 (pjf): Set MFDn driver module in task dictionary.
    - 08/11/17 (pjf): Update for split single-particle and many-body truncation modes.
    - 12/19/17 (pjf): Update for mfdn->ncci rename.
    - 09/07/19 (pjf): Remove Nv from truncation_parameters.
"""

import mcscript
import ncci
import ncci.mfdn_v14

# initialize mcscript
mcscript.init()

##################################################################
# build task list
##################################################################

ncci.environ.interaction_run_list = [
    "run0164-JISP16-ob-9",
    "run0164-JISP16-ob-13",
    "run0164-JISP16-tb-10",
    "run0164-JISP16-tb-20",
    "run0306-N2LOopt500",  # up to tb-20
    "runvc0083-Daejeon16-ob-13"
]

# hw -- linear mesh
hw_range = (15, 25, 5)
hw_list = mcscript.utils.value_range(*hw_range)

# hw -- log mesh
## hw_log_range = (5, 40, 8)
## hw_list = mcscript.utils.log_range(*hw_log_range)

# Nmax
Nmax_range = (2, 20, 2)
Nmax_list = mcscript.utils.value_range(*Nmax_range)

# interactions
interaction_coulomb_truncation_list = [
    ("JISP16", True, ("tb", 20)),
    # ("N2LOopt500", False, ("tb", 20))
]

# General recommendations for iteration order on parameters under old
# scripting (run0391):
#
#    # mj
#    # cycle first on M, since decreasing M-space dimension within each nuclide/Nmax category
#    # should be robust against walltime overruns
#    for Mj in Mj_list
#    # nuclide
#    for nuclide in nuclide_list
#    # many-body-truncation
#    for Nmax in Nmax_list
#    # unit basis
#    for (radial_basis_p, radial_basis_n) in radial_basis_pair_list
#    for beta_ratio in beta_ratio_list
#    # scaling
#    for hw in hw_list
#    # Lawson
#    for hwLawson in hwLawson_list
#    # source xform
#    for hw_int in mcscript.auto_value(hw_int_list, [hw])
#    for (interaction, coulomb, xform_cutoff_list) in interaction_tuple_list
#    for xform_cutoff in xform_cutoff_list


task_list = [
    {
        # nuclide parameters
        "nuclide": (2, 2),

        # Hamiltonian parameters
        "interaction": interaction,
        "use_coulomb": use_coulomb,
        "a_cm": 20.,
        "hw_cm": None,

        # input TBME parameters
        "truncation_int": truncation_int,
        "hw_int": 20.,
        "truncation_coul": ("tb", 20),
        "hw_coul": 20.,

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
            "M": 0,
            "Nmax": Nmax,
            "Nstep": 2,
            },

        # diagonalization parameters
        "eigenvectors": 5,
        "initial_vector": -2,
        "max_iterations": 500,
        "tolerance": 1e-6,
        "partition_filename": None,
        "save_wavefunctions": True,

        # obdme parameters
        ## "hw_for_trans": 20,
        "obdme_multipolarity": 2,
        "obdme_reference_state_list": [(0, 0, 1)],
        "save_obdme": True,

        # two-body observables
        ## "tb_observable_sets": ["H-components","am-sqr"],
        "tb_observable_sets": ["H-components"],

        # version parameters
        "h2_format": 0,
        "mfdn_executable": "v14-beta06/xmfdn-h2-lan",
        "mfdn_driver": ncci.mfdn_v14,
    }
    for Nmax in Nmax_list
    for (interaction, use_coulomb, truncation_int) in interaction_coulomb_truncation_list
    for hw in hw_list
]


##################################################################
# task dictionary postprocessing functions
##################################################################

def task_pool(current_task):
    pool = "Nmax{Nmax:02d}-Mj{M:3.1f}".format(**current_task["truncation_parameters"])
    return pool


def task_mask(current_task):
    ## allow = mcscript.approx_equal(current_task["hw"], 20., 0.1)
    allow = True
    return allow


##################################################################
# task control
##################################################################

mcscript.task.init(
    task_list,
    task_descriptor=ncci.descriptors.task_descriptor_7,
    task_pool=task_pool,
    task_mask=task_mask,
    phase_handler_list=[ncci.handlers.task_handler_oscillator],
    # Note: change to mcscript.task.archive_handler_hsi for tape backup
    archive_phase_handler_list=[ncci.handlers.archive_handler_mfdn_hsi]
    )


################################################################
# termination
################################################################

mcscript.termination()
