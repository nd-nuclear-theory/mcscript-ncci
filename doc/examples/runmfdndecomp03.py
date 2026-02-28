"""runmfdndecomp03.py

    Example Lanczos decomposition runs with wave function truncation.

    Add `mcscript-ncci/docs/examples` to NCCI_DATA_DIR_H2 to ensure that this
    script can find the relevant h2 files.

    Example invocation:

        qsubm mfdndecomp03 --toc
    
        qsubm mfdndecomp03 --pool="*" --serialthreads=8 --phase=0
    
        qsubm mfdndecomp03 --pool=Nmax02 --threads=8 --ranks=1 --phase=1
    
        qsubm mfdndecomp03 --pool=Nmax04 --threads=8 --ranks=1 --phase=1
    
        ## qsubm mfdndecomp03 --pool=Nmax04 --threads=1 --ranks=6 --phase=1
    
        qsubm mfdndecomp03 --pool="*" --phase=2

    Requires previously running:

        runmfdn17 -- to provide wave functions

        runmfdncounting02 -- to provide truncation template info
 
    Ensure that the run directories for these runs are in the current NCCI_LIBRARY_PATH.

    See examples/README.md for full description.

    Mark A. Caprio
    University of Notre Dame

    02/19/26 (mac): Created, from runmfdndecomp02.

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
    "Z03-N03",
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
]
hw_coul = 20.

# truncation parameters
source_Nmax_range = (2, 4, 2)
source_Nmax_list = mcscript.utils.value_range(*source_Nmax_range)
Nmax_orb = 5
num_segments_by_Nmax = {
    2: 1,
    4: 1,  # 3
}

# hw
hw_range = (15, 15, 5)
hw_list = mcscript.utils.value_range(*hw_range)

# decomposition
wf_source_run_list = ["mfdn17"]
qn_list_by_source_Nmax={
    # quantum numbers (J,g,n) for states to decompose at each Nmax
    source_Nmax: [
        (1.0,0,1),
    ]
    for source_Nmax in source_Nmax_list
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
decomposition_type_list = ["Nex", "U3SpSnS"]
decomposition_max_iterations = 100
decomposition_Nmax_list = [2, 4]
decomposition_truncation_template_run = "mfdncounting02"

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

        # decomposition
        "hamiltonian": ncci.decomposition.decomposition_operator(nuclide,decomposition_Nmax,hw,decomposition_type,verbose=False),
        "decomposition_type": decomposition_type,

        # wf selection
        "wf_source_run_list": wf_source_run_list,
        "wf_source_selector": {
            "nuclide": nuclide,
            "interaction": interaction,
            "hw": hw,
            "Nmax": source_Nmax,
            "M": wf_source_M(qn),
            },
        "wf_qn": qn,

        # decomposition truncation model wf selection
        "truncation_model_info": {
            "run": decomposition_truncation_template_run,
            ##"nuclide": nuclide,  # INHERITED
            "truncation_parameters": {
                "M": wf_source_M(qn),
                "Nmax": decomposition_Nmax,
                "Nmax_orb": Nmax_orb,
            },
            "descriptor": ncci.descriptors.task_descriptor_c1,
            # required modes to keep task descriptor function happy
            "basis_mode": ncci.modes.BasisMode.kDirect,
            "sp_truncation_mode": ncci.modes.SingleParticleTruncationMode.kNmax,
            "mb_truncation_mode": ncci.modes.ManyBodyTruncationMode.kNmax,
        },
        
        # input TBME parameters
        "truncation_int": truncation_int,  # used in constructing orbital truncation
        "truncation_coul": ("tb", 20),  # used in constructing an irrelevant orbital truncation, if "use_coulomb"=True in the task dictionary, from the underlying wf run

        # basis parameters
        "basis_mode": ncci.modes.BasisMode.kDirect,
        "hw": hw,

        # one-body and many-body truncation
        #
        # Parameters here (for mfdn run) should match those for decomposition truncation model.
        "sp_truncation_mode": ncci.modes.SingleParticleTruncationMode.kNmax,
        "mb_truncation_mode": ncci.modes.ManyBodyTruncationMode.kNmax,
        "truncation_parameters": {
            "M": wf_source_M(qn),
            "Nmax": decomposition_Nmax,
            "Nstep": 2,
            "Nmax_orb": Nmax_orb,
        },
        "num_segments": num_segments_by_Nmax[decomposition_Nmax],
        
        # diagonalization parameters
        "max_iterations": decomposition_max_iterations,

        # sources
        "tbme_sources": [
            ("CSU3-U", {"filename": "CSU3-U-tb-6.bin", "qn": (0,0,0)}),
            ("CSU3-V", {"filename": "CSU3-V-tb-6.bin", "qn": (0,0,0)}),
        ],

        # version parameters
        "h2_format": 15099,
        "mfdn_executable": "xmfdn-h2-lan",
        "mfdn_driver": ncci.mfdn_v15,
    }
    for nuclide in nuclide_list
    for source_Nmax in source_Nmax_list
    for decomposition_Nmax in decomposition_Nmax_list
    if decomposition_Nmax <= source_Nmax
    for (interaction,coulomb,truncation_int) in interaction_coulomb_truncation_list
    for hw in hw_list
    for qn in qn_list_by_source_Nmax[source_Nmax]
    for decomposition_type in decomposition_type_list
]

##################################################################
# task dictionary postprocessing functions
##################################################################

def task_pool(task):
    # pool should be set by *truncated* Nmax, since that determines requires computing resources
    pool = "Nmax{truncation_model_info[truncation_parameters][Nmax]:02d}".format(**task)
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
