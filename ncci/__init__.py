"""ncci -- define scripting for NCCI runs

    Mark A. Caprio
    University of Notre Dame

    - 12/14/16 (mac): Created, drawing on ncsm.py (created 2/12/13) and
      shell package example code generate_input.py (created 11/7/16).
    - 12/27/16 (mac): Rough in scripting of MFDn v14 run.
    - 12/29/16 (mac): Complete basic scripting for MFDn v14 oscillator-type runs.
    - 1/22-28/17 (pjf): Implement iterated natural orbitals.
      + Turn k_basis_mode_* into Python enum BasisMode
      + Add TruncationMode enumeration
      + Add FilenameConfiguration to hold filename patterns
      + Updated docs to more clearly differentiate between basis modes and
        truncation modes. Basis modes only control the 0th natural orbital run,
        since the nth (n>0) run is always "generic". Truncation modes control
        which states are included in the single and two-body bases.
      + MFDn is now run in a temporary work/ subdirectory. This ensures that MFDn
        can't get confused by earlier natural orbital runs.
      + Rename save_mfdn_output -> save_mfdn_v14_output.
    - 1/30/17 (mac): Downgrade syntax to python 3.4.
    - 1/31/17 (mac): Fix one-body truncation on Hamiltonian tbme files.
    - 2/3/17 (pjf):
      + Make "xform_truncation_int" and "xform_truncation_coul" optional.
      + Fix save_mfdn_v14_output() when Coulomb is turned off.
      + Fix natural orbital indicator in task_descriptor_7.
    - 2/10/17 (pjf):
      + Fix "fci" -> "-fci" flag
      + Add ndiag parameter to task dictionary.
    - 2/20/17 (pjf): Rename mfdn.py -> mfdn/__init__.py
    - 3/17/17 (pjf): Split mfdn/__init__.py into submodules.
    - 7/31/17 (pjf): Add mfdn_driver field.
    - 8/11/17 (pjf):
      + Replace TruncationMode with SingleParticleTruncationMode and ManyBodyTruncationMode.
      + Replace truncation_mode key with sp_truncation_mode and mb_truncation_mode.
      + Fix FCI truncation.
    - 09/22/17 (pjf): Take "observables" as list of tuples instead of dict.
    - 09/24/17 (pjf): Add option to save wavefunctions for postprocessing.
    - 10/25/17 (pjf): Rename "observables" to "tb_observables".
    - 12/19/17 (pjf): Rename mfdn back to ncci
"""

__ALL__ = ['descriptors', 'handlers', 'radial', 'operators', 'tbme', 'utils', 'modes', 'environ']
from . import descriptors, handlers, radial, operators, tbme, utils, modes, postprocessing, environ

if (__name__ == "__MAIN__"):
    pass
