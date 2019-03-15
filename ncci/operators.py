"""operators.py -- define two-body operators for h2mixer input

    - 02/18/17 (pjf): Created.
    - 05/24/17 (pjf):
      + Fixed VC scaling.
      + Added comments explaining scaling.
    - 09/20/17 (pjf): Add isospin operators.
    - 03/15/19 (pjf): Rough in source and channel data structures.
"""
import math
import os

import mcscript.utils
from . import utils


################################################################
# two-body operator representations
################################################################
k_h2mixer_builtin_operators = {
    "identity", "Ursqr", "Vr1r2", "Uksqr", "Vk1k2",
    "L", "Sp", "Sn", "S", "J",
    "T", "Tz"
}

class TwoBodyOperatorSource(object):
    """Represents a two-body operator source channel.
    """
    _xform_filename = None
    _xform_truncation = None
    _filename = None

    def __init__(self, filename=None, xform_filename=None, xform_truncation=None):
        self._xform_filename = xform_filename
        self._xform_truncation = xform_truncation
        self._filename = filename
        super().__init__()

    def get_h2mixer_line(self, id):
        """Construct h2mixer input line.

        Returns: (str) h2mixer input line
        """
        if self._filename is not None:
            if id in k_h2mixer_builtin_operators:
                raise Warning("overriding builtin operator {id} with {tbme_filename}".format(
                    id=id,
                    tbme_filename=tbme_filename
                ))
            tbme_filename = mcscript.utils.expand_path(self._filename)
            if not os.path.isfile(tbme_filename):
                raise FileNotFoundError(tbme_filename)
            if (self._xform_filename is not None) and (self._xform_truncation is not None):
                xform_weight_max = utils.weight_max_string(self._xform_truncation)
                line = ("define-source xform {id} {tbme_filename} {xform_weight_max} {xform_filename}".format(
                    id=id,
                    tbme_filename=tbme_filename,
                    xform_weight_max=xform_weight_max,
                    xform_filename=self._xform_filename
                    ))
            else:
                line = ("define-source input {id} {tbme_filename}".format(
                    id=id, tbme_filename=tbme_filename
                    ))
        elif id in k_h2mixer_builtin_operators:
            line = ("define-source operator {id}".format(id=id))
        else:
            raise mcscript.exception.ScriptError("unknown two-body operator {id}".format(id=id))
        return line



class TwoBodyOperator(mcscript.utils.CoefficientDict):
    """Represents a two-body operator target channel.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)



################################################################
# identity operator
################################################################

def identity():
    return TwoBodyOperator(identity=1.)


################################################################
# radial kinematic operators
################################################################

kinematic_operator_set = {
    "identity", "Ursqr", "Vr1r2", "Uksqr", "Vk1k2"
}

def Ursqr():
    return TwoBodyOperator(Ursqr=1.)

def Vr1r2():
    return TwoBodyOperator(Vr1r2=1.)

def Uksqr():
    return TwoBodyOperator(Uksqr=1.)

def Vk1k2():
    return TwoBodyOperator(Vk1k2=1.)


################################################################
# angular momentum operators
################################################################

angular_momentum_operator_set = {
    "L", "Sp", "Sn", "S", "J"
}

def L2():
    return TwoBodyOperator(L=1.)

def Sp2():
    return TwoBodyOperator(Sp=1.)

def Sn2():
    return TwoBodyOperator(Sn=1.)

def S2():
    return TwoBodyOperator(S=1.)

def J2():
    return TwoBodyOperator(J=1.)


################################################################
# isospin operators
################################################################

isospin_operator_set = {
    "T", "Tz"
}

def T2():
    return TwoBodyOperator(T=1.)

def Tz():
    return TwoBodyOperator(Tz=1.)


################################################################
# interactions
################################################################

def VNN():
    return TwoBodyOperator(VNN=1.)

def VC_unscaled():
    return TwoBodyOperator(VC_unscaled=1.)

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
    out = TwoBodyOperator()
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
    out = TwoBodyOperator()
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
    out = TwoBodyOperator()
    out += (1/(2*bsqr)) * Ursqr()
    out += ((1/2)*bsqr) * Uksqr()
    out += (-3/2*A) * identity()

def Nintr(A, bsqr, **kwargs):
    """Number of oscillator quanta in the intrinsic frame.

    Arguments:
        A (int): mass number
        bsqr (float): beta squared (ratio of b_cm^2 to b^2)

    Returns:
        CoefficientDict containing coefficients for Nintr operator.
    """
    return Ntotal(A, bsqr) - Ncm(A, bsqr)

def Trel(A, hw, **kwargs):
    """Two-body kinetic energy operator.

    Arguments:
        A (int): mass number
        bsqr (float): beta squared

    Returns:
        CoefficientDict containing coefficients for Trel operator.
    """
    out = TwoBodyOperator()
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
    out = TwoBodyOperator()
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
    kinetic_energy = Trel(A, hw)
    lawson_term = a_cm * Ncm(A, bsqr_intr)
    interaction = VNN()
    if use_coulomb:
        coulomb_interaction = VC(bsqr_coul)
    else:
        coulomb_interaction = TwoBodyOperator()
    return (kinetic_energy + interaction + coulomb_interaction + lawson_term)
