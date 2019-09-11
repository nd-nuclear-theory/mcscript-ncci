"""operators.py -- define two-body operators for h2mixer input

    - 02/18/17 (pjf): Created.
    - 05/24/17 (pjf):
      + Fixed VC scaling.
      + Added comments explaining scaling.
    - 09/20/17 (pjf): Add isospin operators.
    - 03/15/19 (pjf): Rough in source and channel data structures.
    - 04/04/19 (pjf): Remove data structures; replace with dictionary
        in tbme.py.
    - 09/04/19 (pjf):
        + Redefine operators for new h2mixer; many (incorrectly)
          predefined operators are now written generically in terms of one- and
          two-body parts.
        + Rename Trel->Tintr.
"""
import math
import os

import mcscript.utils
from . import utils


################################################################
# identity operator
################################################################

def identity():
    return mcscript.utils.CoefficientDict(identity=1.)


################################################################
# radial kinematic operators
################################################################

def Ursqr():
    return mcscript.utils.CoefficientDict({"U[r.r]": 1.})

def Vr1r2():
    return mcscript.utils.CoefficientDict({"V[r,r]": -math.sqrt(3)})


# note (pjf): since <b||k||a> is pure imaginary, we actually store <b||ik||a>;
#   this extra factor of -1 comes from k.k = -(ik).(ik)
def Uksqr():
    return mcscript.utils.CoefficientDict({"U[k.k]": -1.})

def Vk1k2():
    return mcscript.utils.CoefficientDict({"V[k,k]": math.sqrt(3)})


################################################################
# angular momentum operators
################################################################

def L2():
    return mcscript.utils.CoefficientDict({"U[l2]":1., "V[l,l]":2*-math.sqrt(3)})

def Sp2():
    return mcscript.utils.CoefficientDict({"U[sp2]":1., "V[sp,sp]":2*-math.sqrt(3)})

def Sn2():
    return mcscript.utils.CoefficientDict({"U[sn2]":1., "V[sn,sn]":2*-math.sqrt(3)})

def S2():
    return mcscript.utils.CoefficientDict({"U[s2]":1., "V[s,s]":2*-math.sqrt(3)})

def J2():
    return mcscript.utils.CoefficientDict({"U[j2]":1., "V[j,j]":2*-math.sqrt(3)})


################################################################
# isospin operators
################################################################

def T2(A, **kwargs):
    return mcscript.utils.CoefficientDict({"identity":A*0.75, "V[tz,tz]": 2., "V[t+,t-]":2.})

def Tz():
    return mcscript.utils.CoefficientDict({"U[tz]":1.})


################################################################
# interactions
################################################################

def VNN():
    return mcscript.utils.CoefficientDict(VNN=1.)

def VC_unscaled():
    return mcscript.utils.CoefficientDict(VC_unscaled=1.)

def VC(bsqr_coul=1.0):
    """Coulomb interaction operator.

    Arguments:
        bsqr_coul (float): beta squared (ratio of b^2 to b_coul^2)
    """
    return VC_unscaled() * math.sqrt(bsqr_coul)


################################################################
# common observables
################################################################

def rrel2(A, hw, **kwargs):
    """Relative r^2 two-body operator.

    Arguments:
        A (int): mass number
        hw (float): length parameter

    Returns:
        CoefficientDict containing coefficients for rrel2 operator.
    """
    out = mcscript.utils.CoefficientDict()
    out += ((A-1)*(utils.oscillator_length(hw)/A)**2) * Ursqr()
    out += (-2*(utils.oscillator_length(hw)/A)**2) * Vr1r2()
    return out

def Ncm(A, bsqr, **kwargs):
    """Number of oscillator quanta in the center-of-mass.

    Arguments:
        A (int): mass number
        bsqr (float): beta squared (ratio of b_cm^2 to b^2)

    Returns:
        CoefficientDict containing coefficients for Ncm operator.
    """
    out = mcscript.utils.CoefficientDict()
    out += (1/(2*A*bsqr)) * Ursqr()
    out += (1/(A*bsqr)) * Vr1r2()
    out += ((1/(2*A))*bsqr) * Uksqr()
    out += ((1/A)*bsqr) * Vk1k2()
    out += -3/2 * identity()
    return out

def Ntotal(A, bsqr, **kwargs):
    """Total number of oscillator quanta.

    Arguments:
        A (int): mass number
        bsqr (float): beta squared (ratio of b_cm^2 to b^2)

    Returns:
        CoefficientDict containing coefficients for N operator.
    """
    out = mcscript.utils.CoefficientDict()
    out += (1/(2*bsqr)) * Ursqr()
    out += ((1/2)*bsqr) * Uksqr()
    out += (-3/2*A) * identity()
    return out

def Nintr(A, bsqr, **kwargs):
    """Number of oscillator quanta in the intrinsic frame.

    Arguments:
        A (int): mass number
        bsqr (float): beta squared (ratio of b_cm^2 to b^2)

    Returns:
        CoefficientDict containing coefficients for Nintr operator.
    """
    return Ntotal(A, bsqr) - Ncm(A, bsqr)

def Tintr(A, hw, **kwargs):
    """Two-body intrinsic kinetic energy operator.

    Arguments:
        A (int): mass number
        bsqr (float): beta squared

    Returns:
        CoefficientDict containing coefficients for Trel operator.
    """
    out = mcscript.utils.CoefficientDict()
    out += ((A-1)/(2*A)*hw) * Uksqr()
    out += (-1/A*hw) * Vk1k2()
    return out

def Tcm(A, hw, **kwargs):
    """Center-of-mass kinetic energy operator.

    Arguments:
        A (int): mass number
        hw (float): hw of basis

    Returns:
        CoefficientDict containing coefficients for Tcm operator.
    """
    out = mcscript.utils.CoefficientDict()
    out += (hw/(2*A)) * Uksqr()
    out += (hw/A) * Vk1k2()
    return out


################################################################
# standard Hamiltonian
################################################################

def Hamiltonian(A, hw, a_cm, bsqr_intr=1.0, use_coulomb=True, bsqr_coul=1.0, **kwargs):
    """A standard Hamiltonian for shell-model runs.

    Arguments:
        A (int): mass number
        hw (float): oscillator basis parameter
        a_cm (float): Lawson term coefficient
        bsqr_intr (float, default 1.0): beta-squared for Lawson term (ratio of b_cm^2 to b^2)
        use_coulomb (bool, default True): include Coulomb interaction
        bsqr_coul (float, optional): beta-squared for Coulomb scaling (ratio of b^2 to b_coul^2)
    """
    kinetic_energy = Tintr(A, hw)
    lawson_term = a_cm * Ncm(A, bsqr_intr)
    interaction = VNN()
    if use_coulomb:
        coulomb_interaction = VC(bsqr_coul)
    else:
        coulomb_interaction = mcscript.utils.CoefficientDict()
    return (kinetic_energy + interaction + coulomb_interaction + lawson_term)
