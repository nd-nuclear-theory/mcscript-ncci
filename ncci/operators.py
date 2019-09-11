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
    - 09/11/19 (pjf):
        + Eliminate bsqr for explict hw arguments.
        + Improve docstrings.
"""
import math
import os

import mcscript.utils
from . import utils


################################################################
# identity operator
################################################################

def identity(**kwargs):
    return mcscript.utils.CoefficientDict(identity=1.)


################################################################
# radial kinematic operators
################################################################

def Ursqr(**kwargs):
    return mcscript.utils.CoefficientDict({"U[r.r]": 1.})

def Vr1r2(**kwargs):
    return mcscript.utils.CoefficientDict({"V[r,r]": -math.sqrt(3)})


# note (pjf): since <b||k||a> is pure imaginary, we actually store <b||ik||a>;
#   this extra factor of -1 comes from k.k = -(ik).(ik)
def Uksqr(**kwargs):
    return mcscript.utils.CoefficientDict({"U[k.k]": -1.})

def Vk1k2(**kwargs):
    return mcscript.utils.CoefficientDict({"V[k,k]": math.sqrt(3)})


################################################################
# angular momentum operators
################################################################

def L2(**kwargs):
    return mcscript.utils.CoefficientDict({"U[l2]":1., "V[l,l]":2*-math.sqrt(3)})

def Sp2(**kwargs):
    return mcscript.utils.CoefficientDict({"U[sp2]":1., "V[sp,sp]":2*-math.sqrt(3)})

def Sn2(**kwargs):
    return mcscript.utils.CoefficientDict({"U[sn2]":1., "V[sn,sn]":2*-math.sqrt(3)})

def S2(**kwargs):
    return mcscript.utils.CoefficientDict({"U[s2]":1., "V[s,s]":2*-math.sqrt(3)})

def J2(**kwargs):
    return mcscript.utils.CoefficientDict({"U[j2]":1., "V[j,j]":2*-math.sqrt(3)})


################################################################
# isospin operators
################################################################

def T2(A, **kwargs):
    """Isospin-squared operator.

    Arguments:
        A (int): mass number

    Returns:
        CoefficientDict containing coefficients for T^2 operator.
    """
    return mcscript.utils.CoefficientDict({"identity":A*0.75, "V[tz,tz]": 2., "V[t+,t-]":2.})

def Tz(**kwargs):
    """Isospin-projection operator.

    Returns:
        CoefficientDict containing coefficients for Tz operator.
    """
    return mcscript.utils.CoefficientDict({"U[tz]":1.})


################################################################
# interactions
################################################################

def VNN(**kwargs):
    return mcscript.utils.CoefficientDict(VNN=1.)

def VC_unscaled(**kwargs):
    return mcscript.utils.CoefficientDict(VC_unscaled=1.)

def VC(hw, hw_coul, **kwargs):
    """Coulomb interaction operator.

    Arguments:
        hw (float): hw of basis
        hw_coul (float): hw of input Coulomb matrix elements

    Returns:
        CoefficientDict containing coefficients for Coulomb operator.
    """
    return VC_unscaled() * math.sqrt(hw/hw_coul)


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

def Ncm(A, hw, hw_cm=None, **kwargs):
    """Number of oscillator quanta in the center-of-mass.

    Arguments:
        A (int): mass number
        hw (float): hw of basis
        hw_coul (float): hw of cm oscillator Hamiltonian

    Returns:
        CoefficientDict containing coefficients for Ncm operator.
    """
    if hw_cm is None:
        hw_cm = hw
    bsqr = hw/hw_cm
    out = mcscript.utils.CoefficientDict()
    out += (1/(2*A*bsqr)) * Ursqr()
    out += (1/(A*bsqr)) * Vr1r2()
    out += ((1/(2*A))*bsqr) * Uksqr()
    out += ((1/A)*bsqr) * Vk1k2()
    out += -3/2 * identity()
    return out

def Ntotal(A, hw, hw_cm=None, **kwargs):
    """Total number of oscillator quanta.

    Arguments:
        A (int): mass number
        hw (float): hw of basis
        hw_cm (float, default hw): hw of cm oscillator Hamiltonian

    Returns:
        CoefficientDict containing coefficients for N operator.
    """
    if hw_cm is None:
        hw_cm = hw
    bsqr = hw/hw_cm
    out = mcscript.utils.CoefficientDict()
    out += (1/(2*bsqr)) * Ursqr()
    out += ((1/2)*bsqr) * Uksqr()
    out += (-3/2*A) * identity()
    return out

def Nintr(A, hw, hw_cm=None, **kwargs):
    """Number of oscillator quanta in the intrinsic frame.

    Arguments:
        A (int): mass number
        hw (float): hw of basis
        hw_cm (float, default hw): hw of cm oscillator Hamiltonian

    Returns:
        CoefficientDict containing coefficients for Nintr operator.
    """
    return Ntotal(A=A, hw=hw, hw_cm=hw_cm) - Ncm(A=A, hw=hw, hw_cm=hw_cm)

def Tintr(A, hw, **kwargs):
    """Two-body intrinsic kinetic energy operator.

    Arguments:
        A (int): mass number
        hw (float): hw of basis

    Returns:
        CoefficientDict containing coefficients for Tintr operator.
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

def Hamiltonian(A, hw, a_cm=0., hw_cm=None, use_coulomb=True, hw_coul=None, hw_coul_rescaled=None, **kwargs):
    """A standard Hamiltonian for shell-model runs.

    Arguments:
        A (int): mass number
        hw (float): oscillator basis parameter
        a_cm (float, default 0.0): Lawson term coefficient
        hw_cm (float, default hw): Lawson term oscillator frequency
        use_coulomb (bool, default True): include Coulomb interaction
        hw_coul (float): hw for input Coulomb matrix elements
        hw_coul_rescaled (float, default hw): target hw for analytic scaling of Coulomb matrix elements

    Returns:
        CoefficientDict containing coefficients for Hamiltonian.
    """
    if hw_cm is None:
        hw_cm = hw
    if hw_coul_rescaled is None:
        hw_coul_rescaled = hw
    kinetic_energy = Tintr(A=A, hw=hw)
    lawson_term = a_cm * Ncm(A, hw=hw, hw_cm=hw_cm)
    interaction = VNN()
    if use_coulomb:
        coulomb_interaction = VC(hw=hw_coul_rescaled, hw_coul=hw_coul)
    else:
        coulomb_interaction = mcscript.utils.CoefficientDict()
    return (kinetic_energy + interaction + coulomb_interaction + lawson_term)
