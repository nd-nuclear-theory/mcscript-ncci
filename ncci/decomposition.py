"""decomposition.py -- utilities for Lanczos decompositions

Mark A. Caprio
University of Notre Dame

- 02/23/21 (mac): Created, with refactored code from runaem0110.
"""

import glob
import os

import numpy as np

import mcscript
from . import (
    operators
)

################################################################
# annealing coefficient input
################################################################

def read_decomposition_operator_coefs(
        nuclide,
        Nmax,
        decomposition_type,
        decomposition_path,
        coef_filename_format = "decomposition_Z{nuclide[0]:02d}_N{nuclide[1]:02d}_Nmax{Nmax:02d}_{decomposition_type}_coefs.dat",
        verbose=False
):
    """ Read decomposition operator coefficients from coefs.dat file.

    Arguments:
        nuclide (tuple): (Z,N) of nuclide
        Nmax (int): Nmax
        decomposition_type (str): identifier for decomposition type (e.g., "U3SpSnS")
        decomposition_path (str): path to decomposition files
        coef_filename_format (str, optional): format template for coef filename

    Returns:
        coefs (np.array): vector of coefficients
    """
    coef_filename = coef_filename_format.format(nuclide=nuclide,Nmax=Nmax,decomposition_type=decomposition_type)
    coefs = np.loadtxt(os.path.join(decomposition_path,coef_filename))
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
def Nex_operator(nuclide,Nmax,hw):
    return operators.tb.Nex(nuclide, hw)
def CSU3_operator(nuclide,Nmax,hw):
    A = sum(nuclide)
    return mcscript.utils.CoefficientDict({"CSU3-U": 1/(A-1), "CSU3-V": 1.0})
def CSp3R_operator(nuclide,Nmax,hw):
    A = sum(nuclide)
    return mcscript.utils.CoefficientDict({"CSp3R-U": 1/(A-1), "CSp3R-V": 1.0})
def U3S_operator(nuclide,Nmax,hw,coefs):
    return mcscript.utils.dot(
            [operators.tb.Nex(nuclide, hw), CSU3_operator(nuclide,Nmax,hw), operators.tb.S2()],
            coefs
            )
def U3SpSnS_operator(nuclide,Nmax,hw,coefs):
    return mcscript.utils.dot(
            [operators.tb.Nex(nuclide, hw), CSU3_operator(nuclide,Nmax,hw), operators.tb.Sp2(), operators.tb.Sn2(), operators.tb.S2()],
            coefs
            )
def Sp3RS_operator(nuclide,Nmax,hw,coefs):
    return mcscript.utils.dot(
            [CSp3R_operator(nuclide,Nmax,hw), operators.tb.S2()],
            coefs
            )
def Sp3RSpSnS_operator(nuclide,Nmax,hw,coefs):
    return mcscript.utils.dot(
            [CSp3R_operator(nuclide,Nmax,hw), operators.tb.Sp2(), operators.tb.Sn2(), operators.tb.S2()],
            coefs
            )

# registry of decomposition operators
#
#     decomposition_type -> (decomposition_operator,use_coefs)
#
# For use in decomposition_operator wrapper.

decomposition_operator_registry={
    "L" : (L2_operator,False),
    "S": (S2_operator,False),
    "Nex": (Nex_operator,False),
    "SU3": (CSU3_operator,False),
    "Sp3R": (CSp3R_operator,False),
    "U3S": (U3S_operator,True),
    "U3SpSnS": (U3SpSnS_operator,True),
    "Sp3RS": (U3S_operator,True),
    "Sp3RSpSnS": (U3SpSnS_operator,True),
}
    

################################################################
# decomposition operator wrapper
################################################################

def decomposition_operator(
        nuclide,Nmax,hw,decomposition_type,
        decomposition_path,
        coef_filename_format = "decomposition_Z{nuclide[0]:02d}_N{nuclide[1]:02d}_Nmax{Nmax:02d}_{decomposition_type}_coefs.dat",
        verbose=False
):    
    """Generate Lanczos decomposition operator.

    For decomposition operator involving coefficients, uses annealing
    coefficients provided by coefs.dat file.

    Arguments:
        nuclide (tuple): (Z,N) of nuclide
        Nmax (int): Nmax
        decomposition_type (str): identifier for decomposition type (e.g., "U3SpSnS")
        decomposition_path (str): path to decomposition files
        coef_filename_format (str, optional): format template for coef filename
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
        operator = decomposition_operator(nuclide,Nmax,hw,coefs)
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
