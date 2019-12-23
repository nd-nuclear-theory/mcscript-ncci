""" runmfdn14.py

    Example run with two-body transitions. See runmfdn.txt for full description.

    Patrick J. Fasano, Mark A. Caprio
    University of Notre Dame

    - 10/11/19 (pjf): Created, copied from runmfd13.
"""

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
    "run0164-JISP16-ob-9",
    "run0164-JISP16-ob-13",
    "run0164-JISP16-tb-10",
    "run0164-JISP16-tb-20",
    "run0306-N2LOopt500",  # up to tb-20
    "runvc0083-Daejeon16-ob-13"
]

ncci.environ.operator_dir_list = [
    "symplectic-casimir"
]

task = {
    # nuclide parameters
    "nuclide": (3, 3),

    # Hamiltonian parameters
    "interaction": "JISP16",
    "use_coulomb": True,
    "a_cm": 40.,
    "hw_cm": None,

    # input TBME parameters
    "truncation_int": ("tb", 10),
    "hw_int": 20.,
    "truncation_coul": ("tb", 10),
    "hw_coul": 20.,

    # basis parameters
    "basis_mode": ncci.modes.BasisMode.kDirect,
    "hw": 20.,

    # transformation parameters
    "xform_truncation_int": None,
    "xform_truncation_coul": None,
    "hw_coul_rescaled": None,
    "target_truncation": None,

    # traditional oscillator many-body truncation
    "sp_truncation_mode": ncci.modes.SingleParticleTruncationMode.kNmax,
    "mb_truncation_mode": ncci.modes.ManyBodyTruncationMode.kNmax,
    "truncation_parameters": {
        "M": 1.0,
        "Nmax": 6,
        "Nstep": 2,
        },

    # diagonalization parameters
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
    "ob_observables": [('M', 1), ('E', 2)],

    # two-body observables
    ## "observable_sets": ["H-components","am-sqr"],
    "observable_sets": ["H-components"],
    "tb_observables": [
        ("CSp3R", (0,0,0), {"CSp3R-U": 0.5, "CSp3R-V": 1.0}),
        ("UM1", (1,0,0), {
            "U[Dl1p]": 1.0, "U[Ds1p]": 5.585694713, "U[Ds1n]": -3.82608545
        }),
        ("UE2", (2,0,0), {"U[E2p]": 1.0})
        ],
    "tb_transitions": [
        ((2,0,1), [(1,0,1), (2,0,1), (2,0,2)])
    ],
    # sources
    "obme_sources": [
        ("Dl1p", {"filename": ncci.environ.observable_me_filename("", "Dl", 1, "p"), "qn": (1,0,0)}),
        ("Dl1n", {"filename": ncci.environ.observable_me_filename("", "Dl", 1, "n"), "qn": (1,0,0)}),
        ("Ds1p", {"filename": ncci.environ.observable_me_filename("", "Ds", 1, "p"), "qn": (1,0,0)}),
        ("Ds1n", {"filename": ncci.environ.observable_me_filename("", "Ds", 1, "n"), "qn": (1,0,0)}),
        ("E2p",  {"filename": ncci.environ.observable_me_filename("", "E", 2, "p"), "qn": (2,0,0)}),
    ],
    "tbme_sources": [
        ("CSp3R-U", (0,0,0), {"filename": "tbme-CSp3R-U.bin"}),
        ("CSp3R-V", (0,0,0), {"filename": "tbme-CSp3R-V.bin"}),
    ],

    # wavefunction storage
    "save_wavefunctions": True,

    # version parameters
    "h2_format": 15099,
    "mfdn_executable": "v15-beta00/xmfdn-h2-lan",
    "mfdn_driver": ncci.mfdn_v15,
    "mfdn-transitions_executable": "aae547b/xtransitions"
}

################################################################
# run control
################################################################

# add task descriptor metadata field (needed for filenames)
task["metadata"] = {
    "descriptor": ncci.descriptors.task_descriptor_7(task)
    }

ncci.radial.set_up_interaction_orbitals(task)
ncci.radial.set_up_orbitals(task)
ncci.radial.set_up_radial_analytic(task)
ncci.tbme.generate_diagonalization_tbme(task)
ncci.mfdn_v15.run_mfdn(task)
task["h2_format"] = 15200
ncci.postprocessing.generate_em(task)
ncci.tbme.generate_observable_tbme(task)
ncci.postprocessing.run_mfdn_transitions(task)
# ncci.mfdn_v15.save_mfdn_task_data(task)
# ncci.postprocessing.evaluate_ob_observables(task)
# ncci.handlers.task_handler_oscillator(task)

##################################################################
# task control
##################################################################

## mcscript.task.init(
##     tasks,
##     task_descriptor=ncci.descriptors.task_descriptor_7,
##     task_pool=task_pool,
##     phase_handler_list=[ncci.handlers.task_handler_oscillator]
##     )

################################################################
# termination
################################################################

mcscript.termination()
