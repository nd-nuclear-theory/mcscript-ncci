# Task dictionary specification #

Patrick J. Fasano, Mark A. Caprio
University of Notre Dame

+ 01/05/18 (pjf): Created, documentation moved from `__init__.py`.
+ 04/02/18 (pjf): Moved to `input.md`.
+ 11/01/23 (slv): Add descriptions of parameters required for menj mode of MFDn.
+ 02/12/24 (zz): For menj, add description for `interaction` and delete `hamiltonian_rank`.
+ 06/20/24 (mac): Add descriptions of decomposition parameters.
+ 09/12/24 (mac): Update descriptions of menj parameters.
+ 09/26/24 (mac): Update descriptions of Hamiltonian parameters.

----------------------------------------------------------------
## nuclide parameters ##

- `nuclide`: tuple of `int`
  -  (Z,N) tuple

----------------------------------------------------------------
## basis parameters ##

- `basis_mode`: `modes.BasisMode`
  - enumerated value indicating direct oscillator (`modes.BasisMode.kDirect`),
    dilated oscillator (`modes.BasisMode.kDilated`), generic run mode
    (`modes.BasisMode.kGeneric`), or shell model mode
    (`modes.BasisMode.kShellModel`), as explained further in `modes.BasisMode`
  - see also truncation parameters section for additional parameters
    (`sp_truncation_mode`, `mb_truncation_mode`, etc.) which serve to define the
    basis

- `hw`: `float`
  -  hw of basis

----------------------------------------------------------------
## Hamiltonian parameters ##

- `interaction`: `str`
  - name for interaction
    + used in generating task descriptor
    + used in constructing interaction filename, assuming it is of the
      "standard" form `<interaction>-<truncation>-<hw>.{dat,bin}`, e.g.,
      `JISP16-tb-6-20.0.bin`
  - for menj (optional): override interaction name to be used in descriptor,
    which otherwise defaults to an interaction name automatically constructed by
    combining `me2j_file_id` and `me3j_file_id`

- `use_coulomb`: `bool`
  - whether or not to add an explicit point-proton Coulomb potential to the
    given internucleon interaction

- `a_cm`: `float`
  - coefficient of N_cm operator for Lawson term (a_cm*N_cm)
  - related to traditional (dimensionful) lambda parameter, at any given hw, by
    a factor of hw
  - for illustrations of its effect, see, e.g., Figs. 8-9 of PRC 86, 034312
    (2012) [http://dx.doi.org/10.1103/PhysRevC.86.034312]

- `hw_cm`: `float`, optional
  - hw of N_cm for Lawson term
  - If `None`, use hw of basis

- `include_ke`: `bool`, optional
  - whether or not to include the usual (intrinsic) kinetic energy term (Tintr)
    in constructing the Hamiltonian (see `ncci.operators.tb.Hamiltonian`)
  - defaults to `True`
  - provides the ability to "turn off" the explicit kinetic energy if the
    provided "interaction" TBME file already actually contains a complete
    A-specific two-body Hamiltonian (e.g., from IM-SRG)

- `tbme_scaling_power`: `float`, optional
  - exponent for phenomenological scaling of shell model Hamiltonian TBMEs, typically `0.3`
  - used only with phenomenological shell model Hamiltonian

- `hamiltonian`: `CoefficientDict`, optional
  - specification of Hamiltonian as a `CoefficientDict` of
    two-body operators,  passed as sources to h2mixer (see `ncci.operators.tb`)
  - if `None`, the Hamiltonian defaults either to the generic NCCI Hamiltonian H
    = Tintr + VNN + a_cm*N_cm (see `ncci.operators.tb.Hamiltonian`) or the
    generic shell model Hamiltonian H = Hmf + Vres (see
    `ncci.operators.tb.ShellModelHamiltonian`), depending on `basis_mode`


## input TBME parameters ##

- `interaction_file`: `str`
  - path to h2 file for input interaction
  - shell expansions like `~` and `${VAR}` are supported

- `truncation_int`: truncation tuple
  - input interaction TBME cutoff, as tuple `("ob"|"tb", N)`
  - used in constructing h2 filename for interaction
  - also determines orbitals used for representing interaction

- `hw_int`: `float`
  - hw of basis for source interaction TBMEs

- `coulomb_file`: `str`
  - path to h2 file for input Coulomb interaction
  - shell expansions like `~` and `${VAR}` are supported

- `truncation_coul`: truncation tuple
  - input Coulomb TBME cutoff, as tuple `("ob"|"tb",N)`
  - used in constructing h2 filename for Coulomb interaction
  - also determines orbitals used for representing Coulomb interaction

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

- `hw_coul_rescaled`: `float`, optional
  - hw to which to rescale Coulomb TBMEs before two-body transformation
  - If `None`, use hw of basis
  - Suggested values:
    - direct oscillator run: naturally same as `hw` to avoid any two-body transformation
    - dilated oscillator run: naturally same as `hw` to avoid any two-body
      transformation, but one could also prefer `hw_int` for uniformity in the
      two-body transformation (at the expense of introducing some
      transformation error in the Coulomb interaction)
    - generic run: naturally same as `hw_int` for uniformity in the two-body transformation

- `target_truncation`, optional: weight max tuple
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
  - truncation parameters, specific to each enumerated truncation type; see
    docstrings of `modes.SingleParticleTruncationMode` and
    `modes.ManyBodyTruncationMode` for full documentation

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
## decomposition parameters ##

- `decomposition_type`: str
   - identifier for decomposition operator
   - used here just to define the decomposition label in the task descriptor
   - but typically will be the same identifier used in as an argument to
     ncci.decomposition.decomposition_operator() to construct the decomposition
     operator to feed into MFDn as the "hamiltonian"

- `source_wf_qn`: tuple
  - state (J, g, i) to use as pivot vector for Lanczos decomposition [i.e., ith
    state of angular momentum J and parity (-)^g, as determined from the source
    run's res file]

- `wf_source_info`: dict
  - information used to locate the wave function file for the state to decompose
  - this information is used to construct the run directory name and then the task descriptor for the specific task
  - the corresponding res file is then read in and parsed (to obtain the sequence number for the target state)
  - and the eigenvector for the correponsing sequence number is used as the Lanczos pivot
  - `run`: str
    - run directory in which to search for res and wf files
  - `descriptor`: callable
    - function used to construct a descriptor from a given task dictionary,
      e.g., `ncci.descriptors.task_descriptor_7`
  - the remaining fields are passed through in the "task dictionary" given to
    the task descriptor function, to construct the wf descriptor
  - the values of several of these fields (e.g., `nuclide`, `interaction`) will
    generally duplicate the values appearing in the task dictionary for the
    present decomposition run, where instead they are used to construct the
    descriptor for the present decomposition run

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
## postprocessor parameters ##

TODO 03/21/24 (mac): postprocessor parameters need to be documented

- `postprocessor_reverse_canonicalization`: `bool`, optional
  - apply canonicalization constraint on transitions in the anticanonical
    (qnf>qni) sense, rather than the default canonical (qnf<qni) sense

- `postprocessor_relax_canonicalization`: `bool`, optional
  - allows postprocessor to attempt transitions in both canonical (qnf<qni) and
    anticanonical (qnf>qni) sense
  - this leaves it up to the mask to pick the direction actually calculated (can
    be useful, e.g., for manually selecting the sense of transitions to optimize
    use of the multi-ket capability of the postprocessor)

----------------------------------------------------------------
## menj parameters ##

- `mfdn_variant`: `modes.VariantMode`, optional
  - there are two different VariantMode to choose
    ncci.modes.VariantMode.kH2 (default) or ncci.modes.VariantMode.kMENJ
  - certain features of MFDn related to two-body observables (for H2 runs)
    work only if kH2 is selected

- `EMax` : `int`
  - maximum oscillator quanta for 2 body truncation (a.k.a. N2max)
  - it is assumed that the me2j files are in triangular truncation, so that
    eMax=EMax (i.e., N1max=N2max) (see call to ME2J_Init in menj.c)
  - this number is used to construct the "eMax{:d}_EMax{:d}" portion of the filename for
    the me2j interaction, trel, and rsq files to be read  (e.g., E3ax=12 give "eMax12_EMax12")

- `E3Max` : `int`
  - maximum oscillator quanta for 3-body truncation
  - it is assumed that the me3j files are in triangular truncation, so that
    eMax=E3Max (i.e., N1max=N3max) (see call to ME3J_Init in menj.c)
  - this number is used to construct the `eMax{:d}_EMax{:d}` portion of the
    filename for the me3j interaction file to be read (e.g., for E3Max=12 give
    `eMax12_EMax12`)

- `me2j_file_id` : `str`
  - base part of the filename for the me2j interaction file
  - this part typically identifies the interaction and SRG flow parameter
  - it does not contain the truncation or hw parameters

- `me3j_file_id` : `str`
  - base part of the filename for the me3j interaction file
  - this part typically identifies the interaction and SRG flow parameter
  - it does not contain the truncation or hw parameters

- `use_3b` : `bool`
  - whether or not 3-body interactions are to be read and included in the Hamiltonian


