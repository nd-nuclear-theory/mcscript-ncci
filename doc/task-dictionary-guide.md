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
+ 10/22/24 (mac): Update descriptions of version parameters.
+ 04/04/25 (mac): Add descriptions for parameters `calculate_obdme`,
    `calculate_tbo`, and `mfdn_inputlist`.
+ 04/09/25 (mac): Add descriptions of postprocessing parameters.
+ 07/21/25 (mac): Update descriptions of decomposition parameters, to add
    postprocessor-like wf selection parameters.

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
  - can also take form `(N1max, N2max)`, e.g., `(13,14)` would be a typical
    truncation for a p-shell Nmax=12 Hamiltonian
  - used in constructing h2 filename for interaction
  - also determines orbitals used for representing interaction

- `hw_int`: `float`
  - hw of basis for source interaction TBMEs

- `coulomb_file`: `str`
  - path to h2 file for input Coulomb interaction
  - shell expansions like `~` and `${VAR}` are supported

- `truncation_coul`: truncation tuple
  - input Coulomb TBME cutoff, as tuple `("ob"|"tb",N)`
  - can also take form `(N1max, N2max)`, e.g., `(13,14)` would be a typical
    truncation for a p-shell Nmax=12 Hamiltonian
  - used in constructing h2 filename for Coulomb interaction
  - also determines orbitals used for representing Coulomb interaction

- `hw_coul`: `float`
  - hw of basis for source Coulomb TBMEs

----------------------------------------------------------------
## TBME transformation and output parameters ##

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

- `target_truncation`, optional: weight_max tuple
  - truncation of target TBMEs, as tuple `("ob"|"tb",N)`, or other weight_max
    tuple; see docstring of `utils.weight_max_string` for information
  - If `None`, deduce automatically from single-particle and many-body truncation information

----------------------------------------------------------------
## basis truncation parameters (single-particle and many-body) ##

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

- `wf_source_run_list`: `list[str]`
  - list of runs to search for wave functions (omit initial `run` stem from run
    names)

- `wf_source_selector`: `dict`
  - parameters to select results data providing the bra wf file
  - these are parameters used to distinguish a specific "mesh point" in the set
    of diagonaliztion calculation, but not specific states within that mesh
    point
  - typical keys include `nuclide`, `interaction`, `hw`, and `Nmax`

- `wf_source_res_format`: `str`, optional
  - format specifier for res files in source wf runs
  - this will be used as the `res_format` argument to `mfdnres.input.slurp_res_files`
  - it should thus be the identifier for one of the res file formats registered
    with `mfdnres.input.register_data_format`, typically defined in
    `mfdnres.data_parsers`, e.g., `'mfdn_v15'`
  - defaults to `None`

- `wf_source_glob_pattern`: `str`, optional
  - glob pattern to filter the res files to be read as specifying available
    source wave functions
  - defaults to `'*.res'`

- `decomposition_qn`: tuple
  - state (J, g, i) to use as pivot vector for Lanczos decomposition [i.e., ith
    state of angular momentum J and parity (-)^g, as determined from the source
    run's res file]

- `wf_source_run_descriptor`: `tuple[str,str]`, optional
  - for manual selection of a specific wave function, the run and descriptor can
    instead be explicitly specified as a tuple
  - this will take precedence over searching via the `wf_run_list` and
    `wf_source_selector` parameters
  - for example: `("mfdn13",
    "Z3-N3-Daejeon16-coul1-hw15.000-a_cm50-Nmax04-Mj1.0-lan600-tol1.0e-06")`

The following deprecated parameters are still supported for compatibility with
older run scripts:

- `wf_source_info`: dict
  - DEPRECATED: instead, use `wf_source_run_list` and `wf_source_selector`
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

- `source_wf_qn`: tuple
  - DEPRECATED: instead, use `qn`


----------------------------------------------------------------
## obdme parameters ##

- `calculate_obdme`: `bool`
  - whether or not to enable calculation of OBDMEs in MFDn
  - also thus controls calculation of any native MFDn one-body observables
  
- `obdme_multipolarity`: `int`
  - maximum multipolarity for calculation of densities
  - for `mfdn` runs, this must be large enough to support any one-body operators
    desired to be calculated by `mfdn`, e.g., for M1 or E2 moments
  - for postprocessor runs, this parameter is optional, but serves to:
    + request tabulation of obdmes for extra, higher multipolarities beyond
      those which occur as a byproduct of calculating the one-body observables
      (or are specified by the operator quantum numbers specified in
      `obdme_qn_list`)
    + define the multipolarities for the densities to be converted to tabular
      "dens" format for interchange with other codes (see "convert_obdme" option)
      
- `obdme_reference_state_list`: list of tuples
  - list of reference states (J, g, i) for density calculation

- `ob_observables`: list of operators
  - list of operators (type, order) to calculate, e.g., `[('E',2),('M',1)]`

- `calculate_obdme`: `bool`
  - whether or not to enable calculation of OBDMEs in MFDn

- `convert_obdme`: `bool`
  - whether or not to convert OBDMEs to a simple tabular "dens" format for
    interchange with other codes, e.g., reaction codes (see initial code
    comments in `obme2dens.cpp`)

----------------------------------------------------------------
## two-body observables ##

- `calculate_tbo`: `bool`
  - whether or not to enable calculation of two-body observables in MFDn
  
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
  - h2 file format to use for TBME output files from h2mixer (to serve as input to mfdn or mfdn-transitions)
  - must be an h2 format accepted by that code
  - values include: 0, 15099, 15200

- `h2_extension`: `str`
  - h2 file extension to use for TBME output files from h2mixer (to serve as input to mfdn or mfdn-transitions)
  - values: `"dat"`, `"bin"`

- `mfdn_driver`: module
  - mfdn driver module

- `mfdn_executable`: `str`,
  - mfdn executable name

- `mfdn-transitions_executable`: `str`
  - mfdn-transitions executable name

----------------------------------------------------------------
## natural orbital parameters ##

- `natural_orbitals`: `bool`
  - enable/disable natural orbitals

- `natorb_base_state`: `int`
  - MFDn sequence number of state off which to
    build natural orbitals

----------------------------------------------------------------
## postprocessor parameters ##

- Several keys descrived above in the context of the observable calculation
  phase of MFDn are applicable to postprocessor runs as well, e.g.,
  `ob_observables`, `ob_observable_sets`, `tb_observables`,
  `tb_observable_sets`, `hw`, `obdme_multipolarity`, `save_obdme`.

- `obdme_qn_list`: `list[tuple]`
  - list of tuples (J0,g0,Tz0) specifying operator selection rules between
    initial and final states for which densities should be calculated
  - the resulting state pairs *augment* those for which densities are already to
    be calculated due to operators for any one-body observables being calculated
    (specified via `ob_observables` or `ob_observable_sets`)
  - these are basically the quantum numbers of "phantom" one-body operators, for
    which we want the corresponding densities, even if no such one-body operator
    has been specified

- `wf_source_run_list`: `list[str]`
  - list of runs to search for wave functions (omit initial `run` stem from run
    names)

- `wf_source_bra_selector`: `dict`
  - parameters to select results data providing the bra wf file
  - these are parameters used to distinguish a specific "mesh point" in the set
    of diagonaliztion calculation, but not specific states within that mesh
    point
  - typical keys include `nuclide`, `interaction`, `hw`, and `Nmax`
  
- `wf_source_ket_selector`: `dict`
  - parameters to select results data providing the ket wf file
  - these are parameters used to distinguish a specific "mesh point" in the set
    of diagonaliztion calculation, but not specific states within that mesh
    point
  - typical keys include `nuclide`, `interaction`, `hw`, and `Nmax`

- `wf_source_res_format`: `str`, optional
  - format specifier for res files in source wf runs
  - this will be used as the `res_format` argument to `mfdnres.input.slurp_res_files`
  - it should thus be the identifier for one of the res file formats registered
    with `mfdnres.input.register_data_format`, typically defined in
    `mfdnres.data_parsers`, e.g., `'mfdn_v15'`
  - defaults to `None`

- `wf_source_glob_pattern`: `str`, optional
  - glob pattern to filter the res files to be read as specifying available
    source wave functions
  - defaults to `'*.res'`
  
- `postprocessor_mask`: `list[tuple]`
  - set of masks to apply, each given as a tuple of a mask function and a
    parameter dictionary to provide to that function
  - see docstrings for individual mask functions in `masks.py`

- `postprocessor_reverse_canonicalization`: `bool`, optional
  - apply canonicalization constraint on transitions in the anticanonical
    (qnf>qni) sense, rather than the default canonical (qnf<qni) sense

- `postprocessor_relax_canonicalization`: `bool`, optional
  - allows postprocessor to attempt transitions in both canonical (qnf<qni) and
    anticanonical (qnf>qni) sense
  - this leaves it up to the mask to pick the direction actually calculated (can
    be useful, e.g., for manually selecting the sense of transitions to optimize
    use of the multi-ket capability of the postprocessor)

- `postprocessor_mask_verbose`: `bool`
  - whether or not to print detailed diagonstic information to examine mask operation

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


----------------------------------------------------------------
## pass-through parameters ##

- `mfdn_inputlist` : `dict`
   - additional key-value pairs to pass through to MFDn, e.g., `{"blksize":
     16000}` or `{"observables_only": True}`
