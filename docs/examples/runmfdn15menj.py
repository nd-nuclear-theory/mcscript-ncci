"""runmfdn15menj.py

qsubm --toc mfdn15menj
qsubm mfdn15menj --phase=0 --pool="Nmax02"
qsubm mfdn15menj debug 10 --phase=1 --pool="Nmax02" --ranks=1 --nodes=1 --threads=32
qsubm mfdn15menj --phase=2 --pool="Nmax02"
export NCCI_DATA_DIR_H2=${GROUP_HOME}/data/menj/lenpic-sms

"""
import os

import mcscript
import mcscript.control
import mcscript.task
import mcscript.utils

import mcscript.ncci as ncci
import mcscript.ncci.mfdn_v15


# initialize mcscript
mcscript.control.init()

##################################################################
# environment
##################################################################

# TBME paths
ncci.environ.interaction_dir_list = [
    "me2j_smsi",
    "me3j_smsi",
]
ncci.environ.operator_dir_list = [
]

##################################################################
# run parameters
##################################################################

# nuclide
nuclide_list = [(3,3)]
A = sum(nuclide_list[0])  # assumes any nuclei in run are isobars

M = 0

# truncation parameters
Nmax_range = (2, 2, 2)
Nmax_list = mcscript.utils.value_range(*Nmax_range)

# hw
hw_list = [24]

# eigenvector convergence
eigenvectors = 4
max_iterations = 600
tolerance = 1e-6
alpha_list =[400]
# Lawson
a_cm = 60.

tasks = [{
        # nuclide parameters

        "nuclide": nuclide,

        # Lawson
        "a_cm": a_cm,

        # flag to enable menj
        "mfdn_variant": ncci.modes.VariantMode.kMENJ,

        # interaction override: user defined interaction for descriptors
        # "interaction", if not user defined, will be "me2j_file_id"(+"ME3J"+"me3j_file_id" if use_3b is True) by default
        # "interaction": "LENPIC_2C_srg{:04d}".format(alpha),

        # parameters for menj.par
        "EMax" : 16, # Nmax for 2b interaction file
        "me2j_file_id" : "chi2bSMSI2C_srg{:04d}".format(alpha),
        "use_3b" : True, # choose whether to use 3-body
        "E3Max" : 14, # Nmax for 3b interaction file
        "me3j_file_id" : "chi2bSMSI2C_nocd_srg{:04d}ho40J_hwc036".format(alpha),

        # basis parameters
        "basis_mode": ncci.modes.BasisMode.kDirect,
        "hw": hw,

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
        "eigenvectors": eigenvectors,
        "initial_vector": -2,
        "max_iterations": max_iterations,
        "tolerance": tolerance,
        "partition_filename": None,

        # obdme parameters
        "obdme_multipolarity": 2,
        "save_obdme": True,

        # wavefunction storage
        "save_wavefunctions": True,

        # This should be changed to proper executable
        "mfdn_executable": "xmfdn-menj-lan",
        "mfdn_driver": ncci.mfdn_v15,
    }
    for alpha in alpha_list
    for nuclide in nuclide_list
    for Nmax in Nmax_list
    for hw in hw_list
]


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
    archive_phase_handler_list=[ncci.handlers.archive_handler_mfdn_hsi],
    )

################################################################
# termination
################################################################

mcscript.control.termination()

