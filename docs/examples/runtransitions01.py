"""runtransitions01.py

    Example postprocessor run with one-body and two-body observables.  This
    basic example is meant to model a typical production run, covering a range
    of mesh points.  We illustrate here only the use of predefined "observable
    sets", which suffice for common electroweak observables:

        + "M1" (one-body): provides the various components of the M1 operator (lp, ln, sp, sn)

        + "E2" (one-body): provides the proton and neutron E2 operators (Qp, Qn)

        + "intrinsic-E2" (two-body): provides the "intrinsic" proton and neutron
        E2 operators (Qp', Qn')

        These intrinsic E2 operators should yield identical results to those
        from the one-body E2 operators when applied to transitions between
        nonspurious states in an Nmax-truncated oscillator basis calculation
        [see Appendix A.2 of Caprio, McCoy, Fasano, "Intrinsic operators for the
        translationally-invariant many-body problem", JPG 47, 122001 (2020),
        doi:10.1088/1361-6471/ab9d38].

    See module docstrings in operators/ob.py and operators/tb.py for a complete
    listing of predefined observable sets.
 
    Make sure to run runmfdn13 first, and that its work directory is accessible
    in NCCI_LIBRARY_PATH. Also add `mcscript-ncci/docs/examples` to
    NCCI_DATA_DIR_H2 to ensure that this script can find the relevant h2 files.

    See examples/README.md for full description.

    Patrick J. Fasano, Mark A. Caprio
    University of Notre Dame

    - 04/16/25 (mac): Created, from runtransitions00.

"""
import math

import mcscript
import mcscript.control
import mcscript.task
import mcscript.utils

import mcscript.ncci as ncci
import mcscript.ncci.masks
import mcscript.ncci.mfdn_v15
import mcscript.ncci.postprocessing

# initialize mcscript
mcscript.control.init()

##################################################################
# environment
##################################################################

# TBME paths
ncci.environ.interaction_dir_list = [
]
ncci.environ.operator_dir_list = [
]

##################################################################
# run parameters
##################################################################

# nuclide
nuclide = (3, 3)
A = sum(nuclide)

# interaction
interaction_coulomb_truncation_list = [
    ("Daejeon16", True, ("tb",6)),
    ("JISP16",    True, ("tb",6)),
]

# truncation parameters
Nmax_range = (2, 4, 2)
Nmax_list = mcscript.utils.value_range(*Nmax_range)

# hw
hw_range = (15, 20, 5)
hw_list = mcscript.utils.value_range(*hw_range)


##################################################################
# build task list
##################################################################

tasks = [
    {

        # nuclide/Hamiltonian/hw parameters -- for descriptor
        "nuclide": nuclide,
        "interaction": interaction,
        "use_coulomb": coulomb,
        "hw": hw,

        # basis mode parameters for OBME/TBME generation
        #
        # traditional oscillator many-body truncation
        "basis_mode": ncci.modes.BasisMode.kDirect,
        "sp_truncation_mode": ncci.modes.SingleParticleTruncationMode.kNmax,
        "mb_truncation_mode": ncci.modes.ManyBodyTruncationMode.kNmax,
        "truncation_parameters": {
            "Nmax": Nmax,
            "Nstep": 2,
            },

        # wf selection parameters for postprocessor
        "wf_source_run_list": ["mfdn13"],
        "wf_source_bra_selector": {
            "nuclide": nuclide,
            "interaction": interaction,
            "hw": hw,
            "Nmax": Nmax,
            },
        "wf_source_ket_selector": {
            "nuclide": nuclide,
            "interaction": interaction,
            "hw": hw,
            "Nmax": Nmax,
            },
        "postprocessor_mask": [
            (ncci.masks.mask_allow_near_yrast, {"ni_max": 1, "nf_max": 1}),
        ],
        "postprocessor_mask_verbose": True,

        # obdme parameters
        "obdme_multipolarity": 2,
        "save_obdme": True,

        # one-body observables
        "ob_observable_sets": ["M1", "E2"],

        # two-body observables
        "tb_observable_sets": ["intrinsic-M1", "intrinsic-E2"],

        # file format parameters
        "h2_format": 15099,
        "h2_extension": "dat",  # TODO mac (10/12/20): switch to bin when safe

        # executable name
        "mfdn-transitions_executable": "xtransitions"

    }
    for (interaction,coulomb,truncation_int) in interaction_coulomb_truncation_list
    for Nmax in Nmax_list
    for hw in hw_list
]

##################################################################
# task control
##################################################################

def task_pool(current_task):
    pool = "Nmax{truncation_parameters[Nmax]:02d}".format(**current_task)
    return pool

mcscript.task.init(
    tasks,
    task_descriptor=ncci.descriptors.task_descriptor_7_trans,
    task_pool=task_pool,
    phase_handler_list=[
        ncci.handlers.task_handler_mfdn_postprocessor_pre,
        ncci.handlers.task_handler_mfdn_postprocessor_run,
        ncci.handlers.task_handler_mfdn_postprocessor_post,
    ],
    archive_phase_handler_list=[ncci.handlers.archive_handler_mfdn_postprocessor_hsi],
)

################################################################
# termination
################################################################

mcscript.control.termination()
