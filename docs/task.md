# Task dictionary specification #

Patrick J. Fasano, Mark A. Caprio
University of Notre Dame

+ 01/05/18 (pjf): Created, documentation moved from `__init__.py`.
+ 04/02/18 (pjf): Moved to `input.md`.
+ 11/01/23 (slv): Added descriptions of parameters required for menj mode of MFDn

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

- `hamiltonian_rank`: `int`, optional
  - particle rank of the Hamiltonian
  - default is `2` for two body interactions
  - `3` for including three body interactions

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

- `eigenvectors`: `int`, optional
  - number of eigenvectors to calculate
  - must be positive (nonzero!) to avoid failure of MFDn
  - for decomposition run, the value is largely irrelevant, but does
    control how many eigenvalues are shown in the Lanzos convergence diagonostic
    output, which may be useful in test runs
  - If `None`, defaults to `4`.

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

- `save_tbme`: `bool`, optional
  - whether or not to save Hamiltonian (and other operator) tbme files in archive
  - this is useful if you wish to "set up" an MFDn run, by generating the tbme files,
    then hand them off to someone else to do an unscripted run
  - defaults to not saving

- `save_obdme`: `bool`, optional
  - whether or not to save obdme files in archive
  - defaults to not saving

- `save_wavefunctions`: `bool`, optional
  - whether or not to save smwf files in (separate) archive
  - defaults to not saving

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

----------------------------------------------------------------
## menj parameters ##

- `mfdn_variant`: `member of class VariantMode` required
  - there are two different VariantMode to choose.
    ncci.modes.VariantMode.kH2 or ncci.modes.VariantMode.kMENJ
  - certain features of MFDn related to two body observables (for H2 runs)
    work only if kH2 is selected.

- `EMax` : `int`
  - max energy quanta for 2 body truncation
  - this number has to match with the me2j, me3j, trel and rsq interaction
    files that are to be read.

- `E3Max` : `int`
  - Max energy quanta for 3 body truncation
  - this number has to match with the me2j, me3j, trel and rsq interaction
    files that are to be read.

- `me2j_file_id` : `str`
  - file ID of the me2j interaction file.(This is part of the me2j
    interaction filename)
  - part of this string contains the SRG flow parameter

- `me3j_file_id` : `str`
  - file ID of the me3j interaction file.(This is part of the me3j
    interaction filename)
  - part of this string contains the SRG flow parameter

- `use_3b` : `bool`
  - if enabled 3 body interactions are also read


