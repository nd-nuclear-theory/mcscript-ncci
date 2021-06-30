""" runmfdn07.py

    See runmfdn.txt for description.

    Mark A. Caprio
    University of Notre Dame

    - 06/08/17 (pjf): Created, copied from runmfd01; switch to MFDn v15.
    - 07/31/17 (pjf): Set MFDn driver module in task dictionary.
    - 08/11/17 (pjf): Update for split single-particle and many-body truncation modes.
    - 09/24/17 (pjf): Save wavefunctions.
    - 12/19/17 (pjf): Update for mfdn->ncci rename.
    - 09/07/19 (pjf): Remove Nv from truncation_parameters.
    - 09/11/19 (pjf): Fix task-data save.
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
    "example-data",
    "run0164-JISP16-ob-9",
    "run0164-JISP16-ob-13",
    "run0164-JISP16-tb-10",
    "run0164-JISP16-tb-20",
    "run0306-N2LOopt500",  # up to tb-20
    "runvc0083-Daejeon16-ob-13"
]

task = {
    # nuclide parameters
    "nuclide": (2, 2),

    # Hamiltonian parameters
    "interaction": "JISP16",
    "use_coulomb": True,
    "a_cm": 40.,
    "hw_cm": None,

    # input TBME parameters
    "truncation_int": ("tb", 6),
    "hw_int": 20.,
    "truncation_coul": ("tb", 6),
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
        "M": 0.,
        "Nmax": 6,
        "Nstep": 2,
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
    "obdme_reference_state_list": [(0, 0, 1)],
    "save_obdme": True,
    "ob_observable_sets": ['M1', 'E2'],

    # two-body observables
    ## "tb_observable_sets": ["H-components","am-sqr"],
    "tb_observable_sets": ["H-components", "am-sqr", "isospin"],
    "tb_observables": [],

    # version parameters
    "h2_format": 15099,
    "mfdn_executable": "v15-beta00/xmfdn-h2-lan",
    "mfdn_driver": ncci.mfdn_v15,

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
ncci.radial.set_up_xforms_analytic(task)
ncci.radial.set_up_obme_analytic(task)
ncci.tbme.generate_tbme(task)
ncci.mfdn_v15.run_mfdn(task)
ncci.mfdn_v15.save_mfdn_task_data(task)
ncci.postprocessing.evaluate_ob_observables(task)
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
