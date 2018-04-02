""" input.py -- Define default parameters for ncci module.

    Patrick J. Fasano, Mark A. Caprio
    University of Notre Dame

    + 01/05/18 (pjf): Created, documentation moved from __init__.py.
"""

import mcscript.exception

from . import (
    mfdn_v15,
    modes,
    operators,
    )

# singleton instance for marking required parameters
_k_required = object()

_default_task_dict = {
    ################################################################
    # nuclide parameters
    ################################################################
    "nuclide": (2, 2),  # (tuple of int) (Z,N) tuple

    ################################################################
    # basis parameters
    ################################################################
    "basis_mode": modes.BasisMode.kDirect,
    # (BasisMode) enumerated value indicating direct oscillator
    # (modes.BasisMode.kDirect), dilated oscillator (modes.BasisMode.kDilated),
    # or generic run mode (modes.BasisMode.kGeneric), as explained further in
    # modes.BasisMode

    "hw": 20.,
    # (float) hw of basis

    ################################################################
    # Hamiltonian parameters
    ################################################################
    "interaction": "Daejeon16",
    # (string) name for interaction (for use in descriptor and filenames)

    "use_coulomb": True,
    # (bool) whether or not to include Coulomb

    "a_cm": 0.,
    # (float) coefficient of N_cm for Lawson term

    "hw_cm": None,
    # (float) hw of N_cm for Lawson term
    #   None: use hw of basis

    "hamiltonian": None,
    # (CoefficientDict) specification of Hamiltonian as a CoefficientDict of
    # two-body operators passed as sources to h2mixer (see mfdn.operators)
    #   None: use standard H = Tintr + VNN + a_cm*N_cm

    ################################################################
    # input TBME parameters
    ################################################################
    "truncation_int": ("tb", 10),
    # (tuple) input interaction TBME cutoff, as tuple ("ob"|"tb", N)

    "hw_int": 20.,
    # (float) hw of basis for source interaction TBMEs

    "truncation_coul": ("tb", 10),
    # (tuple) input Coulomb TBME cutoff, as tuple ("ob"|"tb",N)

    "hw_coul": 20,  # (float): hw of basis for source Coulomb TBMEs

    ################################################################
    # transformation parameters
    ################################################################
    "xform_truncation_int": None,
    # (tuple, optional) transform cutoff for interaction, as tuple ("ob"|"tb",N)
    #  None: no truncation before h2mixer transformation

    "xform_truncation_coul": None,
    # (tuple, optional) transform cutoff for Coulomb, as tuple ("ob"|"tb",N)
    #  None: no truncation before h2mixer transformation

    "hw_coul_rescaled": None,
    # (float) hw to which to rescale Coulomb TBMEs before two-body
    # transformation
    #   None: use hw of basis
    # Suggested values:
    #   - direct oscillator run: naturally same as hw to avoid any two-body transformation
    #   - dilated oscillator run: naturally same as hw to avoid any two-body
    #     transformation, but one could also prefer hw_int for uniformity in the
    #     two-body transformation (at the expense of introducing some
    #     transformation error in the Coulomb interaction)
    #   - generic run: naturally same as hw_int for uniformity in the two-body transformation

    "target_truncation": None,
    # (tuple) truncation of target TBMEs, as weight_max tuple
    #   None: deduce automatically from single-particle and many-body truncation information

    ################################################################
    # truncation parameters
    ################################################################
    "sp_truncation_mode": modes.SingleParticleTruncationMode.kNmax,
    # (modes.SingleParticleTruncationMode) enumerated value indicating
    # single-particle basis truncation; see docstring of
    # SingleParticleTruncationMode for information.

    "mb_truncation_mode": modes.SingleParticleTruncationMode.kNmax,
    # (modes.ManyBodyTruncationMode) enumerated value indicating many-body basis
    # truncation; see docstring of ManyBodyTruncationMode for information.

    "truncation_parameters": {"Nv": 0, "Nmax": 2, "Nstep": 2, "M": 0},
    # (dict) truncation parameters, specific to each enumerated truncation type;
    # see docstrings of SingleParticleTruncationMode and ManyBodyTruncationMode
    # for full documentation

    ################################################################
    # diagonalization parameters
    ################################################################
    "eigenvectors": 6,
    # (int) number of eigenvectors to calculate

    "max_iterations": 200,
    # (int) maximum number of diagonalization iterations

    "tolerance": 1e-6,
    # (float) diagonalization tolerance parameter

    "ndiag": 0,
    # (int) number of spare diagonal nodes (MFDn v14 only)

    "partition_filename": None,
    # (str) filename for partition file to use with MFDn
    #   None: no partition file
    # NOTE: for now absolute path is required, but path search protocol may
    # be restored in future

    ################################################################
    # obdme parameters
    ################################################################
    "obdme_multipolarity": 2,
    # (int) maximum multipolarity for calculation of densities

    "obdme_reference_state_list": None,
    # (list) list of reference states (J,g,i) for density calculation

    "save_obdme": True,
    # (bool) whether or not to save obdme files in archive

    "ob_observables": [],
    # (list) list of operators (type, order) to calculate, e.g. [('E',2),('M',1)]

    ################################################################
    # two-body observables
    ################################################################
    "tb_observables": [],
    # (list of ("basename", CoefficientDict) tuples) additional observable definitions
    # (see mfdn.operators)

    "observable_sets": [],
    # (list of str) codes for predefined observable sets to include:
    #   "H-components": Hamiltonian terms
    #   "am-sqr": squared angular momenta
    #   "isospin": isospin observables
    #   "R20K20": center-of-mass diagnostic observables (TODO)

    ################################################################
    # wavefunction storage
    ################################################################
    "save_wavefunctions": False,
    # (bool) whether or not to save smwf files in (separate) archive

    ################################################################
    # version parameters
    ################################################################
    "h2_format": 15099,
    # (int) h2 file format to use (values include: 0, 15099)

    "mfdn_executable": "v15-beta00/xmfdn-h2-lan",
    # (string) mfdn executable name

    "mfdn_driver": mfdn_v15,
    # (module) mfdn driver module

    ################################################################
    # natural orbital parameters
    ################################################################
    "natural_orbitals": False,
    # (bool) enable/disable natural orbitals

    "natorb_base_state": 1,
    # (int) MFDn sequence number of state off which to
    # build natural orbitals
}
# legacy keys:
# "Mj" -> truncation_parameters["M"]
# "initial_vector" -> removed

# implicit values that are defined by other parameters
_implicit_value_map = {
    "hw_cm": "hw",
    "xform_truncation_int": "truncation_int",
    "xform_truncation_coul": "truncation_coul",
    "hw_coul_rescaled": "hw",
}


def fill_default_values(task):
    """Fill default options for task dictionary.

    Raises ScriptError on missing required value.
    """
    # loop over default values and insert them if missing
    for (key, value) in _default_task_dict.items():
        if key not in task:
            if value is _k_required:
                raise mcscript.exception.ScriptError(
                    "task dictionary missing required key {:s}".format(key)
                    )
            else:
                task[key] = value

    # loop over defaults which are defined implicitly
    for (target_key, source_key) in _implicit_value_map.items():
        if task[target_key] is None:
            task[target_key] = task[source_key]
