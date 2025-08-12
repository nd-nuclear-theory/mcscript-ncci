""" runmfdncounting01.py

    See examples/README.md for full description.

    Patrick J. Fasano
    University of Notre Dame

    - 09/27/17 (pjf): Created, copied from runmfd07.
    - 12/19/17 (pjf): Update for mfdn->ncci rename.
    - 09/07/19 (pjf): Remove Nv from truncation_parameters.
    - 08/12/25 (seb): Rename and remove unneeded parameters.
"""

import mcscript
import mcscript.control
import mcscript.task

import mcscript.ncci as ncci
import mcscript.ncci.mfdn_v15

# initialize mcscript
mcscript.control.init()

##################################################################
# build task list
##################################################################

tasks = [{
    # nuclide parameters
    "nuclide": (2, 6),

    # basis parameters
    "basis_mode": ncci.modes.BasisMode.kDirect,
    "hw": 20.,

    # traditional oscillator many-body truncation
    "sp_truncation_mode": ncci.modes.SingleParticleTruncationMode.kNmax,
    "mb_truncation_mode": ncci.modes.ManyBodyTruncationMode.kNmax,
    "truncation_parameters": {
        "Nmax": 8,
        "Nstep": 2,
        "M": 0,
        },

    # version parameters
    "h2_format": 15099,
    "mfdn_executable": "xmfdn-h2-lan",
    "mfdn_driver": ncci.mfdn_v15
}]

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
        ncci.handlers.task_handler_nonzeros
        ]
    )

################################################################
# termination
################################################################

mcscript.control.termination()
