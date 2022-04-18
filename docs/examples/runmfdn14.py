""" runmfdn14.py

    Example Lanczos decomposition run using L^2 and S^2. Ensure that the output
    of runmfdn13.py is in the current NCCI_LIBRARY_PATH.

    See examples.md for full description.

    Patrick J. Fasano
    University of Notre Dame
"""

import collections

import mcscript
import ncci
import ncci.mfdn_v15

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

# nuclide
nuclide = (3, 3)

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

# M
M_list = [0.0, 1.0]

# states to be decomposed
qn_list_by_Nmax={
    Nmax: [
        (1.0,0,1),
        (3.0,0,1),
        (0.0,0,1),
    ]
    for Nmax in Nmax_list
}

# decomposition operators
decomposition_operator_by_name={
    "L2": lambda nuclide, hw, **kwargs: ncci.operators.tb.L2(),
    "S2": lambda nuclide, hw, **kwargs: ncci.operators.tb.S2(),
    "Nex": lambda nuclide, hw, **kwargs: ncci.operators.tb.Nex(nuclide, hw),
}

tasks = [
    collections.OrderedDict({
        # nuclide parameters
        "nuclide": nuclide,

        # Hamiltonian parameters -- for descriptor
        "interaction": interaction,
        "use_coulomb": coulomb,
        "a_cm": 40.,
        "hw_cm": None,

        # decomposition
        "hamiltonian": decomposition_operator_function(
            nuclide=nuclide, Nmax=Nmax, hw=hw
        ),
        "decomposition_operator_name": decomposition_operator_name,
        "source_wf_qn": qn,
        "wf_source_info": {
                "run": "mfdn13",
                "nuclide": nuclide,
                "interaction": interaction,
                "use_coulomb": coulomb,
                "hw": hw,
                "truncation_parameters": {
                    "M": M,
                    "Nmax": Nmax
                },
                "a_cm": 40.,
                "max_iterations": 200,
                "tolerance": 1e-6,
                # required modes to keep task descriptor function happy
                "sp_truncation_mode": ncci.modes.SingleParticleTruncationMode.kNmax,
                "mb_truncation_mode": ncci.modes.ManyBodyTruncationMode.kNmax,
                "basis_mode": ncci.modes.BasisMode.kDirect,
                "descriptor": ncci.descriptors.task_descriptor_7
            },

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
        "eigenvectors": 0,
        "initial_vector": -2,
        "max_iterations": 800,
        "tolerance": 0,
        "partition_filename": None,

        # obdme parameters
        "calculate_obdme": False,

        # wavefunction storage
        "save_wavefunctions": False,

        # version parameters
        "h2_format": 15099,
        "mfdn_executable": "v15-beta02/xmfdn-h2-lan",
        "mfdn_driver": ncci.mfdn_v15,
    })
    for (interaction,coulomb,truncation_int) in interaction_coulomb_truncation_list
    for Nmax in Nmax_list
    for M in M_list
    for hw in hw_list
    for qn in qn_list_by_Nmax[Nmax]
    for (decomposition_operator_name,decomposition_operator_function) in decomposition_operator_by_name.items()
    if qn[0]>=abs(M)
]

##################################################################
# task control
##################################################################

def task_pool(current_task):
    ## pool = "Nmax{truncation_parameters[Nmax]:02d}".format(**current_task)
    pool = "Nmax{truncation_parameters[Nmax]:02d}-M{truncation_parameters[M]:.1f}".format(**current_task)
    return pool

mcscript.task.init(
    tasks,
    task_descriptor=ncci.descriptors.task_descriptor_decomposition_1,
    task_pool=task_pool,
    phase_handler_list=[
        ncci.handlers.task_handler_oscillator_pre,
        ncci.handlers.task_handler_oscillator_mfdn_decomposition
        ],
    archive_phase_handler_list=[],
    )

################################################################
# termination
################################################################

mcscript.termination()
