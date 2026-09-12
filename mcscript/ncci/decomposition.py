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
    - 09/12/26 (mac): Reimplement decomposition operator as general linear combination of basis operators.
"""

import numpy as np

import mcscript.utils
from . import (
    operators,
)

################################################################
# decomposition basis operator library
################################################################

# Basis operators for use in generating Lanczos decomposition operator TBMEs.
#
# Operators must accept standardized arguments (nuclide,hw) and return a
# CoefficientDict.
#
# Note: The SU(3) and Sp(3,R) operators currently rely upon external TBME files
# for the one-body and two-body parts of the Casimir operators ("CSU3-U", etc.),
# to be read in as tbme_sources:
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

def identity_op(nuclide, hw):
    """Identity decomposition basis operator."""
    return operators.tb.identity()

def Nex_op(nuclide, hw):
    """Excitation quanta (Nex) decomposition basis operator."""
    return operators.tb.Nex(nuclide, hw)

def CSU3_op(nuclide, hw):
    """SU(3) Casimir decomposition basis operator."""
    A = sum(nuclide)
    return mcscript.utils.CoefficientDict({"CSU3-U": 1/(A-1), "CSU3-V": 1.0})

def CSp3R_op(nuclide, hw):
    """Sp(3,R) Casimir decomposition basis operator."""
    A = sum(nuclide)
    return mcscript.utils.CoefficientDict({"CSp3R-U": 1/(A-1), "CSp3R-V": 1.0})

def L2_op(nuclide, hw):
    """Squared orbital angular momentum (L^2) decomposition basis operator."""
    return operators.tb.L2()

def Sp2_op(nuclide, hw):
    """Squared proton spin (Sp^2) decomposition basis operator."""
    return operators.tb.Sp2()

def Sn2_op(nuclide, hw):
    """Squared neutron spin (Sn^2) decomposition basis operator."""
    return operators.tb.Sn2()
    
def S2_op(nuclide, hw):
    """Squared spin (S^2) decomposition basis operator."""
    return operators.tb.S2()

def T2_op(nuclide, hw):
    """Squared isospin (T^2) decomposition basis operator."""
    A = sum(nuclide)
    return operators.tb.T2(A)

# registry of decomposition basis operators
#
#     dict[str, callable]: identifier -> operator

decomposition_basis_operator_registry = {
    "identity": identity_op,
    "Nex": Nex_op,
    "CSU3": CSU3_op,
    "Sp3R": CSp3R_op,
    "L2": L2_op,
    "Sp2": Sp2_op,
    "Sn2": Sn2_op,
    "S2": S2_op,
    "T2": T2_op,
}


################################################################
# constructing decomposition operator from basis
################################################################

def decomposition_operator_from_coefs(nuclide, hw, coefs):
    """Generate Lanczos decomposition operator from given coefficients.

    Any operator registered in decomposition_basis_operator_registry may be
    included in the coefficient dictionary.

    If a coefficient file is available for the mirror nuclide, you can read that
    file, but specify swap_pn=True to swap the roles of proton and neuton spin
    coefficients (or any other registered proton/neutron operators).

    Arguments:

        nuclide (tuple): (Z,N) of nuclide for the coefficient file.

        hw (float): hw basis paremeter.

        coefs (dict[str, float]): Coefficients by operator identifier.

    """

    decomposition_operator = mcscript.utils.CoefficientDict()
    
    for identifier, coef in coefs.items():
        if identifier not in decomposition_basis_operator_registry:
            raise ValueError("Requested basis operator ({}) not found in decomposition_basis_operator_registry.".format(identifier))
        basis_operator = decomposition_basis_operator_registry[identifier](nuclide, hw)
        decomposition_operator += coef*basis_operator
            
    return decomposition_operator


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
