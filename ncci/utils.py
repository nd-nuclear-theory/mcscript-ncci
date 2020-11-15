"""utils.py -- helper functions for MFDn runs

    - 02/20/17 (pjf): Created, extracted from mfdn.py.
    - 09/05/19 (pjf): Add Nv_for_nuclide.
    - 06/03/20 (pjf): Add check_natorb_base_state.
    - 11/13/20 (pjf): Move physical constants to separate module.
"""

import math

import mcscript

from . import constants

################################################################
# utility calculations
################################################################

def weight_max_string(truncation):
    """Convert (rank,cutoff) to "wp wn wpp wnn wpn" string.

    Valid truncations:
        ("ob",w1b)
        ("tb",w2b)
        (w1b,w2b)
        (wp,wn,wpp,wnn,wpn) -- TODO

    >>> weight_max_string(("ob",4))
        "4 4 8 8 8"
    >>> weight_max_string(("tb",4))
        "4 4 4 4 4"
    """
    if (truncation[0] == "ob"):
        (code, N) = truncation
        cutoffs = (N, N, 2*N, 2*N, 2*N)
    elif (truncation[0] == "tb"):
        (code, N) = truncation
        cutoffs = (N, N, N, N, N)
    elif (len(truncation) == 2):
        (w1, w2) = truncation
        cutoffs = (w1, w1, w2, w2, w2)
    elif (len(truncation) == 5):
        cutoffs = truncation

    return "{0[0]} {0[1]} {0[2]} {0[3]} {0[4]}".format(cutoffs)


def oscillator_length(hw):
    """Calculate oscillator length for given oscillator frequency.

    b(hw) = (hbar c)/[(m_N c^2) (hbar omega)]^(1/2)

    Arguments:
        hw (numeric): hbar omega in MeV

    Returns:
        (float): b in fm
    """
    return constants.k_hbar_c/math.sqrt(constants.k_mN_csqr*hw)


def natural_orbital_indicator(natural_orbital_iteration):
    """Construct natural orbital indicator string."""
    if (natural_orbital_iteration is None):
        indicator = ""
    else:
        indicator = "-no{:1d}".format(natural_orbital_iteration)
    return indicator

################################################################
# shell model Nv
################################################################

def Nv_for_nuclide(nuclide):
    """Calculate oscillator quantum number of valence shell for given nuclide.

    Arguments:
        nuclide (tuple): (Z,N) for nuclide

    Returns:
        Nv (int): oscilllator quantum number for valence shell
    """

    # each major shell eta=2*n+l (for a spin-1/2 fermion) contains (eta+1)*(eta+2) substates

    Nv = 0
    for species_index in (0,1):
        num_particles = nuclide[species_index]
        eta=0
        while(num_particles>0):
            # discard particles in shell
            shell_degeneracy = (eta+1)*(eta+2)
            num_particles_in_shell = min(num_particles,shell_degeneracy)
            num_particles -= num_particles_in_shell

            # update Nv
            Nv = max(Nv, eta)

            # move to next shell
            eta += 1

    return Nv

################################################################
# consistency checks
################################################################

def check_natorb_base_state(task):
    """Perform sanity checks on natural orbital base state quantum numbers."""
    natorb_base_state = task.get("natorb_base_state")
    try:
        (J, g, n) = natorb_base_state
        M = task["truncation_parameters"]["M"]
    except TypeError:
        raise mcscript.exception.ScriptError(
            "invalid natorb_base_state: {}".format(natorb_base_state))
    if (J < abs(M)) or (abs(int(2*J)%2) != abs(int(2*M)%2)):
        raise mcscript.exception.ScriptError(
            "invalid natorb base state J={:3.1f} M={:3.1f}".format(J,M)
        )
    if g not in (0,1):
        raise mcscript.exception.ScriptError(
            "invalid natorb base state g={}".format(g)
        )
