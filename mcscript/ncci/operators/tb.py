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

Predefined sets of two-body observables can be generated by adding
the following to the list tb_observable_sets:
    "H-components": Tintr, Tcm, VNN, VC
    "am-sqr": L2, Sp2, Sn2, S2, J2
    "isospin": T2
    "intrinsic-E0": E0p, E0n
    "intrinsic-M1": M1, DLp, DLn, DSp, DSn
    "intrinsic-E2": E2p, E2n

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
        + Add Nex operator.
    - 07/09/21 (pjf): Add intrinsic operators:
        + Sp, Sn, S, Siv, Lintr, Livintr, Lpintr, Lnintr, M1intr
        + Qintr, Qivintr, Qpintr, Qnintr
    - 07/14/21 (pjf):
        + Add additional intrinsic operators: r2intr, r2ivintr, rp2intr, and rn2intr
        + Add tb_observable_sets: intrinsic-E0, intrinsic-M1, intrinsic-E2
    - 12/29/22 (zz):
        + Add tb_observable_sets: VC
    - 12/30/22 (zz):
        + Add isoscalar coulomb file name support to get_tbme_sources.
    - 05/18/24 (pjf):
        + Add rpp2, rnn2, rpn2, and rNN2.
"""
import collections
import math
import re

import mcscript.utils
from .. import (
    constants,
    environ,
    modes,
    utils,
    )


# legacy -- imported by operators/__init__.py, for older codes which
# expect these operators to lie in the operators namespace (operators.*)
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

def Sp():
    return mcscript.utils.CoefficientDict({"U[sp]":1.})

def Sp2():
    return mcscript.utils.CoefficientDict({"U[sp2]":1., "V[sp,sp]":2*-math.sqrt(3)})

def Sn():
    return mcscript.utils.CoefficientDict({"U[sn]":1.})

def Sn2():
    return mcscript.utils.CoefficientDict({"U[sn2]":1., "V[sn,sn]":2*-math.sqrt(3)})

def S():
    return mcscript.utils.CoefficientDict({"U[s]":1.})

def Siv():
    return mcscript.utils.CoefficientDict({"U[stz]":2.})

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

def Nex(nuclide, hw):
    """Number of oscillator excitation quanta.

    Arguments:
        nuclide (tuple of int): (Z,N) for nuclide
        hw (float): hw of operator-defining oscillator Hamiltonian

    Returns:
        CoefficientDict containing coefficients for Nex operator.
    """
    return Ntotal(A=sum(nuclide), hw=hw) - utils.N0_for_nuclide(nuclide)*identity()

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

def r2intr(A):
    """Intrinsic r^2 two-body operator.

    Arguments:
        A (int): mass number

    Returns:
        CoefficientDict containing coefficients for r2intr operator.
    """
    out = mcscript.utils.CoefficientDict()
    out += (1-1/A) * Ursqr()
    out += (-2/A) * Vr1r2()
    return out

def r2ivintr(nuclide):
    """Two-body intrinsic isovector r^2 operator.

    Arguments:
        nuclide (tuple of int): nuclide N and Z

    Returns:
        CoefficientDict containing coefficients for r2ivintr operator.
    """
    (Z,N) = nuclide
    A = Z+N
    out = 2*mcscript.utils.CoefficientDict({  # overall factor of 2 from tz vs. \tau_0
        "U[r.rtz]": 1-2/A,
        "V[rtz,r]": -2/A*(-math.sqrt(3)),
        "V[r,rtz]": -2/A*(-math.sqrt(3)),
        })
    out += (Z-N)/A**2 * Ursqr() + 2*(Z-N)/A**2 * Vr1r2()
    return out

def rp2intr(nuclide):
    """Two-body intrinsic proton r^2 operator.

    This is (r_p-R)^2, where R is the c-o-m of the A-body system, not the Z-body
    proton subsystem.

    Arguments:
        nuclide (tuple of int): nuclide N and Z

    Returns:
        CoefficientDict containing coefficients for rp2intr operator.
    """
    out = (r2intr(A=sum(nuclide)) + r2ivintr(nuclide=nuclide))/2
    return out

def rn2intr(nuclide):
    """Two-body intrinsic neutron r^2 operator.

    This is (r_n-R)^2, where R is the c-o-m of the A-body system, not the N-body
    neutron subsystem.

    Arguments:
        nuclide (tuple of int): nuclide N and Z

    Returns:
        CoefficientDict containing coefficients for rn2intr operator.
    """
    out = (r2intr(A=sum(nuclide)) - r2ivintr(nuclide=nuclide))/2
    return out

def rNN2(nuclide):
    """Relative nucleon-nucleon r^2 operator.

    This is r_ij^2, the pair distance summed over all pairs of nucleons.

    Arguments:
        nuclide (tuple of int): nuclide N and Z

    Returns:
        CoefficientDict containing coefficients for rNN2 operator.
    """
    (Z,N) = nuclide
    A = Z+N
    out = (A-1)*Ursqr() - 2*Vr1r2()
    return out

def rpp2(nuclide):
    """Relative proton-proton r^2 operator.

    This is r_ij^2, the pair distance summed over all pairs of protons.

    Arguments:
        nuclide (tuple of int): nuclide N and Z

    Returns:
        CoefficientDict containing coefficients for rpp2 operator.
    """
    (Z,N) = nuclide
    out = mcscript.utils.CoefficientDict({
        "U[r.r]": (Z-1)/2,
        "V[r,r]": -1/2*(-math.sqrt(3)),
        "U[r.rtz]": +1*(Z-1), # tauz = 2*tz
        "V[rtz,r]": -1*(-math.sqrt(3)),  # tauz = 2*tz
        "V[r,rtz]": -1*(-math.sqrt(3)),  # tauz = 2*tz
        "V[rtz,rtz]": -2*(-math.sqrt(3)), # tauz1*tauz2 = 4*tz1*tz2
        })
    return out

def rnn2(nuclide):
    """Relative neutron-neutron r^2 operator.

    This is r_ij^2, the pair distance summed over all pairs of neutrons.

    Arguments:
        nuclide (tuple of int): nuclide N and Z

    Returns:
        CoefficientDict containing coefficients for rnn2 operator.
    """
    (Z,N) = nuclide
    out = mcscript.utils.CoefficientDict({
        "U[r.r]": (N-1)/2,
        "V[r,r]": -1/2*(-math.sqrt(3)),
        "U[r.rtz]": -1*(N-1), # tauz = 2*tz
        "V[rtz,r]": +1*(-math.sqrt(3)),  # tauz = 2*tz
        "V[r,rtz]": +1*(-math.sqrt(3)),  # tauz = 2*tz
        "V[rtz,rtz]": -2*(-math.sqrt(3)), # tauz1*tauz2 = 4*tz1*tz2
        })
    return out

def rpn2(nuclide):
    """Relative proton-neutron r^2 operator.

    This is r_ij^2, the pair distance summed over all proton-neutron pairs.

    Arguments:
        nuclide (tuple of int): nuclide N and Z

    Returns:
        CoefficientDict containing coefficients for rNN2 operator.
    """
    (Z,N) = nuclide
    A = Z+N
    out = mcscript.utils.CoefficientDict({
        "U[r.r]": A/2,
        "U[r.rtz]": (N-Z), # tauz = 2*tz
        "V[r,r]": -1*(-math.sqrt(3)),
        "V[rtz,rtz]": -4*(-math.sqrt(3)), # tauz1*tauz2 = 4*tz1*tz2
        })
    return out

def Lintr(A):
    """Two-body intrinsic L operator.

    Arguments:
        A (int): mass number

    Returns:
        CoefficientDict containing coefficients for Lintr operator.
    """
    out = mcscript.utils.CoefficientDict({
        "U[l]": 1.-(1./A),
        "V[r,ik]": 2*math.sqrt(2)/A
        })
    return out

def Livintr(nuclide):
    """Two-body intrinsic isovector L operator.

    Arguments:
        nuclide (tuple of int): nuclide N and Z

    Returns:
        CoefficientDict containing coefficients for Livintr operator.
    """
    (Z,N) = nuclide
    A = Z+N
    out = 2*mcscript.utils.CoefficientDict({  # overall factor of 2 from tz vs. \tau_0
        "U[ltz]": 1-2/A,
        "V[rtz,ik]": 2*math.sqrt(2)/A,
        "V[r,iktz]": 2*math.sqrt(2)/A,
        })
    out += mcscript.utils.CoefficientDict({
        "U[l]": (Z-N)/A**2,
        "V[r,ik]": -2*math.sqrt(2)*(Z-N)/A**2,
        })
    return out

def Lpintr(nuclide):
    """Two-body intrinsic proton L operator.

    Arguments:
        nuclide (tuple of int): nuclide N and Z

    Returns:
        CoefficientDict containing coefficients for Lpintr operator.
    """
    out = (Lintr(sum(nuclide)) + Livintr(nuclide))/2
    return out

def Lnintr(nuclide):
    """Two-body intrinsic neutron L operator.

    Arguments:
        nuclide (tuple of int): nuclide N and Z

    Returns:
        CoefficientDict containing coefficients for Lnintr operator.
    """
    out = (Lintr(sum(nuclide)) - Livintr(nuclide))/2
    return out

def M1intr(nuclide):
    """Two-body intrinsic M1 operator.

    Arguments:
        nuclide (tuple of int): nuclide N and Z

    Returns:
        CoefficientDict containing coefficients for M1intr operator.
    """
    out = Lpintr(nuclide) + constants.k_gp*(S()+Siv())/2 + constants.k_gn*(S()-Siv())/2
    out *= math.sqrt(3/(4*math.pi))
    return out

def Qintr(A):
    """Two-body intrinsic quadrupole operator.

    Arguments:
        A (int): mass number

    Returns:
        CoefficientDict containing coefficients for Lintr operator.
    """
    out = mcscript.utils.CoefficientDict({
        "U[r2Y2]": 1.-(1./A),
        "V[r,r]": -2*math.sqrt(15/(8*math.pi))/A
        })
    return out

def Qivintr(nuclide):
    """Two-body intrinsic isovector quadrupole operator.

    Arguments:
        nuclide (tuple of int): nuclide N and Z

    Returns:
        CoefficientDict containing coefficients for Livintr operator.
    """
    (Z,N) = nuclide
    A = Z+N
    out = 2*mcscript.utils.CoefficientDict({  # overall factor of 2 from tz vs. \tau_0
        "U[r2Y2tz]": 1-2/A,
        "V[rtz,r]": -2*math.sqrt(15/(8*math.pi))/A,
        "V[r,rtz]": -2*math.sqrt(15/(8*math.pi))/A
        })
    out += mcscript.utils.CoefficientDict({
        "U[r2Y2]": (Z-N)/A**2,
        "V[r,r]": 2*math.sqrt(15/(8*math.pi))*(Z-N)/A**2
        })
    return out

def Qpintr(nuclide):
    """Two-body intrinsic proton quadrupole operator.

    Arguments:
        nuclide (tuple of int): nuclide N and Z

    Returns:
        CoefficientDict containing coefficients for Qpintr operator.
    """
    out = (Qintr(sum(nuclide)) + Qivintr(nuclide))/2
    return out

def Qnintr(nuclide):
    """Two-body intrinsic neutron quadrupole operator.

    Arguments:
        nuclide (tuple of int): nuclide N and Z

    Returns:
        CoefficientDict containing coefficients for Qnintr operator.
    """
    out = (Qintr(sum(nuclide)) - Qivintr(nuclide))/2
    return out


################################################################
# standard Hamiltonian
################################################################

def Hamiltonian(
        A, hw, a_cm=0., hw_cm=None, use_coulomb=True, hw_coul=None, hw_coul_rescaled=None,
        **kwargs,
):
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
# J filter term for Hamiltonian
################################################################

def J_filter_term(
        M, energy_shift, mode=modes.JFilterMode.kEnabled, delta_J=1.0
):
    """Shift term (~J^2) to add to Hamiltonian to filter out higher-J states.

    Arguments:

        M (float): M quantum number for run

        energy_shift (float): energy shift for next higher M in J filtered run

        mode (modes.JFilterMode, default modes.JFilterMode.kEnabled): selection mode for which M
            runs are subject to J filtering (kEnabled, kDisabled, kM0Only)

        delta_J (int, default 1.0): difference to next higher angular momentum of interest

    Returns:

        CoefficientDict containing coefficients for Hamiltonian.
    """

    if mode==modes.JFilterMode.kEnabled or (mode==modes.JFilterMode.kM0Only and M==0.0):
        coefficient = utils.J_sqr_coefficient_for_energy_shift(M, energy_shift, delta_J=delta_J)
        term = coefficient*(J2() - M*(M+1)*identity())
    else:
        term = mcscript.utils.CoefficientDict()

    return term


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
    # coulomb component
    if "VC" in tb_observable_sets:
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
    # intrinsic electromagnetic operators
    if "intrinsic-E0" in tb_observable_sets:
        targets[(0,0,0)]["E0p"] = rp2intr(nuclide=nuclide)
        targets[(0,0,0)]["E0n"] = rn2intr(nuclide=nuclide)
    if "intrinsic-M1" in tb_observable_sets:
        # sqrt(3/4pi) comes from the normalization of the spherical harmonics
        targets[(1,0,0)]["M1"] = M1intr(nuclide=nuclide)
        targets[(1,0,0)]["DLp"] = math.sqrt(3/(4*math.pi))*Lpintr(nuclide=nuclide)
        targets[(1,0,0)]["DLn"] = math.sqrt(3/(4*math.pi))*Lnintr(nuclide=nuclide)
        targets[(1,0,0)]["DSp"] = math.sqrt(3/(4*math.pi))*Sp()
        targets[(1,0,0)]["DSn"] = math.sqrt(3/(4*math.pi))*Sn()
    if "intrinsic-E2" in tb_observable_sets:
        targets[(2,0,0)]["E2p"] = Qpintr(nuclide=nuclide)
        targets[(2,0,0)]["E2n"] = Qnintr(nuclide=nuclide)

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
        xform_truncation_int = task.get("xform_truncation_int")
        if VNN_filename is None:
            VNN_filename = environ.find_interaction_file(
                task["interaction"],
                task["truncation_int"],
                task["hw_int"]
            )

        if task["basis_mode"] is modes.BasisMode.kDirect and xform_truncation_int is None:
            tbme_sources["VNN"] = dict(filename=VNN_filename)
        else:
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
        xform_truncation_coul = task.get("xform_truncation_coul")
        if VC_filename is None:
            use_isoscalar_coulomb = task.get("use_isoscalar_coulomb")
            if use_isoscalar_coulomb is True:
                VC_filename = environ.find_interaction_file(
                    "VCis",
                    task["truncation_coul"],
                    task["hw_coul"]
                )
            else:
                VC_filename = environ.find_interaction_file(
                    "VC",
                    task["truncation_coul"],
                    task["hw_coul"]
                )
        if task["basis_mode"] in (modes.BasisMode.kDirect, modes.BasisMode.kDilated) and xform_truncation_coul is None:
            tbme_sources["VC_unscaled"] = dict(filename=VC_filename)
        else:
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
