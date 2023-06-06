# Summary of example run scripts #

05/09/23 (mac): Expand setup instructions.  Eliminate --here from example qsubm
invocations.

05/31/23 (mac): Add perlmutter-cpu parallel environment example.

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
    estimate using mfdnmem) and queue submission information (otherwise you'll
    be trying to run MFDn interactively on the front end, which may get people
    yelling at you -- or it may simply fail if the front-end machine has a
    different architecture from the compute nodes and the executable file is not
    compatible!).  However, at least the Nmax=2 example runs are are not
    computationally demanding.

    So first please make sure you are familiar with the principles of running
    jobs on your machine and of doing so properly with mcscript.

    E.g., for a single-node run at NERSC on perlmutter-cpu, the following
    command line would be reasonable for a first test run:

    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    qsubm mfdn13 debug 30 --phase=1 --pool="Nmax02" --ranks=1 --nodes=1 --threads=32 --serialthreads=256 --mail-type=END,FAIL
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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

    Sets up for runtransitions00.

    Uses operator TBMEs from `example-data`.  Make sure to set NCCI_DATA_DIR_H2 to
    include `mcscript-ncci/docs/examples` (see `mcscript-ncci/INSTALL.md`).

    See mcscript-ncci/docs/examples/example-results for example results output.

runmfdn14: harmonic oscillator Lanczos decomposition run with MFDn v15

    6Li Nmax02,Nmax04 hw15,hw20 (direct) op L2,S2,Nex

    Usage:

        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        qsubm --pool=ALL --phase=0 mfdn14
        qsubm --pool=ALL --phase=1 mfdn14
        qsubm --pool=ALL --phase=2 mfdn14
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    or, for a quick test with just Nmax=2 runs, select

        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        qsubm --pool=Nmax02 --phase=0 mfdn14
        qsubm --pool=Nmax02 --phase=1 mfdn14
        qsubm --pool=Nmax02 --phase=2 mfdn14
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Uses wave functions created by runmfdn13.  Make sure to set
    NCCI_LIBRARY_PATH to include `mcscript-ncci/docs/examples` (see
    `mcscript-ncci/INSTALL.md`).  For this example, you also need to set
    NCCI_DATA_DIR_DECOMPOSITION to include `mcscript-ncci/docs/examples`.

    The resulting Lanczos alpha-beta coefficients will be found in
    `results/lanczos`.


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