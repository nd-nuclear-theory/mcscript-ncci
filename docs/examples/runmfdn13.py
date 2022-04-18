""" runmfdn13.py

    Example diagonalization run as setup for two-body transitions. Add
    `mcscript-ncci/docs/examples` to NCCI_DATA_DIR_H2 to ensure that this
    script can find the relevant h2 files.

    See examples.md for full description.

    Patrick J. Fasano, Mark A. Caprio
    University of Notre Dame
"""

import collections

import mcscript
import ncci
import ncci.mfdn_v15
import ncci.postprocessing

# initialize mcscript
mcscript.init()

##################################################################
# build task list
##################################################################

ncci.environ.interaction_run_list = [
    "example-data",
]

ncci.environ.operator_dir_list = [
    "example-data"
]

# hw -- linear mesh
hw_range = (15, 20, 5)
hw_list = mcscript.utils.value_range(*hw_range)

# hw -- log mesh
## hw_log_range = (5, 40, 8)
## hw_list = mcscript.utils.log_range(*hw_log_range)

# interaction
interaction_coulomb_truncation_list = [
    ("Daejeon16", True, ("tb",6)),
    ("JISP16",    True, ("tb",6)),
]

# Nmax
Nmax_range = (2, 4, 2)
Nmax_list = mcscript.utils.value_range(*Nmax_range)

# M
M_list = [0.0, 1.0]

tasks = [
    collections.OrderedDict({
        # nuclide parameters
        "nuclide": (3, 3),

        # Hamiltonian parameters
        "interaction": interaction,
        "use_coulomb": coulomb,
        "a_cm": 40.,
        "hw_cm": None,

        # input TBME parameters
        "truncation_int": truncation_int,
        "hw_int": hw,
        "truncation_coul": truncation_int,
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
            "Nmax": Nmax,
            "Nstep": 2,
            "M": M,
            },

        # diagonalization parameters
        "diagonalization": True,
        "eigenvectors": 15,
        "initial_vector": -2,
        "max_iterations": 200,
        "tolerance": 1e-6,
        "partition_filename": None,

        # obdme parameters
        ## "hw_for_trans": 20,
        "obdme_multipolarity": 2,
        # "obdme_reference_state_list": [(0.0, 0, 1)],
        "save_obdme": True,
        "ob_observable_sets": ['M1', 'E2'],

        # two-body observables
        "tb_observable_sets": ["H-components","am-sqr", "isospin"],
        # "tb_observable_sets": ["H-components"],
        "tb_observables": [
            ("CSU3",  (0,0,0), {"CSU3-U": 1/(6-1), "CSU3-V": 1.0}),
            ("CSp3R", (0,0,0), {"CSp3R-U": 1/(6-1), "CSp3R-V": 1.0}),
            ],

        # sources
        "obme_sources": [],
        "tbme_sources": [
            ("CSU3-U", {"filename": "CSU3-U-tb-6.bin", "qn": (0,0,0)}),
            ("CSU3-V", {"filename": "CSU3-V-tb-6.bin", "qn": (0,0,0)}),
            ("CSp3R-U", {"filename": "CSp3R-U-tb-6.bin", "qn": (0,0,0)}),
            ("CSp3R-V", {"filename": "CSp3R-V-tb-6.bin", "qn": (0,0,0)}),
        ],

        # wavefunction storage
        "save_wavefunctions": True,

        # version parameters
        "h2_format": 15099,
        "mfdn_executable": "v15-beta02/xmfdn-h2-lan",
        "mfdn_driver": ncci.mfdn_v15,
    })
    for (interaction,coulomb,truncation_int) in interaction_coulomb_truncation_list
    for Nmax in Nmax_list
    for M in M_list
    for hw in hw_list
]

################################################################
# run control
################################################################

# add task descriptor metadata field (needed for filenames)
# task["metadata"] = {
#     "descriptor": ncci.descriptors.task_descriptor_7(task)
#     }

# ncci.radial.set_up_interaction_orbitals(task)
# ncci.radial.set_up_orbitals(task)
# ncci.radial.set_up_xforms_analytic(task)
# ncci.radial.set_up_obme_analytic(task)
# ncci.tbme.generate_tbme(task)
# ncci.mfdn_v15.run_mfdn(task)
# ncci.postprocessing.evaluate_ob_observables(task)
# ncci.mfdn_v15.save_mfdn_task_data(task)
# ncci.handlers.task_handler_oscillator(task)

##################################################################
# task control
##################################################################

def task_pool(current_task):
    pool = "Nmax{truncation_parameters[Nmax]:02d}".format(**current_task)
    return pool

mcscript.task.init(
    tasks,
    task_descriptor=ncci.descriptors.task_descriptor_7,
    task_pool=task_pool,
    phase_handler_list=[ncci.handlers.task_handler_oscillator]
    )

################################################################
# termination
################################################################

mcscript.termination()
