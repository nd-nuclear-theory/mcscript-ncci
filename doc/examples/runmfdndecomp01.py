"""runmfdndecomp01.py

    "Bare bones" example of Lanczos decomposition with MFDn, for an explicitly
    specified operator (i.e., not using predefined "decomposition types").

    Decomposition is by the total number of oscillator quanta in the NCCI
    configuration, that is, by the Ntot operator.  Then the Nex operator (which
    differs by a constant) is taken for comparison.

    We also only demonstrate the simplest (but least convenient) way of
    specifying the source wave function to decompose, that is, by manually
    specifying the run
  
       "mfdn13"

    and the descriptor within that run

       "Z3-N3-Daejeon16-coul1-hw15.000-a_cm50-Nmax04-Mj1.0-lan600-tol1.0e-06"


    This example accompanies the decomposition tutorial
    decomposition-tutorial.md.

    Ensure that the wave function and task data results of runmfdn13.py are in
    the current NCCI_LIBRARY_PATH.

    See examples/README.md for full description.

    Debugging: Some tasks may intermittently fail.  This appears to be related
    to numerical issues in the presence of highly-degenerate 0 eigenvalues.

    Mark A. Caprio
    University of Notre Dame

    03/27/25 (mac): Created from runmfdn14.
    07/21/25 (mac): Switch to wf selection by "wf_source_runs" and "wf_source_selector".

"""

import mcscript
import mcscript.control
import mcscript.task
import mcscript.utils

import mcscript.ncci as ncci
import mcscript.ncci.mfdn_v15
import mcscript.ncci.decomposition

# initialize mcscript
mcscript.control.init()


##################################################################
# environment
##################################################################

# TBME paths (for operators used in decompositions)
ncci.environ.operator_dir_list = [
]

# decomposition coefficient paths
ncci.environ.decomposition_dir_list = [
]

##################################################################
# run parameters
##################################################################

# nuclide
nuclide = (3,3)
A = sum(nuclide)

# interaction
interaction_coulomb_truncation_list = [
    ("Daejeon16", True, ("tb",6)),
]
hw_coul = 20.

# truncation parameters
Nmax_range = (4, 4, 2)
Nmax_list = mcscript.utils.value_range(*Nmax_range)

# hw
hw_range = (15, 15, 5)
hw_list = mcscript.utils.value_range(*hw_range)

# decomposition
wf_run_dir = "mfdn13"
qn = (1.0,0,1)
M = 1.0
## decomposition_type = "Ntot"
decomposition_type_list = ["Ntot", "Nex"]
## decomposition_max_iterations = 1200  # TODO (mac): Reduce (to make example run faster) and update tutorial.
decomposition_max_iterations = 100

##################################################################
# build task list
##################################################################

tasks = [
    {
        # nuclide parameters
        "nuclide": nuclide,

        # Hamiltonian parameters -- for descriptor
        "interaction": interaction,
        "use_coulomb": coulomb,

        # input TBME parameters
        "truncation_int": truncation_int,  # used in constructing orbital truncation
        "truncation_coul": ("tb", 20),  # used in constructing an irrelevant orbital truncation, if "use_coulomb"=True in the task dictionary, from the underlying wf run

        # basis parameters
        "basis_mode": ncci.modes.BasisMode.kDirect,
        "hw": hw,

        # one-body and many-body truncation
        "sp_truncation_mode": ncci.modes.SingleParticleTruncationMode.kNmax,
        "mb_truncation_mode": ncci.modes.ManyBodyTruncationMode.kNmax,
        "truncation_parameters": {
            "M": M,
            "Nmax": Nmax,
            "Nstep": 2
        },

        # diagonalization parameters
        "max_iterations": decomposition_max_iterations,
        "partition_filename": None,

        # decomposition
        ## "hamiltonian": ncci.operators.tb.Ntotal(A, hw),
        "hamiltonian": (
            ncci.operators.tb.Ntotal(A, hw)  # Ntot
            if decomposition_type=="Ntot" else
            ncci.operators.tb.Nex(nuclide, hw)  # Nex
        ),
        "decomposition_type": decomposition_type,
        "decomposition_qn": qn,

        # wf source selection
        "wf_source_run_list": ["mfdn13"],
        "wf_source_selector": {
            "nuclide": nuclide,
            "interaction": interaction,
            "hw": hw,
            "Nmax": Nmax,
            "M": M,
            },

        # obdme parameters
        "calculate_obdme": False,
        
        # version parameters
        "h2_format": 15099,
        "mfdn_executable": "xmfdn-h2-lan",
        "mfdn_driver": ncci.mfdn_v15,
    }
    ## for nuclide in nuclide_list
    for Nmax in Nmax_list
    for (interaction,coulomb,truncation_int) in interaction_coulomb_truncation_list
    for hw in hw_list
    ## for qn in qn_list
    for decomposition_type in decomposition_type_list
]


##################################################################
# task dictionary postprocessing functions
##################################################################

def task_pool(task):
    ## pool = "Nmax{truncation_parameters[Nmax]:02d}-M{truncation_parameters[M]:.1f}".format(**task)
    pool = "Nmax{truncation_parameters[Nmax]:02d}".format(**task)
    return pool


##################################################################
# task control
##################################################################

mcscript.task.init(
    tasks,
    task_descriptor=ncci.descriptors.task_descriptor_7_decomposition,
    task_pool=task_pool,
    phase_handler_list=ncci.handlers.task_handler_mfdn_decomposition_phases,
    archive_phase_handler_list=[ncci.handlers.archive_handler_mfdn_hsi],
)


################################################################
# termination
################################################################

mcscript.control.termination()
