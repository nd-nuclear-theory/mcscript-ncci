"""utils.py -- helper functions for MFDn runs

    - 02/20/17 (pjf): Created, extracted from mfdn.py.
    - 09/05/19 (pjf): Add Nv_for_nuclide.
    - 06/03/20 (pjf): Add check_natorb_base_state.
    - 11/13/20 (pjf): Move physical constants to separate module.
    - 11/14/20 (pjf):
        + Add nuclide_string function.
        + Add N0_for_nuclide function (copied from mfdnres).
    - 12/02/20 (pjf): Allow J<M natorb base states.
    - 07/08/21 (pjf): Check that J of natorb base state matches nuclide.
    - 04/27/22 (pjf): Add hw_from_oscillator_length().
    - 01/03/23 (mac): Add J_sqr_coefficient_for_energy_shift().
    - 07/05/24 (mac): Add partition_filename().
"""

import math
import os

import mcscript.exception

from . import constants


################################################################
# strings for descriptors/filenames
################################################################

def nuclide_string(nuclide, **kwargs):
    """Convert (Z,N) to "ZXX-NXX" string.

    Note: This function can be called directly on a task dict. For example:
    >>> nuclide_string(**task)
        "Z02-N02"

    Arguments:
        nuclide (tuple of int): (Z,N) of nuclide
    """
    return "Z{:02d}-N{:02d}".format(*nuclide)


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


def natural_orbital_indicator(natural_orbital_iteration):
    """Construct natural orbital indicator string."""
    if (natural_orbital_iteration is None):
        indicator = ""
    else:
        indicator = "-no{:1d}".format(natural_orbital_iteration)
    return indicator


################################################################
# oscillator length calculations
################################################################

def oscillator_length(hw):
    """Calculate oscillator length for given oscillator frequency.

    b(hw) = (hbar c)/[(m_N c^2) (hbar omega)]^(1/2)

    Arguments:
        hw (numeric): hbar omega in MeV

    Returns:
        (float): b in fm
    """
    return constants.k_hbar_c/math.sqrt(constants.k_mN_csqr*hw)


def hw_from_oscillator_length(b):
    """Calculate oscillator frequency for given oscillator length.

    hw(b) = (hbar c)^2/[(m_N c^2) (b^2)]

    Arguments:
        b (numeric): oscillator length in fm

    Returns:
        (float): hbar omega in MeV
    """
    return constants.k_hbar_c**2/(constants.k_mN_csqr*b**2)


################################################################
# J^2 term calculation
################################################################

def J_sqr_coefficient_for_energy_shift(M, energy_shift, delta_J=1):
    """Determine coefficient needed on J^2 operator for given energy shift.

    In a J-filtered run of given M, we generally want to shift the J=M+1 states
    upward by at least a given amount relative to the J=M states.  This function
    calculates the coefficient on |J|^2-M*(M+1) needed to accomplish such a
    shift.

    Argument:

        M (float): M for run

        energy_shift (float): desired energy shift

        delta_J (int, optional): difference to next higher angular momentum of interest

    Returns:

        a_J2 (float): coefficient for J^2 operator

    """

    J = M
    Jp = M + delta_J
    a_J2 = energy_shift/(Jp*(Jp+1) - J*(J+1))
    return a_J2


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
# shell model N0
################################################################

def N0_for_nuclide(nuclide):
    """Calculate quanta in lowest oscillator configuration for given nuclide.

    Natural parity grade can then be obtained as N0_for_nuclide(nuclide)%2.

    Inspired by spncci lgi::Nsigma0ForNuclide.

    Arguments:
        nuclide (tuple): (Z,N) for nuclide

    Returns:
        N0 (int): number of quanta
    """

    # each major shell eta=2*n+l (for a spin-1/2 fermion) contains (eta+1)*(eta+2) substates

    N0 = 0;
    for species_index in (0,1):
        num_particles = nuclide[species_index]
        eta=0
        while(num_particles>0):
            # add contribution from particles in shell
            shell_degeneracy = (eta+1)*(eta+2)
            num_particles_in_shell = min(num_particles,shell_degeneracy)
            N0 += num_particles_in_shell*eta

            # discard particles in shell
            num_particles -= num_particles_in_shell

            # move to next shell
            eta += 1

    return N0

################################################################
# consistency checks
################################################################

def check_natorb_base_state(task):
    """Perform sanity checks on natural orbital base state quantum numbers."""
    nuclide = task["nuclide"]
    natorb_base_state = task.get("natorb_base_state")
    try:
        (J, g, n) = natorb_base_state
    except TypeError:
        raise mcscript.exception.ScriptError(
            "invalid natorb_base_state: {}".format(natorb_base_state))
    if round(2*J)%2 != sum(nuclide)%2:
        raise mcscript.exception.ScriptError(
            "invalid natorb base state J={:3.1f}".format(J)
        )
    if g not in (0,1):
        raise mcscript.exception.ScriptError(
            "invalid natorb base state g={}".format(g)
        )

################################################################
# partition filename generation
################################################################

def partition_filename(
        nuclide, Nmax,
        Nshell=None,
        Nshell_for_default_partition=set(range(9, 18+1)),
        Nshell_for_partition_by_A={},
        partition_file_by_Nshell={},
        partition_file_dir="/global/cfs/cdirs/m2032/data/partitioning/v15",
        partition_filename_template_for_default_partition="mfdn_partitioning.info_Nshell{Nshell:02d}",
        partition_filename_template_for_partition_by_A="by-A/A{A:02d}/mfdn_partitioning.info_Nshell{Nshell:02d}",
        verbose=False,
):
    """Deduce partition file to use for given Nmax.

    Assumes partition file to use might depend generically upon Nshell, upon both
    Nshell and A, or be given as a custom override.

    Default filename templates reflect the organization of partition files within the
    ncci-counting repository.

    Arguments:

        nuclide (tuple): (Z,N)

        Nmax (int): Nmax

        Nshell (int, optional): 1-based number of shells for single-particle
        basis (if None, deduced from Nmax for given nuclide)

        Nshell_for_default_partition (set or list, optional): Nshell values for which
        generic (nuclide-independent) default partition files are provided

        Nshell_for_partition_by_A (set or list, optional): Nshell values for which
        A-dependent partition files are provided

        partition_file_by_Nshell (dict, optional): explicit overrides (Nshell -> filename)

        partition_file_dir (str, optional): base directory under which to find partition files

        partition_filename_template_for_default_partition (str, optional):
            fmt template string for filenames of generic (nuclide-independent)
            default partition files (can depend upon template parameter Nshell)

        partition_filename_template_for_partition_by_A (str, optional):
            fmt template string for filenames of A-dependent partition files
            (can depend upon template parameters A and Nshell)

    """
    # deduce parameters
    A = sum(nuclide)
    Nv = Nv_for_nuclide(nuclide)
    if Nshell is None:
        Nshell = Nv+Nmax+1  # 1-based number of shells

    # select partition file
    if Nshell in partition_file_by_Nshell:
        partition_filename = "{}".format(partition_file_by_Nshell[Nshell])
    elif Nshell in Nshell_for_partition_by_A:
        partition_filename = partition_filename_template_for_partition_by_A.format(A=A,Nshell=Nshell)
    elif Nshell in Nshell_for_default_partition:  # fallthrough to generic partition file
        partition_filename = partition_filename_template_for_default_partition.format(Nshell=Nshell)
    else:
        partition_filename = None

    # qualify filename with full path
    if partition_filename is not None:
        partition_filename = os.path.join(partition_file_dir, partition_filename)

    # diagnostic output
    if verbose:
        print("  Nmax {:02d}: Nshell {:02d} -> {}".format(Nmax, Nshell, partition_filename))

    return partition_filename

    
