# This is a code to test if both mfdn.input and menj.par file are created using mfdn_v15.py

# This code is adapted from runmfdn13.py


import mcscript
import ncci
import ncci.mfdn_v15

mcscript.init()
##################################################################
# environment
##################################################################

# TBME paths
ncci.environ.interaction_dir_list = [
    "example-data",
]
ncci.environ.operator_dir_list = [
    "example-data"
]

##################################################################
# run parameters
##################################################################

# nuclide
nuclide_list = [(3,3)]
A = sum(nuclide_list[0])  # assumes any nuclei in run are isobars

# interaction
# interaction_coulomb_truncation_list = [
#     ("Daejeon16", True, ("tb",6)),
#     ("JISP16",    True, ("tb",6)),
# ]

hw_coul = 20.

# truncation parameters
# Nmax_range = (2, 4, 2)
# Nmax_list = mcscript.utils.value_range(*Nmax_range)
# M_list = [0.0, 1.0]
M = 0

# hw
# hw_range = (15, 20, 5)
# hw_list = mcscript.utils.value_range(*hw_range)

hw = 20

# eigenvector convergence
eigenvectors = 4
max_iterations = 600
tolerance = 1e-6

# Lawson
a_cm = 50.

##################################################################
# build task list
##################################################################

tasks = {
        # nuclide parameters
        "nuclide": nuclide_list[0],

        # Hamiltonian parameters
        # "interaction": interaction,
        # "use_coulomb": coulomb,
        "a_cm": a_cm,
        "hw_cm": None,

        # input TBME parameters
        # "truncation_int": truncation_int,
        "hw_int": hw,
        # "truncation_coul": truncation_int,
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
            "Nmax": 2,
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
        ## "hw_for_trans": 20,
        "obdme_multipolarity": 2,
        # "obdme_reference_state_list": [(0.0, 0, 1)],
        "save_obdme": True,
        "ob_observable_sets": ['M1', 'E2'],

        # two-body observables
        "tb_observable_sets": ["H-components","am-sqr", "isospin"],
        # "tb_observable_sets": ["H-components"],
        # "tb_observables": [
           # ("CSU3",  (0,0,0), {"CSU3-U": 1/(A-1), "CSU3-V": 1.0}),
           # ("CSp3R", (0,0,0), {"CSp3R-U": 1/(A-1), "CSp3R-V": 1.0}),
           # ],

        # sources
        "obme_sources": [],
        "tbme_sources": [
            # ("CSU3-U", {"filename": "CSU3-U-tb-6.bin", "qn": (0,0,0)}),
            # ("CSU3-V", {"filename": "CSU3-V-tb-6.bin", "qn": (0,0,0)}),
            # ("CSp3R-U", {"filename": "CSp3R-U-tb-6.bin", "qn": (0,0,0)}),
            # ("CSp3R-V", {"filename": "CSp3R-V-tb-6.bin", "qn": (0,0,0)}),
            ("chi2b_srg0625", {"filename": "chi2b_srg0625_eMax12_EMax12_hwHO020.me2j.bin", "qn":(0,0,0)}),
            ("trel",{"filename": "trel_eMax12_EMax12.me2j.bin", "qn":(0,0,0)}),
            ("rsq",{"filename": "rsq_eMax12_EMax12.me2j.bin", "qn":(0,0,0)}),
            ("chi2b3b_srg0625ho40C",{"filename": "chi2b3b_srg0625ho40C_eMax12_EMax12_hwHO020.me3j.bin","qn":(0,0,0)}),
        ],

        # Flag to enable menj
        "menj_enabled":True,
        
        # parameters for menj.par
        # "lamHcm" : 3.0,
        "NN" : 1,
        "EMax" : 12,
        "MEID" : "chi2b_srg0625",
        "TrelID" : "trel",
        "RsqID" : "rsq",
        "NNN" : 0,
        "E3Max" : 12,
        "ME3ID" : "chi2b3b_srg0625ho40C",

        # wavefunction storage
        "save_wavefunctions": True,

        # version parameters
        "h2_format": 15099,
        # This should be changed to proper executable
        "mfdn_executable": "xmfdn-menj-lan",
        "mfdn_driver": ncci.mfdn_v15,
    }

"""
##################################################################
# Test generate mfdn input
##################################################################

ncci.mfdn_v15.generate_mfdn_input(tasks)

"""

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
    )

################################################################
# termination
################################################################

mcscript.termination()
