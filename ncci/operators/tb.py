"""operators.py -- define two-body operators for h2mixer input

A tbme source is defined by the mapping:
    (id, parameters)
where parameters is a dict possibly containing the following:
    "qn": (J0,g0,Tz0)
    "filename": input TBME filename
    "xform_filename": input xform matrix elements
    "xform_truncation": xform truncation parameters
    "operatorU": ob_id
    "operatorV": [ob_factor_a, ob_factor_b]

A tb_operator is the tuple:
    (id, qn, CoefficientDict)
where CoefficientDict can contain some special keys:
    "U[obme_id]"
    "V[obme_id_a,obme_id_b]"

Patrick J. Fasano
University of Notre Dame

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
    - 09/09/20 (pjf):
        + Move from operators.py to operators/tb.py.
        + Add target and source generation functions.
    - 09/12/20 (pjf):
        + Fix tbme sources for xform inputs.
        + Fix scaling of operators with radial dependence.
    - 09/15/20 (pjf): Fix H-components when using custom Hamiltonian.
    - 09/16/20 (pjf):
        + Use diagonalization key to decide whether to generate Hamiltonian TBMEs.
        + Don't include "tbme-" in target names.
    - 11/15/20 (pjf):
        + Make hw dependence consistent across operators.
        + Remove unused kwargs from operators.
"""
import collections
import math
import os
import re

import mcscript.utils
from .. import (
    constants,
    environ,
    modes,
    utils,
    )


# legacy -- imported by operators/__init__.py, for older codes which
# expect operators.*
__all__ = [
    'identity', 'Ursqr', 'Vr1r2', 'Uksqr', 'Vk1k2',
    'L2', 'Sp2', 'Sn2', 'S2', 'J2', 'T2', 'Tz',
    'VNN', 'VC_unscaled', 'VC',
    'rrel2', 'Ncm', 'Ntotal', 'Nintr',
    'Tintr', 'Tcm',
    'Hamiltonian'
    ]


################################################################
# predefined sets
################################################################

k_h2mixer_builtin= {
    "identity",
}

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
    return mcscript.utils.CoefficientDict({"U[ik.ik]": -1.})

def Vk1k2():
    return mcscript.utils.CoefficientDict({"V[ik,ik]": math.sqrt(3)})


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

def T2(A):
    """Isospin-squared operator.

    Arguments:
        A (int): mass number

    Returns:
        CoefficientDict containing coefficients for T^2 operator.
    """
    return mcscript.utils.CoefficientDict({"identity":A*0.75, "V[tz,tz]": 2., "V[t+,t-]":2.})

def Tz():
    """Isospin-projection operator.

    Returns:
        CoefficientDict containing coefficients for Tz operator.
    """
    return mcscript.utils.CoefficientDict({"U[tz]":1.})


################################################################
# interactions
################################################################

def VNN():
    return mcscript.utils.CoefficientDict(VNN=1.)

def VC_unscaled():
    return mcscript.utils.CoefficientDict(VC_unscaled=1.)

def VC(hw_basis, hw_coul):
    """Coulomb interaction operator.

    Arguments:
        hw_basis (float): hw of basis
        hw_coul (float): hw of input Coulomb matrix elements

    Returns:
        CoefficientDict containing coefficients for Coulomb operator.
    """
    return VC_unscaled() * math.sqrt(hw_basis/hw_coul)


################################################################
# common observables
################################################################

def rrel2(A):
    """Relative r^2 two-body operator.

    Arguments:
        A (int): mass number

    Returns:
        CoefficientDict containing coefficients for rrel2 operator.
    """
    out = mcscript.utils.CoefficientDict()
    out += ((A-1)/A**2) * Ursqr()
    out += (-2/A**2) * Vr1r2()
    return out

def Ncm(A, hw):
    """Number of oscillator quanta in the center-of-mass.

    Arguments:
        A (int): mass number
        hw (float): hw of operator-defining oscillator Hamiltonian

    Returns:
        CoefficientDict containing coefficients for Ncm operator.
    """
    bsqr = utils.oscillator_length(hw)**2
    out = mcscript.utils.CoefficientDict()
    out += (1/(2*A*bsqr)) * Ursqr()
    out += (1/(A*bsqr)) * Vr1r2()
    out += ((1/(2*A))*bsqr) * Uksqr()
    out += ((1/A)*bsqr) * Vk1k2()
    out += -3/2 * identity()
    return out

def Ntotal(A, hw):
    """Total number of oscillator quanta.

    Arguments:
        A (int): mass number
        hw (float): hw of operator-defining oscillator Hamiltonian

    Returns:
        CoefficientDict containing coefficients for N operator.
    """
    bsqr = utils.oscillator_length(hw)**2
    out = mcscript.utils.CoefficientDict()
    out += (1/(2*bsqr)) * Ursqr()
    out += ((1/2)*bsqr) * Uksqr()
    out += (-3/2*A) * identity()
    return out

def Nintr(A, hw):
    """Number of oscillator quanta in the intrinsic frame.

    Arguments:
        A (int): mass number
        hw (float): hw of operator-defining oscillator Hamiltonian

    Returns:
        CoefficientDict containing coefficients for Nintr operator.
    """
    return Ntotal(A=A, hw=hw) - Ncm(A=A, hw=hw)

def Tintr(A):
    """Two-body intrinsic kinetic energy operator.

    Arguments:
        A (int): mass number

    Returns:
        CoefficientDict containing coefficients for Tintr operator.
    """
    out = mcscript.utils.CoefficientDict()
    out += ((A-1)/(2*A)) * (constants.k_hbar_c**2/constants.k_mN_csqr) * Uksqr()
    out += (-1/A) * (constants.k_hbar_c**2/constants.k_mN_csqr) * Vk1k2()
    return out

def Tcm(A):
    """Center-of-mass kinetic energy operator.

    Arguments:
        A (int): mass number

    Returns:
        CoefficientDict containing coefficients for Tcm operator.
    """
    out = mcscript.utils.CoefficientDict()
    out += (1/(2*A)) * (constants.k_hbar_c**2/constants.k_mN_csqr) * Uksqr()
    out += (1/A) * (constants.k_hbar_c**2/constants.k_mN_csqr) * Vk1k2()
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
    kinetic_energy = Tintr(A=A)
    lawson_term = a_cm * Ncm(A=A, hw=hw_cm)
    interaction = VNN()
    if use_coulomb:
        coulomb_interaction = VC(hw_basis=hw_coul_rescaled, hw_coul=hw_coul)
    else:
        coulomb_interaction = mcscript.utils.CoefficientDict()
    return (kinetic_energy + interaction + coulomb_interaction + lawson_term)

################################################################
# tbme target extraction
################################################################

def get_tbme_targets(task):
    """Extract list of TBME targets from task.

    Arguments:
        task (dict): as described in module docstring

    Returns:
        (dict of OrderedDict of CoefficientDict): targets and definitions
            grouped by quantum number
    """
    # extract parameters for convenience
    nuclide = task.get("nuclide")
    if nuclide is None:
        A = task["A"]
    else:
        A = sum(nuclide)
    hw = task.get("hw", None)
    hw_cm = task.get("hw_cm")
    if hw_cm is None:
        hw_cm = hw
    a_cm = task.get("a_cm", 0)
    hw_coul = task.get("hw_coul")
    if hw_coul is None:
        hw_coul = hw
    hw_coul_rescaled = task.get("hw_coul_rescaled")
    if hw_coul_rescaled is None:
        hw_coul_rescaled = hw
    tb_observable_sets = task.get("tb_observable_sets", [])

    # accumulate h2mixer targets
    targets = collections.defaultdict(collections.OrderedDict)

    # targets for diagonalization
    if task.get("diagonalization"):
        # target: radius squared (must be first, for built-in MFDn radii)
        targets[(0,0,0)]["rrel2"] = rrel2(A=A)

    # targets for diagonalization or part of Hamiltonian components set
    if task.get("diagonalization") or ("H-components" in tb_observable_sets):
        # target: Hamiltonian
        if isinstance(task.get("hamiltonian"), collections.abc.MutableMapping):
            targets[(0,0,0)]["H"] = task["hamiltonian"]
        else:
            targets[(0,0,0)]["H"] = Hamiltonian(
                A=A, hw=hw, a_cm=a_cm, hw_cm=hw_cm,
                use_coulomb=task["use_coulomb"], hw_coul=hw_coul,
                hw_coul_rescaled=hw_coul_rescaled
            )
        # target: Ncm
        targets[(0,0,0)]["Ncm"] = Ncm(A=A, hw=hw_cm)

    # optional observable sets
    # Hamiltonian components
    if "H-components" in tb_observable_sets:
        # target: Trel (diagnostic)
        targets[(0,0,0)]["Tintr"] = Tintr(A=A)
        # target: Tcm (diagnostic)
        targets[(0,0,0)]["Tcm"] = Tcm(A=A)
        # target: VNN (diagnostic)
        if "VNN" in targets[(0,0,0)]["H"]:
            targets[(0,0,0)]["VNN"] = VNN()
        # target: VC (diagnostic)
        if "VC_unscaled" in targets[(0,0,0)]["H"]:
            targets[(0,0,0)]["VC"] = VC(hw_basis=hw_coul_rescaled, hw_coul=hw_coul)
    # squared angular momenta
    if "am-sqr" in tb_observable_sets:
        targets[(0,0,0)]["L2"] = L2()
        targets[(0,0,0)]["Sp2"] = Sp2()
        targets[(0,0,0)]["Sn2"] = Sn2()
        targets[(0,0,0)]["S2"] = S2()
        targets[(0,0,0)]["J2"] = J2()
    if "isospin" in tb_observable_sets:
        targets[(0,0,0)]["T2"] = T2(A=A)

    # accumulate user observables
    for (basename, qn, operator) in task.get("tb_observables", []):
        targets[qn][basename] = mcscript.utils.CoefficientDict(operator)

    return dict(targets)

def get_tbme_sources(task, targets, postfix):
    """Get TBME sources needed for given targets.

    Arguments:
        task (dict): as described in module docstring
        targets (dict of CoefficientDict): target channels

    Returns:
        (OrderedDict of dict): source id to source mapping
    """
    # determine required sources
    required_tbme_sources = set()
    required_tbme_sources.update(*[op.keys() for op in targets.values()])

    # tbme sources: accumulate definitions
    tbme_sources = collections.OrderedDict()

    # tbme sources: VNN
    if "VNN" in required_tbme_sources:
        VNN_filename = task.get("interaction_file")
        if VNN_filename is None:
            VNN_filename = environ.interaction_filename(
                task["interaction"],
                task["truncation_int"],
                task["hw_int"]
            )

        if task["basis_mode"] is modes.BasisMode.kDirect:
            tbme_sources["VNN"] = dict(filename=VNN_filename)
        else:
            xform_truncation_int = task.get("xform_truncation_int")
            if xform_truncation_int is None:
                xform_truncation_int = task["truncation_int"]
            tbme_sources["VNN"] = dict(
                filename=VNN_filename,
                xform_filename=environ.radial_olap_int_filename(postfix),
                xform_truncation=xform_truncation_int
            )

    # tbme sources: Coulomb
    #
    # Note: This is the "unscaled" Coulomb, still awaiting the scaling
    # factor from dilation.
    if "VC_unscaled" in required_tbme_sources:
        VC_filename = task.get("coulomb_file")
        if VC_filename is None:
            VC_filename = environ.interaction_filename(
                "VC",
                task["truncation_coul"],
                task["hw_coul"]
            )
        if task["basis_mode"] in (modes.BasisMode.kDirect, modes.BasisMode.kDilated):
            tbme_sources["VC_unscaled"] = dict(filename=VC_filename)
        else:
            xform_truncation_coul = task.get("xform_truncation_coul")
            if xform_truncation_coul is None:
                xform_truncation_coul = task["truncation_coul"]
            tbme_sources["VC_unscaled"] = dict(
                filename=VC_filename,
                xform_filename=environ.radial_olap_coul_filename(postfix),
                xform_truncation=xform_truncation_coul
            )

    # tbme sources: h2mixer built-ins
    builtin_tbme_sources = k_h2mixer_builtin
    for source in sorted(builtin_tbme_sources - set(tbme_sources.keys())):
        tbme_sources[source] = dict()

    # tbme sources: upgraded one-body and separable operators
    for source in sorted(required_tbme_sources - set(tbme_sources.keys())):
        # parse upgraded one-body operator
        match = re.fullmatch(r"U\[(.+)\]", source)
        if match:
            tbme_sources[source] = {"operatorU": match.group(1)}
            continue

        # parse separable operator
        match = re.fullmatch(r"V\[(.+),(.+)\]", source)
        if match:
            tbme_sources[source] = {"operatorV": (match.group(1), match.group(2))}
            continue

    # tbme sources: override with user-provided
    user_tbme_sources = task.get("tbme_sources", [])
    for (source_id, source) in user_tbme_sources:
        if source_id in required_tbme_sources:
            tbme_sources[source_id] = source

    return tbme_sources
