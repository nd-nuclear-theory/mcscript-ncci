""" runtransitions00.py

    Example run with two-body transitions. Make sure to run runmfdn13 first,
    and that its work directory is accessible in NCCI_LIBRARY_PATH. Also add
    `mcscript-ncci/docs/examples` to NCCI_DATA_DIR_H2 to ensure that this
    script can find the relevant h2 files.

    See examples.md for full description.

    Patrick J. Fasano, Mark A. Caprio
    University of Notre Dame
"""
import math

import mcscript
import ncci
import ncci.mfdn_v15
import ncci.postprocessing

# initialize mcscript
mcscript.init()

##################################################################
# build task list
##################################################################

ncci.environ.operator_dir_list = [
    "example-data",
]

# nuclide
nuclide = (3, 3)
A = sum(nuclide)

# hw -- linear mesh
hw_range = (15, 20, 5)
hw_list = mcscript.utils.value_range(*hw_range)

# interaction
interaction_coulomb_truncation_list = [
    ("Daejeon16", True, ("tb",6)),
    ("JISP16",    True, ("tb",6)),
]

# Nmax
Nmax_range = (2, 4, 2)
Nmax_list = mcscript.utils.value_range(*Nmax_range)

def mask_allow_near_yrast(task,mask_params,qn_pair,verbose=False):
    """Mask function for transitions involving only low-lying states of each J.

    Mask parameters:
        "ni_max" (int or dict): maximum ni, or dictionary Ji->ni_max
        "nf_max" (int or dict): maximum nf, or dictionary Jf->nf_max

    Arguments:
        task (dict): task dictionary
        mask_params (dict): parameters specific to this mask
        qn_pair (tuple): (qnf,qni) for transition
        verbose (book, optional): verbosity (argument required by handler)

    Returns:
        allow (bool): mask value

    """

    # unpack quantum numbers
    (qnf,qni)=qn_pair
    (Ji,gi,ni)=qni
    (Jf,gf,nf)=qnf

    # calculate mask value
    ni_max = mask_params.get("ni_max",5)
    if (isinstance(ni_max, dict)):
        ni_max = ni_max.get(Ji,0)
    nf_max = mask_params.get("nf_max",999)
    if (isinstance(nf_max, dict)):
        nf_max = nf_max.get(Jf,0)
    if (verbose):
        print("  Mask yrast check: Jf {} nf {} nf_max {} {} ; Ji {} ni {} ni_max {} {}".format(Jf,nf,nf_max,(nf<=nf_max),Ji,ni,ni_max,(ni<=ni_max)))
    allow=(ni<=ni_max)
    allow&=(nf<=nf_max)

    return allow

tasks = [{

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
        (mask_allow_near_yrast, {"ni_max": 1, "nf_max": 1}),
    ],
    "postprocessor_mask_verbose": False,
    
    # obdme parameters
    "obdme_multipolarity": 2,
    "save_obdme": True,

    # one-body observables
    #  ob_observable_sets: ["E0", "E1", "M1", "E2", "M2", ..., "GT", "F"]
    "ob_observable_sets": ["M1", "E2"],
    "ob_observables": [
        # (name, qn, operator_id)
        #            ^-from obme_sources (or builtin)
    ],

    # two-body observables
    # "tb_observable_sets": ["H-components", "am-sqr", "isospin", "intrinsic-E0", "intrinsic-M1", "intrinsic-E2"],
    "tb_observable_sets": ["intrinsic-M1", "intrinsic-E2"],
    "tb_observables": [
        # examples of direct construction:
        # Casimir operators
        ("CSU3", (0,0,0), {"CSU3-U": 1/(A-1), "CSU3-V": 1.0}),
        ("CSp3R", (0,0,0), {"CSp3R-U": 1/(A-1), "CSp3R-V": 1.0}),
        # one-body evaluated as two-body -- for validation/illustration
        ("UDlp", (1,0,0), {"U[Dlp]": 1.0}),
        ("UDln", (1,0,0), {"U[Dln]": 1.0}),
        ("UDsp", (1,0,0), {"U[Dsp]": 1.0}),
        ("UDsn", (1,0,0), {"U[Dsn]": 1.0}),
        ("UE2p", (2,0,0), {"U[E2p]": 1.0}),
        ("UE2n", (2,0,0), {"U[E2n]": 1.0}),
        # one-body Q-invariant (contains cm contribution)
        #     Note: V[a,b] = V[(a*b + b*a)/2]
        ("QxQ_0", (0,0,0), {"U[QxQ_0]": 1.0, "V[Q,Q]": 2.0}),
        ("QpxQp_0", (0,0,0), {"U[QpxQp_0]": 1.0, "V[Qp,Qp]": 2.0}),
        ("QnxQn_0", (0,0,0), {"U[QnxQn_0]": 1.0, "V[Qn,Qn]": 2.0}),
        ],

    # one-body sources
    "obme_sources": [
        # examples of direct construction:
        # operators for quadratic quadrupole shape invariants
        ("r2C2", {"builtin": "solid-harmonic", "coordinate": "r", "order": 2, "qn": (2,0,0)}),
        ("Q", {"linear-combination": {"r2C2": math.sqrt(5/(4*math.pi))}, "qn": (2,0,0)}),
        ("Qp", {"tensor-product": ["delta_p","Q"], "qn": (2,0,0)}),
        ("Qn", {"tensor-product": ["delta_n","Q"], "qn": (2,0,0)}),
        ("Qiv", {"tensor-product": ["tz","Q"], "coefficient": 2., "qn": (2,0,0)}),
        ("QxQ_0", {"tensor-product": ["Q","Q"], "qn": (0,0,0)}),
        ("QpxQp_0", {"tensor-product": ["Qp","Qp"], "qn": (0,0,0)}),
        ("QnxQn_0", {"tensor-product": ["Qn","Qn"], "qn": (0,0,0)}),
    ],

    # two-body sources
    "tbme_sources": [
        ("CSU3-U", {"filename": "CSU3-U-tb-6.bin", "qn": (0,0,0)}),
        ("CSU3-V", {"filename": "CSU3-V-tb-6.bin", "qn": (0,0,0)}),
        ("CSp3R-U", {"filename": "CSp3R-U-tb-6.bin", "qn": (0,0,0)}),
        ("CSp3R-V", {"filename": "CSp3R-V-tb-6.bin", "qn": (0,0,0)}),
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

################################################################
# run control
################################################################

# # add task descriptor metadata field (needed for filenames)
# task["metadata"] = {
#     "descriptor": ncci.descriptors.task_descriptor_7(task)
#     }

# ncci.radial.set_up_orbitals(task)
# ncci.radial.set_up_obme_analytic(task)
# ncci.tbme.generate_tbme(task)
# ncci.postprocessing.run_postprocessor(task)

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
    phase_handler_list=[ncci.handlers.task_handler_postprocessor],
    )

################################################################
# termination
################################################################

mcscript.termination()
