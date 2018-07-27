# Task dictionary specification #

Patrick J. Fasano, Mark A. Caprio
University of Notre Dame

+ 01/05/18 (pjf): Created, documentation moved from `__init__.py`.
+ 04/02/18 (pjf): Moved to `input.md`.

----------------------------------------------------------------
## nuclide parameters ##

- `nuclide`: tuple of `int`
  -  (Z,N) tuple

----------------------------------------------------------------
## basis parameters ##

- `basis_mode`: `modes.BasisMode`
  + enumerated value indicating direct oscillator
    (`modes.BasisMode.kDirect`), dilated oscillator (`modes.BasisMode.kDilated`),
    or generic run mode (`modes.BasisMode.kGeneric`), as explained further in
    `modes.BasisMode`

- `hw`: `float`
  -  hw of basis

----------------------------------------------------------------
## Hamiltonian parameters ##

- `interaction`: `str`
  - name for interaction (for use in descriptor and filenames)

- `use_coulomb`: `bool`
  - whether or not to include Coulomb

- `a_cm`: `float`
  - coefficient of N_cm for Lawson term

- `hw_cm`: `float`, optional
  - hw of N_cm for Lawson term
  - If `None`, use hw of basis

- `hamiltonian`: `CoefficientDict`
  - specification of Hamiltonian as a `CoefficientDict` of
    two-body operators passed as sources to h2mixer (see `mfdn.operators`)
  - If `None`, use standard H = Tintr + VNN + a_cm*N_cm

----------------------------------------------------------------
## input TBME parameters ##

- `interaction_file`: `str`
  - path to h2 file for input interaction
  - shell expansions like `~` and `${VAR}` are supported

- `truncation_int`: truncation tuple
  - input interaction TBME cutoff, as tuple `("ob"|"tb", N)`

- `hw_int`: `float`
  - hw of basis for source interaction TBMEs

- `coulomb_file`: `str`
  - path to h2 file for input Coulomb interaction
  - shell expansions like `~` and `${VAR}` are supported

- `truncation_coul`: truncation tuple
  - input Coulomb TBME cutoff, as tuple `("ob"|"tb",N)`

- `hw_coul`: `float`
  - hw of basis for source Coulomb TBMEs

----------------------------------------------------------------
## transformation parameters ##

- `xform_truncation_int`: truncation tuple, optional
  - transform cutoff for interaction, as tuple `("ob"|"tb",N)`
  - If `None`, no truncation before h2mixer transformation

- `xform_truncation_coul`: truncation tuple, optional
  - transform cutoff for Coulomb, as tuple `("ob"|"tb",N)`
  - If `None`, no truncation before h2mixer transformation

- `hw_coul_rescaled`: `float`
  - hw to which to rescale Coulomb TBMEs before two-body transformation
  - If `None`, use hw of basis
  - Suggested values:
    - direct oscillator run: naturally same as hw to avoid any two-body transformation
    - dilated oscillator run: naturally same as hw to avoid any two-body
      transformation, but one could also prefer hw_int for uniformity in the
      two-body transformation (at the expense of introducing some
      transformation error in the Coulomb interaction)
    - generic run: naturally same as hw_int for uniformity in the two-body transformation

- `target_truncation`: weight max tuple
  - truncation of target TBMEs, as weight_max tuple
  - If `None`, deduce automatically from single-particle and many-body truncation information

----------------------------------------------------------------
## truncation parameters ##

- `sp_truncation_mode`: `modes.SingleParticleTruncationMode`
  - enumerated value indicating
    single-particle basis truncation; see docstring of
    `SingleParticleTruncationMode` for information.

- `mb_truncation_mode`: `modes.ManyBodyTruncationMode`
  - enumerated value indicating many-body basis
    truncation; see docstring of `ManyBodyTruncationMode` for information.

- `truncation_parameters`: `dict`
  - truncation parameters, specific to each enumerated truncation type;
    see docstrings of `SingleParticleTruncationMode` and `ManyBodyTruncationMode`
    for full documentation

----------------------------------------------------------------
## diagonalization parameters ##

- `eigenvectors`: `int`
  - number of eigenvectors to calculate

- `max_iterations`: `int`
  - maximum number of diagonalization iterations

- `tolerance`: `float`
  - diagonalization tolerance parameter

- `ndiag`: `int`
  - number of spare diagonal nodes (MFDn v14 only)

- `partition_filename`: `str`, optional
  - (str) filename for partition file to use with MFDn
  - If `None`, no partition file
  - NOTE: for now absolute path is required, but path search protocol may
    be restored in future.

----------------------------------------------------------------
## obdme parameters ##

- `obdme_multipolarity`: `int`
  - maximum multipolarity for calculation of densities

- `obdme_reference_state_list`: list of tuples
  - list of reference states (J, g, i) for density calculation

- `ob_observables`: list of operators
  - list of operators (type, order) to calculate, e.g. `[('E',2),('M',1)]`

----------------------------------------------------------------
## two-body observables ##

- `tb_observables`: list of `("basename", CoefficientDict)` tuples
  - additional observable definitions (see `ncci.operators`)

- `observable_sets`: list of `str`
  - codes for predefined observable sets to include:
    - "H-components": Hamiltonian terms
    - "am-sqr": squared angular momenta
    - "isospin": isospin observables
    - "R20K20": center-of-mass diagnostic observables (TODO)

----------------------------------------------------------------
## storage ##
- `save_obdme`: `bool`
  - whether or not to save obdme files in archive

- `save_wavefunctions`: `bool`
  - whether or not to save smwf files in (separate) archive

----------------------------------------------------------------
## version parameters ##

- `h2_format`: `int`
  - h2 file format to use (values include: 0, 15099)

- `mfdn_executable`: `str`,
  - mfdn executable name

- `mfdn_driver`: module
  - mfdn driver module

----------------------------------------------------------------
## natural orbital parameters ##

- `natural_orbitals`: `bool`
  - enable/disable natural orbitals

- `natorb_base_state`: `int`
  - MFDn sequence number of state off which to
    build natural orbitals
