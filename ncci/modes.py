"""modes.py -- define configuration options for MFDn scripting

Patrick Fasano
University of Notre Dame

- 03/22/17 (pjf): Created, split from __init__.py.
- 04/07/17 (pjf): Rename Configuration -> Environment.
- 06/03/17 (pjf): Remove dependence of filenames on natural orbital iteration.
- 06/05/17 (pjf): Clean up formatting.
- 08/11/17 (pjf): Split TruncationMode into SingleParticleTruncationMode and
    ManyBodyTruncationMode.
- 08/26/17 (pjf): Add parity flag for WeightMax many-body truncation mode.
- 09/12/17 (mac): Put mfdn executable filename under common mcscript install directory.
- 09/12/17 (pjf): Split config.py -> mode.py + environ.py.
- 09/27/17 (pjf): Add MFDnRunMode options for counting-only modes.
- 01/04/18 (pjf): Add MFDnRunMode kManual for user-provided orbital file.
- 09/07/19 (pjf): Remove Nv from truncation_parameters.
- 10/24/19 (mac): Add MFDnRunMode kLanczosOnly.
- 06/04/23 (mac): Add JFilterMode.
- 09/14/23 (slv): Add VariantMode

"""

import enum

################################################################
# radial basis modes
################################################################

@enum.unique
class BasisMode(enum.Enum):
    """General modes of operation for radial basis

    kDirect:
      - no0 basis is oscillator basis (hw)
      - source basis for VNN is oscillator basis of same
        oscillator length (hw_int=hw); therefore no transformation
        needed on VNN TBMEs
      - Coulomb TBMEs need only scaling for dilation (hw_c -> hw)
      - MFDn can use built-in oscillator OBMEs for observables

    kDilated:
      - no0 basis is oscillator basis (hw)
      - source basis for VNN is oscillator basis of different
        oscillator length; therefore transformation
        needed on VNN TBMEs (hw_int -> hw)
      - Coulomb TBMEs need only scaling for dilation (hw_c -> hw)
      - MFDn can use built-in oscillator OBMEs for observables

    kGeneric:
      - no0 basis is not assumed to be oscillator basis
        (still has nominal hw to define a length parameter)
      - transformation needed on VNN TBMEs (hw_int HO -> hw generic)
      - Coulomb TBMEs may be rescaled (hw_c -> hw_cp) but then need
        transformation (hw_cp HO -> hw generic)
      - MFDn *cannot* use built-in oscillator OBMEs for observables
    """

    kDirect = 0
    kDilated = 1
    kGeneric = 2

################################################################
# J filtering modes
################################################################

@enum.unique
class JFilterMode(enum.Enum):
    """General modes of operation for J filtering

    kEnabled:
      - filter for all M

    kDisabled:
      - do not filter for any M

    kM0Only:
      - filter only for M=0.0
      - for common case where J=0.0 states are obtained from M=0.0 run,
        while all other states are obtained from M=1.0 run, to avoid
        vanishing "parity" Clebsch-Gordan coefficients when calculating
        observable RMEs)
    """

    kDisabled = 0
    kEnabled = 1
    kM0Only = 2


################################################################
# truncation modes
################################################################

@enum.unique
class SingleParticleTruncationMode(enum.Enum):
    """General truncation modes for single-particle basis

    kManual:
        - manually provided orbital file
        - compatible with MFDn v15+
        - "truncation_parameters" (dict) must contain:
            - "sp_filename" (str): full path to orbital file
            - "sp_weight_max" (float): maximum weight for single-particle orbitals

    kNmax:
        - traditional Nmax truncation; weight is (2*n + l)
        - compatible with MFDn v14+
        - "truncation_parameters" (dict) must contain:
            - "Nmax" (int): single-particle excitation oscillator cutoff
                (interpreted as one-body Nmax_orb for "FCI" truncation, or
                many-body excitation cutoff Nmax for "Nmax" truncation)
            - "Nstep" (int): Nstep (2 for single parity, 1 for mixed parity)


    kTriangular:
        - weight is (n_coeff*n + l_coeff*l)
        - compatible with MFDn v15+
        - "truncation_parameters" (dict) must contain:
            - "n_coeff" (float): coefficient in front of n
            - "l_coeff" (float): coefficient in front of l
            - "sp_weight_max" (float): maximum weight for single-particle orbitals

    """

    kManual = 0
    kNmax = 1
    kTriangular = 2


@enum.unique
class ManyBodyTruncationMode(enum.Enum):
    """General truncation modes for many-body basis

    kNmax:
        - traditional Nmax truncation; weight is (2*n + l)
        - compatible with MFDn v14+
        - must be used with SingleParticleTruncationMode.kNmax
        - "truncation_parameters" (dict) must contain:
            - "Nmax" (int): many-body excitation cutoff
            - "Nstep" (int): Nstep (2 for single parity, 1 for mixed parity)
            - "M" (float): M-scheme angular momentum projection value


    kWeightMax:
        - compatible with MFDn v15+
        - "truncation_parameters" (dict) must contain:
            - "mb_weight_max" (float): maximum weight for many-body states
            - "parity" (int): absolute parity for run (+1, 0, or -1)
            - "M" (float): M-scheme angular momentum projection value


    kFCI:
        - compatible with MFDn v14+
        - many-body basis constrained only by single-particle basis
        - "truncation_parameters" (dict) must contain:
            - "parity" (int): absolute parity for run (+1, 0, or -1)
            - "M" (float): M-scheme angular momentum projection value
    """

    kNmax = 1
    kWeightMax = 2
    kFCI = 3


################################################################
# MFDn run modes
################################################################

@enum.unique
class MFDnRunMode(enum.IntEnum):
    """MFDn run mode (IFLAG_mode)

    kNormal: 0, normal MFDn diagonalization run

    kDimension: 1, count basis dimension

    kNonzeros: 3, count nonzero matrix elements

    kLanczosOnly: 4

    """

    kNormal = 0
    kDimension = 1
    kNonzeros = 3
    kLanczosOnly = 4

    
################################################################
# MFDn variant  modes
################################################################

@enum.unique
class VariantMode(enum.IntEnum):
    """MFDn variant mode

    Different compilation variants of MFDn, corresponding to different input
    matrix element formats, require different handling in the scripting.

    kH2: 0, H2 mode 

    kMENJ: 1, MENJ mode

    """
    kH2 = 0
    kMENJ = 1    
