"""decomposition.py -- utilities for Lanczos decompositions

Mark A. Caprio
University of Notre Dame

    - 02/23/21 (mac): Created, with refactored code from runaem0110.
    - 02/22/21 (aem):
        +  Add U3LS type operators
        +  Add option to search list of paths for decomposition coefficients.
    - 02/26/21 (mac): Fix operator mapping for Sp3RS and Sp3RSpSnS decompositions.
    - 03/31/21 (zz):
        +  Add LS operator
        +  Add support for swapping p and n parts.
    - 04/24/22 (zz):
        +  Add T operator.
    - 06/05/23 (mac): Use decomposition coefficient search path from environ.
"""

import glob
import os

import numpy as np

import mcscript.utils
from . import (
    operators,
    environ,
)

################################################################
# annealing coefficient input
################################################################

def read_decomposition_operator_coefs(
        nuclide,
        Nmax,
        decomposition_type,
        decomposition_path,
        coef_filename_format,
        verbose=False
):
    """ Read decomposition operator coefficients from coefs.dat file.

    Arguments:
        nuclide (tuple): (Z,N) of nuclide
        Nmax (int): Nmax
        decomposition_type (str): identifier for decomposition type (e.g., "U3SpSnS")
        decomposition_path (str,list[str], optional): path to decomposition coefficient file
        coef_filename_format (str, optional): format template for decomposition coefficient filename

    Returns:
        coefs (np.array): vector of coefficients
    """


    coef_filename = coef_filename_format.format(nuclide=nuclide,Nmax=Nmax,decomposition_type=decomposition_type)
    if type(decomposition_path)==str:
        coefs = np.loadtxt(os.path.join(decomposition_path,coef_filename))
    else:
        if decomposition_path is None:
            decomposition_path = environ.decomposition_dir_list
        coefs = np.loadtxt(
            mcscript.utils.search_in_subdirectories(
                environ.data_dir_decomposition_list,
                decomposition_path,
                coef_filename,
                error_message="file not found",
                verbose=verbose
            )
        )

    if (verbose):
        print("nuclide {}, Nmax {}, operator {}: {}".format(nuclide,Nmax,decomposition_type,coefs))
    return coefs

################################################################
# decomposition operator library
################################################################

# Operators for use in generating Lanczos decomposition operator TBMEs.
#
# Accept standardized arguments (nuclide,Nmax,hw) or (nuclide,Nmax,hw,coefs).
#
# The SU(3) and Sp(3,R) operators currently rely upon external TBME files for
# the one-body and two-body parts of the Casimir operators ("CSU3-U", etc.), to
# be read in as tbme_sources:
#
#      # two-body sources
#      "tbme_sources": [
#          ("CSU3-U", {"filename":"tbme-CSU3-U-tb-14.bin", "qn": (0,0,0)}),
#          ("CSU3-V", {"filename":"tbme-CSU3-V-tb-14.bin", "qn": (0,0,0)}),
#          ("CSp3R-U", {"filename":"tbme-CSp3R-U-tb-14.bin", "qn": (0,0,0)}),
#          ("CSp3R-V", {"filename":"tbme-CSp3R-V-tb-14.bin", "qn": (0,0,0)}),
#      ],
#
# These could ultimately be generated on-the-fly:
#     runs/mcaprio/h2mixer/symplectic-casimir_h2mixer.in

def L2_operator(nuclide,Nmax,hw):
    return operators.tb.L2()
def S2_operator(nuclide,Nmax,hw):
    return operators.tb.S2()
def T2_operator(nuclide,Nmax,hw):
    A = sum(nuclide)
    return operators.tb.T2(A)
def LS_operator(nuclide,Nmax,hw,coefs,swap):
    return mcscript.utils.dot(
    	[operators.tb.S2(), operators.tb.L2()],
    	coefs
    	)
def Nex_operator(nuclide,Nmax,hw):
    return operators.tb.Nex(nuclide, hw)
def CSU3_operator(nuclide,Nmax,hw):
    A = sum(nuclide)
    return mcscript.utils.CoefficientDict({"CSU3-U": 1/(A-1), "CSU3-V": 1.0})
def CSp3R_operator(nuclide,Nmax,hw):
    A = sum(nuclide)
    return mcscript.utils.CoefficientDict({"CSp3R-U": 1/(A-1), "CSp3R-V": 1.0})
def U3S_operator(nuclide,Nmax,hw,coefs,swap):
    return mcscript.utils.dot(
            [operators.tb.Nex(nuclide, hw), CSU3_operator(nuclide,Nmax,hw), operators.tb.S2()],
            coefs
            )
def U3LS_operator(nuclide,Nmax,hw,coefs,swap):
    return mcscript.utils.dot(
            [operators.tb.Nex(nuclide, hw), CSU3_operator(nuclide,Nmax,hw), operators.tb.S2(),operators.tb.L2()],
            coefs
            )

def U3SpSnS_operator(nuclide,Nmax,hw,coefs,swap):
    if swap:
        ops = [operators.tb.Nex(nuclide, hw), CSU3_operator(nuclide,Nmax,hw), operators.tb.Sn2(), operators.tb.Sp2(), operators.tb.S2()]
    else:
        ops = [operators.tb.Nex(nuclide, hw), CSU3_operator(nuclide,Nmax,hw), operators.tb.Sp2(), operators.tb.Sn2(), operators.tb.S2()]
    return mcscript.utils.dot(ops,coefs)

def U3LSpSnS_operator(nuclide,Nmax,hw,coefs,swap):
    if swap:
        ops = [operators.tb.Nex(nuclide, hw), CSU3_operator(nuclide,Nmax,hw), operators.tb.Sn2(), operators.tb.Sp2(), operators.tb.S2(),operators.tb.L2()]
    else:
        ops = [operators.tb.Nex(nuclide, hw), CSU3_operator(nuclide,Nmax,hw), operators.tb.Sp2(), operators.tb.Sn2(), operators.tb.S2(),operators.tb.L2()]
    return mcscript.utils.dot(ops,coefs)

def Sp3RS_operator(nuclide,Nmax,hw,coefs,swap):
    return mcscript.utils.dot(
            [CSp3R_operator(nuclide,Nmax,hw), operators.tb.S2()],
            coefs
            )
def Sp3RSpSnS_operator(nuclide,Nmax,hw,coefs,swap):
    if swap:
        ops = [CSp3R_operator(nuclide,Nmax,hw), operators.tb.Sn2(), operators.tb.Sp2(), operators.tb.S2()]
    else:
        ops = [CSp3R_operator(nuclide,Nmax,hw), operators.tb.Sp2(), operators.tb.Sn2(), operators.tb.S2()]
    return mcscript.utils.dot(ops,coefs)

# registry of decomposition operators
#
#     decomposition_type -> (decomposition_operator,use_coefs)
#
# For use in decomposition_operator wrapper.

decomposition_operator_registry={
    "L" : (L2_operator,False),
    "S": (S2_operator,False),
    "T": (T2_operator,False),
    "LS": (LS_operator,True),
    "Nex": (Nex_operator,False),
    "SU3": (CSU3_operator,False),
    "Sp3R": (CSp3R_operator,False),
    "U3S": (U3S_operator,True),
    "U3LS": (U3LS_operator,True),
    "U3SpSnS": (U3SpSnS_operator,True),
    "U3LSpSnS": (U3LSpSnS_operator,True),
    "Sp3RS": (Sp3RS_operator,True),
    "Sp3RSpSnS": (Sp3RSpSnS_operator,True),
}


################################################################
# decomposition operator wrapper
################################################################

def decomposition_operator(
        nuclide,Nmax,hw,decomposition_type,
        decomposition_path=None,
        coef_filename_format = "decomposition_Z{nuclide[0]:02d}_N{nuclide[1]:02d}_Nmax{Nmax:02d}_{decomposition_type}_coefs.dat",
        swap=False,
        verbose=False
):
    """Generate Lanczos decomposition operator.

    For decomposition operator involving coefficients, uses annealing
    coefficients provided by coefs.dat file.

    If a coefficient file is available for the mirror nuclide, you
    can read that file, but specify swap=True to swap the roles of
    proton and neuton spin coefficients.

    Arguments:
        nuclide (tuple): (Z,N) of nuclide for the coefficient file
        Nmax (int): Nmax
        decomposition_type (str): identifier for decomposition type (e.g., "U3SpSnS")
        decomposition_path (str,list[str], optional): path to decomposition files
        coef_filename_format (str, optional): format template for coef filename
        swap (bool,optional): whether swapping Z and N is needed to find the decomposition files
    """


    (decomposition_operator,use_coefs) = decomposition_operator_registry[decomposition_type]

    if use_coefs:
        coefs = read_decomposition_operator_coefs(
            nuclide,
            Nmax,
            decomposition_type,
            decomposition_path,
            coef_filename_format,
            verbose
            )
        operator = decomposition_operator(nuclide,Nmax,hw,coefs,swap)
    else:
        operator = decomposition_operator(nuclide,Nmax,hw)

    return operator

################################################################
# decomposition task descriptor
################################################################

def task_descriptor_decomposition(task):
    """Task descriptor for decomposition.

    Uses task's "wf_source_info" to generate descriptor for underlying wave
    functions, then appends decomposition-specific fields to descriptor string.

    """

    template_string = (
        "{source_wf_descriptor:s}"
        "-J{source_wf_qn[0]:04.1f}-g{source_wf_qn[1]:1d}-n{source_wf_qn[2]:02d}"
        "-{decomposition_type:s}-dlan{max_iterations:d}"
    )

    descriptor_function = task["wf_source_info"]["descriptor"]
    descriptor_str = template_string.format(
        source_wf_descriptor=descriptor_function(task["wf_source_info"]),
        **task
    )

    return descriptor_str
