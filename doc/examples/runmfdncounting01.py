""" runmfdncounting01.py

    See examples.md for full description.

    Patrick J. Fasano
    University of Notre Dame

    - 09/27/17 (pjf): Created, copied from runmfd07.
    - 12/19/17 (pjf): Update for mfdn->ncci rename.
    - 09/07/19 (pjf): Remove Nv from truncation_parameters.
    - 08/12/25 (seb): Rename and remove unneeded parameters.
    - 08/19/25 (mac):
      + Change example nuclide to 6Li (matching runmfdn13).
      + Add post phase to save wf indexing files.
"""

import mcscript
import mcscript.control
import mcscript.task

import mcscript.ncci as ncci
import mcscript.ncci.mfdn_v15

# initialize mcscript
mcscript.control.init()

# truncation parameters
Nmax_range = (2, 4, 2)
Nmax_list = mcscript.utils.value_range(*Nmax_range)
M_list = [0.0, 1.0]

##################################################################
# build task list
##################################################################

tasks = [
    {
        # nuclide parameters
        "nuclide": (3, 3),

        # basis parameters
        "basis_mode": ncci.modes.BasisMode.kDirect,
        
        # single-particle and many-body bases
        "sp_truncation_mode": ncci.modes.SingleParticleTruncationMode.kNmax,
        "mb_truncation_mode": ncci.modes.ManyBodyTruncationMode.kNmax,
        "truncation_parameters": {
            "Nmax": Nmax,
            "Nstep": 2,
            "M": M,
        },

        # wavefunction storage -- save mfdn_smwf.info and mfdn_MBgroups files
        "save_wavefunctions": False,
        
        # version parameters
        "h2_format": 15099,
        "mfdn_executable": "xmfdn-h2-lan",
        "mfdn_driver": ncci.mfdn_v15
    }
    for M in M_list
    for Nmax in Nmax_list
]

##################################################################
# task dictionary postprocessing functions
##################################################################

def task_pool(current_task):
    pool = "Nmax{truncation_parameters[Nmax]:02d}-M{truncation_parameters[M]:3.1f}".format(**current_task)
    return pool


##################################################################
# task control
##################################################################

mcscript.task.init(
    tasks,
    task_descriptor=ncci.descriptors.task_descriptor_c1,
    task_pool=task_pool,
    phase_handler_list=[
        ncci.handlers.task_handler_dimension,
        ncci.handlers.task_handler_nonzeros,
        ncci.handlers.task_handler_mfdn_post,
    ]
    )

################################################################
# termination
################################################################

mcscript.control.termination()
