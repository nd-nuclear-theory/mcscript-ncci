# This is a code to test if both mfdn.input and menj.par file are created using mfdn_v15.py

# This code is adapted from runmfdn13.py
# -9/13/2023 (slv): Made the following changes to the Input parameters specific to calling menj extension of MFDn
#    + Created ncci.modes.VariantMode.kMENJ as a mode to differ from h2 mode
#      This will be used to construct the appropriate descriptor
#    + The following task dictionary keys are deprecated for MENJ
#      use_coulomb, hw_cm, NN, TrelID, RsqID 
#    + Rename NNN to use_3n
#    + Hardcode TRel and Rsq file id
# -10/2/2023 (slv): Changed a_cm to 60 so that lamHcm = 3.0

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
alpha =[625] # can be [625, 400]
# Lawson
a_cm = 60.

##################################################################
# build task list
##################################################################

tasks = [{
        # nuclide parameters

        "nuclide": nuclide,

        # Hamiltonian parameters
        "interaction": "EntemMachleidt",

        "a_cm": a_cm,

        # Flag to enable menj
        #"menj_enabled":True, # MODE VARIABLE AS kMENJ
        #mfdn_variant": ncci.modes.VariantMode.kH2,
        "mfdn_variant": ncci.modes.VariantMode.kMENJ,
    
        
        # parameters for menj.par
        
        "EMax" : 12, # NOT REQUIRED IN THE DESCRIPTOR
        "me2j_file_id" : "chi2b_srg{:04d}".format(a),  # NAME??
        "use_3b" : False,
        "E3Max" : 12, # "N3_max", "N3max", "E3_max"???   how will this appear in the descriptor?
        "me3j_file_id" : "chi2b3b_srg{:04d}ho40C".format(a),  # NAME??
        # relation of MEID and ME3ID to interaction?  Is a dummy ok for ME3ID if use_3n=False???
        # and how will we reflect that in the interaction name used in the descriptor?

        # basis parameters
        "basis_mode": ncci.modes.BasisMode.kDirect, 
        "hw": hw,

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
        #"tb_observable_sets": ["H-components","am-sqr", "isospin"],
        # "tb_observable_sets": ["H-components"],
        # "tb_observables": [
           # ("CSU3",  (0,0,0), {"CSU3-U": 1/(A-1), "CSU3-V": 1.0}),
           # ("CSp3R", (0,0,0), {"CSp3R-U": 1/(A-1), "CSp3R-V": 1.0}),
           # ],

        # sources
        "obme_sources": [],
        "tbme_sources": [],

        # wavefunction storage
        "save_wavefunctions": True,

        # version parameters
        "h2_format": 15099,
        # This should be changed to proper executable
        "mfdn_executable": "xmfdn-menj-lan",
        "mfdn_driver": ncci.mfdn_v15,
    }
    for a in alpha
    for nuclide in nuclide_list
]   

"""
##################################################################
# Test generate mfdn input
##################################################################

ncci.mfdn_v15.generate_menj_par(tasks)

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
    task_descriptor=ncci.descriptors.task_descriptor_menj,
    task_pool=task_pool,
    phase_handler_list=ncci.handlers.task_handler_mfdn_phases,
    )

################################################################
# termination
################################################################

mcscript.termination()

