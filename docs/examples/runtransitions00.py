""" runtransitions00.py

    Example run with two-body transitions. Make sure to run runmfdn14 first,
    and that its work directory is accessible in NCCI_LIBRARY_PATH. Also add
    `mcscript-ncci/docs/examples` to NCCI_DATA_DIR_H2 to ensure that this
    script can find the relevant h2 files.

    See runmfdn.txt for full description.

    Patrick J. Fasano, Mark A. Caprio
    University of Notre Dame

    - 10/11/19 (pjf): Created, copied from runmfd13.
"""
import math

import mcscript
import ncci
import ncci.mfdn_v15
import ncci.postprocessing

# initialize mcscript
mcscript.init()

#ncci.library.LIBRARY_BASE = "$HOME/Research/tmp/runs"

##################################################################
# build task list
##################################################################

ncci.environ.operator_dir_list = [
    "example-data",
]

# hw -- linear mesh
hw_range = (15, 25, 5)
hw_list = mcscript.utils.value_range(*hw_range)

# interaction
interaction_coulomb_truncation_list = [
    ("Daejeon16", True, ("tb",6)),
    ("JISP16",    True, ("tb",6)),
]

# Nmax
Nmax_range = (2, 4, 2)
Nmax_list = mcscript.utils.value_range(*Nmax_range)

tasks = [{
    # nuclide parameters
    "nuclide": (3, 3),

    "wf_source_run_list": ["mfdn14"],
    "wf_source_bra_selector": {
        "nuclide": (3, 3),
        "interaction": interaction,
        "hw": hw,
        "Nmax": Nmax,
        },
    "wf_source_ket_selector": {
        "nuclide": (3, 3),
        "interaction": interaction,
        "hw": hw,
        "Nmax": Nmax,
        },

    # basis parameters
    "basis_mode": ncci.modes.BasisMode.kDirect,
    "hw": hw,

    # Hamiltonian parameters
    "interaction": interaction,
    "use_coulomb": coulomb,
    "a_cm": 40.,
    "hw_cm": None,

    # truncation parameters for TBME generation
    # traditional oscillator many-body truncation
    "sp_truncation_mode": ncci.modes.SingleParticleTruncationMode.kNmax,
    "mb_truncation_mode": ncci.modes.ManyBodyTruncationMode.kNmax,
    "truncation_parameters": {
        "Nmax": Nmax,
        "Nstep": 2,
        },

    # obdme parameters
    "obdme_multipolarity": 2,
    "save_obdme": True,

    # one-body observables
    #  ob_observable_sets: ['E0', 'E1', 'M1', 'E2', 'M2', ..., 'GT', 'F']
    "ob_observable_sets": ['M1', 'E2'],
    "ob_observables": [
        # (name, qn, operator_id)
        #            ^-from obme_sources (or builtin)
    ],

    # two-body observables
    ## "observable_sets": ["H-components","am-sqr","isospin"],
    "tb_observable_sets": ["am-sqr"],
    "tb_observables": [
        ("CSU3", (0,0,0), {"CSU3-U": 1/(6-1), "CSU3-V": 1.0}),
        ("CSp3R", (0,0,0), {"CSp3R-U": 1/(6-1), "CSp3R-V": 1.0}),
        ("UDlp", (1,0,0), {"U[Dlp]": 1.0}),
        ("UDln", (1,0,0), {"U[Dln]": 1.0}),
        ("UDsp", (1,0,0), {"U[Dsp]": 1.0}),
        ("UDsn", (1,0,0), {"U[Dsn]": 1.0}),
        ("UE2p", (2,0,0), {"U[E2p]": 1.0}),
        ("UE2n", (2,0,0), {"U[E2n]": 1.0}),
        # V[a,b] = V[(a*b + b*a)/2]
        ("QxQ_0", (0,0,0), {"U[QxQ_0]": 1.0, "V[Q,Q]": 2.0})
        ],

    # one-body sources
    "obme_sources": [
        # examples of direct construction:
        ("Q",    {"builtin": "solid-harmonic", "coordinate": "r", "order": 2, "qn": (0,0,0)}),
        ("Qp",   {"tensor-product": ["delta_p","Q"], "qn": (2,0,0)}),
        ("Qn",   {"tensor-product": ["delta_n","Q"], "qn": (2,0,0)}),
        ("Qiv",  {"tensor-product": ["tz","Q"], "coefficient": 2., "qn": (2,0,0)}),
        ("QxQ_0", {"tensor-product": ["Q","Q"], "qn": (0,0,0)}),
    ],

    # two-body sources
    "tbme_sources": [
        ("CSU3-U", {"filename": "CSU3-U-tb-6.bin", "qn": (0,0,0)}),
        ("CSU3-V", {"filename": "CSU3-V-tb-6.bin", "qn": (0,0,0)}),
        ("CSp3R-U", {"filename": "CSp3R-U-tb-6.bin", "qn": (0,0,0)}),
        ("CSp3R-V", {"filename": "CSp3R-V-tb-6.bin", "qn": (0,0,0)}),
    ],

    "h2_format": 15099,
    "h2_extension": "dat",
    "mfdn-transitions_executable": "d76d226/xtransitions"

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
