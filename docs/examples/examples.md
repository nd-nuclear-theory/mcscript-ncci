# Summary of example run scripts #

Setup: These examples make use of small example input TBME files found in the
subdirectory `example-data`.  In order for the scripting to find these input files,
make sure to set the environment variable `NCCI_DATA_DIR_H2` to include
`mcscript-ncci/docs/examples` (see `mcscript-ncci/INSTALL.md`).

runmfdn07: harmonic oscillator direct run with MFDn v15

    4He Nmax02 hw20 (direct)

    Interaction: example-data

    Usage: qsubm --here mfdn07

    We use tb-6 from `example-data`. Make sure to set NCCI_DATA_DIR_H2 to include
    `mcscript-ncci/docs/examples` (see `mcscript-ncci/INSTALL.md`).

runmfdn08: harmonic oscillator direct run with MFDn v15 b01

    4He Nmax02 hw20 (direct)

    Interaction: run0164-JISP16-tb-10

    Usage: qsubm --here mfdn08

    We use tb-10 as the smallest available set of files.  These are not provided
    in `mcscript-ncci/docs/examples`.

runmfdn09: general truncation direct run with MFDn v15

    4He weight=n+l<2.1 hw20 (direct)

    Interaction: run0164-JISP16-tb-10

    Usage: qsubm --here mfdn09

    We use tb-10 as the smallest available set of files.  These are not provided
    in `mcscript-ncci/docs/examples`.

runmfdn10: counting-only run with MFDn v15

    6He Nmax08 (counting)

    Usage: qsubm --here mfdn10

runmfdn11: manual orbital direct run with MFDn v15

    4He manual orbital file hw20 (direct)

    Interaction: run0164-JISP16-tb-10

    Usage: qsubm --here mfdn11

    We use tb-10 as the smallest available set of files.  These are not provided
    in `mcscript-ncci/docs/examples`.

runmfdn12: harmonic oscillator direct run with MFDn v15, plus custom input TBO

    4He Nmax02 hw20 (direct)

    Interaction: example-data

    Usage: qsubm --here mfdn12

    Uses operator TBMEs from `example-data`.  Make sure to set NCCI_DATA_DIR_H2 to
    include `mcscript-ncci/docs/examples` (see `mcscript-ncci/INSTALL.md`).

runmfdn13: harmonic oscillator direct run with MFDn v15, for use with postprocessor

    6Li Nmax02,Nmax04 hw15,hw20 (direct)

    Interaction: example-data

    Usage:

        qsubm --here --pool=ALL mfdn13

    or, for a quick test with just Nmax=2 runs

        qsubm --here --pool=Nmax02 mfdn13

    Sets up for runtransitions00.

    Uses operator TBMEs from `example-data`.  Make sure to set NCCI_DATA_DIR_H2 to
    include `mcscript-ncci/docs/examples` (see `mcscript-ncci/INSTALL.md`).

    See mcscript-ncci/docs/examples/example-results for example results output.

runmfdn14: harmonic oscillator Lanczos decomposition run with MFDn v15

    6Li Nmax02,Nmax04 hw15,hw20 (direct) op L2,S2,Nex

    Usage:

        qsubm --here --pool=ALL mfdn14

    or, for a quick test with just Nmax=2, M=1.0 runs

        qsubm --here --pool=Nmax02-M1.0 mfdn14

    Uses wave functions created by runmfdn13.  Make sure to set
    NCCI_LIBRARY_PATH to include `mcscript-ncci/docs/examples`
    (see `mcscript-ncci/INSTALL.md`).

runtransitions00: mfdn-transitions postprocessor run

    6Li Nmax02,Nmax04, hw15,hw20

    Interaction/operator: example-data

    Usage:

        qsubm --here --pool=ALL transitions00

    or, for a quick test with just Nmax=2 runs

        qsubm --here --pool=Nmax02 transitions00

    Uses operator TBMEs from `example-data`.  Make sure to set NCCI_DATA_DIR_H2 to
    include `mcscript-ncci/docs/examples` (see `mcscript-ncci/INSTALL.md`).

    Uses wave functions created by runmfdn13.  Make sure to set
    NCCI_LIBRARY_PATH to include `mcscript-ncci/docs/examples` (see `mcscript-ncci/INSTALL.md`).

    Check that the task dictionary parameter `"mfdn-transitions_executable"` gives
    the correct location for your mfdn-transitions executable file within your
    mfdn installation directory.

    See `mcscript-ncci/docs/examples/example-results` for example results output.