# Summary of example run scripts #

05/09/23 (mac): Expand setup instructions.  Eliminate --here from example qsubm
invocations.

05/31/23 (mac): Add perlmutter-cpu parallel environment example.

09/30/23 (mac): Add perlmutter-gpu parallel environment example.

08/20/24 (mac): Add runmfdn16 sd-shell example.

12/06/24 (mac): Move runs runmfdn12 and earlier to legacy.

04/16/25 (mac): Rearrange postprocessor runs into tutorial sequence.

06/19/25 (mac): Update example paths and add threading options.

08/19/25 (mac): Add runmfdncounting01 counting run example.

----------------------------------------------------------------

## Setup ##

  - These examples make use of small example input TBME files found in the
    subdirectory `doc/examples/data/h2`.  In order for the scripting to find these input
    files, make sure to set the environment variable `NCCI_DATA_DIR_H2` to
    include that directory.  Please follow the instructions in the "Environment
    configuration" section of `INSTALL.md`.

  - Make sure you are familiar with the principles described in the mcscript
    package's `INSTALL.md` file.  In particular, to run a run script with qsubm,
    you need to create a symlink to the run file from your run
    directory, e.g.,

    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    % cd ${MCSCRIPT_RUN_HOME}
    % ln -s ${HOME}/code/mcscript-ncci/doc/examples/runex01.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Alternatively, you can run these scripts wiht the `examples` directory as
    the current working directory, by adding the `--here` argument to `qsubm`.

  - The examples below are for small runs, run locally on your own computer.
    The example submission command lines given below do not fully illustrate the
    very-important parallel environment parameters for multi-rank MPI
    parallelized runs.  They also omit the queue submission information, which
    varies from one computing system to another.  (Otherwise you'll be trying to
    run MFDn interactively on the front-end machine, which may get people
    yelling at you -- although at least the Nmax=2 example runs are are not
    computationally demanding.  Moreover, execution may simply fail on a
    front-end machine has a different architecture from the compute nodes, and
    the executable file is not compatible!)

    So first please make sure you are familiar with the principles of running
    jobs on your machine and of doing so properly with `mcscript`.  Some notes
    on submission at NERSC are provided under examples `runmfdn13` and
    `runmfdn13gpu` below.

Recommended basic examples for getting started with standard MFDn NCCI runs:

  - runmfdn13: This runs mfdn, to set up the wave functions you will need for the next two
    examples.

  - runtransitions00: This runs mfdn-transitions, to calculate transitions for
    the wave functions from runmfdn13.

There are also several more specialized examples.  Although a basic summary of
the runs is provided below, please be sure to also see the docstring at the
start of each run script, for further commentary.


## MFDn diagonalization runs ##

  * runmfdn13: harmonic oscillator basis run with MFDn v15 (CPU version)

    6Li Nmax02..04 hw15..20

    For a quick test with just Nmax=2 runs, select

        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        qsubm mfdn13 --pool=Nmax02 --phase=0 --serialthreads=8
        qsubm mfdn13 --pool=Nmax02 --phase=1 --threads=8
        qsubm mfdn13 --pool=Nmax02 --phase=2
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    The command lines above assume, for illustration, that you want OpenMP
    parallelization with 8 threads (e.g., if you are running on a machine with
    at least 8 virtual cores), but you should choose the threading parameters
    appropriately for your system.
 
    The following instead provides an example of a single-node run on a
    computing cluster, namely, NERSC.  First, make sure the appropriate module
    files are loaded for the programming environment for which the code was
    compiled.  Then, for the setup phase:

    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    qsubm mfdn13 debug 30 --phase=0 --pool=Nmax02 --serialthreads=256 --mail-type=END,FAIL
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Then, for the MFDn diagonalization phase:

    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    qsubm mfdn13 debug 30 --phase=1 --pool=Nmax02 --ranks=1 --nodes=1 --threads=32 --mail-type=END,FAIL
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Then, the mop-up phase only involves some file system operations, and it can
    run either in a regular compute cue on the transfer queue:

    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    qsubm mfdn13 xfer 30 --phase=2 --pool=Nmax02 --mail-type=END,FAIL
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    You can use a dependency option (`--dependency=afterok:<job_id>`) to
    sequence these jobs, without having to wait for each one to finish before
    submitting the next one.


  * runmfdn13gpu: harmonic oscillator direct run with MFDn v15 (GPU version)

    For a GPU run, we must disable calculation of one-body observables, since
    these are not yet GPU enabled, and use gpu version of the mfdn executable.
    Otherwise, this example is identical to `runmfdn13` above.
    
    Notes on job submission at NERSC.  The setup phase still should be submitted
    to CPU nodes, as in `runmfdn13` above (be sure to load the appropriate
    module files for the CPU programming environment):

    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    qsubm mfdn13gpu debug 30 --phase=0 --pool=Nmax02 --serialthreads=256 --mail-type=END,FAIL
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Then, for the MFDn diagonalization phase should be submitted to the GPU
    nodes (for this phase, now load the appropriate module files for the GPU
    programming environment):

    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    qsubm mfdn13gpu debug 30 --phase=1 --pool=Nmax02 --node-type=gpu --ranks=1 --nodes=1 --threads=32 --mail-type=END,FAIL --account=<account>
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Notice the `--node-type=gpu` option.  In place of `<account>` you should
    substitute the appropriate GPU allocation repository that the job is to be
    charged to (e.g., `m2032_g`).  And mop-up is the same as in `runmfdn13`
    above:

    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    qsubm mfdn13gpu xfer 30 --phase=2 --pool=Nmax02 --mail-type=END,FAIL
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


  * runmfdn15menj: diagonalization run with MFDn v15 3-body (menj) variant

    - Note: The input interaction files required for this run (including a large
      3-body interaction file) are not provided.


  * runmfdn16: shell model diagonalization runs in sd shell, with MFDn v15 (CPU version)

    18O/20O/18F/19F/20N/25Mg, Wildenthal USD and Brown-Richter USDB interactions

    Usage:

        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        qsubm --pool=ALL --phase=0 mfdn16
        qsubm --pool=ALL --phase=1 mfdn16
        qsubm --pool=ALL --phase=2 mfdn16
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


## mfdn-transitions postprocessing runs ##

  * runtransitions01: postprocessing run with standard M1/E2 "observable sets"

    6Li Nmax02..04, hw15..20

    Example postprocessor run with one-body and two-body observables.  This
    basic example is meant to model a typical production run, covering a range
    of mesh points.  We illustrate here only the use of predefined "observable
    sets", which suffice for common electroweak observables (M1, E2, etc.).
    
    This run uses wave functions created by `runmfdn13`.  Make sure to set
    NCCI_LIBRARY_PATH to include `mcscript-ncci/doc/examples` (see
    `INSTALL.md`).  And make sure to first run `runmfdn13`.

    For a quick test with just Nmax=2 runs

        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        qsubm transitions01 --pool=Nmax02 --phase=0
        qsubm transitions01 --pool=Nmax02 --phase=1
        qsubm transitions01 --pool=Nmax02 --phase=2
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    See `mcscript-ncci/doc/examples/example-output` for example results output.

    Notes on job submission at NERSC.  This provides a simple example of a
    single-node run.  First, make sure the appropriate module files are loaded
    for the programming environment for which the code was compiled.  For the
    setup phase:

    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    qsubm transitions01 debug 30 --phase=0 --pool=Nmax02 --serialthreads=256 --mail-type=END,FAIL
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Then, for the MFDn diagonalization phase:

    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    qsubm transitions01 debug 30 --phase=1 --pool=Nmax02 --ranks=8 --nodes=1 --threads=32 --mail-type=END,FAIL
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Then, the mop-up phase only involves some file system operations, and it can
    run either in a regular compute cue on the transfer queue:

    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    qsubm transitions01 xfer 30 --phase=2 --pool=Nmax02 --mail-type=END,FAIL
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    You can use a dependency option (`--dependency=afterok:<job_id>`) to
    sequence these jobs, without having to wait for each one to finish.

  * runtransitions02: example of explicitly defining one-body and two-body observables

    Here we explicitly construct the intrinsic kinetic energy operator from its
    expression as a sum of one-body and separable two-body terms, e.g, equation
    (4) of "intrinsic" [Caprio, McCoy, Fasano, "Intrinsic operators for the
    translationally-invariant many-body problem", JPG 47, 122001 (2020),
    doi:10.1088/1361-6471/ab9d38].

    We also construct the naive one-body lab-frame kinetic energy operator,
    which will contain a spurious contribution from the zero-point motion of the
    center of mass.


## MFDn counting runs ##

  * runmfdncounting01: counting run
  
      6Li Nmax02..04

      Example counting runs matching the cases (M=0.0/1.0, Nmax=2/4) actually
      run in `runmfdn13`.
      
      - Phase 0: Just count dimension.  This is faster, and has lowest memory
        demands, than a full counting run for dimension and number of nonzeros
        (phase 1 below).  The dimension will be found in the res file.
      
      - Phase 1: Count dimension and number of nonzeros.  This subsumes the simple
        dimension counting run, but takes longer (and has higher memory
        demands). The dimension and number of nonzeros will be found in the res
        file.
      
      - Phase 2: Save wave function indexing information (`mfdn_smwf.info` and
        `mfdn_MBgroups`).  These files may be needed for codes which postprocess
        MFDn wave functions.


## MFDn Lanczos decomposition runs ##

  - See tutorial in `doc/decomposition-tutorial.md`.

  - These examples make use of example decomposition parameter files found in
    the subdirectory `doc/examples/data/decomposition`.  In order for the
    scripting to find these input files, make sure to set the environment
    variable `NCCI_DATA_DIR_DECOMPOSITION` to include that directory.  Please
    follow the instructions in the "Environment configuration" section of
    `INSTALL.md`.

  * runmfdndecomp01: Basic illustration of decomposition using Nex operator.
  
  * runmfdndecomp02: Examples of angular momentum and joint U(3) decompositions.
