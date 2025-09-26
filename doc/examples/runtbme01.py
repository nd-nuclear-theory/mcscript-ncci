"""runmtbme01.py

    Example generation of TBME files, e.g, for use in many-body codes other than MFDn.

    Truncation: Examples are included of triangular truncation (that is, by a
    cutoff on two-body oscillator quanta) and square truncation (by a cutoff on
    one-body oscillator quanta).  Note that this differs from the truncation
    used in the h2 files generated in the setup phase for an mfdn run, which is
    a hybrid truncation involving both one-body and two-body oscillator cutoffs,
    takes into account which pairs actually show up in a given Nmax truncation,
    for the given nucleus ("valence" shell).

    Conversion: Includes conversion of output TBMEs from h2 to me2j format.

    Mark A. Caprio
    University of Notre Dame

"""

import glob
import os

import mcscript
import mcscript.control
import mcscript.task
import mcscript.utils

import mcscript.ncci as ncci

# initialize mcscript
mcscript.control.init()

##################################################################
# environment
##################################################################

# TBME paths
ncci.environ.interaction_dir_list = [
    # paths to TBME files for interactions
]
ncci.environ.operator_dir_list = [
    # paths to TBME files for operators
    "casimir-tb-6",
]

##################################################################
# run parameters
##################################################################

# nuclide
nuclide_list = [
    (1,1),  # 2H
    (2,2),  # 4He
]

# truncation
target_truncation_list = [
    ("ob", 3),
    ("tb", 4),
]

# hw
hw_list = [20.]

##################################################################
# build task list
##################################################################

tasks = [
    {
        # nuclide/hw parameters
        "nuclide": nuclide,
        "hw": hw,

        # two-body truncation
        "target_truncation": target_truncation,
        
        # two-body observables
        "tb_observable_sets": ["am-sqr", "isospin"],
        "tb_observables": [
            ("Nex", (0,0,0), mcscript.ncci.operators.tb.Nex(nuclide, hw)),
            ("Ncm", (0,0,0), mcscript.ncci.operators.tb.Ncm(sum(nuclide), hw)),
            ("CSU3", (0,0,0), {"CSU3-U": 1/(sum(nuclide)-1), "CSU3-V": 1.0}),
        ],

        # two-body sources
        "tbme_sources": [
            ("CSU3-U", {"filename": "CSU3-U-tb-6.bin", "qn": (0,0,0)}),
            ("CSU3-V", {"filename": "CSU3-V-tb-6.bin", "qn": (0,0,0)}),
        ],

        # file format parameters
        "h2_format": 0,
        "h2_extension": "bin",
        "tbme_conversion": {
            "target_format": "me2j",
            "me2j_extension": "bin",
            "me2j_precision": "double",  # applies to binary format only
            "keep_h2": True,
        },
    }
    for target_truncation in target_truncation_list
    for nuclide in nuclide_list
    for hw in hw_list
]


##################################################################
# task dictionary postprocessing functions
##################################################################

def task_pool(task):
    pool = "{target_truncation[0]}-{target_truncation[1]}".format(**task)
    return pool


##################################################################
# task control
##################################################################

mcscript.task.init(
    tasks,
    task_descriptor=ncci.descriptors.task_descriptor_tbme_1,
    task_pool=task_pool,
    phase_handler_list=[ncci.handlers.task_handler_tbme],
    archive_phase_handler_list=[ncci.handlers.archive_handler_mfdn_hsi],
)

################################################################
# termination
################################################################

mcscript.control.termination()
