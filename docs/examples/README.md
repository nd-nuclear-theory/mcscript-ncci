# Summary of example run scripts #

05/09/23 (mac): Expand setup instructions.  Eliminate --here from example qsubm
invocations.

05/31/23 (mac): Add perlmutter-cpu parallel environment example.

09/30/23 (mac): Add perlmutter-gpu parallel environment example.

08/20/24 (mac): Add runmfdn16 sd-shell example.

----------------------------------------------------------------

Setup:

  - These examples make use of small example input TBME files found in the
    subdirectory `example-data`.  In order for the scripting to find these input
    files, make sure to set the environment variable `NCCI_DATA_DIR_H2` to
    include the present example directory.  Please follow the instructions in
    the "Environment configuration" section of `mcscript-ncci/INSTALL.md`.

  - Make sure you are familiar with the principles described in the mcscript
    package's `INSTALL.md` file.  In particular, to run a run script with qsubm,
    you need to create a symlink to the run file from your run
    directory, e.g.,

    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    % cd ${MCSCRIPT_RUN_HOME}
    % ln -s ${HOME}/code/mcscript-ncci/docs/examples/runex01.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Alternatively, you can run these scripts wiht the `examples` directory as
    the current working directory, by adding the `--here` argument to `qsubm`.

  - The example submission command lines given for the individual examples below
    leave off the very-important parallel environment parameters (which we
    estimate using `mfdnmem`).  They also omit the queue submission information,
    which varies from one computing system to another.  (Otherwise you'll be
    trying to run MFDn interactively on the front-end machine, which may get
    people yelling at you -- although at least the Nmax=2 example runs are are
    not computationally demanding.  Moreover, execution may simply fail on a
    front-end machine has a different architecture from the compute nodes, and
    the executable file is not compatible!)

    So first please make sure you are familiar with the principles of running
    jobs on your machine and of doing so properly with `mcscript`.  Some notes
    on submission at NERSC are provided under examples `runmfdn13` and
    `runmfdn13gpu` below.

Recommended examples:

The following set of examples is somewhat encyclopedic, e.g., covering some
older versions of mfdn and some more advanced special features.  The best models
starting point as a model for actual run scripts would be some of the newer
examples:

  - runmfdn13: This runs mfdn, to set up the wave functions you will need for the next two
    examples.

  - runmfdn14: This is an example of doing Lanczos decompositions with mfdn
    (only try this example if such decompositions are of interest to you).

  - runtransitions00: This runs mfdn-transitions, to calculate transitions for
    the wave functions from runmfdn13.

----------------------------------------------------------------

runmfdn07: harmonic oscillator direct run with MFDn v15

    4He Nmax02 hw20 (direct)

    Interaction: example-data

    Usage: qsubm mfdn07

    We use tb-6 from `example-data`. Make sure to set NCCI_DATA_DIR_H2 to include
    `mcscript-ncci/docs/examples` (see `mcscript-ncci/INSTALL.md`).


runmfdn08: harmonic oscillator direct run with MFDn v15 b01

    4He Nmax02 hw20 (direct)

    Interaction: run0164-JISP16-tb-10

    Usage: qsubm mfdn08

    We use tb-10 as the smallest available set of files.  These are not provided
    in `mcscript-ncci/docs/examples`.


runmfdn09: general truncation direct run with MFDn v15

    4He weight=n+l<2.1 hw20 (direct)

    Interaction: run0164-JISP16-tb-10

    Usage: qsubm mfdn09

    We use tb-10 as the smallest available set of files.  These are not provided
    in `mcscript-ncci/docs/examples`.


runmfdn10: counting-only run with MFDn v15

    6He Nmax08 (counting)

    Usage: qsubm mfdn10


runmfdn11: manual orbital direct run with MFDn v15

    4He manual orbital file hw20 (direct)

    Interaction: run0164-JISP16-tb-10

    Usage: qsubm mfdn11

    We use tb-10 as the smallest available set of files.  These are not provided
    in `mcscript-ncci/docs/examples`.


runmfdn12: harmonic oscillator direct run with MFDn v15, plus custom input TBO

    4He Nmax02 hw20 (direct)

    Interaction: example-data

    Usage: qsubm mfdn12

    Uses operator TBMEs from `example-data`.  Make sure to set NCCI_DATA_DIR_H2 to
    include `mcscript-ncci/docs/examples` (see `mcscript-ncci/INSTALL.md`).


runmfdn13: harmonic oscillator direct run with MFDn v15, for use with postprocessor

    6Li Nmax02,Nmax04 hw15,hw20 (direct)

    Interaction: example-data

    Usage:

        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        qsubm --pool=ALL --phase=0 mfdn13
        qsubm --pool=ALL --phase=1 mfdn13
        qsubm --pool=ALL --phase=2 mfdn13
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    or, for a quick test with just Nmax=2 runs, select

        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        qsubm --pool=Nmax02 --phase=0 mfdn13
        qsubm --pool=Nmax02 --phase=1 mfdn13
        qsubm --pool=Nmax02 --phase=2 mfdn13
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Generates wave functions needed for runtransitions00.

    Uses operator TBMEs from `example-data`.  Make sure to set NCCI_DATA_DIR_H2 to
    include `mcscript-ncci/docs/examples` (see `mcscript-ncci/INSTALL.md`).

    See mcscript-ncci/docs/examples/example-results for example results output.

    Notes on job submission at NERSC.  This provides a simple example of a
    single-node run.  First, make sure the appropriate module files are loaded
    for the programming environment for which the code was compiled.  For the
    setup phase:

    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    qsubm mfdn13 debug 30 --phase=0 --pool="Nmax02" --serialthreads=256 --mail-type=END,FAIL
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Then, for the MFDn diagonalization phase:

    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    qsubm mfdn13 debug 30 --phase=1 --pool="Nmax02" --ranks=1 --nodes=1 --threads=32 --mail-type=END,FAIL
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Then, the mop-up phase only involves some file system operations, and it can
    run either in a regular compute cue on the transfer queue:

    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    qsubm mfdn13 xfer 30 --phase=2 --pool="Nmax02" --mail-type=END,FAIL
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    You can use a dependency option (`--dependency=afterok:<job_id>`) to
    sequence these jobs, without having to wait for each one to finish.


runmfdn13gpu: harmonic oscillator direct run with MFDn v15, for use with postprocessor

    For a GPU run, we must disable calculation of one-body observables, since
    these are not yet GPU enabled, and use gpu version of the mfdn executable.
    Otherwise, this example is identical to `runmfdn13` above.
    
    Notes on job submission at NERSC.  The setup phase still should be submitted
    to CPU nodes, as in `runmfdn13` above (be sure to load the appropriate
    module files for the CPU programming environment):

    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    qsubm mfdn13gpu debug 30 --phase=0 --pool="Nmax02" --serialthreads=256 --mail-type=END,FAIL
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Then, for the MFDn diagonalization phase should be submitted to the GPU
    nodes (for this phase, now load the appropriate module files for the GPU
    programming environment):

    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    qsubm mfdn13gpu debug 30 --phase=1 --pool="Nmax02" --node-type=gpu --ranks=1 --nodes=1 --threads=32 --mail-type=END,FAIL --account=<account>
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Notice the `--node-type=gpu` option.  In place of `<account>` you should
    substitute the appropriate GPU allocation repository that the job is to be
    charged to (e.g., `m2032_g`).  And mop-up is the same as in `runmfdn13`
    above:

    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    qsubm mfdn13gpu xfer 30 --phase=2 --pool="Nmax02" --mail-type=END,FAIL
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

runmfdn15menj: diagonalization run with MFDn v15 menj 3-body variant

    (input interaction files not provided)

runmfdn16: shell model diagonalization runs in sd shell, with MFDn v15

    18O/20O/18F/19F/20N/25Mg, Wildenthal USD and Brown-Richter USDB interactions

    Interaction: example-data
    
    Usage:

        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        qsubm --pool=ALL --phase=0 mfdn16
        qsubm --pool=ALL --phase=1 mfdn16
        qsubm --pool=ALL --phase=2 mfdn16
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

runtransitions00: mfdn-transitions postprocessor run

    6Li Nmax02,Nmax04, hw15,hw20

    Interaction/operator: example-data

    Usage:

        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        qsubm --pool=ALL --phase=0 transitions00
        qsubm --pool=ALL --phase=1 transitions00
        qsubm --pool=ALL --phase=2 transitions00
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    or, for a quick test with just Nmax=2 runs

        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        qsubm --pool=Nmax02 --phase=0 transitions00
        qsubm --pool=Nmax02 --phase=1 transitions00
        qsubm --pool=Nmax02 --phase=2 transitions00
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Uses operator TBMEs from `example-data`.  Make sure to set NCCI_DATA_DIR_H2 to
    include `mcscript-ncci/docs/examples` (see `mcscript-ncci/INSTALL.md`).

    Uses wave functions created by runmfdn13.  Make sure to set
    NCCI_LIBRARY_PATH to include `mcscript-ncci/docs/examples` (see `mcscript-ncci/INSTALL.md`).

    Check that the task dictionary parameter `"mfdn-transitions_executable"` gives
    the correct location for your mfdn-transitions executable file within your
    mfdn installation directory.

    See `mcscript-ncci/docs/examples/example-results` for example results output.

    Notes on job submission at NERSC.  This provides a simple example of a
    single-node run.  First, make sure the appropriate module files are loaded
    for the programming environment for which the code was compiled.  For the
    setup phase:

    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    qsubm transitions00 debug 30 --phase=0 --pool="Nmax02" --serialthreads=256 --mail-type=END,FAIL
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Then, for the MFDn diagonalization phase:

    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    qsubm transitions00 debug 30 --phase=1 --pool="Nmax02" --ranks=8 --nodes=1 --threads=32 --mail-type=END,FAIL
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Then, the mop-up phase only involves some file system operations, and it can
    run either in a regular compute cue on the transfer queue:

    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    qsubm transitions00 xfer 30 --phase=2 --pool="Nmax02" --mail-type=END,FAIL
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    You can use a dependency option (`--dependency=afterok:<job_id>`) to
    sequence these jobs, without having to wait for each one to finish.
