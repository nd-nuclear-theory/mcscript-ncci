"""runtransitions02.py

    Example of explicitly defining a one-body observable and a two-body
    observable.

    Here we explicitly construct the intrinsic kinetic energy
    operator from its expression as a sum of one-body and separable two-body
    terms, e.g, equation (4) of "intrinsic" [Caprio, McCoy, Fasano, "Intrinsic
    operators for the translationally-invariant many-body problem", JPG 47,
    122001 (2020), doi:10.1088/1361-6471/ab9d38].

    We also construct the naive one-body lab-frame kinetic energy operator,
    which will contain a spurious contribution from the zero-point motion of the
    center of mass.

    We compare their expectation values in the eigenstates of 6Li, already
    calculated in runmfdn13.

    Make sure to run runmfdn13 first, and that its work directory is accessible
    in NCCI_LIBRARY_PATH. Also add `mcscript-ncci/docs/examples` to
    NCCI_DATA_DIR_H2 to ensure that this script can find the relevant h2 files.

    ----------------------------------------------------------------

    Let us compare results...

    The "H-components" observable set is calculated in runmfdn13.  We thus
    already know the expectation values from the file

    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    runmfdn13-mfdn15-Z3-N3-Daejeon16-coul1-hw15.000-a_cm50-Nmax02-Mj0.0-lan600-tol1.0e-06.res
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # TBME files for additional operators
    TBMEfile(2) = tbme-H.bin
    TBMEfile(3) = tbme-Ncm.bin
    TBMEfile(4) = tbme-Tintr.bin
    TBMEfile(5) = tbme-Tcm.bin
    TBMEfile(6) = tbme-VNN.bin
    TBMEfile(7) = tbme-VC.bin
    TBMEfile(8) = tbme-T2.bin
    
    ...
        [Other 2-body observables]
    # Seq    J    n      T     see header for TBME file names of observables
        1   1.0   1   0.000     -25.5777         0.337532E-10      75.1700          11.2500         -102.499          1.75138         0.924282E-04
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Thus, <Tintr>=75.170, and <Tcm>=11.250., from which we surmise <T>=<Tintr>+<Tcm>=86.42.

    For Tintr from the postprocessor, we look in the two-body results file

    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    runtransitions02-transitions-tb-Z3-N3-Daejeon16-coul1-hw15.000-Nmax02.res
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Here we find

    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    [Two-body observable]
    #  J0  g0 Tz0  name
        0   0   0  Tintr
    #   Jf  gf  nf    Ji  gi  ni              rme
       1.0   0   1   1.0   0   1   1.30198310e+02
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Does this agree for <Tintr>?  It might look like it does not, since 130.198
    is not 75.170!  But this is actually the RME.  We must divide by the angular
    momentum factor sqrt(2*J+1) to get the expectation value (which agrees with
    the mfdn result above):

        <Tintr>=130.198/sqrt(3)=75.170

    For Tlab from the postprocessor, we look in the one-body results file

    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    runtransitions02-transitions-ob-Z3-N3-Daejeon16-coul1-hw15.000-Nmax02.res
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Here we find

    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    [One-body observable]
    #  J0  g0 Tz0  name
        0   0   0  Tlab
    #   Jf  gf  nf    Ji  gi  ni              rme
       1.0   0   1   1.0   0   1   1.49683889e+02
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    We thus get the expectation value (which agrees from what we deduced from the
    mfdn results for Tintr and Tcm above)

        <Tlab>=149.684/sqrt(3)=86.420

    ----------------------------------------------------------------

    See examples/README.md for full description.

    Patrick J. Fasano, Mark A. Caprio
    University of Notre Dame

    - 04/14/25 (mac): Created, with overall structure from runtransitions00.

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
nuclide = (3, 3)
A = sum(nuclide)

# interaction
interaction_coulomb_truncation_list = [
    ("Daejeon16", True, ("tb",6)),
    ## ("JISP16",    True, ("tb",6)),
]

# truncation parameters
Nmax_range = (2, 2, 2)
Nmax_list = mcscript.utils.value_range(*Nmax_range)

# hw
hw_range = (15, 15, 5)
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
            (ncci.masks.mask_transitions, {"transitions": [((1.0,0,1), (1.0,0,1))]}),
        ],
        "postprocessor_mask_verbose": False,

        # obdme parameters
        "obdme_multipolarity": 0,
        "save_obdme": False,

        # one-body observables
        "ob_observable_sets": [],
        "ob_observables": [
            # naive one-body (lab frame) kinetic energy (T, or Tlab)
            #
            #       T = 1/(2*mN) sum_i p_i^2
            ("Tlab", (0,0,0), "Tlab"),
        ],
        "obme_sources": [
            (
                "Tlab",
                {
                    "qn": (0,0,0),
                    "linear-combination": mcscript.utils.CoefficientDict({"ik.ik": -(ncci.constants.k_hbar_c**2/(2*ncci.constants.k_mN_csqr))}),
                },
            ),
        ],

        # two-body observables
        "tb_observables": [
            # intrinsic kinetic energy (Tintr)
            #
            #   The intrinsic kinetic energy operator Tintr contributes to the
            #   NCCI Hamiltonian.  It is "built into" the mcscript.ncci
            #   scripting, for this purpose, and is also one of the operators
            #   provided as part of the "H-components" set of two-body
            #   observables.  So you would not neet to construct it directly.
            #   But this serves as a useful example, illustrating how you would
            #   build up such an operator.
            #
            #   The decomposition of the intrinsic kinetic enegy into a one-body
            #   part and a separable two-body part is summarized in, e.g.,
            #   equation (4) of "intrinsic" [Caprio 2020,
            #   doi:10.1088/1361-6471/ab9d38]:
            #
            #       Tintr = (A-1)/(2*mN*A) sum_i p_i^2 - 1/(2*mN*A) sum'_ij p_i.p_j
            ("Tintr", (0,0,0), {
                # one-body term:
                #  - two-body upgrade
                #  - of builtin one-body source ik.ik
                "U[ik.ik]": - ((A-1)/(2*A)) * (ncci.constants.k_hbar_c**2/ncci.constants.k_mN_csqr),
                # separable two-body term:
                #   - spherical tensor coupled product (to J0=0 given by qn above)
                #   - of builtin one-body source ik with itself
                #   - keeping in mind the relative factor between
                #     the definitions of the vector dot product A.B and the
                #     zero-coupled product (AxB)_0
                "V[ik,ik]": math.sqrt(3) * (-1/A) * (ncci.constants.k_hbar_c**2/ncci.constants.k_mN_csqr),
            }),
            #   The built-in version of the Tintr operator implements this same
            #   formula, in the function operators.tb.Tintr.  We can compare the
            #   results.
            ("builtin_Tintr", (0,0,0), ncci.operators.tb.Tintr(A)),
        ],

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
