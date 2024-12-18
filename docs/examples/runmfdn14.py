"""runmfdn14.py

    Example Lanczos decomposition run using L^2 and S^2. Ensure that the output
    of runmfdn13.py is in the current NCCI_LIBRARY_PATH.

    See examples/README.md for full description.

    Debugging: Some tasks may intermittently fail.  This appears to be related
    to numerical issues in the presence of highly-degenerate 0 eigenvalues.

    Patrick J. Fasano
    University of Notre Dame

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
    "casimir-tb-6",
]

# decomposition coefficient paths
ncci.environ.decomposition_dir_list = [
    "decomposition-Z03-N03",
]

##################################################################
# run parameters
##################################################################

# nuclide
nuclide_list = [(3,3)]
A = sum(nuclide_list[0])  # assumes any nuclei in run are isobars

# interaction
interaction_coulomb_truncation_list = [
    ("Daejeon16", True, ("tb",6)),
    ## ("JISP16",    True, ("tb",6)),
]
hw_coul = 20.

# truncation parameters
Nmax_range = (2, 4, 2)
Nmax_list = mcscript.utils.value_range(*Nmax_range)

# hw
hw_range = (15, 20, 5)
hw_list = mcscript.utils.value_range(*hw_range)

# eigenvector convergence -- for source wave functions
max_iterations = 600
tolerance = 1e-6

# Lawson
a_cm = 50.

# decomposition
wf_run_dir = "mfdn13"
qn_list_by_Nmax={
    # quantum numbers (J,g,n) for states to decompose at each Nmax
    Nmax: [
        (1.0,0,1),
        (3.0,0,1),
        (0.0,0,1),
    ]
    for Nmax in Nmax_list
}
def wf_source_M(qn):
    """ M value for source wave function to use (for given state).
    """
    J, g, n = qn
    if int(2*J)%2:
        # odd half-integer
        M = 1/2
    else:
        # even half-integer
        M = (0.0 if J==0.0 else 1.0)
    return M
decomposition_type_list = ["L", "S", "Nex", "U3SpSnS"]
decomposition_max_iterations = 1200

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
        "a_cm": 40.,
        "hw_cm": None,

        # decomposition
        "hamiltonian": ncci.decomposition.decomposition_operator(nuclide,Nmax,hw,decomposition_type,verbose=False),
        "decomposition_type": decomposition_type,
        "source_wf_qn": qn,
        "wf_source_info": {
            "run": wf_run_dir,
            "nuclide": nuclide,
            "interaction": interaction,
            "use_coulomb": coulomb,
            "hw": hw,
            "truncation_parameters": {
                "M": wf_source_M(qn),
                "Nmax": Nmax
            },
            "a_cm": a_cm,
            "max_iterations": max_iterations,
            "tolerance": tolerance,
            "descriptor": ncci.descriptors.task_descriptor_7,
            # required modes to keep task descriptor function happy
            "basis_mode": ncci.modes.BasisMode.kDirect,
            "sp_truncation_mode": ncci.modes.SingleParticleTruncationMode.kNmax,
            "mb_truncation_mode": ncci.modes.ManyBodyTruncationMode.kNmax,
        },

        ## # input TBME parameters
        ## "truncation_int": truncation_int,
        ## "hw_int": hw,
        ## "truncation_coul": truncation_int,
        ## "hw_coul": 20.,
        ## "save_tbme": False,

        # input TBME parameters -- TO PRUNE? are these needed for decomposition?
        "truncation_int": truncation_int,  # used in constructing orbital truncation
        "truncation_coul": ("tb", 20),  # used in constructing an irrelevant orbital truncation in "use_coulomb"=True in the task dictionary, from the underlying wf run

        # basis parameters
        "basis_mode": ncci.modes.BasisMode.kDirect,
        "hw": hw,

        # one-body and many-body truncation
        "sp_truncation_mode": ncci.modes.SingleParticleTruncationMode.kNmax,
        "mb_truncation_mode": ncci.modes.ManyBodyTruncationMode.kNmax,
        "truncation_parameters": {
            "M": wf_source_M(qn),
            "Nmax": Nmax,
            "Nstep": 2
        },

        # diagonalization parameters
        "diagonalization": True,
        "max_iterations": decomposition_max_iterations,
        "tolerance": 0,  # iterate to max iterations
        "partition_filename": None,

        # obdme parameters
        "calculate_obdme": False,

        # sources
        "tbme_sources": [
            ("CSU3-U", {"filename": "CSU3-U-tb-6.bin", "qn": (0,0,0)}),
            ("CSU3-V", {"filename": "CSU3-V-tb-6.bin", "qn": (0,0,0)}),
            ("CSp3R-U", {"filename": "CSp3R-U-tb-6.bin", "qn": (0,0,0)}),
            ("CSp3R-V", {"filename": "CSp3R-V-tb-6.bin", "qn": (0,0,0)}),
        ],

        # version parameters
        "h2_format": 15099,
        "mfdn_executable": "xmfdn-h2-lan",
        "mfdn_driver": ncci.mfdn_v15,
    }
    for nuclide in nuclide_list
    for Nmax in Nmax_list
    for (interaction,coulomb,truncation_int) in interaction_coulomb_truncation_list
    for hw in hw_list
    for qn in qn_list_by_Nmax[Nmax]
    for decomposition_type in decomposition_type_list
]

##################################################################
# task dictionary postprocessing functions
##################################################################

def task_pool(current_task):
    ## pool = "Nmax{truncation_parameters[Nmax]:02d}-M{truncation_parameters[M]:.1f}".format(**current_task)
    pool = "Nmax{truncation_parameters[Nmax]:02d}".format(**current_task)
    return pool

##################################################################
# task control
##################################################################

mcscript.task.init(
    tasks,
    task_descriptor=ncci.descriptors.task_descriptor_decomposition_2,
    task_pool=task_pool,
    phase_handler_list=ncci.handlers.task_handler_mfdn_decomposition_phases,
    archive_phase_handler_list=[ncci.handlers.archive_handler_mfdn_hsi],
)

################################################################
# termination
################################################################

mcscript.control.termination()
