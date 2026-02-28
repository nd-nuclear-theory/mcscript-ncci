"""runmfdncounting02.py

    Example "counting" run to generate template wave function indexing files.

    See examples.md for full description.

    Example invocation:

        qsubm mfdncounting02 --toc

        qsubm mfdncounting02 --pool="Nmax02-M*-n*" --threads=8 --phase=0

        qsubm mfdncounting02 --pool="Nmax04-M*-n001" --threads=1 --phase=0

        qsubm mfdncounting02 --pool="Nmax04-M*-n003" --threads=1 --ranks=6 --phase=0

        ## qsubm mfdncounting02 --pool="Nmax04-M*-n005" --threads=1 --ranks=5 --phase=0  # to demonstrate scripting check on number of ranks

        qsubm mfdncounting02 --pool="Nmax04-M*-n005" --threads=1 --ranks=15 --phase=0

        qsubm mfdncounting02 --pool="*" --phase=1

    Mark A. Caprio
    University of Notre Dame

    - 02/18/26 (mac): Created, based on runmfdncounting01.

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
M_list = [1.0]
Nmax_orb = 5  # set uniform orbital set independent of Nmax (for template wave function info files)
num_segments_list_by_Nmax = {
    2: [1],
    4: [1,3,5],
}

##################################################################
# build task list
##################################################################

tasks = [
    {
        # nuclide parameters
        "nuclide": (3, 3),

        # basis parameters
        "basis_mode": ncci.modes.BasisMode.kDirect,
        "num_segments": num_segments,
        
        # single-particle and many-body bases
        "sp_truncation_mode": ncci.modes.SingleParticleTruncationMode.kNmax,
        "mb_truncation_mode": ncci.modes.ManyBodyTruncationMode.kNmax,
        "truncation_parameters": {
            "Nmax": Nmax,
            "Nstep": 2,
            "M": M,
            "Nmax_orb": Nmax_orb,
        },
        "partition_filename": None,
        
        # wavefunction storage -- save mfdn_smwf.info and mfdn_MBgroups files
        "save_wavefunctions": True,
        
        # version parameters
        "h2_format": 15099,
        "mfdn_executable": "xmfdn-h2-lan",
        "mfdn_driver": ncci.mfdn_v15
    }
    for M in M_list
    for Nmax in Nmax_list
    for num_segments in num_segments_list_by_Nmax[Nmax]
]

##################################################################
# task dictionary postprocessing functions
##################################################################

def task_pool(current_task):
    pool = "Nmax{truncation_parameters[Nmax]:02d}-M{truncation_parameters[M]:3.1f}-n{num_segments:03d}".format(**current_task)
    return pool


##################################################################
# task control
##################################################################

mcscript.task.init(
    tasks,
    task_descriptor=ncci.descriptors.task_descriptor_c1,
    task_pool=task_pool,
    phase_handler_list=[
        ncci.handlers.task_handler_nonzeros,
        ncci.handlers.task_handler_mfdn_post,
    ]
    )

################################################################
# termination
################################################################

mcscript.control.termination()
